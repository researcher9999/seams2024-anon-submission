# Generated by the gRPC Python protocol compiler plugin. DO NOT EDIT!
"""Client and server classes corresponding to protobuf-defined services."""
import grpc

from . import api_pb2 as api__pb2


class MARLStub(object):
    """Missing associated documentation comment in .proto file."""

    def __init__(self, channel):
        """Constructor.

        Args:
            channel: A grpc.Channel.
        """
        self.GetActions = channel.unary_unary(
                '/proto.grpc.MARL/GetActions',
                request_serializer=api__pb2.MotesActionRequest.SerializeToString,
                response_deserializer=api__pb2.MotesActionResponse.FromString,
                )
        self.InitMARL = channel.unary_unary(
                '/proto.grpc.MARL/InitMARL',
                request_serializer=api__pb2.InitRequest.SerializeToString,
                response_deserializer=api__pb2.InitResponse.FromString,
                )
        self.NotifyDone = channel.unary_unary(
                '/proto.grpc.MARL/NotifyDone',
                request_serializer=api__pb2.DoneNotification.SerializeToString,
                response_deserializer=api__pb2.DoneNotificationResponse.FromString,
                )


class MARLServicer(object):
    """Missing associated documentation comment in .proto file."""

    def GetActions(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def InitMARL(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def NotifyDone(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')


def add_MARLServicer_to_server(servicer, server):
    rpc_method_handlers = {
            'GetActions': grpc.unary_unary_rpc_method_handler(
                    servicer.GetActions,
                    request_deserializer=api__pb2.MotesActionRequest.FromString,
                    response_serializer=api__pb2.MotesActionResponse.SerializeToString,
            ),
            'InitMARL': grpc.unary_unary_rpc_method_handler(
                    servicer.InitMARL,
                    request_deserializer=api__pb2.InitRequest.FromString,
                    response_serializer=api__pb2.InitResponse.SerializeToString,
            ),
            'NotifyDone': grpc.unary_unary_rpc_method_handler(
                    servicer.NotifyDone,
                    request_deserializer=api__pb2.DoneNotification.FromString,
                    response_serializer=api__pb2.DoneNotificationResponse.SerializeToString,
            ),
    }
    generic_handler = grpc.method_handlers_generic_handler(
            'proto.grpc.MARL', rpc_method_handlers)
    server.add_generic_rpc_handlers((generic_handler,))


 # This class is part of an EXPERIMENTAL API.
class MARL(object):
    """Missing associated documentation comment in .proto file."""

    @staticmethod
    def GetActions(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/proto.grpc.MARL/GetActions',
            api__pb2.MotesActionRequest.SerializeToString,
            api__pb2.MotesActionResponse.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def InitMARL(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/proto.grpc.MARL/InitMARL',
            api__pb2.InitRequest.SerializeToString,
            api__pb2.InitResponse.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def NotifyDone(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/proto.grpc.MARL/NotifyDone',
            api__pb2.DoneNotification.SerializeToString,
            api__pb2.DoneNotificationResponse.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)
