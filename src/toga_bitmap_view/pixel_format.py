from __future__ import annotations

from typing import ClassVar, Literal, Protocol, runtime_checkable

from travertino.colors import Color, rgb


@runtime_checkable
class PixelFormat(Protocol):
    pixel_size: ClassVar[int]
    channel_bits: ClassVar[int | tuple[int, int, int] | tuple[int, int, int]]

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


class RGB888(PixelFormat):
    pixel_size = 3
    channel_bits = 8

    def __init__(self, value: bytes | bytearray | tuple[int, int, int]):
        self._bytes = bytes(value)

    @classmethod
    def from_color(cls, color: Color):
        color = color.rgb
        return cls((color.r, color.g, color.b))

    @property
    def bytes(self) -> bytes:
        return self._bytes

    @property
    def color(self) -> Color:
        return rgb(*self._bytes)


class RGBA8888(PixelFormat):
    pixel_size = 4
    channel_bits = 8

    def __init__(self, value: bytes | bytearray | tuple[int, int, int, int]):
        self._bytes = bytes(value)

    @classmethod
    def from_color(cls, color: Color):
        color = color.rgba
        return cls((color.r, color.g, color.b, int(color.a * 255)))

    @property
    def bytes(self) -> bytes:
        return self._bytes

    @property
    def color(self) -> Color:
        return rgb(*self._bytes)


class RGB565(PixelFormat):
    pixel_size = 2
    channel_bits = (5, 6, 5)
    byteorder: ClassVar[Literal["little", "big"]] = "big"

    def __init__(self, value: bytes | bytearray | tuple[int, int, int]):
        if isinstance(value, tuple):
            r, g, b = value
            r >>= 3
            g >>= 2
            b >>= 3
            value = ((r << 11) | (g << 5) | b).to_bytes(2, self.byteorder)
        self._bytes = bytes(value)

    @classmethod
    def from_color(cls, color: Color):
        color = color.rgb
        return cls((color.r, color.g, color.b))

    @property
    def bytes(self) -> bytes:
        return self._bytes

    @property
    def color(self) -> Color:
        int_value = int.from_bytes(self._bytes, self.byteorder)
        r = int(round((int_value >> 11) * (0xff / 0b11111)))
        g = int(round((int_value >> 5) & 0b111111) * (0xff / 0b111111))
        b = int(round(int_value & 0b11111) * (0xff / 0b11111))
        return rgb(r, g, b)
