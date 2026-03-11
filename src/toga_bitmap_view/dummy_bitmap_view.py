from toga_dummy.widgets.base import Widget

from .bitmap import Bitmap
from .pixel_format import RGBA32


class BitmapView(Widget):
    _format = RGBA32

    def create(self):
        self._action("create BitmapView")
        # Allocate a memory buffer to store pixel data.
        self.memory_stride = self.interface.size[0] * self._format.pixel_size
        self.memory_size = self.memory_stride * self.interface.size[1]
        self.memory = bytearray(self.memory_size)

        # create a bitmap around the memory
        self.bitmap = Bitmap(self.interface.size, self.memory, format=self._format)

        # Current state of redraw updates
        self._suspended = 0
        self._update_pending = False

    def set_on_key_press(self, on_key_press):
        self._set_value("on_key_press", on_key_press)

    def set(self, x, y, color):
        self._action(f"set pixel ({x}, {y}) to {color}")
        pixel = self._format.from_color(color)
        self.bitmap.set_pixel(x, y, pixel)
        self.update_display()

    def get(self, x, y):
        self._action(f"get pixel ({x}, {y})")
        return self.bitmap.get_pixel(x, y).color

    def rect(self, x, y, width, height, color):
        self._action(f"set rect ({x}, {y}, {width}, {height}) to {color}")
        pixel = self._format.from_color(color)
        self.bitmap.set_rect(x, y, width, height, pixel)
        self.update_display()

    def scroll(self, x, y, width, height, dx, dy):
        self._action(f"scroll ({x}, {y}, {width}, {height}) by ({dx}, {dy})")
        self.bitmap.scroll_rect(x, y, width, height, dx, dy)
        self.update_display()

    def suspend_updates(self):
        """Temporarily suspend updates on the bitmap view.

        Operates as a stack; multiple suspend operations will
        increase the suspension "depth". Updates will only
        resume when the depth returns to 0.
        """
        self._action("updates suspended")
        self._suspended += 1

    def update_display(self):
        """Request an update of the bitmap display."""
        if self._suspended:
            self._update_pending = True
            self._action("update pending")
        else:
            self._update_pending = False
            self._action("display updated")

    def resume_updates(self):
        """Reduce the suspension depth by 1 level.

        Operates as a stack; multiple suspend operations will
        increase the suspension "depth". Updates will only
        resume when the depth returns to 0.
        """
        if self._suspended > 0:
            self._suspended -= 1
            self._action("updates still suspended")

        if self._suspended == 0:
            if self._update_pending:
                self._update_pending = False
                self._action("display updated")

    def simulate_key_press(self, key, modifiers, text):
        self.interface.on_key_press(
            key=key,
            modifiers=modifiers,
            text=text,
        )
