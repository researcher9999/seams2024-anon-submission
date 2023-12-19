from proto_generated.api_pb2.api_pb2_grpc import MARLServicer, MARLStub, add_MARLServicer_to_server
from proto_generated.api_pb2.api_pb2 import MotesActionResponse, MotesActionRequest, InitResponse, QtablesRewards, QtableReward, DoneNotificationResponse
import grpc
from concurrent import futures
from algorithms.qlearning import QLearning

import logging
from logging import info,warning, error

import argparse

import threading

import random
import numpy as np

from sys import exit

DO_ADAPTATION = True

class DingNetMote:
    def __init__(self, name, moves, EUI, spreadingFactor):
        self.name = name
        self.EUI = EUI
        self.moves = moves
        self.spreadingFactor = spreadingFactor

class Rewarder:
    def __init__(self, motes):
        self.motes = motes

    def compute_reward(self, observations):
        return {} 

class MARLServer(MARLServicer):
    def __init__(self, adaptation_type, seed, results_path, stop_event):
        self.env = None
        self.alg = None
        self.rewarder = None
        self.is_first_iter = True
        self.adaptation_type = adaptation_type
        self.stop_event = stop_event
        self.seed = seed
        self.results_path = results_path
        super().__init__()

    def NotifyDone(self, request, context):
        print("We are done!")
        self.alg.plot()
        print("Iterations: ", self.alg.iteration)
        self.stop_event.set()
        return DoneNotificationResponse()

    def InitMARL(self, request, context):
        print("Running InitMARL")
        print(request)
        response = InitResponse()
        if self.alg is not None:
            response.success = False
            return response
        
        print("Environment is not yet initialized. Initializing...")
        motes = []
        for moteInfo in request.moteInfos:
            mote = DingNetMote(moteInfo.moteName, False, moteInfo.EUI, moteInfo.spreadingFactor)
            motes.append(mote)
        #self.env = parallel_env(motes)
        self.alg = QLearning(motes, self.seed, adaptation_type=self.adaptation_type, results_path=self.results_path)
        self.rewarder = Rewarder(motes)
        self.is_first_iter = True

        response.success = True
        return response

    def GetActions(self, request, context):
        print("Running GetActions!") 
        print(request)
        if not self.is_first_iter:
            self.alg.reward(request)
        else:
            self.is_first_iter = False
        
        response = self.alg.take_action(request)
        return response

def main():
    parser = argparse.ArgumentParser(
                prog='MARL client for DingNet',
                description='This program does adaptation via multi-agent reinforcement learning.')

    parser.add_argument("--seed", dest="seed", action="store", 
                            default=1, type=int, required=False, help="Seed for the random number generator.") 
    parser.add_argument("--adaptation", dest="adaptation_type", action="store", 
                            choices=["coordinated", "uncoordinated", "noadaptation", "random"], default="coordinated", 
                            type=str, required=False, help="How should adaptation take place")
    parser.add_argument("--resultspath", dest="results_path", action="store",
                            default="results.sqlite3",
                            type=str, required=False, help="Where should the results be saved.")
    args = parser.parse_args()
    
    random.seed(args.seed)
    np.random.seed(args.seed)

    stop_event = threading.Event()
    # port = "50051"
    listen_address = "unix:///tmp/socket_grpc"
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    add_MARLServicer_to_server(MARLServer(args.adaptation_type, args.seed, args.results_path, stop_event), server)
    # server.add_insecure_port("[::]:" + port)
    server.add_insecure_port(listen_address)
    # server.add_insecure_port("127.0.0.1:50009")
    server.start()
    # print("Server started, listening on " + port)
    print("Server started, listening on " + listen_address)
    stop_event.wait()
    server.stop(10)
    #server.wait_for_termination()

if __name__ == "__main__":
    main()
