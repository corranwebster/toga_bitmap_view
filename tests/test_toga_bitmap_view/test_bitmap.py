import pytest

from toga_bitmap_view.bitmap import Bitmap
from toga_bitmap_view.pixel_format import RGB24, RGBA32

WHITE = RGB24((255, 255, 255))
BLACK = RGB24((0, 0, 0))
RED = RGB24((255, 0, 0))
MAGENTA = RGB24((255, 0, 255))

sample_mask = """
..xxx..
.x...x.
.x...x.
.x...x.
..xxx..
"""

sample_palette = {".": BLACK, "x": WHITE}


def sample_bytes(
    mask=sample_mask,
    palette=sample_palette,
):
    """Generate a bytearray from string and palette."""
    sample = b"".join(
        b"".join(palette[char].bytes for char in line.strip()) for line in mask.strip()
    )
    return bytearray(sample)


def test_create_empty():
    """Test creating an empty bitmap."""
    bitmap = Bitmap((640, 480))

    assert bitmap.size == (640, 480)
    assert bitmap.format == RGB24
    assert bitmap.n_bytes == 640 * 480 * 3
    assert bitmap.bytes == b"\x00" * 640 * 480 * 3


def test_to_format():
    """Test converting a bitmap to another pixel format."""
    bitmap = Bitmap((640, 480), format=RGBA32)

    result = bitmap.to_format(RGB24)

    assert result.size == (640, 480)
    assert result.format == RGB24
    assert result.n_bytes == 640 * 480 * 3
    assert result.bytes == b"\x00" * 640 * 480 * 3


def test_iterator():
    """Test iterating over pixels."""
    bitmap = Bitmap((640, 480))

    assert all([pixel == BLACK for pixel in bitmap])


def test_len():
    """Test length of bitmap (number of pixels)."""
    bitmap = Bitmap((640, 480))

    assert len(bitmap) == 640 * 480


@pytest.mark.parametrize(
    "x,y,pixel",
    [
        (0, 0, BLACK),
        (6, 4, BLACK),
        (-7, -5, BLACK),
        (1, 2, WHITE),
        (-2, 2, WHITE),
        (1, -2, WHITE),
        (-1, -2, BLACK),
    ],
)
def test_get_pixel(x, y, pixel):
    """Test get_pixel method."""
    bitmap = Bitmap((7, 5), sample_bytes())

    result = bitmap.get_pixel(x, y)
    assert result == pixel


@pytest.mark.parametrize(
    "x,y",
    [
        (7, 0),
        (0, 5),
        (-8, 0),
        (0, -6),
    ],
)
def test_get_pixel_error(x, y):
    """Test get_pixel method for invalid coordinates."""
    bitmap = Bitmap((7, 5), sample_bytes())

    with pytest.raises(IndexError):
        bitmap.get_pixel(x, y)


@pytest.mark.parametrize(
    "x,y",
    [
        (0, 0),
        (6, 4),
        (-7, -5),
        (1, 2),
        (-2, 2),
        (1, -2),
        (-1, -2),
    ],
)
def test_set_pixel(x, y):
    """Test set_pixel method."""
    bitmap = Bitmap((7, 5))

    bitmap.set_pixel(x, y, RED)
    assert bitmap.get_pixel(x, y) == RED


@pytest.mark.parametrize(
    "x,y,pixel,result",
    [
        (0, 0, RGBA32((255, 0, 0, 255)), RED),
    ],
)
def test_set_pixel_other_format(x, y, pixel, result):
    """Test setting a pixel with a different pixel format."""
    bitmap = Bitmap((7, 5))

    bitmap.set_pixel(x, y, pixel)
    assert bitmap.get_pixel(x, y) == result


@pytest.mark.parametrize(
    "x,y",
    [
        (7, 0),
        (0, 5),
        (-8, 0),
        (0, -6),
    ],
)
def test_set_pixel_index_error(x, y):
    """Test set_pixel method for invalid coordinates."""
    bitmap = Bitmap((7, 5), sample_bytes())

    with pytest.raises(IndexError):
        bitmap.set_pixel(x, y, BLACK)


def test_get_rect():
    """Test get_rect method."""
    bitmap = Bitmap((7, 5), sample_bytes())

    rect_bitmap = bitmap.get_rect(1, 2, 2, 3)
    assert rect_bitmap.size == (2, 3)
    assert rect_bitmap.format == RGB24
    assert rect_bitmap.bytes == bytes(sample_bytes("x.\nx.\n.x"))


def test_set_rect_pixel():
    """Test set_rect method with a pixel."""
    bitmap = Bitmap((7, 5), sample_bytes())

    bitmap.set_rect(1, 2, 2, 3, RED)
    assert all(
        (
            bitmap.get_pixel(x, y) == RED
            if (1 <= x < 3 and 2 <= y < 5)
            else bitmap.get_pixel(x, y) != RED
        )
        for x in range(7)
        for y in range(5)
    )


def test_set_rect_bitmap():
    """Test set_rect method with a bitmap."""
    bitmap = Bitmap((7, 5), sample_bytes())
    source = Bitmap((2, 3), sample_bytes(".x\n.x\nx."))

    bitmap.set_rect(1, 2, 2, 3, source)

    assert bitmap.bytes == sample_bytes(
        """
        ..xxx..
        .x...x.
        ..x..x.
        ..x..x.
        .x.xx..
        """
    )


def test_set_rect_bitmap_other_format():
    """Test set_rect method with a bitmap in a different format."""
    bitmap = Bitmap((7, 5), sample_bytes())

    palette = {
        ".": RGBA32((0, 0, 0, 0)),
        "x": RGBA32((255, 255, 255, 255)),
    }
    source = Bitmap((2, 3), sample_bytes(".x\n.x\nx.", palette), format=RGBA32)

    bitmap.set_rect(1, 2, 2, 3, source)

    assert bitmap.bytes == sample_bytes(
        """
        ..xxx..
        .x...x.
        ..x..x.
        ..x..x.
        .x.xx..
        """
    )


@pytest.mark.parametrize(
    "x,y,pixel",
    [
        (0, 0, BLACK),
        (6, 4, BLACK),
        (-7, -5, BLACK),
        (1, 2, WHITE),
        (-2, 2, WHITE),
        (1, -2, WHITE),
        (-1, -2, BLACK),
    ],
)
def test_getitem_pixel(x, y, pixel):
    """Test __getitem__"""
    bitmap = Bitmap((7, 5), sample_bytes())

    result = bitmap[x, y]
    assert result == pixel


@pytest.mark.parametrize(
    "x,y",
    [
        (7, 0),
        (0, 5),
        (-8, 0),
        (0, -6),
    ],
)
def test_getitem_pixel_error(x, y):
    """Test __getitem__ for invalid coordinates"""
    bitmap = Bitmap((7, 5), sample_bytes())

    with pytest.raises(IndexError):
        bitmap[x, y]


def test_getitem_slice():
    """Test __getitem__ method with a slices."""
    bitmap = Bitmap((7, 5), sample_bytes())

    rect_bitmap = bitmap[1:3, 2:5]
    assert isinstance(rect_bitmap, Bitmap)
    assert rect_bitmap.size == (2, 3)
    assert rect_bitmap.format == RGB24
    assert rect_bitmap.bytes == bytes(sample_bytes("x.\nx.\n.x"))


def test_getitem_slice_and_item():
    """Test __getitem__ method with a combination of slices and indices."""
    bitmap = Bitmap((7, 5), sample_bytes())

    rect_bitmap = bitmap[1, 2:5]
    assert rect_bitmap.size == (1, 3)
    assert rect_bitmap.format == RGB24
    assert rect_bitmap.bytes == bytes(sample_bytes("x\nx\n."))

    rect_bitmap = bitmap[1:3, 2]
    assert rect_bitmap.size == (2, 1)
    assert rect_bitmap.format == RGB24
    assert rect_bitmap.bytes == bytes(sample_bytes("x."))


def test_getitem_slice_no_step():
    """Test __getitem__ method with a slices."""
    bitmap = Bitmap((7, 5), sample_bytes())

    with pytest.raises(IndexError):
        bitmap[1:3:2, 2:5]

    with pytest.raises(IndexError):
        bitmap[1:3, 2:5:-1]


@pytest.mark.parametrize(
    "x,y",
    [
        (0, 0),
        (6, 4),
        (-7, -5),
        (1, 2),
        (-2, 2),
        (1, -2),
        (-1, -2),
    ],
)
def test_setitem(x, y):
    """Test setitem method with a single pixel."""
    bitmap = Bitmap((7, 5))

    bitmap[x, y] = RED
    assert bitmap.get_pixel(x, y) == RED


@pytest.mark.parametrize(
    "x,y,pixel,result",
    [
        (0, 0, RGBA32((255, 0, 0, 255)), RED),
    ],
)
def test_setitem_other_format(x, y, pixel, result):
    """Test setitem with a different pixel format."""
    bitmap = Bitmap((7, 5))

    bitmap[x, y] = pixel
    assert bitmap.get_pixel(x, y) == result


@pytest.mark.parametrize(
    "x,y",
    [
        (7, 0),
        (0, 5),
        (-8, 0),
        (0, -6),
    ],
)
def test_setitem_index_error(x, y):
    """Test set_pixel method for invalid coordinates."""
    bitmap = Bitmap((7, 5), sample_bytes())

    with pytest.raises(IndexError):
        bitmap[x, y] = BLACK


def test_setitem_slice_and_index_pixel():
    """Test setitem setting a slices with a pixel."""
    bitmap = Bitmap((7, 5), sample_bytes())
    bitmap[1:3, 2:5] = RED
    assert all(
        (
            bitmap.get_pixel(x, y) == RED
            if (1 <= x < 3 and 2 <= y < 5)
            else bitmap.get_pixel(x, y) != RED
        )
        for x in range(7)
        for y in range(5)
    )

    bitmap = Bitmap((7, 5), sample_bytes())
    bitmap[1, 2:5] = RED
    assert all(
        (
            bitmap.get_pixel(x, y) == RED
            if (x == 1 and 2 <= y < 5)
            else bitmap.get_pixel(x, y) != RED
        )
        for x in range(7)
        for y in range(5)
    )

    bitmap = Bitmap((7, 5), sample_bytes())
    bitmap[1:3, 2] = RED
    assert all(
        (
            bitmap.get_pixel(x, y) == RED
            if (1 <= x < 3 and y == 2)
            else bitmap.get_pixel(x, y) != RED
        )
        for x in range(7)
        for y in range(5)
    )


def test_setitem_slice_bitmap():
    """Test setitem method with a bitmap."""
    bitmap = Bitmap((7, 5), sample_bytes())
    source = Bitmap((2, 3), sample_bytes(".x\n.x\nx."))

    bitmap[1:3, 2:5] = source

    assert bitmap.bytes == sample_bytes(
        """
        ..xxx..
        .x...x.
        ..x..x.
        ..x..x.
        .x.xx..
        """
    )


def test_setitem_slice_size_mismatch():
    """Test setitem method with a bitmap which is too big."""
    bitmap = Bitmap((7, 5), sample_bytes())
    source = Bitmap((2, 3), sample_bytes(".x\n.x\nx."))

    bitmap[1, 2:5] = source

    assert bitmap.bytes == sample_bytes(
        """
        ..xxx..
        .x...x.
        .....x.
        .....x.
        .xxxx..
        """
    )

    bitmap = Bitmap((7, 5), sample_bytes())
    source = Bitmap((2, 3), sample_bytes(".x\n.x\nx."))

    bitmap[1:4, 2:5] = source

    assert bitmap.bytes == sample_bytes(
        """
        ..xxx..
        .x...x.
        ..x..x.
        ..x..x.
        .x.xx..
        """
    )


def test_setitem_slice_bitmap_format():
    """Test setitem method with a bitmap in a different format."""
    bitmap = Bitmap((7, 5), sample_bytes())
    source = Bitmap((2, 3), sample_bytes(".x\n.x\nx."))

    palette = {
        ".": RGBA32((0, 0, 0, 0)),
        "x": RGBA32((255, 255, 255, 255)),
    }
    source = Bitmap((2, 3), sample_bytes(".x\n.x\nx.", palette), format=RGBA32)

    bitmap[1:3, 2:5] = source

    assert bitmap.bytes == sample_bytes(
        """
        ..xxx..
        .x...x.
        ..x..x.
        ..x..x.
        .x.xx..
        """
    )


def test_scroll_rect_full():
    """Test scrolling."""
    bitmap = Bitmap((7, 5), sample_bytes())
    bitmap.scroll_rect(0, 0, 7, 5, 0, 0)
    assert bitmap.bytes == sample_bytes()

    bitmap = Bitmap((7, 5), sample_bytes())
    bitmap.scroll_rect(0, 0, 7, 5, 1, 1)
    assert bitmap.bytes == sample_bytes(
        """
        ..xxx..
        ...xxx.
        ..x...x
        ..x...x
        ..x...x
        """
    )

    bitmap = Bitmap((7, 5), sample_bytes())
    bitmap.scroll_rect(0, 0, 7, 5, -1, -1)
    assert bitmap.bytes == sample_bytes(
        """
        x...x..
        x...x..
        x...x..
        .xxx...
        ..xxx..
        """
    )


def test_scroll_rect():
    """Test scrolling."""
    bitmap = Bitmap((7, 5), sample_bytes())
    bitmap.scroll_rect(1, 2, 2, 3, 1, 1)
    assert bitmap.bytes == sample_bytes(
        """
        ..xxx..
        .x...x.
        .x...x.
        .xx..x.
        ..xxx..
        """
    )
