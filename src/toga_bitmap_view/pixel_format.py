from __future__ import annotations

from typing import ClassVar, Protocol, runtime_checkable

from travertino.colors import Color, rgb


@runtime_checkable
class PixelFormat(Protocol):
    pixel_size: ClassVar[int]
    channel_bits: ClassVar[int]

    def __init__(self, value: bytes | bytearray): ...
    @classmethod
    def from_color(cls, color: Color) -> PixelFormat: ...
    @property
    def bytes(self) -> bytes: ...
    @property
    def color(self) -> Color: ...

    def __eq__(self, other: object) -> bool:
        if isinstance(other, type(self)):
            return self.bytes == other.bytes
        return NotImplemented

    def __hash__(self):
        return hash(self.bytes)

    def __repr__(self):
        return f"{self.__class__.__name__}({self.bytes!r})"


class RGB24(PixelFormat):
    pixel_size: ClassVar[int] = 3
    channel_bits: ClassVar[int] = 8

    def __init__(self, value: bytes | bytearray | tuple[int, int, int]):
        self._bytes = bytes(value)

    @classmethod
    def from_color(cls, color: Color):
        return cls((color.r, color.g, color.b))

    @property
    def bytes(self) -> bytes:
        return self._bytes

    @property
    def color(self) -> Color:
        return rgb(*self._bytes)


class RGBA32(PixelFormat):
    pixel_size: ClassVar[int] = 4
    channel_bits: ClassVar[int] = 8

    def __init__(self, value: bytes | bytearray | tuple[int, int, int, int]):
        self._bytes = bytes(value)

    @classmethod
    def from_color(cls, color: Color):
        return cls((color.r, color.g, color.b, int(color.a * 255)))

    @property
    def bytes(self) -> bytes:
        return self._bytes

    @property
    def color(self) -> Color:
        return rgb(*self._bytes)
