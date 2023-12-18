package iot;

import java.util.concurrent.TimeUnit;

import io.grpc.Channel;
import io.grpc.Grpc;
import io.grpc.InsecureChannelCredentials;
import io.grpc.ManagedChannel;
import io.grpc.ManagedChannelBuilder;
import io.grpc.StatusRuntimeException;
import proto.grpc.Api.DoneNotification;
import proto.grpc.Api.DoneNotificationResponse;
import proto.grpc.Api.InitRequest;
import proto.grpc.Api.InitResponse;
import proto.grpc.Api.MotesActionRequest;
import proto.grpc.Api.MotesActionResponse;
import proto.grpc.MARLGrpc.MARLBlockingStub;

public class MARLClient {
    private final MARLBlockingStub blockingStub;
    private ManagedChannel channel;

    public MARLClient(String host, int port) {
        // this(ManagedChannelBuilder.forAddress(host, port).usePlaintext());
        // this(Grpc.newChannelBuilder("localhost:7779", InsecureChannelCredentials.create()));
        // this(Grpc.newChannelBuilderForAddress("132.252.251.219", 50009, InsecureChannelCredentials.create()));
        // this(Grpc.newChannelBuilderForAddress("127.0.0.1", 50009, InsecureChannelCredentials.create()));
        // this(ManagedChannelBuilder.forAddress("http://132.252.251.219", 7779).usePlaintext());
        // this(ManagedChannelBuilder.forAddress("0:0:0:0:0:0:0:1", 7779).usePlaintext());
        // this(ManagedChannelBuilder.forAddress("tcp://132.252.251.219", 7779).usePlaintext());
        // this(ManagedChannelBuilder.forAddress("[0:0:0:0:0:0:0:1]", 7779).usePlaintext());
        // this(Grpc.newChannelBuilder("127.0.0.1:50051", InsecureChannelCredentials.create()));
        // this(Grpc.newChannelBuilderForAddress("127.0.0.1", 50051, InsecureChannelCredentials.create()));
        // this(ManagedChannelBuilder.forAddress("132.252.228.239", 50051).usePlaintext());
        //this(ManagedChannelBuilder.forTarget("dns:///132.252.228.239:50051").usePlaintext());
        //this(ManagedChannelBuilder.forTarget("ipv4:132.252.228.239:50051").usePlaintext());
        this(Grpc.newChannelBuilder("unix:///tmp/socket_grpc", InsecureChannelCredentials.create()));
        // this(Grpc.newChannelBuilder("ipv4://127.0.0.1:50051", InsecureChannelCredentials.create()));
    }

    public MARLClient(ManagedChannelBuilder<?> channelBuilder) {
        channel = channelBuilder.build();
        blockingStub = proto.grpc.MARLGrpc.newBlockingStub(channel);
    }

    public MotesActionResponse getActions(MotesActionRequest request) throws StatusRuntimeException {
        MotesActionResponse response;
        // System.out.println("Sending request...");
        try { 
            response = blockingStub.getActions(request); 
            // System.out.println("Got response...");
        } finally {
            // try {
            //     channel.shutdownNow().awaitTermination(5, TimeUnit.SECONDS);
            // } catch (InterruptedException e) {
            //     e.printStackTrace();
            // }
        }
        // response = MotesActionResponse.newBuilder().build();
        return response;
    }

    public InitResponse initialize(InitRequest request) throws StatusRuntimeException {
        InitResponse response;
        // System.out.println("Sending request...");
        try { 
            response = blockingStub.initMARL(request); 
            // System.out.println("Got response...");
        } finally {
            // try {
            //     channel.shutdownNow().awaitTermination(5, TimeUnit.SECONDS);
            // } catch (InterruptedException e) {
            //     e.printStackTrace();
            // }
        }
        // response = MotesActionResponse.newBuilder().build();
        return response;
    }

    public void notifyDone() throws StatusRuntimeException {
        System.out.println("Sending DONE notification.");
        try { 
            blockingStub.notifyDone(DoneNotification.newBuilder().setDone(true).build()); 

        } finally {

        }
    }   

}
