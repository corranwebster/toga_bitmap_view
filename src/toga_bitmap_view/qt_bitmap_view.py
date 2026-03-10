from PySide6.QtCore import Qt
from PySide6.QtGui import QImage, QKeyEvent, QPixmap, QKeySequence
from PySide6.QtWidgets import QLabel
from travertino.size import at_least

from toga_qt.keys import qt_to_toga_key
from toga.handlers import WeakrefCallable
from toga_qt.widgets.base import Widget

from .bitmap import Bitmap
from .pixel_format import RGBA32


class QBitmapView(QLabel):

    def __init__(self, impl, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.impl = impl
        self.interface = impl.interface

    def keyPressEvent(self, ev: QKeyEvent) -> None:
        key_sequence = QKeySequence(ev.keyCombination())
        keys = qt_to_toga_key(key_sequence)
        if keys is not None:
            keys['text'] = ev.text()
            self.interface.on_key_press(**keys)


class BitmapView(Widget):
    _format = RGBA32

    def create(self):
        # Allocate a memory buffer to store pixel data.
        self.memory_stride = self.interface.size[0] * self._format.pixel_size
        self.memory_size = self.memory_stride * self.interface.size[1]
        self.memory = bytearray(self.memory_size)

        # create a bitmap around the memory
        self.bitmap = Bitmap(self.interface.size, self.memory, format=self._format)
        width, height = self.interface.size
        self.native_image = QImage(self.memory, width, height, QImage.Format.Format_RGBA8888)

        # Create an image from the pixel buffer.
        self.native = QBitmapView(self)
        self.native.setScaledContents(True)
        self.native.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.native.setPixmap(self.create_pixmap())

        # Current state of redraw updates
        self._suspended = 0
        self._update_pending = False

    def set_on_key_press(self, on_key_press):
        pass

    def create_pixmap(self):
        pixmap = QPixmap.fromImage(self.native_image)
        return pixmap

    def rehint(self):
        self.interface.intrinsic.width = at_least(self.interface.size[0])
        self.interface.intrinsic.height = at_least(self.interface.size[1])

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
            self.native.setPixmap(
                self.create_pixmap()
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
                self.native.setPixmap(
                    self.create_pixmap()
                )
                self._update_pending = False
