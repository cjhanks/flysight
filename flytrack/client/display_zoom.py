from PySide2 import (
        QtWidgets,
        QtCore,
        QtGui,
        )


class DisplayZoom(QtWidgets.QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.image = None

    def update_image(self, image):
        self.image = image
        self.update()

    def sizeHint(self):
        return QtCore.QSize(128, 128)

    def paintEvent(self, ev):
        if self.image is None:
            return

        painter = QtGui.QPainter()
        painter.begin(self)
        try:
            painter.drawPixmap(0, 0, self.image)
        except Exception as err:
            print(err)
        painter.end()

