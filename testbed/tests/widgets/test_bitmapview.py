import pytest

import toga

from toga_bitmap_view.bitmapview import BitmapView

from .conftest import build_cleanup_test
from .properties import (  # noqa: F401
    test_focus,
    test_background_color,
    test_background_color_reset,
    test_background_color_transparent,
    # test_color,
    # test_color_reset,
    # test_enabled,
    # test_flex_horizontal_widget_size,
    # test_focus_noop,
    # test_font,
    # test_font_attrs,
    # test_text,
    # test_text_align,
    # test_text_width_change,
)


@pytest.fixture
async def widget():
    return BitmapView(size=(100, 75))


test_cleanup = build_cleanup_test(toga.Label, args=("hello, this is a label",))

