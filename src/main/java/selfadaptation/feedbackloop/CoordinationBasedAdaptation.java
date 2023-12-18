package selfadaptation.feedbackloop;

import java.util.HashMap;
import java.util.LinkedList;
import java.util.List;
import java.util.Map;

import be.kuleuven.cs.som.annotate.Basic;
import be.kuleuven.cs.som.annotate.Model;
import iot.QualityOfService;
import iot.SimulationRunner;
import iot.lora.LoraTransmission;
import iot.networkentity.Gateway;
import iot.networkentity.Mote;
import selfadaptation.instrumentation.FeedbackLoopGatewayBuffer;
import selfadaptation.instrumentation.MoteEffector;
import selfadaptation.instrumentation.MoteProbe;

/**
 * A class representing an adaptation approach for the simulation.
 */
public class CoordinationBasedAdaptation extends GenericFeedbackLoop {
    /**
     * A map to keep track of which gateway has already sent the packet.
     */
    @Model
    private FeedbackLoopGatewayBuffer gatewayBuffer;

    @Model
    private Map<Mote, List<Double>> reliableMinPowerBuffers;
    @Model
    private Map<Mote, List<Double>> getReliableMinPowerBuffers() {
        return this.reliableMinPowerBuffers;
    }
    @Model
    private void putReliableMinPowerBuffer(Mote mote, List<Double> reliableMinPowerBuffer) {
        this.reliableMinPowerBuffers.put(mote, reliableMinPowerBuffer);
    }


    @Model
    private Map<Mote, List<Double>> reliableDistanceGatewayBuffers;
    @Model
    private Map<Mote, List<Double>> getReliableDistanceGatewayBuffers() {
        return this.reliableDistanceGatewayBuffers;
    }
    @Model
    private void putReliableDistanceGatewayBuffers(Mote mote, List<Double> reliableDistanceGatewayBuffer) {
        this.reliableDistanceGatewayBuffers.put(mote,reliableDistanceGatewayBuffer);
    }

    private Map<Mote, Double> strengthAverage;
    public double getStrengthAverage(Mote mote) {
        return this.strengthAverage.getOrDefault(mote, 0.0);
    }

    private Map<Mote, Double> distanceAverage;
    public double getDistanceAverage(Mote mote) {
        return this.distanceAverage.getOrDefault(mote, 0.0);
    }

    public CoordinationBasedAdaptation() {
        super("Coordination-based");
        gatewayBuffer = new FeedbackLoopGatewayBuffer();
        reliableMinPowerBuffers = new HashMap<>();
        reliableDistanceGatewayBuffers = new HashMap<>();
        strengthAverage = new HashMap<>();
        distanceAverage = new HashMap<>();
    }

    /**
     * returns a map with gateway buffers.
     * @return A map with gateway buffers.
     */
    private FeedbackLoopGatewayBuffer getGatewayBuffer() {
        return gatewayBuffer;
    }

    /**
     * A method describing what the approach should do when being called on a mote.
     * @param mote The mote to adapt.
     */
    public void adapt(Mote mote, Gateway dataGateway) {
        getGatewayBuffer().add(mote,dataGateway);
        if (getGatewayBuffer().hasReceivedAllSignals(mote)) {
            List<LoraTransmission> receivedSignals;
            // compute signal strength
            receivedSignals = getGatewayBuffer().getReceivedSignals(mote);
            double receivedPower = receivedSignals.get(0).getTransmissionPower();

            for (LoraTransmission transmission : receivedSignals) {
                // System.out.println(transmission.getSender() + " " + transmission.getReceiver());
                if (receivedPower < transmission.getTransmissionPower()) {
                    receivedPower = transmission.getTransmissionPower();
                }
            }

            /**
             * If the buffer has an entry for the current mote, the new highest received signal strength is added to it,
             * else a new buffer is created and added to which we can add the signal strength.
             */
            List<Double> reliableMinPowerBuffer = new LinkedList<>();
            if (getReliableMinPowerBuffers().containsKey(mote)) {
                reliableMinPowerBuffer = getReliableMinPowerBuffers().get(mote);
            }
            reliableMinPowerBuffer.add(receivedPower);
            putReliableMinPowerBuffer(mote, reliableMinPowerBuffer);
            /**
             * If the buffer for the mote has 5 entries, the algorithm can start making adjustments.
             */
            if (getReliableMinPowerBuffers().get(mote).size() == 5) {
                /**
                 * The average is taken of the 5 entries.
                 */
                double average = getReliableMinPowerBuffers().get(mote).stream()
                    .mapToDouble(o -> o)
                    .average()
                    .orElse(0L);
                this.strengthAverage.put(mote, average);

                putReliableMinPowerBuffer(mote, new LinkedList<>());
            }

            System.out.println("Received signals " + receivedSignals.size());
            // compute distance1
            var env = SimulationRunner.getInstance().getEnvironment();
            double shortestDistance = Math.sqrt(Math.pow(env.getNetworkEntityById(receivedSignals.get(0).getReceiver()).getYPosInt()-receivedSignals.get(0).getYPos(),2)+
                    Math.pow(env.getNetworkEntityById(receivedSignals.get(0).getReceiver()).getXPosInt()-receivedSignals.get(0).getXPos(),2));

            for (LoraTransmission transmission: receivedSignals) {
                if (shortestDistance>Math.sqrt(Math.pow(env.getNetworkEntityById(transmission.getReceiver()).getYPosInt()-transmission.getYPos(),2)+
                        Math.pow(env.getNetworkEntityById(transmission.getReceiver()).getXPosInt()-transmission.getXPos(),2))) {
                    shortestDistance = Math.sqrt(Math.pow(env.getNetworkEntityById(transmission.getReceiver()).getYPosInt()-transmission.getYPos(),2)+
                            Math.pow(env.getNetworkEntityById(transmission.getReceiver()).getXPosInt()-transmission.getXPos(),2));
                }
            }

            /**
             * If the buffer has an entry for the current mote, the new the distance to the nearest gateway is added to it,
             * else a new buffer is created and added to which we can add the the distance to the nearest gateway.
             */
            List<Double> reliableDistanceGatewayBuffer;
            if (!getReliableDistanceGatewayBuffers().containsKey(mote)) {
                putReliableDistanceGatewayBuffers(mote, new LinkedList<>());
            }
            reliableDistanceGatewayBuffer = getReliableDistanceGatewayBuffers().get(mote);
            reliableDistanceGatewayBuffer.add(shortestDistance);
            putReliableDistanceGatewayBuffers(mote,reliableDistanceGatewayBuffer);
            /**
             * If the buffer for the mote has 4 entries, the algorithm can start making adjustments.
             */
            if (getReliableDistanceGatewayBuffers().get(mote).size() == 4) {
                /**
                 * The average is taken of the 4 entries.
                 */
                double average = 0;
                for (double distance : getReliableDistanceGatewayBuffers().get(mote)) {
                    average += distance;
                }
                average = average / 4;
                this.distanceAverage.put(mote, average);
            }
        }
    }
}

