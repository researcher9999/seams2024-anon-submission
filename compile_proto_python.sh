#!/bin/bash

python -m grpc_tools.protoc -I./src/main/proto --python_out=./src/main/python/proto_generated/api_pb2/ --pyi_out=./src/main/python/proto_generated/api_pb2/ --grpc_python_out=./src/main/python/proto_generated/api_pb2/ ./src/main/proto/api.proto

sed -i 's/import api_pb2/from \. import api_pb2/g' ./src/main/python/proto_generated/api_pb2/api_pb2_grpc.py
