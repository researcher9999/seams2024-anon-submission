package nogui;

import java.io.BufferedWriter;
import java.io.File;
import java.io.FileWriter;
import java.io.IOException;
import java.util.LinkedList;
import java.util.List;

import org.jfree.data.xy.XYSeries;
import org.jfree.data.xy.XYSeriesCollection;

import util.Pair;
import util.Statistics;

import iot.networkentity.Gateway;
import iot.networkentity.Mote;
import iot.networkentity.MoteSensor;
import iot.networkentity.NetworkEntity;
import iot.SimulationRunner;
import iot.lora.LoraTransmission;
import iot.Simulation;
import iot.Environment;
import iot.InputProfile;
import iot.QualityOfService;
import selfadaptation.adaptationgoals.IntervalAdaptationGoal;
import selfadaptation.adaptationgoals.ThresholdAdaptationGoal;
import util.Constants;

public class MainNoGUI {
	private static double usedEnergy = 0;
	private static int packetsLost = 0;
	private static int packetsSent = 0;

    public static void main(String[] args) {
	SimulationRunner simulationRunner = SimulationRunner.getInstance();
	System.out.println("Hello world!");
	File configFile = new File("/home/paul/Documents/Projects/DingNet/settings/configurations/demo_3_motes.xml");
	simulationRunner.loadConfigurationFromFile(configFile);

	Simulation simulation = simulationRunner.getSimulation();
    QualityOfService QoS = simulationRunner.getQoS();
	IntervalAdaptationGoal intervalAdaptationGoal = new IntervalAdaptationGoal(2.0, 5.0);

	System.out.println("Running with SEED: " + Constants.SEED);

	for (InputProfile profile : simulationRunner.getInputProfiles()) {
	    System.out.println(profile.getName());
	}

	simulation.setInputProfile(simulationRunner.getInputProfiles().get(0));
	// simulationRunner.setApproach("Signal-based");
	// simulationRunner.setApproach("Distance-based");
	simulationRunner.setApproach("Coordination-based");
        // simulation.getInputProfile().ifPresent(inputProfile -> {
        //     inputProfile.putAdaptationGoal("reliableCommunication", intervalAdaptationGoal);
        //     QoS.putAdaptationGoal("reliableCommunication", inputProfile.getQualityOfServiceProfile().getAdaptationGoal("reliableCommunication"));
        //     // updateAdaptationGoals();
        // });

	simulationRunner.setupSingleRun();
	simulationRunner.simulateNoUpdate(true);

	try {
		simulationRunner.simulationWaitFinish();
	} catch (InterruptedException e) {
		e.printStackTrace();
	}

	System.out.println(simulationRunner.getEnvironment().getClock().getTime());

	int i = 0;
	for (Mote mote: simulationRunner.getEnvironment().getMotes()){
		writePowerDataForMotes(mote, 0, simulationRunner.getEnvironment());
		writeDistanceDataForMotes(mote, 0, simulationRunner.getEnvironment());
		writeStatisticsForMote(mote, 0, simulationRunner.getEnvironment());
		i = i+1;
	}
	writeTotalStatistics(0, simulationRunner.getEnvironment());

	File result_file = new File("/home/paul/Documents/Projects/DingNet/nogui-output-signalbased-reliableefficient-demo.xml");
	simulationRunner.saveSimulationToFile(result_file);
    }

	private static void writePowerDataForMotes(Mote mote, int run, Environment environment) {
		LinkedList<List<Pair<NetworkEntity, Pair<Integer, Double>>>> transmissionsMote = new LinkedList<>();

		Statistics statistics = Statistics.getInstance();

		for (Gateway gateway : environment.getGateways()) {
			transmissionsMote.add(new LinkedList<>());
			for (LoraTransmission transmission : statistics.getAllReceivedTransmissions(gateway.getEUI(), run)) {
				if (transmission.getSender() == mote.getEUI()) {
					if (!transmission.isCollided())
						transmissionsMote.getLast().add(
								new Pair<>(environment.getNetworkEntityById(transmission.getReceiver()),
										new Pair<>(transmission.getDepartureTime().toSecondOfDay(),
												transmission.getTransmissionPower())));
					else {
						transmissionsMote.getLast().add(
								new Pair<>(environment.getNetworkEntityById(transmission.getReceiver()),
										new Pair<>(transmission.getDepartureTime().toSecondOfDay(), (double) 20)));
					}
				}
			}
			if (transmissionsMote.getLast().isEmpty()) {
				transmissionsMote.remove(transmissionsMote.size() - 1);
			}
		}
		for (List<Pair<NetworkEntity, Pair<Integer, Double>>> list : transmissionsMote) {
			NetworkEntity receiver = list.get(0).getLeft();
			int gatewayIndex = environment.getGateways().indexOf(receiver) + 1;
			File power_results_file = new File("/home/paul/Documents/Projects/DingNet/power_results_"
			+ mote.getEUI() + "_" + gatewayIndex + ".csv");
			try (BufferedWriter writer = new BufferedWriter(new FileWriter(power_results_file))) {
				// noinspection SuspiciousMethodCalls Here we know for certain that the receiver
				// is a gateway (packets are only sent to gateways)

				for (Pair<NetworkEntity, Pair<Integer, Double>> data : list) {
					writer.write("" + data.getRight().getLeft() + "," + data.getRight().getRight());
					writer.newLine();
				}
				writer.close();
			} catch (IOException e) {
				// TODO Auto-generated catch block
				e.printStackTrace();
			}
		}
	}

	private static void writeDistanceDataForMotes(Mote mote, int run, Environment environment) {
        LinkedList<LinkedList<LoraTransmission>> transmissionsMote = new LinkedList<>();
        Statistics statistics = Statistics.getInstance();

        for (Gateway gateway : environment.getGateways()) {
            transmissionsMote.add(new LinkedList<>());
            for (LoraTransmission transmission : statistics.getAllReceivedTransmissions(gateway.getEUI(), run)) {
                if (transmission.getSender() == mote.getEUI()) {
                    transmissionsMote.getLast().add(transmission);
                }
            }
            if (transmissionsMote.getLast().isEmpty()) {
                transmissionsMote.remove(transmissionsMote.size() - 1);
            }
        }
        for (LinkedList<LoraTransmission> list : transmissionsMote) {
            NetworkEntity receiver = environment.getNetworkEntityById(list.get(0).getReceiver());

            //noinspection SuspiciousMethodCalls Here we know for certain that the receiver is a gateway (packets are only sent to gateways)
            int i = 0;
			int gatewayIndex = environment.getGateways().indexOf(receiver) + 1;
			File distance_results_file = new File("/home/paul/Documents/Projects/DingNet/distance_results_"
			+ mote.getEUI() + "_" + gatewayIndex + ".csv");
			try (BufferedWriter writer = new BufferedWriter(new FileWriter(distance_results_file))) {
				for (LoraTransmission transmission : list) {			
					Number dist = (Number) Math.sqrt(Math.pow(environment.getNetworkEntityById(transmission.getReceiver()).getYPosInt() - transmission.getYPos(), 2) +
									Math.pow(environment.getNetworkEntityById(transmission.getReceiver()).getXPosInt() - transmission.getXPos(), 2));
					writer.write("" + i + "," + dist);
					writer.newLine();
					i = i + 1;
				}
			writer.close();
			} catch (IOException e) {
				// TODO Auto-generated catch block
				e.printStackTrace();
			}
        }

    }

	private static void writeStatisticsForMote(Mote mote, int run, Environment environment) {
		MainNoGUI.packetsSent = 0;
		MainNoGUI.packetsLost = 0;
		MainNoGUI.usedEnergy = 0;

        Statistics statistics = Statistics.getInstance();
        environment.getGateways().forEach(gw ->
            statistics.getAllReceivedTransmissions(gw.getEUI(), run).stream()
                .filter(t -> t.getSender() == mote.getEUI())
                .forEach(t -> {
                    MainNoGUI.packetsSent++;
                    if (t.isCollided()) {
                        MainNoGUI.packetsLost++;
                    }
                })
        );
        statistics.getUsedEnergy(mote.getEUI(), run).forEach(energy -> MainNoGUI.usedEnergy += energy);

		File mote_stats_file = new File("/home/paul/Documents/Projects/DingNet/mote_stats_results_"
		+ mote.getEUI() + ".csv");

		try (BufferedWriter writer = new BufferedWriter(new FileWriter(mote_stats_file))) {
			// noinspection SuspiciousMethodCalls Here we know for certain that the receiver
			// is a gateway (packets are only sent to gateways)
			writer.write("" + MainNoGUI.packetsSent + "," + MainNoGUI.packetsLost + "," + MainNoGUI.usedEnergy);
			writer.newLine();
			writer.close();
		} catch (IOException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}
	}

	private static void writeTotalStatistics(int run, Environment environment) {
		MainNoGUI.packetsSent = 0;
		MainNoGUI.packetsLost = 0;
		MainNoGUI.usedEnergy = 0;

        Statistics statistics = Statistics.getInstance();
        environment.getGateways().forEach(gw ->
            statistics.getAllReceivedTransmissions(gw.getEUI(), run).stream()
                .forEach(t -> {
                    MainNoGUI.packetsSent++;
                    if (t.isCollided()) {
                        MainNoGUI.packetsLost++;
                    }
                })
        );
		environment.getMotes().forEach(mo -> 
			statistics.getUsedEnergy(mo.getEUI(), run).forEach(energy -> MainNoGUI.usedEnergy += energy)
		);

		File mote_stats_file = new File("/home/paul/Documents/Projects/DingNet/total_stats_results.csv");

		try (BufferedWriter writer = new BufferedWriter(new FileWriter(mote_stats_file))) {
			// noinspection SuspiciousMethodCalls Here we know for certain that the receiver
			// is a gateway (packets are only sent to gateways)
			writer.write("" + MainNoGUI.packetsSent + "," + MainNoGUI.packetsLost + "," + MainNoGUI.usedEnergy);
			writer.newLine();
			writer.close();
		} catch (IOException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}
	}

    // private void updateAdaptationGoals() {
    //     QualityOfService QoS = simulationRunner.getQoS();

    //     relComLabel.setText(String.format("Interval: %s", QoS.getAdaptationGoal("reliableCommunication").toString()));
    //     enConLabel.setText(String.format("Threshold: %s", QoS.getAdaptationGoal("energyConsumption").toString()));
    //     colBoundLabel.setText(String.format("Threshold: %.2f", Double.parseDouble(QoS.getAdaptationGoal("collisionBound").toString()) * 100));
    // }
}
