from __future__ import annotations

from functools import cached_property
from typing import Any, Protocol

from travertino.colors import rgb

import toga
from toga.handlers import wrapped_handler
from toga.platform import get_factory



class OnKeyPressHandler(Protocol):
    def __call__(self, widget: BitmapView, key: toga.Key, **kwargs: Any) -> None:
        """A handler to invoke when the a key is pressed.

        :param widget: The BitmapView that gained focus.
        :param key: The key that was pressed.
        :param kwargs: Ensures compatibility with arguments added in future versions.
        """


class OnGainFocusHandler(Protocol):
    def __call__(self, widget: BitmapView, **kwargs: Any) -> None:
        """A handler to invoke when the bitmap view gains focus.

        :param widget: The BitmapView that gained focus.
        :param kwargs: Ensures compatibility with arguments added in future versions.
        """


class OnLoseFocusHandler(Protocol):
    def __call__(self, widget: BitmapView, **kwargs: Any) -> None:
        """A handler to invoke when the bitmap view loses focus.

        :param widget: The BitmapView that lost focus.
        :param kwargs: Ensures compatibility with arguments added in future versions.
        """


class BitmapView(toga.Widget):

    def __init__(
        self,
        id: str | None = None,
        size: tuple[int, int] = (320, 200),
        style: toga.StyleT | None = None,
        on_key_press: OnKeyPressHandler | None = None,
        on_gain_focus: OnGainFocusHandler | None = None,
        on_lose_focus: OnLoseFocusHandler | None = None,
        enabled: bool = True,
        **kwargs
    ):
        """Create a new single-line text input widget.

        :param id: The ID for the widget.
        :param style: A style object. If no style is provided, a default style will be
            applied to the widget.
        :param on_key_press: A handler that will be invoked when the user presses a key
            on the keyboard.
        :param on_gain_focus: A handler that will be invoked when the widget gains
            input focus.
        :param on_lose_focus: A handler that will be invoked when the widget loses
            input focus.
        :param kwargs: Initial style properties.
        """
        self._size = size

        super().__init__(
            id=id, style=style, **kwargs
        )

        # Set handlers
        self.on_key_press = on_key_press
        self.on_lose_focus = on_lose_focus
        self.on_gain_focus = on_gain_focus

        self.enabled = enabled

    @cached_property
    def factory(self):
        return get_factory("togax_bitmap_view")

    def _create(self):
        return self.factory.BitmapView(interface=self)

    @property
    def size(self):
        return self._size

    def set(self, x, y, color):
        self._impl.set(x, y, color)

    def get(self, x, y):
        return rgb(self._impl.get(x, y))

    def __enter__(self):
        self._impl.suspend_updates()
        return self

    def __exit__(self, type, value, traceback):
        self._impl.resume_updates()

    @property
    def on_key_press(self) -> OnKeyPressHandler:
        """The handler to invoke when a key is pressed.

        Returns:
            The function ``callable`` that is called on key press.
        """
        return self._on_key_press

    @on_key_press.setter
    def on_key_press(self, handler: OnKeyPressHandler | None):
        """Set the handler to invoke when a key is pressed.

        Args:
            handler (:obj:`callable`): The handler to invoke when a key
            is pressed.
        """
        self._on_key_press = wrapped_handler(self, handler)
        self._impl.set_on_key_press(self._on_key_press)

    @property
    def on_gain_focus(self) -> OnGainFocusHandler:
        """The handler to invoke when the widget gains input focus."""
        return self._on_gain_focus

    @on_gain_focus.setter
    def on_gain_focus(self, handler: OnGainFocusHandler | None) -> None:
        self._on_gain_focus = wrapped_handler(self, handler)

    @property
    def on_lose_focus(self) -> OnLoseFocusHandler:
        """The handler to invoke when the widget loses input focus."""
        return self._on_lose_focus

    @on_lose_focus.setter
    def on_lose_focus(self, handler: OnLoseFocusHandler | None) -> None:
        self._on_lose_focus = wrapped_handler(self, handler)
