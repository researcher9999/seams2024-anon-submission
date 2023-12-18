from proto_generated.api_pb2.api_pb2 import MotesActionResponse, MotesActionRequest, RANDOM, COORDINATED, UNCOORDINATED, NOADAPTATION, QtablesRewards, QtableReward

import itertools

import numpy as np
import networkx as nx
import time

import matplotlib.pyplot as plt

# from pydcop.dcop.dcop import DCOP
# from pydcop.dcop.objects import Domain, Variable, create_variables, create_agents
# from pydcop.dcop.relations import NAryFunctionRelation, UnaryFunctionRelation, NAryMatrixRelation
# from pydcop.infrastructure.run import solve
# from pydcop.utils.graphs import display_graph, display_bipartite_graph
# from pydcop.computations_graph import pseudotree
# from pydcop.distribution import oneagent

from enum import Enum

import pytoulbar2 as ptb2

import pandas as pd
import sqlalchemy

import math

import sys

# DISCRETIZATION_STEPS = 5
DISCRETIZATION_STEPS = 5
DISCRETIZATION_STEPS_FT = 1
DISCRETIZATION_STEPS_SF = 6
DISCRETIZATION_STEPS_SR = 1

ACTION_SIZE_PREF = DISCRETIZATION_STEPS * DISCRETIZATION_STEPS_SR * DISCRETIZATION_STEPS_SF
ACTION_SIZE_CONST = ACTION_SIZE_PREF * ACTION_SIZE_PREF

#REWARD_COEFF_FAILEDTRANS = 1.0
REWARD_COEFF_FAILEDTRANS = 0.0
REWARD_COEFF_ENERGY = 0.001 # for 6 motes
# REWARD_COEFF_ENERGY = 0.01 # for 4 motes
# REWARD_COEFF_ENERGY = 0.01 # for 3 motes
#REWARD_COEFF_COLLISIONS = 10.0
REWARD_COEFF_COLLISIONS = 1.0

#ENGINE_MOTES = sqlalchemy.create_engine("sqlite:///results_motes.sqlite3", echo=False)
#ENGINE_REWARDS = sqlalchemy.create_engine("sqlite:///results_rewards.sqlite3", echo=False)
# ENGINE = sqlalchemy.create_engine("sqlite:///results.sqlite3", echo=False)

Q_INIT_VAL = 0
DECIMALS = 6

import cProfile

class AdaptationType(Enum):
    COORDINATED = 1
    UNCOORDINATED = 2
    NOADAPTATION = 3
    RANDOM = 4

    @staticmethod
    def from_str(label):
        if label == "coordinated":
            return AdaptationType.COORDINATED
        elif label == "uncoordinated":
            return AdaptationType.UNCOORDINATED
        elif label == "noadaptation":
            return AdaptationType.NOADAPTATION
        elif label == "random":
            return AdaptationType.RANDOM
        else:
            NotImplementedError

    @staticmethod
    def to_str(enum):
        if enum == AdaptationType.COORDINATED:
            return "coordinated"
        elif enum == AdaptationType.UNCOORDINATED:
            return "uncoordinated"
        elif enum == AdaptationType.RANDOM:
            return "random"
        elif enum == AdaptationType.NOADAPTATION:
            return "noadaptation"

    @staticmethod
    def to_proto(enum):
        if enum == AdaptationType.COORDINATED:
            return COORDINATED
        elif enum == AdaptationType.UNCOORDINATED:
            return UNCOORDINATED
        elif enum == AdaptationType.RANDOM:
            return RANDOM
        elif enum == AdaptationType.NOADAPTATION:
            return NOADAPTATION

class QLearning:
    def __init__(self, motes, seed, adaptation_type="coordinated", results_path="results.sqlite3"):
        self.motes = motes
        self.epsilon = 0.8
        self.learning_rate = 0.2
        self.discount_factor = 0.9
        self.epsilon_decay = 0.995
    
        self.iteration = 0

        self.results_path = results_path

        self.seed = seed
        np.random.seed(seed)

        self.transmission_powers = np.arange(2, 12, dtype=np.int32)
        self.spreading_factors = np.arange(7, 13, dtype=np.int32)
        self.period_sending_packets = np.zeros(10, dtype=np.int32) + 5

        self.last_action = {}
        self.last_observation = None

        self.adaptation_type = AdaptationType.from_str(adaptation_type)


        if self.adaptation_type == AdaptationType.UNCOORDINATED:
            self.Qtables_uncoordinated = {}
            for m in self.motes:
                Qtable = self.construct_q_table_uncoordinated()
                self.Qtables_uncoordinated[m.name] = Qtable
        else:
            #self.graph = self.construct_coordination_graph("cycle")
            #self.graph = self.construct_coordination_graph_sf()
            self.graph = self.construct_coordination_graph_pairwise()
            self.construct_q_tables(self.graph)

        self.history_observations = []
        self.history_actions = []
        self.history_rewards = []

        self.history_benchmarks = {"iteration": [], "execTime": []}

        if self.adaptation_type == AdaptationType.RANDOM:
            self.epsilon = 1.0

        self.profiler = cProfile.Profile()

        self.ENGINE = sqlalchemy.create_engine("sqlite:///{}".format(self.results_path), echo=False)

    def get_epsilon(self):
        epsilon = self.epsilon * math.pow(self.epsilon_decay, self.iteration)
        return epsilon
        
    def do_coordination(self, observations):
        start_time = time.perf_counter()
        # results_dcop = self.construct_dcop_instance(self.graph, observations)
        results_toulbar = self.construct_toulbar2_instance(self.graph, observations)

        #print("DCOP ",results_dcop, " value ", self.get_actions_value(results_dcop, observations))
        #print("Toulbar ", results_toulbar, " value ", self.get_actions_value(results_dcop, observations))
        #time.sleep(3)
        end_time = time.perf_counter()
        self.history_benchmarks["iteration"].append(self.iteration)
        self.history_benchmarks["execTime"].append(end_time - start_time) # in seconds
        return results_toulbar
        # return results_dcop

    def take_action(self, observations):
        response = MotesActionResponse()
        self.history_observations.append(observations)
        self.last_observation = observations

        if self.adaptation_type == AdaptationType.NOADAPTATION:
            for m in self.motes:
                m_request = list(filter(lambda mproto : m.EUI == mproto.EUI, observations.moteStates))[0]
                m_proto = response.moteActions.add()
                m_proto.moteName = m.name
                m_proto.EUI = m.EUI
                m_proto.transmissionPower = m_request.transmissionPower
                m_proto.periodSendingPacket = m_request.periodSendingPacket
                m_proto.spreadingFactor = m_request.spreadingFactor            
                m_proto.selWay = AdaptationType.to_proto(self.adaptation_type)

                #self.last_action[m.name] = action

            #    response.timestep = observations.timestep
            #    self.history_actions.append(response)
            #return response

        elif np.random.random_sample() < self.get_epsilon() or self.adaptation_type == AdaptationType.RANDOM:
            print("Picking random actions.")
            for m in self.motes:
                m_proto = response.moteActions.add()
                m_proto.moteName = m.name
                m_proto.EUI = m.EUI
                idx_TP = np.random.choice(DISCRETIZATION_STEPS)
                idx_SR = np.random.choice(DISCRETIZATION_STEPS_SR)
                idx_SF = np.random.choice(DISCRETIZATION_STEPS_SF)
                m_proto.transmissionPower = self.transmission_powers[idx_TP]
                m_proto.periodSendingPacket = self.period_sending_packets[idx_SR]
                m_proto.spreadingFactor = self.spreading_factors[idx_SF]
                #print("Random action: ", (m_proto.transmissionPower, m_proto.periodSendingPacket, m_proto.spreadingFactor ))
                self.last_action[m.name] = (idx_TP, idx_SR, idx_SF)
                #print(self.last_action[m.name])
                m_proto.selWay = RANDOM
        elif self.adaptation_type == AdaptationType.COORDINATED:
            actions = self.do_coordination(observations)
            for m in self.motes:
                action = actions[m.name]
                m_proto = response.moteActions.add()
                m_proto.moteName = m.name
                m_proto.EUI = m.EUI
                m_proto.transmissionPower = self.transmission_powers[action[0]]
                m_proto.periodSendingPacket = self.period_sending_packets[action[1]]
                m_proto.spreadingFactor = self.spreading_factors[action[2]]
                self.last_action[m.name] = action
                # print("{} actions is {}".format(m.name, action))

                m_proto.selWay = AdaptationType.to_proto(self.adaptation_type)
            print(self.get_actions_value(self.last_action, observations))
        elif self.adaptation_type == AdaptationType.UNCOORDINATED:
            for m in self.motes:
                Qtable = self.Qtables_uncoordinated[m.name]
                state_indices = self.map_state_uncoordinated(list(filter(lambda mproto : m.EUI == mproto.EUI, observations.moteStates))[0])
                possible_actions = Qtable[state_indices]
                # print(Qtable.shape, possible_actions.shape, state_indices)
                m_proto = response.moteActions.add()
                m_proto.moteName = m.name
                m_proto.EUI = m.EUI

                action = np.unravel_index(np.argmax(possible_actions), possible_actions.shape)
                # print(action)
                m_proto.transmissionPower = self.transmission_powers[action[0]]
                m_proto.periodSendingPacket = self.period_sending_packets[action[1]]
                m_proto.spreadingFactor = self.spreading_factors[action[2]]

                self.last_action[m.name] = action
                # print(state_indices, possible_actions, action)

                m_proto.selWay = UNCOORDINATED

        response.timestep = observations.timestep
        response.iteration = self.iteration
        self.history_actions.append(response)


        return response

    def map_state_uncoordinated(self, observation):
        indices = []
        indices.append(self.discretize_val_usedEnergy(observation.deltaUsedEnergy))
        indices.append(self.discretize_val_failedTransmissions(observation.deltaFailedTransmissionsGateways))

        indices.append(self.discretize_val_averageStrength(observation.averageReceivedTransmissionPow))
        indices.append(self.discretize_val_averageDistance(observation.averageGatewayDistance))

        indices.append(self.discretize_val_collidedTransmissions(observation.deltaCollisions))

        return tuple(indices)


    def map_state_preference(self, observation):
        indices = []

        indices.append(self.discretize_val_usedEnergy(observation.deltaUsedEnergy))
        indices.append(self.discretize_val_failedTransmissions(observation.deltaFailedTransmissionsGateways))
        #indices.append(self.discretize_val_position(observation.posX))
        #indices.append(self.discretize_val_position(observation.posY))

        indices.append(self.discretize_val_averageStrength(observation.averageReceivedTransmissionPow))
        indices.append(self.discretize_val_averageDistance(observation.averageGatewayDistance))
               
        return tuple(indices)

    def compute_state_indices_consistency(self, mote1, mote2, observations):
        # we need distances and collisions -> those are the "states" for consistency constraints
        x1, y1 = [(ob.posX, ob.posY) for ob in observations.moteStates if ob.moteName == mote1.name][0]
        x2, y2 = [(ob.posX, ob.posY) for ob in observations.moteStates if ob.moteName == mote2.name][0]
        dist = math.sqrt(math.pow(x1 - x2, 2) + math.pow(y1 - y2, 2))
        # collisions = [ob.collidedWith.get(mote2.EUI, 0) for ob in observations.moteStates if ob.moteName == mote1.name][0]
        collisions = [ob.deltaCollidedWith.get(mote2.EUI, 0) for ob in observations.moteStates if ob.moteName == mote1.name][0]

        tup = self.discretize_val_distance(dist), self.discretize_val_collidedTransmissions(collisions)
        print("Distance ", dist, " collisions ", collisions, " ", tup)
        return tup

    def discretize_val_averageStrength(self, average):
        Min = -20.0
        Max = 0.0
        # print("Average strength ", average)
        return self.discretize_val(Min, Max, average, DISCRETIZATION_STEPS)
    
    def discretize_val_averageDistance(self, average):
        Min = 0
        Max = 900
        # print("Average distance ", average)
        return self.discretize_val(Min, Max, average, DISCRETIZATION_STEPS)


    def discretize_val_energyLevel(self, energy):
        Min = 0
        Max = 2.0
        return self.discretize_val(Min, Max, energy, DISCRETIZATION_STEPS)
    
    def discretize_val_transmissionPower(self, power):
        Min = 0
        Max = 20
        # print("Transmission power", power)
        return self.discretize_val(Min, Max, power, DISCRETIZATION_STEPS)

    def discretize_val_movementSpeed(self, speed):
        Min = 0.0
        Max = 1.0
        return self.discretize_val(Min, Max, speed, DISCRETIZATION_STEPS)

    def discretize_val_collidedTransmissions(self, collided):
        Min = 0
        Max = 20
        # print("Collided transmissions ", collided)
        return self.discretize_val(Min, Max, collided, DISCRETIZATION_STEPS)

    def discretize_val_failedTransmissions(self, failed):
        Min = 0
        Max = 15
        # print("Failed transmissions ", failed)
        return self.discretize_val(Min, Max, failed, DISCRETIZATION_STEPS_FT)

    def discretize_val_usedEnergy(self, usedEnergy):
        Min = 0.0
        Max = 10.0
        # print("Used energy ", usedEnergy)
        return self.discretize_val(Min, Max, usedEnergy, DISCRETIZATION_STEPS)

    def discretize_val_position(self, position):
        Min = 0.0
        Max = 2773.0
        return self.discretize_val(Min, Max, position, DISCRETIZATION_STEPS)

    def discretize_val_distance(self, distance):
        Min = 0.0
        Max = 2000.0
        # print("Distance ", distance)
        return self.discretize_val(Min, Max, distance, DISCRETIZATION_STEPS)

    def discretize_val(self, Min, Max, val, steps):
        clipped = np.clip(val, Min, Max)
        discretized = int(np.fix(np.interp(clipped, [Min, Max], [0, steps - 1])))
        return discretized

    def compute_rewards(self, observations):
        rewards = {}
        for m in self.motes:
            m_proto = list(filter(lambda mproto : m.EUI == mproto.EUI, observations.moteStates))[0]
            reward = - (m_proto.collidedTransmissions + m_proto.usedEnergy)
            rewards[m.name] = reward
        # print(rewards)
        return rewards

    def compute_reward_preference(self, mote, observations, prev_observations):
        obs_new = list(filter(lambda mproto : mote.EUI == mproto.EUI, observations.moteStates))[0]
        obs_old = list(filter(lambda mproto : mote.EUI == mproto.EUI, prev_observations.moteStates))[0]

        delta_failed = obs_new.failedTransmissionsGateways - obs_old.failedTransmissionsGateways
        delta_energy = obs_new.usedEnergy - obs_old.usedEnergy

        if delta_failed < 0:
            print("Something is wrong with delta_failed")
        if delta_energy < 0:
            print("Something is wrong with delta_energy")

        reward_failed = - REWARD_COEFF_FAILEDTRANS * delta_failed
        reward_energy = - REWARD_COEFF_ENERGY * delta_energy
        #reward_energy = 2.0 * delta_energy

        return reward_failed, reward_energy

    def compute_reward_consistency(self, mote1, mote2, observations, prev_observations):
        obs_new_1 = list(filter(lambda mproto : mote1.EUI == mproto.EUI, observations.moteStates))[0]
        obs_old_1 = list(filter(lambda mproto : mote1.EUI == mproto.EUI, prev_observations.moteStates))[0]

        obs_new_2 = list(filter(lambda mproto : mote2.EUI == mproto.EUI, observations.moteStates))[0]
        obs_old_2 = list(filter(lambda mproto : mote2.EUI == mproto.EUI, prev_observations.moteStates))[0]

        collisions_new = obs_new_1.collidedWith[mote2.EUI]
        collisions_old = obs_old_1.collidedWith[mote2.EUI]

        delta_collisions = collisions_new - collisions_old

        if delta_collisions < 0:
            print("Something is wrong with delta_collisions")

        # For fairness to uncoordinated we need to add 2*
        reward_collisions = - 2 * REWARD_COEFF_COLLISIONS * delta_collisions

        return reward_collisions

    def compute_reward_uncoordinated(self, mote, observations, prev_observations):
        obs_new = list(filter(lambda mproto : mote.EUI == mproto.EUI, observations.moteStates))[0]
        obs_old = list(filter(lambda mproto : mote.EUI == mproto.EUI, prev_observations.moteStates))[0]

        delta_failed = obs_new.failedTransmissionsGateways - obs_old.failedTransmissionsGateways
        delta_energy = obs_new.usedEnergy - obs_old.usedEnergy
        delta_collisions = obs_new.collidedTransmissions - obs_old.collidedTransmissions

        delta_collisions_alt = sum([d[1] for d in obs_new.collidedWith.items() if d[0] != mote.EUI]) - sum([d[1] for d in obs_old.collidedWith.items() if d[0] != mote.EUI])

        print("delta_collisions vs delta_collisions_alt: {} vs {}".format(delta_collisions, delta_collisions_alt))

        if delta_collisions < 0:
            print("Something is wrong with delta_collisions")
        if delta_failed < 0:
            print("Something is wrong with delta_failed")
        if delta_energy < 0:
            print("Something is wrong with delta_energy")

        reward_failed = - REWARD_COEFF_FAILEDTRANS * delta_failed
        reward_energy = - REWARD_COEFF_ENERGY * delta_energy
        reward_collisions = - REWARD_COEFF_COLLISIONS * delta_collisions

        return reward_failed, reward_energy, reward_collisions 

    def compute_state_indices_preference(self, mote, observations):
        return self.map_state_preference(list(filter(lambda mproto : mote.EUI == mproto.EUI, observations.moteStates))[0])

    def compute_new_q(self, Qtable, old_index, new_index, reward):
        # update = (1 - self.learning_rate) * Qtable[old_index] + self.learning_rate * (reward + self.discount_factor * Qtable[new_index])
        update = Qtable[old_index] + self.learning_rate * (reward + self.discount_factor * Qtable[new_index] - Qtable[old_index])
        return update

    def reward(self, observations):
        if self.adaptation_type in [AdaptationType.NOADAPTATION, AdaptationType.RANDOM]:
            pass
        
        if self.adaptation_type is AdaptationType.COORDINATED:
            self.reward_coordination_graph(observations)

        if self.adaptation_type is AdaptationType.UNCOORDINATED:
            self.reward_uncoordinated(observations)

        if self.adaptation_type is AdaptationType.RANDOM:
            self.fake_reward_random(observations)

        self.iteration = self.iteration + 1
        print("Iteration: ", self.iteration)

    def fake_reward_random(self, observations):
        qtables_rewards = QtablesRewards()
        qtables_rewards.timestepCurrentObservation = observations.timestep
        qtables_rewards.timestepLastObservation = self.last_observation.timestep

        for m in self.motes:
            Qtable_name = "Q" + m.name

            reward_failed, reward_energy, reward_collisions = self.compute_reward_uncoordinated(m, observations, self.last_observation)
            reward = reward_failed + reward_energy + reward_collisions

            qtable_reward = qtables_rewards.qtableRewards.add()
            qtable_reward.rewardFailures = reward_failed
            qtable_reward.rewardEnergy = reward_energy
            qtable_reward.rewardCollisions = reward_collisions
            qtable_reward.rewardTotal = reward
            qtable_reward.constraintType = "random"
            qtable_reward.qtableName = "Q{}".format(m.name)

        qtables_rewards.selWay = self.history_actions[-1].moteActions[0].selWay
        qtables_rewards.iteration = self.iteration
        self.history_rewards.append(qtables_rewards)

    def reward_uncoordinated(self, observations):
        qtables_rewards = QtablesRewards()
        qtables_rewards.timestepCurrentObservation = observations.timestep
        qtables_rewards.timestepLastObservation = self.last_observation.timestep

        for m in self.motes:
            Qtable = self.Qtables_uncoordinated[m.name]
            new_state_indices = self.map_state_uncoordinated(list(filter(lambda mproto : m.EUI == mproto.EUI, observations.moteStates))[0])
            old_state_indices = self.map_state_uncoordinated(list(filter(lambda mproto : m.EUI == mproto.EUI, self.last_observation.moteStates))[0])
            old_action_index = self.last_action[m.name]
            old_index = old_state_indices + old_action_index

            #print(old_action_index, old_index)

            possible_actions = Qtable[new_state_indices]
            new_action = np.unravel_index(np.argmax(possible_actions), possible_actions.shape)
            new_index = new_state_indices + new_action

            reward_failed, reward_energy, reward_collisions = self.compute_reward_uncoordinated(m, observations, self.last_observation)
            reward = reward_failed + reward_energy + reward_collisions

            update = self.compute_new_q(Qtable, old_index, new_index, reward)
            update = round(update, DECIMALS)
            #print(update)
            Qtable[old_index] = update

            self.Qtables_uncoordinated[m.name] = Qtable

            qtable_reward = qtables_rewards.qtableRewards.add()
            qtable_reward.rewardFailures = reward_failed
            qtable_reward.rewardEnergy = reward_energy
            qtable_reward.rewardCollisions = reward_collisions
            qtable_reward.rewardTotal = reward
            qtable_reward.constraintType = "uncoordinated"
            qtable_reward.qtableName = "Q{}".format(m.name)

        qtables_rewards.selWay = self.history_actions[-1].moteActions[0].selWay
        qtables_rewards.iteration = self.iteration
        self.history_rewards.append(qtables_rewards)

    def reward_coordination_graph(self, observations):
        if self.adaptation_type in [AdaptationType.NOADAPTATION, AdaptationType.RANDOM]:
            return

        qtables_rewards = QtablesRewards()

        qtables_rewards.timestepCurrentObservation = observations.timestep
        qtables_rewards.timestepLastObservation = self.last_observation.timestep

        max_actions_indices = self.do_coordination(observations)
        mote_nodes, q_nodes = nx.bipartite.sets(self.graph)
        attributes = nx.get_node_attributes(self.graph, "constraint")
        for qnode in [qn for qn in q_nodes if self.graph.nodes[qn]["constraint"] == "preference"]:
            if (len(self.graph.nodes[qnode]["motes"]) != 1):
                print("Something has gone wrong in the preference constraint")
            mote = self.graph.nodes[qnode]["motes"][0]
            Qtable = self.graph.nodes[qnode]["qtable"]
            new_state_indices = self.compute_state_indices_preference(mote, observations)
            old_state_indices = self.compute_state_indices_preference(mote, self.last_observation)
            old_action_index = self.last_action[mote.name]
            old_index = old_state_indices + old_action_index

            reward_failed, reward_energy = self.compute_reward_preference(mote, observations, self.last_observation)
            reward = reward_failed + reward_energy

            max_actions = max_actions_indices[mote.name]
            new_index = new_state_indices + max_actions

            # print("Reward preference for {}. reward failed: {}    reward energy: {}".format(qnode, reward_failed, reward_energy))
            update = self.compute_new_q(Qtable, old_index, new_index, reward)

            update = round(update, DECIMALS)

            Qtable[old_index] = update
            #print(qnode, Qtable)

            qtable_reward = qtables_rewards.qtableRewards.add()
            qtable_reward.rewardCollisions = 0
            qtable_reward.rewardFailures = reward_failed
            qtable_reward.rewardEnergy = reward_energy
            qtable_reward.rewardTotal = reward
            qtable_reward.constraintType = "preference"
            qtable_reward.qtableName = qnode

        for qnode in [qn for qn in q_nodes if self.graph.nodes[qn]["constraint"] == "consistency"]:
            if (len(self.graph.nodes[qnode]["motes"]) < 2):
                print("Something has gone wrong in the consistency constraint")

            motes = self.graph.nodes[qnode]["motes"]
            Qtable = self.graph.nodes[qnode]["qtable"]
            new_state_indices = self.compute_state_indices_consistency(motes[0], motes[1], observations)
            old_state_indices = self.compute_state_indices_consistency(motes[0], motes[1], self.last_observation)
            old_action_index_1 = self.last_action[motes[0].name]
            old_action_index_2 = self.last_action[motes[1].name]
            old_index = old_state_indices + old_action_index_1 + old_action_index_2

            reward = self.compute_reward_consistency(motes[0], motes[1], observations, self.last_observation)

            max_actions_1 = max_actions_indices[motes[0].name]
            max_actions_2 = max_actions_indices[motes[1].name]
            new_index = new_state_indices + max_actions_1 + max_actions_2

            # print("Reward consistency for {}. reward collisions: {}".format(qnode, reward))
            update = self.compute_new_q(Qtable, old_index, new_index, reward)

            update = round(update, DECIMALS)

            if self.adaptation_type == AdaptationType.UNCOORDINATED:
                # To basically turn off coordination we can set the reward to the initialized value
                # update = 0
                update = Q_INIT_VAL

            Qtable[old_index] = update

            qtable_reward = qtables_rewards.qtableRewards.add()
            qtable_reward.rewardFailures = 0
            qtable_reward.rewardEnergy = 0
            qtable_reward.rewardCollisions = reward
            qtable_reward.rewardTotal = reward
            qtable_reward.constraintType = "consistency"
            qtable_reward.qtableName = qnode
            #print(qnode, Qtable)

        qtables_rewards.iteration = self.iteration
        qtables_rewards.selWay = self.history_actions[-1].moteActions[0].selWay
        self.history_rewards.append(qtables_rewards)

    def construct_coordination_graph_pairwise(self):
        # construct a coordination graph where there is coordination between every possible pair of motes
        graph = nx.Graph()
        graph.add_nodes_from([m.name for m in self.motes], bipartite=0)

        # preference constraints
        for m in self.motes:
            qnode_name = "Q" + m.name
            graph.add_node(qnode_name, bipartite=1)
            graph.add_edge(m.name, qnode_name)
            nx.set_node_attributes(graph, {qnode_name: {"motes": [m]}})

        #consistency constraints
        for p in itertools.combinations(self.motes, 2):
            qnode_name = "Q" + "".join([pp.name for pp in p])
            graph.add_node(qnode_name, bipartite=1)
            for pp in p:
                graph.add_edge(pp.name, qnode_name)
            nx.set_node_attributes(graph, {qnode_name: {"motes": p[:]}})
        # print(sorted(graph))

        mote_nodes, q_nodes = nx.bipartite.sets(graph)
        nx.nx_pydot.write_dot(graph, "pydot_graph.dot")
            #     with open("pydot_graph.dot", "w") as fp:
            # fp.write(nx.nx_pydot.to_pydot(graph))
        # pos = dict()
        # pos.update( (n, (1, i)) for i, n in enumerate(mote_nodes) ) # put nodes from X at x=1
        # pos.update( (n, (2, i)) for i, n in enumerate(q_nodes) ) # put nodes from Y at x=2
        # nx.write_latex(graph, "latex_graph.tex", as_document=True, pos=pos)
        # nx.write_latex(graph, "latex_graph.tex", as_document=True)
        #plt.show()
        return graph

    def construct_q_table_uncoordinated(self):
        states = ["EN", "FT", "AS", "AD", "COL"]
        #state_shape = tuple(DISCRETIZATION_STEPS for _ in states)
        state_shape = (DISCRETIZATION_STEPS, DISCRETIZATION_STEPS_FT, DISCRETIZATION_STEPS, DISCRETIZATION_STEPS, DISCRETIZATION_STEPS)
        action_shape = (DISCRETIZATION_STEPS, DISCRETIZATION_STEPS_SR, DISCRETIZATION_STEPS_SF)
        #table = np.zeros(state_shape + action_shape, dtype=np.float64) + Q_INIT_VAL
        table = np.random.random_sample(state_shape + action_shape) * (-1.0)
        table = np.around(table, DECIMALS)
        return table

    def construct_q_table_preference(self):
        # states: EN, FT, PX, PY
        states = ["EN", "FT", "AS", "AD"]
        #state_shape = tuple(DISCRETIZATION_STEPS for _ in states)
        state_shape = (DISCRETIZATION_STEPS, DISCRETIZATION_STEPS_FT, DISCRETIZATION_STEPS, DISCRETIZATION_STEPS)
        # actions: TP, SR, SF
        # actions = ["TP", "SR", "SF"]
        action_shape = (DISCRETIZATION_STEPS, DISCRETIZATION_STEPS_SR, DISCRETIZATION_STEPS_SF)
        #table = np.zeros(state_shape + action_shape, dtype=np.float64) + Q_INIT_VAL
        table = np.random.random_sample(state_shape + action_shape) * (-1.0)
        table = np.around(table, DECIMALS)
        return table

    def construct_q_table_consistency(self):
        # states: DIST, COL
        states = ["DIST", "COL"]
        state_shape = tuple(DISCRETIZATION_STEPS for _ in states)
        # actions: TP1, TP2, SR1, SR2, SF1, SF2
        # actions = ["TP1", "TP2", "SR1", "SR2", "SF1", "SF2"]
        # action_shape = tuple(DISCRETIZATION_STEPS for _ in actions)
        action_shape = (DISCRETIZATION_STEPS, DISCRETIZATION_STEPS_SR, DISCRETIZATION_STEPS_SF,
                        DISCRETIZATION_STEPS, DISCRETIZATION_STEPS_SR, DISCRETIZATION_STEPS_SF)
        #table = np.zeros(state_shape + action_shape, dtype=np.float64) + Q_INIT_VAL
        table = np.random.random_sample(state_shape + action_shape) * (-1.0)
        table = np.around(table, DECIMALS)
        return table

    def construct_q_tables(self, graph):
        mote_nodes, q_nodes = nx.bipartite.sets(graph)
        for qn in q_nodes:
            no_edges = len(graph.edges(qn))
            if no_edges == 1:
                # it's a preference constraint
                nx.set_node_attributes(graph, {qn: 
                                                #{"qtable": np.zeros([10, 10, 10, 10, 10, 10], dtype=np.float64), 
                                                #{"qtable": np.random.random_sample([10, 10, 10, 10, 10, 10]) * 5,
                                                # {"qtable": np.random.randint(0, 5, [10, 10, 10, 10, 10, 10]),
                                                {"qtable": self.construct_q_table_preference(),
                                                 "constraint": "preference"
                                                }})
            else:
                #it's a consistency constraint
                # shape = (10, 10) + tuple(10 for i in range(no_edges))
                nx.set_node_attributes(graph, {qn: {
                                                    #"qtable": np.zeros(shape, dtype=np.float64), 
                                                    #"qtable": np.random.random_sample(shape) * 5,
                                                    # "qtable": np.random.randint(0, 5, shape),
                                                    "qtable": self.construct_q_table_consistency(),
                                                    "constraint": "consistency" 
                                                    }})
        
        mote_nodes, q_nodes = nx.bipartite.sets(graph)
        attributes = nx.get_node_attributes(graph, "qtable")
        for k, v in attributes.items():
            print(k, v.shape, v.size * v.itemsize / 1024 / 1024)

        attributes = nx.get_node_attributes(graph, "motes")
        for k, v in attributes.items():
            print(k, v)

        attributes = nx.get_node_attributes(graph, "constraint")
        for k, v in attributes.items():
            print(k, v)

    # def construct_dcop_instance(self, graph, observations):
    #     dcop = DCOP("coord")

    #     domain_vals = []
    #     domain_map = {}
    #     i = 0
    #     for tp in range(DISCRETIZATION_STEPS):
    #         for sr in range(DISCRETIZATION_STEPS_SR):
    #             for sf in range(DISCRETIZATION_STEPS_SF):
    #                 domain_vals.append((tp, sr, sf))
    #                 domain_map[i] = (tp, sr, sf)
    #                 i = i + 1
    #     # domain = Domain("mote_domain", "TP_SR_SF", domain_vals)
    #     domain = Domain("mote_domain", "TP_SR_SF", range(DISCRETIZATION_STEPS * DISCRETIZATION_STEPS_SR * DISCRETIZATION_STEPS_SF))
    #     #print(domain_vals)
    #     #sys.exit()
    #     variables = {}
    #     for m in self.motes:
    #         variables[m.name] = Variable(m.name, domain)
    #     # print(variables)

    #     preference_constraints = []
    #     mote_nodes, q_nodes = nx.bipartite.sets(graph)
    #     # preference constraints
    #     for qn in [n for n in q_nodes if len(graph.edges(n)) == 1]:
    #         Qtable = graph.nodes[qn]["qtable"]
    #         mote = graph.nodes[qn]["motes"][0]
    #         state_indices = self.compute_state_indices_preference(mote, observations)

    #         reduced_Qtable = Qtable[state_indices].flatten()
    #         # print(state_indices, reduced_Qtable.shape, len(domain_vals))

    #         # the solvers do minimization, while we need maximization
    #         reduced_Qtable = -reduced_Qtable

    #         preference_constraint = NAryMatrixRelation([variables[mote.name]],
    #                                     reduced_Qtable,
    #                                     "{}_pref".format(mote.name))
    #         # print(preference_constraint)
    #         preference_constraints.append(preference_constraint)

    #     # consistency constraints
    #     consistency_constraints = []
    #     mote_nodes, q_nodes = nx.bipartite.sets(graph)
    #     for qn in [n for n in q_nodes if len(graph.edges(n)) > 1]:
    #         Qtable = graph.nodes[qn]["qtable"]

    #         motes = graph.nodes[qn]["motes"]
    #         state_indices = self.compute_state_indices_consistency(motes[0], motes[1], observations)

    #         reduced_Qtable = np.reshape(Qtable[state_indices], (len(domain_vals), len(domain_vals)))
    #         # print("Hello", state_indices, reduced_Qtable.shape, Qtable.shape)

    #         # the solvers do minimization, while we need maximization
    #         reduced_Qtable = -reduced_Qtable

    #         consistency_constraint = NAryMatrixRelation([variables[m.name] for m in motes],
    #                                                     reduced_Qtable,
    #                                                     "_".join([m.name for m in motes]) + "_const")
    #         consistency_constraints.append(consistency_constraint)

    #     for c in preference_constraints:
    #         dcop.add_constraint(c)
    #     for c in consistency_constraints:
    #         dcop.add_constraint(c)

    #     dcop.add_agents(create_agents('a', list(range(3*len(variables.keys()))), capacity=5000))

    #     cg = pseudotree.build_computation_graph(dcop)
    #     print(cg)
    #     dist = oneagent.distribute(cg, dcop.agents.values())
    #     print(dcop)
    #     # metrics = solve(dcop, 'dpop', dist, cg, timeout=10)
    #     # metrics = self.profiler.runcall(solve, dcop, 'dpop', 'oneagent', timeout=None)
    #     metrics = solve(dcop, 'dpop', 'oneagent', timeout=None)
    #     # metrics = solve(dcop, 'maxsum', 'oneagent', timeout=None)
    #     # metrics = solve(dcop, 'dsa', 'oneagent', timeout=None)
    #     # metrics = solve(dcop, 'maxsum', 'adhoc')
    #     print(metrics)
    #     assignment = metrics["assignment"]
    #     print("DCOP results: ", assignment)
    #     #toulbar_assignment = self.construct_toulbar2_instance(self.graph, observations)
    #     #print("Toulbar results:", toulbar_assignment)


    #     #self.profiler.dump_stats("profile_data.dump")
    #     #self.profiler.print_stats(sort="cumtime")
    #     #self.profiler.print_stats(sort="tottime")
    #     #sys.exit()

    #     final_assignments = {}
    #     for mote in self.motes:
    #         mass = assignment[mote.name]
    #         final_assignments[mote.name] = domain_map[mass]
    #     #toulbar_assignment = self.construct_toulbar2_instance(self.graph, observations)
    #     #print("Final DCOP results:", final_assignments)
    #     #print("Toulbar results:", toulbar_assignment)
    #     return final_assignments

    def construct_toulbar2_instance(self, graph, observations):
        prob = ptb2.CFN(resolution=4)
        domain_vals = []
        domain_map = {}
        i = 0
        for tp in range(DISCRETIZATION_STEPS):
            for sr in range(DISCRETIZATION_STEPS_SR):
                for sf in range(DISCRETIZATION_STEPS_SF):
                    val = (tp, sr, sf)
                    domain_vals.append(val)
                    domain_map[i] = val
                    i = i + 1

        variables = {}
        for m in self.motes:
            variables[m.name] = m.name
            prob.AddVariable(m.name, range(DISCRETIZATION_STEPS * DISCRETIZATION_STEPS_SR * DISCRETIZATION_STEPS_SF))
        # print(prob)

        #print(domain_vals)
        #sys.exit()

        mote_nodes, q_nodes = nx.bipartite.sets(graph)
        # preference constraints
        for qn in [n for n in q_nodes if len(graph.edges(n)) == 1]:
            Qtable = graph.nodes[qn]["qtable"]
            mote = graph.nodes[qn]["motes"][0]
            state_indices = self.compute_state_indices_preference(mote, observations)

            reduced_Qtable = np.ravel(Qtable[state_indices])
            # print(state_indices, reduced_Qtable.shape, len(domain_vals))

            # the solvers do minimization, while we need maximization
            reduced_Qtable = -reduced_Qtable
            prob.AddFunction([variables[mote.name]], reduced_Qtable.tolist())

        # consistency constraints
        mote_nodes, q_nodes = nx.bipartite.sets(graph)
        for qn in [n for n in q_nodes if len(graph.edges(n)) > 1]:
            Qtable = graph.nodes[qn]["qtable"]

            motes = graph.nodes[qn]["motes"]
            state_indices = self.compute_state_indices_consistency(motes[0], motes[1], observations)
            #print(Qtable[state_indices].shape)
            #sys.exit()
            #reduced_Qtable = np.reshape(Qtable[state_indices], (len(domain_vals), len(domain_vals)))
            reduced_Qtable = Qtable[state_indices]
            # print("Hello", state_indices, reduced_Qtable.shape, Qtable.shape)

            # the solvers do minimization, while we need maximization
            reduced_Qtable = -reduced_Qtable
            prob.AddFunction([variables[motes[0].name], variables[motes[1].name]], reduced_Qtable.flatten().tolist())

        solution = prob.Solve(showSolutions=3)
        print(solution)
        #sys.exit()

        final_assignments = {}
        for idx, mote in enumerate(self.motes):
            mass = solution[0][idx]
            final_assignments[mote.name] = domain_map[mass]
        return final_assignments

    def get_actions_value(self, actions, observations):
        value = 0
        mote_nodes, q_nodes = nx.bipartite.sets(self.graph)
        for qnode in [qn for qn in q_nodes if self.graph.nodes[qn]["constraint"] == "preference"]:
            if (len(self.graph.nodes[qnode]["motes"]) != 1):
                print("Something has gone wrong in the preference constraint")
            mote = self.graph.nodes[qnode]["motes"][0]
            Qtable = self.graph.nodes[qnode]["qtable"]
            state_indices = self.compute_state_indices_preference(mote, observations)
            index = state_indices + actions[mote.name]
            value = value + Qtable[index]

            best_act = np.unravel_index(np.argmax(Qtable[state_indices], axis=None), Qtable[state_indices].shape)
            print("Best actions for {} is {}".format(qnode, best_act))

        for qnode in [qn for qn in q_nodes if self.graph.nodes[qn]["constraint"] == "consistency"]:
            if (len(self.graph.nodes[qnode]["motes"]) < 2):
                print("Something has gone wrong in the consistency constraint")
            motes = self.graph.nodes[qnode]["motes"]
            Qtable = self.graph.nodes[qnode]["qtable"]
            state_indices = self.compute_state_indices_consistency(motes[0], motes[1], observations)
            index = state_indices + actions[motes[0].name] + actions[motes[1].name]
            value = value + Qtable[index]
        
        return value

    def plot(self):
        records = []
        experiment_name = AdaptationType.to_str(self.adaptation_type) + "_" + str(self.seed)
        experiment_type = AdaptationType.to_str(self.adaptation_type)
        for obs in self.history_observations:
            act = [a for a in self.history_actions if a.timestep == obs.timestep][0]
            # rew = [r for r in self.history_rewards if r.timestepLastObservation == obs.timestep][0]
            for mproto in obs.moteStates:
                mproto_action = [mp for mp in act.moteActions if mp.moteName == mproto.moteName][0]
                #mproto_reward = [mp for mp in rew.qtableRewards if mproto.moteName in mp.qtableName]
                new_record = {"timestep": obs.timestep,
                              "seed": self.seed,
                              "moteName": mproto.moteName,
                              "EUI": mproto.EUI,
                              "collisions": mproto.collidedTransmissions,
                              "deltaCollisions": mproto.deltaCollisions,
                              "usedEnergy": mproto.usedEnergy,
                              "deltaUsedEnergy": mproto.deltaUsedEnergy,
                              "failedTransmissions": mproto.failedTransmissionsGateways,
                              "deltaFailedTransmissions": mproto.deltaFailedTransmissionsGateways,
                              "spreadingFactor": mproto_action.spreadingFactor,
                              "transmissionPower": mproto_action.transmissionPower,
                              "periodSendingPacket": mproto_action.periodSendingPacket,
                              "movementSpeed": mproto.movementSpeed,
                              "selWay": mproto_action.selWay,
                              "experimentType": experiment_type,
                              "experimentName": experiment_name
                              }
                records.append(new_record)
        # obs_df = pd.concat([obs_df, new_record], ignore_index=True)
        #obs_df = pd.DataFrame(records, columns=["timestep", "moteName", "EUI", "collisions", "usedEnergy"])
        obs_df = pd.DataFrame(records)

        #obs_df.to_hdf("experiment_data_motes.hdf5", key=AdaptationType.to_str(self.adaptation_type) + "_" + str(self.seed),
        #                mode="a", complevel=9, format="table")
        obs_df.to_sql(name="motes", con=self.ENGINE, if_exists="append")

        records = []
        for rew in self.history_rewards:
            # act = [a for a in self.history_actions if a.timestep == obs.timestep][0]
            # rew = [r for r in self.history_rewards if r.timestepLastObservation == obs.timestep][0]
            for mproto in rew.qtableRewards:
                # mproto_action = [mp for mp in act.moteActions if mp.moteName == mproto.moteName][0]
                #mproto_reward = [mp for mp in rew.qtableRewards if mproto.moteName in mp.qtableName]
                new_record = {"timestepLastObservation": rew.timestepLastObservation,
                              "timestepCurrentObservation": rew.timestepCurrentObservation,
                              "seed": self.seed,
                              "qtableName": mproto.qtableName,
                              "constraintType": mproto.constraintType,
                              "rewardEnergy": mproto.rewardEnergy,
                              "rewardFailures": mproto.rewardFailures,
                              "rewardCollisions": mproto.rewardCollisions,
                              "rewardTotal": mproto.rewardTotal,
                              "selWay": rew.selWay,
                              "experimentType": experiment_type,
                              "experimentName": experiment_name}
                records.append(new_record)
        rew_df = pd.DataFrame(records)
        #rew_df.to_hdf("experiment_data_rewards.hdf5", key=AdaptationType.to_str(self.adaptation_type) + "_" + str(self.seed),
        #                mode="a", complevel=9, format="table")
        rew_df.to_sql(name="rewards", con=self.ENGINE, if_exists="append")


        benchmark_time_arr = np.array(self.history_benchmarks["execTime"])

        if self.adaptation_type == AdaptationType.UNCOORDINATED:
            qtableMemory = sum([qt.size for _, qt in self.Qtables_uncoordinated.items()])
            coordinationMemory = sum([ACTION_SIZE_PREF for _, qt in self.Qtables_uncoordinated.items()])
        elif self.adaptation_type == AdaptationType.COORDINATED:
            mote_nodes, q_nodes = nx.bipartite.sets(self.graph)
            qtableMemory = sum([self.graph.nodes[qn]["qtable"].size for qn in q_nodes])
            coordinationMemory = sum([ACTION_SIZE_PREF for qn in q_nodes if self.graph.nodes[qn]["constraint"] == "preference"] + [ACTION_SIZE_CONST for qn in q_nodes if self.graph.nodes[qn]["constraint"] == "consistency"])
        else:
            qtableMemory = 0
            coordinationMemory = 0

        
        benchmark = {"experimentType": experiment_type,
                     "experimentName": experiment_name,
                     "seed": self.seed,
                     "meanExecTime": np.mean(benchmark_time_arr),
                     "medianExecTime": np.median(benchmark_time_arr),
                     "stdExecTime": np.std(benchmark_time_arr),
                     "varExecTime": np.var(benchmark_time_arr),
                     "qtableMemory": qtableMemory,
                     "coordinationMemory": coordinationMemory
                     }
        benchmark = [benchmark]
        benchmark_df = pd.DataFrame(benchmark)
        benchmark_df.to_sql(name="benchmarks", con=self.ENGINE, if_exists="append")


        #collisions_df = obs_df.groupby("timestep")[].sum()
        collisions_df = obs_df[obs_df["moteName"] == "mote0"]
        # collisions_df["collisions"] = collisions_df["collisions"].diff()
        # print(obs_df)
        # print(collisions_df)

        #fig, ax = plt.subplots(1, 1, sharex=True, figsize=(12.5, 2.5), tight_layout=True)
        fig, ax = plt.subplots(1, 1)
        #collisions_df.plot(x="timestep", y="collisions")
        for k, g in obs_df.groupby("moteName"):
            print(k)
            g.plot(x="timestep", y="collisions", ax=ax, label=k)
        plt.savefig('figure1.pdf')

        #collisions_df.plot(x="timestep", y="usedEnergy")
        #plt.savefig('figure2.pdf')

        fig, ax = plt.subplots(1, 1)
        for k, g in obs_df.groupby("moteName"):         
            g.plot(x="timestep", y="usedEnergy", ax=ax, label=k)
        plt.savefig('figure2.pdf')

        fig, ax = plt.subplots(1, 1)
        for k, g in obs_df.groupby("moteName"):  
            g_diffed = g["usedEnergy"].diff().rolling(10).mean()
            g_diffed.plot(x="timestep", y="usedEnergyDiff", ax=ax, label=k)
        plt.savefig('figure3.pdf')
