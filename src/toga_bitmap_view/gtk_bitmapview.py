from gi.repository import GTK_VERSION, Gtk, GdkPixbuf, GLib
from travertino.size import at_least

from toga_gtk.keys import toga_key
from toga.handlers import WeakrefCallable
from toga_gtk.widgets.base import Widget

from .bitmap import Bitmap
from .pixel_format import RGB888


class BitmapView(Widget):
    _format = RGB888

    def create(self):
        # Allocate a memory buffer to store pixel data.
        self.memory_stride = self.interface.size[0] * self._format.pixel_size
        self.memory_size = self.memory_stride * self.interface.size[1]
        self.memory = bytearray(self.memory_size)

        # create a bitmap around the memory
        self.bitmap = Bitmap(self.interface.size, self.memory, format=self._format)

        # Create an image from the pixel buffer.
        self.native = Gtk.Image()
        self.native.set_can_focus(True)

        if GTK_VERSION < (4, 0, 0):  # pragma: no-cover-if-gtk4
            self.native.connect("key-press-event", self.gtk_key_press_event)
        else:
            self.key_controller = Gtk.EventControllerKey.new()
            self.native.add_controller(self.key_controller)
            self.key_controller.connect(
                "key-pressed", WeakrefCallable(self.gtk_key_pressed)
            )

        # Current state of redraw updates
        self._suspended = 0
        self._update_pending = False

    def create_pixbuf(self, width, height):
        pixbuf = GdkPixbuf.Pixbuf.new_from_bytes(
            data=GLib.Bytes(self.memory),
            colorspace=GdkPixbuf.Colorspace.RGB,
            has_alpha=False,
            bits_per_sample=8,
            width=self.interface.size[0],
            height=self.interface.size[1],
            rowstride=self.memory_stride,
        )
        return pixbuf.scale_simple(width, height, GdkPixbuf.InterpType.BILINEAR)

    if GTK_VERSION < (4, 0, 0):  # pragma: no-cover-if-gtk4

        def gtk_key_press_event(self, _entry, event):
            key_pressed = toga_key(event.keyval, event.state)
            if key_pressed:
                self.interface.on_key_press(**key_pressed)

    else:  # pragma: no-cover-if-gtk3

        def gtk_key_pressed(self, _controller, keyval, _keycode, state):
            key_pressed = toga_key(keyval, state)
            if key_pressed:
                self.interface.on_key_press(**key_pressed)

    def rehint(self):
        self.interface.intrinsic.width = at_least(self.interface.size[0])
        self.interface.intrinsic.height = at_least(self.interface.size[1])

    def set_on_key_press(self, on_key_press):
        pass

    def set(self, x, y, color):
        pixel = self._format.from_color(color)
        self.bitmap.set_pixel(x, y, pixel)
        self.update_display()

    def get(self, x, y, color):
        return self.bitmap.get_pixel(x, y).color

    def rect(self, x, y, width, height, color):
        pixel = self._format.from_color(color)
        self.bitmap.set_rect(x, y, width, height, pixel)
        self.update_display()

    def scroll(self, x, y, width, height, dx, dy):
        self.bitmap.scroll_rect(x, y, width, height, dx, dy)
        self.update_display()

    def suspend_updates(self):
        """Temporarily suspend updates on the bitmap view.

        Operates as a stack; multiple suspend operations will
        increase the suspension "depth". Updates will only
        resume when the depth returns to 0.
        """
        self._suspended += 1

    def update_display(self):
        """Request an update of the bitmap display.

        The update may be suspended if the
        """
        if self._suspended:
            self._update_pending = True
        else:
            allocation = self.native.get_allocation()
            self.native.set_from_pixbuf(
                self.create_pixbuf(
                    allocation.width,
                    allocation.height,
                )
            )
            self._update_pending = False

    def resume_updates(self):
        """Reduce the suspension depth by 1 level.

        Operates as a stack; multiple suspend operations will
        increase the suspension "depth". Updates will only
        resume when the depth returns to 0.
        """
        if self._suspended > 0:
            self._suspended -= 1

        if self._suspended == 0:
            if self._update_pending:
                allocation = self.native.get_allocation()
                self.native.set_from_pixbuf(
                    self.create_pixbuf(
                        allocation.width,
                        allocation.height,
                    )
                )
                self._update_pending = False
