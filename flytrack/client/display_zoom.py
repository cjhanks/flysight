import numpy as np
from PySide2 import (
        QtWidgets,
        QtCore,
        QtGui,
        )


class DisplayZoom(QtWidgets.QWidget):
    """
    :class DisplayZoom:

    This handles the 2x zoom box for the widget.
    """
    ZOOM_DIM = 64

    def __init__(self, parent):
        super().__init__(parent)
        self.image = None

    def update_image(self, image: np.array):
        """
        Set the zoom image data and redraw.
        """
        self.image = image
        self.update()

    def sizeHint(self):
        """
        This works in conjunction with the main widget to set a fixed size for
        this widget.
        """
        return QtCore.QSize(DisplayZoom.ZOOM_DIM * 2,
                            DisplayZoom.ZOOM_DIM * 2)

    def paintEvent(self, ev):
        """
        Overloaded QWidget paint update.
        """
        if self.image is None:
            return

        painter = QtGui.QPainter()
        painter.begin(self)
        painter.drawPixmap(0, 0, self.image)
        painter.end()

