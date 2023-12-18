from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class ActionSelectionWay(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = []
    RANDOM: _ClassVar[ActionSelectionWay]
    UNCOORDINATED: _ClassVar[ActionSelectionWay]
    COORDINATED: _ClassVar[ActionSelectionWay]
    NOADAPTATION: _ClassVar[ActionSelectionWay]
RANDOM: ActionSelectionWay
UNCOORDINATED: ActionSelectionWay
COORDINATED: ActionSelectionWay
NOADAPTATION: ActionSelectionWay

class DoneNotification(_message.Message):
    __slots__ = ["done"]
    DONE_FIELD_NUMBER: _ClassVar[int]
    done: bool
    def __init__(self, done: bool = ...) -> None: ...

class DoneNotificationResponse(_message.Message):
    __slots__ = ["status"]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    status: bool
    def __init__(self, status: bool = ...) -> None: ...

class InitRequest(_message.Message):
    __slots__ = ["moteInfos"]
    MOTEINFOS_FIELD_NUMBER: _ClassVar[int]
    moteInfos: _containers.RepeatedCompositeFieldContainer[MoteInfoInit]
    def __init__(self, moteInfos: _Optional[_Iterable[_Union[MoteInfoInit, _Mapping]]] = ...) -> None: ...

class InitResponse(_message.Message):
    __slots__ = ["success"]
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    success: bool
    def __init__(self, success: bool = ...) -> None: ...

class MoteInfoInit(_message.Message):
    __slots__ = ["moteName", "EUI", "spreadingFactor", "sensors", "moteState"]
    MOTENAME_FIELD_NUMBER: _ClassVar[int]
    EUI_FIELD_NUMBER: _ClassVar[int]
    SPREADINGFACTOR_FIELD_NUMBER: _ClassVar[int]
    SENSORS_FIELD_NUMBER: _ClassVar[int]
    MOTESTATE_FIELD_NUMBER: _ClassVar[int]
    moteName: str
    EUI: int
    spreadingFactor: float
    sensors: _containers.RepeatedScalarFieldContainer[str]
    moteState: MoteState
    def __init__(self, moteName: _Optional[str] = ..., EUI: _Optional[int] = ..., spreadingFactor: _Optional[float] = ..., sensors: _Optional[_Iterable[str]] = ..., moteState: _Optional[_Union[MoteState, _Mapping]] = ...) -> None: ...

class MotesActionRequest(_message.Message):
    __slots__ = ["moteStates", "timestep"]
    MOTESTATES_FIELD_NUMBER: _ClassVar[int]
    TIMESTEP_FIELD_NUMBER: _ClassVar[int]
    moteStates: _containers.RepeatedCompositeFieldContainer[MoteState]
    timestep: int
    def __init__(self, moteStates: _Optional[_Iterable[_Union[MoteState, _Mapping]]] = ..., timestep: _Optional[int] = ...) -> None: ...

class MoteState(_message.Message):
    __slots__ = ["moteName", "EUI", "energyLevel", "spreadingFactor", "transmissionPower", "movementSpeed", "collidedTransmissions", "usedEnergy", "collidedWith", "duplicatedTransmissions", "duplicatedWith", "posX", "posY", "failedTransmissionsGateways", "periodSendingPacket", "deltaUsedEnergy", "deltaFailedTransmissionsGateways", "deltaCollisions", "averageReceivedTransmissionPow", "averageGatewayDistance", "deltaCollidedWith"]
    class CollidedWithEntry(_message.Message):
        __slots__ = ["key", "value"]
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: int
        value: int
        def __init__(self, key: _Optional[int] = ..., value: _Optional[int] = ...) -> None: ...
    class DuplicatedWithEntry(_message.Message):
        __slots__ = ["key", "value"]
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: int
        value: int
        def __init__(self, key: _Optional[int] = ..., value: _Optional[int] = ...) -> None: ...
    class DeltaCollidedWithEntry(_message.Message):
        __slots__ = ["key", "value"]
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: int
        value: int
        def __init__(self, key: _Optional[int] = ..., value: _Optional[int] = ...) -> None: ...
    MOTENAME_FIELD_NUMBER: _ClassVar[int]
    EUI_FIELD_NUMBER: _ClassVar[int]
    ENERGYLEVEL_FIELD_NUMBER: _ClassVar[int]
    SPREADINGFACTOR_FIELD_NUMBER: _ClassVar[int]
    TRANSMISSIONPOWER_FIELD_NUMBER: _ClassVar[int]
    MOVEMENTSPEED_FIELD_NUMBER: _ClassVar[int]
    COLLIDEDTRANSMISSIONS_FIELD_NUMBER: _ClassVar[int]
    USEDENERGY_FIELD_NUMBER: _ClassVar[int]
    COLLIDEDWITH_FIELD_NUMBER: _ClassVar[int]
    DUPLICATEDTRANSMISSIONS_FIELD_NUMBER: _ClassVar[int]
    DUPLICATEDWITH_FIELD_NUMBER: _ClassVar[int]
    POSX_FIELD_NUMBER: _ClassVar[int]
    POSY_FIELD_NUMBER: _ClassVar[int]
    FAILEDTRANSMISSIONSGATEWAYS_FIELD_NUMBER: _ClassVar[int]
    PERIODSENDINGPACKET_FIELD_NUMBER: _ClassVar[int]
    DELTAUSEDENERGY_FIELD_NUMBER: _ClassVar[int]
    DELTAFAILEDTRANSMISSIONSGATEWAYS_FIELD_NUMBER: _ClassVar[int]
    DELTACOLLISIONS_FIELD_NUMBER: _ClassVar[int]
    AVERAGERECEIVEDTRANSMISSIONPOW_FIELD_NUMBER: _ClassVar[int]
    AVERAGEGATEWAYDISTANCE_FIELD_NUMBER: _ClassVar[int]
    DELTACOLLIDEDWITH_FIELD_NUMBER: _ClassVar[int]
    moteName: str
    EUI: int
    energyLevel: int
    spreadingFactor: int
    transmissionPower: int
    movementSpeed: float
    collidedTransmissions: int
    usedEnergy: float
    collidedWith: _containers.ScalarMap[int, int]
    duplicatedTransmissions: int
    duplicatedWith: _containers.ScalarMap[int, int]
    posX: float
    posY: float
    failedTransmissionsGateways: int
    periodSendingPacket: int
    deltaUsedEnergy: float
    deltaFailedTransmissionsGateways: int
    deltaCollisions: int
    averageReceivedTransmissionPow: float
    averageGatewayDistance: float
    deltaCollidedWith: _containers.ScalarMap[int, int]
    def __init__(self, moteName: _Optional[str] = ..., EUI: _Optional[int] = ..., energyLevel: _Optional[int] = ..., spreadingFactor: _Optional[int] = ..., transmissionPower: _Optional[int] = ..., movementSpeed: _Optional[float] = ..., collidedTransmissions: _Optional[int] = ..., usedEnergy: _Optional[float] = ..., collidedWith: _Optional[_Mapping[int, int]] = ..., duplicatedTransmissions: _Optional[int] = ..., duplicatedWith: _Optional[_Mapping[int, int]] = ..., posX: _Optional[float] = ..., posY: _Optional[float] = ..., failedTransmissionsGateways: _Optional[int] = ..., periodSendingPacket: _Optional[int] = ..., deltaUsedEnergy: _Optional[float] = ..., deltaFailedTransmissionsGateways: _Optional[int] = ..., deltaCollisions: _Optional[int] = ..., averageReceivedTransmissionPow: _Optional[float] = ..., averageGatewayDistance: _Optional[float] = ..., deltaCollidedWith: _Optional[_Mapping[int, int]] = ...) -> None: ...

class MoteAction(_message.Message):
    __slots__ = ["moteName", "EUI", "energyLevel", "spreadingFactor", "transmissionPower", "movementSpeed", "periodSendingPacket", "selWay"]
    MOTENAME_FIELD_NUMBER: _ClassVar[int]
    EUI_FIELD_NUMBER: _ClassVar[int]
    ENERGYLEVEL_FIELD_NUMBER: _ClassVar[int]
    SPREADINGFACTOR_FIELD_NUMBER: _ClassVar[int]
    TRANSMISSIONPOWER_FIELD_NUMBER: _ClassVar[int]
    MOVEMENTSPEED_FIELD_NUMBER: _ClassVar[int]
    PERIODSENDINGPACKET_FIELD_NUMBER: _ClassVar[int]
    SELWAY_FIELD_NUMBER: _ClassVar[int]
    moteName: str
    EUI: int
    energyLevel: int
    spreadingFactor: int
    transmissionPower: int
    movementSpeed: float
    periodSendingPacket: int
    selWay: ActionSelectionWay
    def __init__(self, moteName: _Optional[str] = ..., EUI: _Optional[int] = ..., energyLevel: _Optional[int] = ..., spreadingFactor: _Optional[int] = ..., transmissionPower: _Optional[int] = ..., movementSpeed: _Optional[float] = ..., periodSendingPacket: _Optional[int] = ..., selWay: _Optional[_Union[ActionSelectionWay, str]] = ...) -> None: ...

class MotesActionResponse(_message.Message):
    __slots__ = ["moteActions", "timestep", "iteration"]
    MOTEACTIONS_FIELD_NUMBER: _ClassVar[int]
    TIMESTEP_FIELD_NUMBER: _ClassVar[int]
    ITERATION_FIELD_NUMBER: _ClassVar[int]
    moteActions: _containers.RepeatedCompositeFieldContainer[MoteAction]
    timestep: int
    iteration: int
    def __init__(self, moteActions: _Optional[_Iterable[_Union[MoteAction, _Mapping]]] = ..., timestep: _Optional[int] = ..., iteration: _Optional[int] = ...) -> None: ...

class QtablesRewards(_message.Message):
    __slots__ = ["qtableRewards", "timestepLastObservation", "timestepCurrentObservation", "selWay", "iteration"]
    QTABLEREWARDS_FIELD_NUMBER: _ClassVar[int]
    TIMESTEPLASTOBSERVATION_FIELD_NUMBER: _ClassVar[int]
    TIMESTEPCURRENTOBSERVATION_FIELD_NUMBER: _ClassVar[int]
    SELWAY_FIELD_NUMBER: _ClassVar[int]
    ITERATION_FIELD_NUMBER: _ClassVar[int]
    qtableRewards: _containers.RepeatedCompositeFieldContainer[QtableReward]
    timestepLastObservation: int
    timestepCurrentObservation: int
    selWay: ActionSelectionWay
    iteration: int
    def __init__(self, qtableRewards: _Optional[_Iterable[_Union[QtableReward, _Mapping]]] = ..., timestepLastObservation: _Optional[int] = ..., timestepCurrentObservation: _Optional[int] = ..., selWay: _Optional[_Union[ActionSelectionWay, str]] = ..., iteration: _Optional[int] = ...) -> None: ...

class QtableReward(_message.Message):
    __slots__ = ["qtableName", "constraintType", "rewardEnergy", "rewardFailures", "rewardCollisions", "rewardTotal"]
    QTABLENAME_FIELD_NUMBER: _ClassVar[int]
    CONSTRAINTTYPE_FIELD_NUMBER: _ClassVar[int]
    REWARDENERGY_FIELD_NUMBER: _ClassVar[int]
    REWARDFAILURES_FIELD_NUMBER: _ClassVar[int]
    REWARDCOLLISIONS_FIELD_NUMBER: _ClassVar[int]
    REWARDTOTAL_FIELD_NUMBER: _ClassVar[int]
    qtableName: str
    constraintType: str
    rewardEnergy: float
    rewardFailures: float
    rewardCollisions: float
    rewardTotal: float
    def __init__(self, qtableName: _Optional[str] = ..., constraintType: _Optional[str] = ..., rewardEnergy: _Optional[float] = ..., rewardFailures: _Optional[float] = ..., rewardCollisions: _Optional[float] = ..., rewardTotal: _Optional[float] = ...) -> None: ...
