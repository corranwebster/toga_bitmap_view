from unittest.mock import Mock

import toga
from toga_dummy.utils import assert_action_performed
from travertino.colors import rgb

from toga_bitmap_view.bitmap import Bitmap
from toga_bitmap_view.bitmap_view import BitmapView


def dummy_on_key_press(widget, **kwargs):
    pass


def test_create():
    """A BitmapView can be created."""
    bitmap_view = BitmapView()

    assert bitmap_view._impl.interface is bitmap_view
    assert_action_performed(bitmap_view, "create BitmapView")

    assert bitmap_view.size == (320, 200)
    assert isinstance(bitmap_view.bitmap, Bitmap)
    assert bitmap_view.bitmap.size == (320, 200)
    assert bitmap_view.enabled


def test_get():
    """A pixel value can be retrieved."""
    bitmap_view = BitmapView()
    color = bitmap_view.get(10, 20)

    assert_action_performed(bitmap_view, "get pixel (10, 20)")

    assert color.rgb.r == 0
    assert color.rgb.g == 0
    assert color.rgb.b == 0


def test_set():
    """A pixel value can be set."""
    bitmap_view = BitmapView()
    bitmap_view.set(10, 20, rgb(255, 0, 0))

    assert_action_performed(
        bitmap_view,
        "set pixel (10, 20) to rgb(255 0 0 / 1.0)",
    )
    assert_action_performed(bitmap_view, "display updated")


def test_rect():
    """A pixel value can be set."""
    bitmap_view = BitmapView()
    bitmap_view.rect(10, 20, 30, 40, rgb(255, 0, 0))

    assert_action_performed(
        bitmap_view,
        "set rect (10, 20, 30, 40) to rgb(255 0 0 / 1.0)",
    )
    assert_action_performed(bitmap_view, "display updated")


def test_scroll():
    """A pixel value can be set."""
    bitmap_view = BitmapView()
    bitmap_view.scroll(10, 20, 30, 40, 5, -15)

    assert_action_performed(
        bitmap_view,
        "scroll (10, 20, 30, 40) by (5, -15)",
    )
    assert_action_performed(bitmap_view, "display updated")


def test_with():
    """A pixel value can be set."""
    bitmap_view = BitmapView()

    with bitmap_view:
        assert_action_performed(bitmap_view, "updates suspended")

        bitmap_view.set(10, 10, rgb(255, 0, 0))

        assert_action_performed(
            bitmap_view,
            "set pixel (10, 10) to rgb(255 0 0 / 1.0)",
        )
        assert_action_performed(bitmap_view, "update pending")

        with bitmap_view:
            assert_action_performed(bitmap_view, "updates suspended")

            bitmap_view.set(11, 10, rgb(255, 0, 0))

            assert_action_performed(
                bitmap_view,
                "set pixel (11, 10) to rgb(255 0 0 / 1.0)",
            )
            assert_action_performed(bitmap_view, "update pending")

        assert_action_performed(bitmap_view, "updates still suspended")

    assert_action_performed(bitmap_view, "display updated")


def test_on_key_press():
    bitmap_view = BitmapView()

    assert bitmap_view._on_key_press._raw is None

    handler = Mock()

    bitmap_view.on_key_press = handler

    assert bitmap_view._on_key_press._raw is handler

    bitmap_view._impl.simulate_key_press(toga.Key.A, {toga.Key.SHIFT}, "A")

    handler.assert_called_once_with(
        bitmap_view,
        key=toga.Key.A,
        modifiers={toga.Key.SHIFT},
        text="A",
    )
