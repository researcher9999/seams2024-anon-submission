package iot;

import be.kuleuven.cs.som.annotate.Basic;
import datagenerator.SensorDataGenerator;
import io.grpc.StatusRuntimeException;
import iot.lora.LoraTransmission;
import iot.networkentity.Gateway;
import iot.networkentity.Mote;
import iot.networkentity.MoteSensor;
import proto.grpc.Api.InitRequest;
import proto.grpc.Api.MoteAction;
import proto.grpc.Api.MoteInfoInit;
import proto.grpc.Api.MoteState;
import proto.grpc.Api.MotesActionRequest;
import proto.grpc.Api.MotesActionResponse;
import selfadaptation.feedbackloop.GenericFeedbackLoop;
import selfadaptation.feedbackloop.CoordinationBasedAdaptation;
import util.Statistics;
import util.TimeHelper;

import java.lang.ref.WeakReference;
import java.time.LocalTime;
import java.util.*;
import java.util.function.Predicate;

import com.google.rpc.Status;

/**
 * A class representing a simulation.
 */
public class Simulation {

    // region fields
    /**
     * The InputProfile used in the simulation.
     */
    private InputProfile inputProfile;
    /**
     * The Environment used in th simulation.
     */
    private WeakReference<Environment> environment;
    /**
     * The GenericFeedbackLoop used in the simulation.
     */
    private GenericFeedbackLoop approach;

    /**
     * A condition which determines if the simulation should continue (should return {@code false} when the simulation is finished).
     */
    private Predicate<Environment> continueSimulation;

    /**
     * Intermediate parameters used during simulation
     */
    private Map<Mote, LocalTime> timeMap;

    private MARLClient marlClient;

    private MotesActionResponse lastActionResponse;

    private boolean coordinationIsInitialized;

    private MotesActionRequest lastActionRequest;

    // endregion

    // region constructors

    public Simulation() {}

    // endregion

    // region getter/setters

    /**
     * Gets the Environment used in th simulation.
     * @return The Environment used in the simulation.
     */
    @Basic
    public Environment getEnvironment() {
        return environment.get();
    }
    /**
     * Sets the Environment used in th simulation.
     * @param environment  The Environment to use in the simulation.
     */
    @Basic
    public void setEnvironment(WeakReference<Environment> environment) {
        this.environment = environment;
    }

    /**
     * Gets the InputProfile used in th simulation.
     * @return The InputProfile used in the simulation.
     */
    @Basic
    public Optional<InputProfile> getInputProfile() {
        return Optional.ofNullable(inputProfile);
    }
    /**
     * Sets the InputProfile used in th simulation.
     * @param inputProfile  The InputProfile to use in the simulation.
     */
    @Basic
    public void setInputProfile(InputProfile inputProfile) {
        this.inputProfile = inputProfile;
    }

    /**
     * Gets the GenericFeedbackLoop used in th simulation.
     * @return The GenericFeedbackLoop used in the simulation.
     */
    @Basic
    public GenericFeedbackLoop getAdaptationAlgorithm() {
        return approach;
    }
    /**
     * Sets the GenericFeedbackLoop used in th simulation.
     * @param approach  The GenericFeedbackLoop to use in the simulation.
     */
    @Basic
    public void setAdaptationAlgorithm(GenericFeedbackLoop approach) {
        this.approach = approach;
    }


    public GenericFeedbackLoop getApproach() {
        return approach;
    }
    /**
     * Sets the GenericFeedbackLoop.
     * @param approach The GenericFeedbackLoop to set.
     */
    @Basic
    void setApproach(GenericFeedbackLoop approach) {
        if (getApproach()!= null) {
            getApproach().stop();
        }
        this.approach = approach;
        getApproach().start();
    }
    // endregion


    /**
     * Gets the probability with which a mote should be active from the input profile of the current simulation.
     * If no probability is specified, the probability is set to one.
     * Then it performs a pseudo-random choice and sets the mote to active/inactive for the next run, based on that probability.
     */
    private void setupMotesActivationStatus() {
        List<Mote> motes = this.getEnvironment().getMotes();
        Set<Integer> moteProbabilities = this.inputProfile.getProbabilitiesForMotesKeys();
        for (int i = 0; i < motes.size(); i++) {
            Mote mote = motes.get(i);
            double activityProbability = 1;
            if (moteProbabilities.contains(i))
                activityProbability = this.inputProfile.getProbabilityForMote(i);
            if (Math.random() >= 1 - activityProbability)
                mote.enable(true);
        }
    }

    /**
     * Check if all motes have arrived at their destination.
     * @return True if the motes are at their destinations.
     */
    private boolean areAllMotesAtDestination() {
        boolean arrived = this.getEnvironment().getMotes().stream()
        .allMatch(m -> !m.isEnabled() || m.isArrivedToDestination());
        // System.out.println("Motes arrived at destination " + arrived);
        // if (arrived == false) {
        //     for (Mote m : this.getEnvironment().getMotes()) {
        //         if (!m.isArrivedToDestination()) {
        //             System.out.println("Mote " + m.getEUI() + " has not arrived [" + m.getPosInt().getLeft() + " " + m.getPosInt().getRight() + "] movement speed " + m.getMovementSpeed());
        //         }
        //     }
        // }
        return arrived;
    }

    /**
     * Simulate a single step in the simulator.
     */
    public void simulateStep() {
        //noinspection SimplifyStreamApiCallChains

        this.getEnvironment().getMotes().stream()
            .filter(Mote::isEnabled)
            .map(mote -> { mote.consumePackets(); return mote;}) //DON'T replace with peek because the filtered mote after this line will not do the consume packet
            .filter(mote -> !mote.isArrivedToDestination())
            .filter(mote -> TimeHelper.secToMili( 1 / mote.getMovementSpeed()) <
                TimeHelper.nanoToMili(this.getEnvironment().getClock().getTime().toNanoOfDay() - timeMap.get(mote).toNanoOfDay()))
            .filter(mote -> TimeHelper.nanoToMili(this.getEnvironment().getClock().getTime().toNanoOfDay()) > TimeHelper.secToMili(Math.abs(mote.getStartMovementOffset())))
            .forEach(mote -> {
                timeMap.put(mote, this.getEnvironment().getClock().getTime());
                mote.getPath().getNextPoint(mote.getPathPositionIndex()).ifPresent(dst ->
                    this.getEnvironment().moveMote(mote, dst));
            });
        this.getEnvironment().getClock().tick(1);
    }

    public void simulateStepCoordination(boolean coordinate) {
        //noinspection SimplifyStreamApiCallChains
        // Coordination state machine
        if (coordinate) {
            if (!this.coordinationIsInitialized) {
                System.out.println("Initializing coordination.");
                var initRequestBuilder = InitRequest.newBuilder();
                int i = 0;
                for (Mote m : this.getEnvironment().getMotes()) {
                    var moteInitBuilder = MoteInfoInit.newBuilder();
                    moteInitBuilder.setMoteName("mote" + i);
                    moteInitBuilder.setEUI(m.getEUI());
                    moteInitBuilder.setSpreadingFactor(m.getSF());
                    for (MoteSensor ms : m.getSensors()) {
                        moteInitBuilder.addSensors(ms.name());
                    }
                    initRequestBuilder.addMoteInfos(moteInitBuilder.build());
                    i = i + 1;
                }
                marlClient.initialize(initRequestBuilder.build());
                this.coordinationIsInitialized = true;
            }

            switch(this.getEnvironment().getCoordinationStatus()) {
                case NOT_COORDINATED:
                if (this.getEnvironment().getClock().getTime().compareTo(this.getEnvironment().getNextCoordinationTime()) > 0) {
                    // System.out.println("NOT_COORDINATED -> COORDINATION_STARTED");
                    // iterate over motes, get observations, ask for actions
                    System.out.println(this.getEnvironment().getClock().getTime() + " " + this.getEnvironment().getNextCoordinationTime());
                    
                    var actionRequestBuilder = MotesActionRequest.newBuilder();
                    int i = 0;

                    actionRequestBuilder.setTimestep(this.getEnvironment().getClock().getTime().toNanoOfDay());

                    Statistics statistics = Statistics.getInstance();
                    for (Mote m : this.getEnvironment().getMotes()) {
                        var moteStateBuilder = MoteState.newBuilder();
                        String moteName = "mote" + i;
                        moteStateBuilder.setMoteName(moteName);
                        moteStateBuilder.setEUI(m.getEUI());
                        moteStateBuilder.setEnergyLevel(m.getEnergyLevel());
                        moteStateBuilder.setMovementSpeed(m.getMovementSpeed());
                        moteStateBuilder.setTransmissionPower(m.getTransmissionPower());
                        moteStateBuilder.setSpreadingFactor(m.getSF());
                        moteStateBuilder.setPosX(m.getXPosDouble());
                        moteStateBuilder.setPosY(m.getYPosDouble());
                        moteStateBuilder.setPeriodSendingPacket(m.getPeriodSendingPacket());
                        
                        long collidedTransmissions = 0;
                        for (Gateway gw : this.getEnvironment().getGateways()) {
                            long ct = statistics.getAllReceivedTransmissions(gw.getEUI(), this.getEnvironment().getNumberOfRuns() - 1).stream()
                                        .filter(t -> t.getSender() == m.getEUI())
                                        .filter(t -> t.isCollided())
                                        .map(t -> {t.getCollidedWith().forEach(tc -> moteStateBuilder.putCollidedWith(tc.getSender(), moteStateBuilder.getCollidedWithOrDefault(tc.getSender(), 0) + 1)); return t;})
                                        .count();
                            collidedTransmissions += ct;
                        }
                        System.out.println(collidedTransmissions);
                        moteStateBuilder.setCollidedTransmissions(collidedTransmissions);

                        // We won't consider "duplicated" transmissions
                        // long duplicatedTransmissions = 0;
                        // for (Gateway gw : this.getEnvironment().getGateways()) {
                        //     long ct = statistics.getAllReceivedTransmissions(gw.getEUI(), this.getEnvironment().getNumberOfRuns() - 1).stream()
                        //                 .filter(t -> t.getSender() == m.getEUI())
                        //                 .filter(t -> t.isDuplicated())
                        //                 .map(t -> {t.getDuplicatedBy().forEach(tc -> moteStateBuilder.putDuplicatedWith(tc.getSender(), moteStateBuilder.getDuplicatedWithOrDefault(tc.getSender(), 0) + 1)); return t;})
                        //                 .count();
                        //     duplicatedTransmissions += ct;
                        // }
                        // moteStateBuilder.setDuplicatedTransmissions(duplicatedTransmissions);

                        long countFailedTransmissionsGateway = 0L;
                        List<Long> failedTransmissionsGateway = statistics.getFailedTransmissionToGatewaysEntry(m.getEUI(), this.getEnvironment().getNumberOfRuns() - 1);
                        if (failedTransmissionsGateway.size() > 0) {
                            System.out.println("failedTransmissionsGateway.size() > 0");
                            // Doesn't seem to do anything so we disable it
                            // countFailedTransmissionsGateway = failedTransmissionsGateway.stream().reduce(0L, Long::sum);
                            countFailedTransmissionsGateway = 0L;
                            moteStateBuilder.setFailedTransmissionsGateways(countFailedTransmissionsGateway);
                        } else {
                            moteStateBuilder.setFailedTransmissionsGateways(0);
                        }

                        double usedEnergy = 0.0;
                        try {
                            usedEnergy = statistics.getUsedEnergy(m.getEUI(), this.getEnvironment().getNumberOfRuns() - 1).stream().reduce(0.0, Double::sum);
                        } catch (NullPointerException e) {
                            // e.printStackTrace();
                        }
                        moteStateBuilder.setUsedEnergy(usedEnergy);

                        double deltaEnergy = usedEnergy;
                        long deltaFailed = countFailedTransmissionsGateway;
                        long deltaCollisions = collidedTransmissions;
                        if (this.lastActionRequest != null) {
                            MoteState oldMoteState = this.lastActionRequest.getMoteStatesList().stream().filter(mproto -> mproto.getEUI() == m.getEUI()).findFirst().orElseThrow();
                            deltaEnergy = usedEnergy - oldMoteState.getUsedEnergy();
                            deltaFailed = countFailedTransmissionsGateway - oldMoteState.getFailedTransmissionsGateways();
                            deltaCollisions = collidedTransmissions - oldMoteState.getCollidedTransmissions();

                            for (Mote mo : this.getEnvironment().getMotes()) {
                                long deltaCollidedWith = moteStateBuilder.getCollidedWithMap().getOrDefault(mo.getEUI(), 0L) - oldMoteState.getCollidedWithMap().getOrDefault(mo.getEUI(), 0L);
                                moteStateBuilder.putDeltaCollidedWith(mo.getEUI(), deltaCollidedWith);
                            }
                        } else {
                            for (Mote mo : this.getEnvironment().getMotes()) {
                                long deltaCollidedWith = 0L;
                                moteStateBuilder.putDeltaCollidedWith(mo.getEUI(), deltaCollidedWith);
                            }
                        }

                        moteStateBuilder.setDeltaUsedEnergy(deltaEnergy);
                        moteStateBuilder.setDeltaFailedTransmissionsGateways(deltaFailed);
                        moteStateBuilder.setDeltaCollisions(deltaCollisions);

                        CoordinationBasedAdaptation instrumentation = (CoordinationBasedAdaptation) this.approach;
                        moteStateBuilder.setAverageGatewayDistance(instrumentation.getDistanceAverage(m));
                        moteStateBuilder.setAverageReceivedTransmissionPow(instrumentation.getStrengthAverage(m));

                        actionRequestBuilder.addMoteStates(moteStateBuilder.build());
                        i = i + 1;
                    }
                    
                    MotesActionRequest actionRequest = actionRequestBuilder.build();
                    this.lastActionRequest = actionRequest;
                    lastActionResponse = marlClient.getActions(actionRequest);

                    this.getEnvironment().setCoordinationStarted();
                    this.getEnvironment().setCoordinationStatus(Environment.CoordinationStatusEnum.COORDINATION_STARTED);
                }
                break;
                case COORDINATION_STARTED:
                if (this.getEnvironment().getClock().getTime().compareTo(this.getEnvironment().getCoordinationFinish()) > 0) {
                    // System.out.println("COORDINATION_STARTED -> COORDINATION_FINISHED");
                    this.getEnvironment().setCoordinationStatus(Environment.CoordinationStatusEnum.COORDINATION_FINISHED);
                }   
                break;
                case COORDINATION_FINISHED:
                // System.out.println("COORDINATION_FINISHED -> NO_COORDINATION");   
                for (MoteAction ma : lastActionResponse.getMoteActionsList()) {
                    Optional<Mote> mo  = this.getEnvironment().getMotes().stream().filter(mote -> mote.getEUI() == ma.getEUI()).findFirst();
                    if (mo.isPresent()) {
                        Mote m = mo.get();
                        // m.setEnergyLevel(ma.getEnergyLevel());
                        // m.setMovementSpeed(ma.getMovementSpeed());
                        System.out.println(ma.getTransmissionPower() + " " + ma.getPeriodSendingPacket() + " " + ma.getSpreadingFactor());
                        m.setTransmissionPower(ma.getTransmissionPower());
                        m.setPeriodSendingPacket(ma.getPeriodSendingPacket());
                        m.setSF(ma.getSpreadingFactor());
                    }
                }
                this.getEnvironment().tickCoordinationClock();
                this.getEnvironment().setCoordinationStatus(Environment.CoordinationStatusEnum.NOT_COORDINATED);
                break;
            }
        }

        this.getEnvironment().getMotes().stream()
            .filter(Mote::isEnabled)
            .map(mote -> { mote.consumePackets(); return mote;}) //DON'T replace with peek because the filtered mote after this line will not do the consume packet
            .filter(mote -> !mote.isArrivedToDestination())
            .filter(mote -> TimeHelper.secToMili( 1 / mote.getMovementSpeed()) <
                TimeHelper.nanoToMili(this.getEnvironment().getClock().getTime().toNanoOfDay() - timeMap.get(mote).toNanoOfDay()))
            .filter(mote -> TimeHelper.nanoToMili(this.getEnvironment().getClock().getTime().toNanoOfDay()) > TimeHelper.secToMili(Math.abs(mote.getStartMovementOffset())))
            .forEach(mote -> {
                timeMap.put(mote, this.getEnvironment().getClock().getTime());
                mote.getPath().getNextPoint(mote.getPathPositionIndex()).ifPresent(dst ->
                    this.getEnvironment().moveMote(mote, dst));
            });
        this.getEnvironment().getClock().tick(1);
    }




    public boolean isFinished() {
	Environment env = this.getEnvironment();
        return !this.continueSimulation.test(env);
    }


    private void setupSimulation(Predicate<Environment> pred) {
        this.timeMap = new HashMap<>();

        marlClient = new MARLClient("127.0.0.1", 7779);
        this.coordinationIsInitialized = false;
        setupMotesActivationStatus();

        this.getEnvironment().getGateways().forEach(Gateway::reset);

        this.getEnvironment().getMotes().forEach(mote -> {
            // Reset all the sensors of the mote
            mote.getSensors().stream()
                .map(MoteSensor::getSensorDataGenerator)
                .forEach(SensorDataGenerator::reset);

            // Initialize the mote (e.g. reset starting position)
            mote.reset();

            timeMap.put(mote, this.getEnvironment().getClock().getTime());

            // Add initial triggers to the clock for mote data transmissions (transmit sensor readings)
            this.getEnvironment().getClock().addTrigger(LocalTime.ofSecondOfDay(mote.getStartSendingOffset()), () -> {
                mote.sendToGateWay(
                    mote.getSensors().stream()
                        .flatMap(s -> s.getValueAsList(mote.getPosInt(), mote.getPathPosition(), this.getEnvironment().getClock().getTime()).stream())
                        .toArray(Byte[]::new),
                    new HashMap<>());
                return this.getEnvironment().getClock().getTime().plusSeconds(mote.getPeriodSendingPacket());
            });
        });

        this.continueSimulation = pred;
    }

    void setupSingleRun(boolean shouldResetHistory) {
        if (shouldResetHistory) {
            this.getEnvironment().resetHistory();
        }

        this.setupSimulation((env) -> !areAllMotesAtDestination());
    }

    void setupTimedRun() {
        this.getEnvironment().resetHistory();

        var finalTime = this.getEnvironment().getClock().getTime()
            .plus(inputProfile.getSimulationDuration(), inputProfile.getTimeUnit());
        this.setupSimulation((env) -> env.getClock().getTime().isBefore(finalTime));
    }

    public MARLClient getMarlClient() {
        return marlClient;
    }
}
