from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar, Iterable, Optional

DESCRIPTOR: _descriptor.FileDescriptor

class SensorReadingPacket(_message.Message):
    __slots__ = ["data", "time_s"]
    DATA_FIELD_NUMBER: ClassVar[int]
    TIME_S_FIELD_NUMBER: ClassVar[int]
    data: _containers.RepeatedScalarFieldContainer[float]
    time_s: float
    def __init__(self, time_s: Optional[float] = ..., data: Optional[Iterable[float]] = ...) -> None: ...
