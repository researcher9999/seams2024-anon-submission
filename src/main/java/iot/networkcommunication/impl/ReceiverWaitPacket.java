package iot.networkcommunication.impl;

import iot.GlobalClock;
import iot.lora.LoraTransmission;
import iot.networkcommunication.api.Receiver;
import iot.networkentity.Mote;
import iot.networkentity.MoteSensor;
import iot.networkentity.NetworkEntity;
import util.Pair;
import util.TimeHelper;

import java.time.Duration;
import java.time.temporal.ChronoUnit;
import java.util.ArrayList;
import java.util.LinkedList;
import java.util.List;
import java.util.function.Consumer;
import java.util.stream.Collectors;

public class ReceiverWaitPacket implements Receiver {

    // The levels of power in between which it can discriminate.
    private final double transmissionPowerThreshold;
    private Consumer<LoraTransmission> consumerPacket;

    private List<LoraTransmission> transmissions = new LinkedList<>();

    private GlobalClock clock;

    private final NetworkEntity receiver;

    public ReceiverWaitPacket(NetworkEntity receiver, double transmissionPowerThreshold, GlobalClock clock) {
        this.transmissionPowerThreshold = transmissionPowerThreshold;
        this.receiver = receiver;
        this.clock = clock;
    }

    @Override
    public long getID() {
        return receiver.getEUI();
    }

    @Override
    public void receive(LoraTransmission transmission) {
        var collidedTransmission = transmissions.stream()
            .filter(t -> collision(transmission, t))
            .map(t -> transmission.addToCollidedWith(t))
            .map(t -> t.addToCollidedWith(transmission))
            .collect(Collectors.toList());
        collidedTransmission.forEach(LoraTransmission::setCollided);
        if (!collidedTransmission.isEmpty()) {
            transmission.setCollided();
        }
        // var duplicatedTransmission = transmissions.stream()
        //     .filter(t-> duplication(transmission, t))
        //     .map(t -> transmission.addToDuplicatedBy(t))
        //     .map(t -> t.addToDuplicatedBy(transmission))
        //     .collect(Collectors.toList());
        // duplicatedTransmission.forEach(LoraTransmission::setDuplicated);
        // if (!duplicatedTransmission.isEmpty()) {
        //     transmission.setDuplicated();
        // }
        transmissions.add(transmission);
        clock.addTriggerOneShot(transmission.getDepartureTime().plus((long)transmission.getTimeOnAir(), ChronoUnit.MILLIS),()->{
            transmission.setArrived();
            consumerPacket.accept(transmission);
        });
    }

    /**
     * Checks if two packets collide according to the model
     * @param a The first packet.
     * @param b The second packet.
     * @return true if the packets collide, false otherwise.
     */
    private boolean collision(LoraTransmission a, LoraTransmission b) {
	//System.out.println("[" + a.getSender() + " " + a.getReceiver() + "] " + " [" + b.getSender() + " " + b.getReceiver() + "]");

	// transmissionPowerThresholds seems to be 1.0 for motes.
        return a.getSpreadingFactor() == b.getSpreadingFactor() &&     //check spreading factor
            a.getTransmissionPower() - b.getTransmissionPower() < transmissionPowerThreshold && //check transmission power
            Math.abs(Duration.between(a.getDepartureTime().plusNanos(TimeHelper.miliToNano((long)a.getTimeOnAir()) / 2), //check time on air
                b.getDepartureTime().plusNanos(TimeHelper.miliToNano((long)b.getTimeOnAir()) / 2)).toNanos())
                < TimeHelper.miliToNano((long)a.getTimeOnAir()) / 2 + TimeHelper.miliToNano((long)b.getTimeOnAir()) / 2;
    }

    // if two motes have the same sensor type and are within a certain distance to each other,
    // then their transmissions are considered "duplicated"
    private boolean duplication(LoraTransmission a, LoraTransmission b) {
        NetworkEntity entity_a = this.receiver.getEnvironment().getNetworkEntityById(a.getSender());
        NetworkEntity entity_b = this.receiver.getEnvironment().getNetworkEntityById(b.getSender());

        boolean duplicated = false;
        if ((entity_a instanceof Mote) && (entity_b instanceof Mote) && (entity_a.getEUI() != entity_b.getEUI())) {
            Mote mote_a = (Mote) entity_a;
            Mote mote_b = (Mote) entity_b;

            boolean same_sensor = false;
            for (var sensor_a : mote_a.getSensors()) {
                for (var sensor_b : mote_b.getSensors()) {
                    if (sensor_a == sensor_b) {
                        same_sensor = true;
                        break;
                    }
                }
                if (same_sensor) {
                    break;
                }
            }
            if (same_sensor) {
                double distance = Math.sqrt(Math.pow(a.getXPos() - b.getXPos(), 2) + Math.pow(a.getYPos() - b.getYPos(), 2)); 
                if (distance < 250.0) {
                    duplicated = true;
                }
                // System.out.println(distance + " " + mote_a.getEUI() + " " + mote_b.getEUI() + " " + duplicated);
            }
        }
        return duplicated;
    }

    @Override
    public Pair<Double, Double> getReceiverPosition() {
        return new Pair<>(receiver.getXPosDouble(), receiver.getYPosDouble());
    }

    @Override
    public Pair<Integer, Integer> getReceiverPositionAsInt() {
        return receiver.getPosInt();
    }

    @Override
    public Receiver setConsumerPacket(Consumer<LoraTransmission> consumerPacket) {
        this.consumerPacket = consumerPacket;
        return this;
    }

    @Override
    public void reset() {
        transmissions.clear();
    }
}
