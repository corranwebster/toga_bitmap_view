from __future__ import annotations

from typing import overload

from .pixel_format import RGB888, PixelFormat


class Bitmap:

    def __init__(
        self,
        size: tuple[int, int],
        buffer: bytearray | memoryview | None = None,
        stride: int | None = None,
        offset: int | None = None,
        format: type[PixelFormat] = RGB888,
    ):
        super().__init__()
        self._format = format

        if buffer is None:
            buffer = bytearray(self._format.pixel_size * size[0] * size[1])
        if stride is None:
            stride = self._format.pixel_size * size[0]
        if offset is None:
            offset = 0

        self._size = size
        self._buffer = buffer
        self._stride = stride
        self._offset = offset

    @property
    def format(self) -> type[PixelFormat]:
        return self._format

    @property
    def size(self) -> tuple[int, int]:
        return self._size

    @property
    def n_bytes(self):
        return self._format.pixel_size * self._size[0] * self._size[1]

    @property
    def bytes(self) -> bytes:
        if self._stride == self._format.pixel_size * self._size[0]:
            # contiguous
            return bytes(self._buffer[self._offset : self._offset + self.n_bytes])
        else:
            row_size = self._format.pixel_size * self._size[0]
            return b"".join(
                bytes(self._buffer[row_offset : row_offset + row_size])
                for row_offset in range(
                    self._offset,
                    self._offset + self._size[1] * self._stride,
                    self._stride,
                )
            )

    def to_format(self, format: type[PixelFormat]) -> Bitmap:
        if type(self._format) is format:
            return self
        else:
            result = Bitmap(self._size, format=format)
            result.set_rect(0, 0, self._size[0], self._size[1], self)
            return result

    def __iter__(self):
        offset = self._offset
        for y in range(self._size[1]):
            row_offset = offset
            for x in range(self._size[0]):
                yield self.format(
                    self._buffer[offset : offset + self._format.pixel_size]
                )
                offset += self._format.pixel_size
            offset = row_offset + self._stride

    def __len__(self):
        return self._size[0] * self._size[1]

    def _normalize(self, value, dimension):
        if value < 0:
            value += self._size[dimension]
        return value

    # Unsafe access methods

    def _get_offset(self, x: int, y: int):
        return self._offset + x * self._format.pixel_size + y * self._stride

    def _get_pixel(self, x: int, y: int) -> PixelFormat:
        offset = self._get_offset(x, y)
        return self.format(self._buffer[offset : offset + self._format.pixel_size])

    def _set_pixel(self, x: int, y: int, pixel: PixelFormat):
        offset = self._get_offset(x, y)
        self._buffer[offset : offset + self._format.pixel_size] = pixel.bytes

    # Safe public access methods

    def get_pixel(self, x: int, y: int) -> PixelFormat:
        if not (-self._size[0] <= x < self._size[0]) or not (
            -self._size[1] <= y < self._size[1]
        ):
            raise IndexError(f"Coordinates ({x}, {y}) outside bitmap size {self.size}.")
        x = self._normalize(x, 0)
        y = self._normalize(y, 1)
        return self._get_pixel(x, y)

    def set_pixel(self, x: int, y: int, pixel: PixelFormat):
        if not (-self._size[0] <= x < self._size[0]) or not (
            -self._size[1] <= y < self._size[1]
        ):
            raise IndexError(f"Coordinates ({x}, {y}) outside bitmap size {self.size}.")
        x = self._normalize(x, 0)
        y = self._normalize(y, 1)
        if not isinstance(pixel, self._format):
            pixel = self.format.from_color(pixel.color)
        self._set_pixel(x, y, pixel)

    def get_rect(self, x: int, y: int, width: int, height: int):
        if abs(x) >= self._size[0] or abs(y) >= self._size[1]:
            raise IndexError(f"Coordinates ({x}, {y}) outside bitmap size {self.size}.")
        x = self._normalize(x, 0)
        y = self._normalize(y, 1)
        offset = self._get_offset(x, y)
        width = min(width, self.size[0] - abs(x))
        height = min(height, self.size[1] - abs(y))
        return Bitmap((width, height), self._buffer, self._stride, offset, self._format)

    def set_rect(
        self, x: int, y: int, width: int, height: int, source: Bitmap | PixelFormat
    ):
        if abs(x) >= self._size[0] or abs(y) >= self._size[1]:
            raise IndexError(f"Coordinates ({x}, {y}) outside bitmap size {self.size}.")
        x = self._normalize(x, 0)
        y = self._normalize(y, 1)
        if isinstance(source, Bitmap):
            width = min(width, self.size[0] - abs(x), source.size[0])
            height = min(height, self.size[1] - abs(y), source.size[1])
        else:
            width = min(width, self.size[0] - abs(x))
            height = min(height, self.size[1] - abs(y))
        if isinstance(source, PixelFormat):
            if not isinstance(source, self._format):
                source = self._format.from_color(source.color)
            offset = self._get_offset(x, y)
            row_values = source.bytes * width
            buffer_width = len(row_values)
            for row in range(height):
                self._buffer[offset : offset + buffer_width] = row_values
                offset += self._stride
        elif self.format == source.format:
            # use direct memory copy
            offset = self._get_offset(x, y)
            buffer_width = self._format.pixel_size * width
            source_offset = source._get_offset(0, 0)
            for row in range(height):
                self._buffer[offset : offset + buffer_width] = source._buffer[
                    source_offset : source_offset + buffer_width
                ]
                offset += self._stride
                source_offset += source._stride
        else:
            # copy pixel by pixel
            for dy in range(height):
                for dx in range(width):
                    self._set_pixel(
                        x + dx,
                        y + dy,
                        self._format.from_color(source._get_pixel(dx, dy).color),
                    )

    def scroll_rect(self, x, y, width, height, dx, dy):
        if dx == 0 and dy == 0:
            # no scrolling!
            return

        # memory inefficient but simple
        source_x = x if dx >= 0 else x - dx
        source_y = y if dy >= 0 else y - dy
        width = width - abs(dx)
        height = height - abs(dy)

        source_buffer = bytearray(
            self.get_rect(source_x, source_y, width, height).bytes
        )
        source = Bitmap((width, height), source_buffer, format=self._format)

        x = x if dx < 0 else x + dx
        y = y if dy < 0 else y + dy

        self.set_rect(x, y, width, height, source)

    @overload
    def __getitem__(self, index: tuple[int, int]) -> PixelFormat: ...

    @overload
    def __getitem__(
        self,
        index: (
            int | slice | tuple[slice, int] | tuple[int, slice] | tuple[slice, slice]
        ),
    ) -> Bitmap: ...

    def __getitem__(self, index):
        if isinstance(index, tuple) and len(index) == 2:
            x, y = index
            if isinstance(x, int) and isinstance(y, int):
                return self.get_pixel(x, y)
            else:
                if isinstance(x, int):
                    width = 1
                elif isinstance(x, slice):
                    if x.step not in {1, None}:
                        raise IndexError(f"Slice step must be 1, got {x.step}")
                    x_start = self._normalize(x.start, 0) if x.start is not None else 0
                    x_stop = (
                        self._normalize(x.stop, 0)
                        if x.stop is not None
                        else self._size[0]
                    )
                    width = max(0, x_stop - x_start)
                    x = x_start
                else:
                    raise IndexError(f"Invalid index {index}")
                if isinstance(y, int):
                    height = 1
                elif isinstance(y, slice):
                    if y.step not in {1, None}:
                        raise IndexError(f"Slice step must be 1, got {y.step}")
                    y_start = self._normalize(y.start, 1) if y.start is not None else 0
                    y_stop = (
                        self._normalize(y.stop, 1)
                        if y.stop is not None
                        else self._size[1]
                    )
                    height = y_stop - y_start
                    y = y_start
                else:
                    raise IndexError(f"Invalid index {index}")
                return self.get_rect(x, y, width, height)
        elif isinstance(index, int):
            index = self._normalize(index, 1)
            offset = self._get_offset(0, index)
            return Bitmap(
                (self._size[0], 1), self._buffer, self._stride, offset, self._format
            )
        elif isinstance(index, slice):
            if index.step not in {1, None}:
                raise IndexError(f"Slice step must be 1, got {index.step}")
            y_start = self._normalize(index.start, 0) if index.start is not None else 0
            y_stop = (
                self._normalize(index.stop, 0)
                if index.stop is not None
                else self._size[1]
            )
            height = max(0, y_stop - y_start)
            y = y_start
            return self.get_rect(0, y, self._size[0], height)
        else:
            raise IndexError(f"Invalid index {index}")

    @overload
    def __setitem__(self, index: tuple[int, int], value: PixelFormat): ...

    @overload
    def __setitem__(
        self,
        index: (
            int | slice | tuple[slice, int] | tuple[int, slice] | tuple[slice, slice]
        ),
        value: PixelFormat | Bitmap,
    ): ...

    def __setitem__(self, index, value):
        if isinstance(index, tuple) and len(index) == 2:
            x, y = index
            if isinstance(x, int) and isinstance(y, int):
                if isinstance(value, PixelFormat):
                    return self.set_pixel(x, y, value)
                else:
                    raise ValueError(f"Invalid value for pixel {index}: {value}")
            else:
                if isinstance(x, int):
                    width = 1
                elif isinstance(x, slice):
                    if x.step not in {1, None}:
                        raise IndexError(f"Slice step must be 1, got {x.step}")
                    x_start = self._normalize(x.start, 0) if x.start is not None else 0
                    x_stop = (
                        self._normalize(x.stop, 0)
                        if x.stop is not None
                        else self._size[0]
                    )
                    width = max(0, x_stop - x_start)
                    x = x_start
                else:
                    raise IndexError(f"Invalid index {index}")
                if isinstance(y, int):
                    height = 1
                elif isinstance(y, slice):
                    if y.step not in {1, None}:
                        raise IndexError(f"Slice step must be 1, got {y.step}")
                    y_start = self._normalize(y.start, 1) if y.start is not None else 0
                    y_stop = (
                        self._normalize(y.stop, 1)
                        if y.stop is not None
                        else self._size[1]
                    )
                    height = y_stop - y_start
                    y = y_start
                else:
                    raise IndexError(f"Invalid index {index}")
                return self.set_rect(x, y, width, height, value)
        elif isinstance(index, int):
            index = self._normalize(index, 1)
            offset = self._get_offset(0, index)
            return Bitmap(
                (self._size[0], 1), self._buffer, self._stride, offset, self._format
            )
        elif isinstance(index, slice):
            if index.step not in {1, None}:
                raise IndexError(f"Slice step must be 1, got {index.step}")
            y_start = self._normalize(index.start, 0) if index.start is not None else 0
            y_stop = (
                self._normalize(index.stop, 0)
                if index.stop is not None
                else self._size[1]
            )
            height = max(0, y_stop - y_start)
            y = y_start
            return self.get_rect(0, y, self._size[0], height)
        else:
            raise IndexError(f"Invalid index {index}")
