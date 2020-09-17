import numpy as np
from matplotlib import cm
from PySide2 import (
        QtWidgets,
        QtCore,
        QtGui,
        )

class DisplayMain(QtWidgets.QWidget):
    def __init__(self, parent, client, width, height):
        super().__init__(parent)
        self.p = parent
        self.client = client
        self.resize(width, height)
        self.setup_ui()

        # {
        self.show_image = False
        self.show_peaks= False
        self.show_heatmap = False
        # }

        # {
        self.frame_idx = -1
        self.last_frame_idx = -2
        # }

        # {
        self.image = None
        self.heatmap = None
        self.peaks = None
        # }

    def setup_ui(self):
        policy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding,
                                       QtWidgets.QSizePolicy.Expanding)
        policy.setHorizontalStretch(0)
        policy.setVerticalStretch(0)
        policy.setHeightForWidth(False)
        self.setSizePolicy(policy)
        self.setMouseTracking(True)

        pal = self.palette()
        pal.setColor(QtGui.QPalette.Background, QtCore.Qt.black)
        self.setAutoFillBackground(True)
        self.setPalette(pal)

        # {
        indices = np.linspace(0, 1, 256)
        rgbas = cm.inferno(indices)

        self.rgbas_noalpha = [
                QtGui.QColor(
                    int(r * 255),
                    int(g * 255),
                    int(b * 255),
                    int(a * 255)).rgba() for r, g, b, a in rgbas]

        rgbas[:,3] *= indices
        self.rgbas_alpha = [
                QtGui.QColor(
                    int(r * 255),
                    int(g * 255),
                    int(b * 255),
                    int(a * 255)).rgba() for r, g, b, a in rgbas]

        # }

    def set_show_image(self, doit):
        self.show_image = doit
        self.update()

    def set_show_peaks(self, doit):
        self.show_peaks = doit
        self.update()

    def set_show_heatmap(self, doit):
        self.show_heatmap = doit
        self.update()

    def load_image(self, frame_idx, image):
        self.image = image[:, :, 0].copy()
        (self.heatmap, self.peaks) = self.client.detect(self.image)
        self.frame_idx = frame_idx
        self.update()

    def mouseMoveEvent(self, e):
        screen = QtWidgets.QApplication.primaryScreen()
        region = screen.grabWindow(
                        self.winId(),
                        e.x() - 32,
                        e.y() - 32,
                        64,
                        64)
        region = region.scaled(128, 128)
        self.p.update_zoom(region)

    def paintEvent(self, e):
        painter = QtGui.QPainter()
        painter.begin(self)

        if self.image is not None:
            self.__draw_base(painter)

        if self.heatmap is not None:
            self.__draw_heatmap(painter)

        if self.peaks is not None:
            self.__draw_peaks(painter)

        self.last_frame_idx = self.frame_idx

        painter.end()

    def __draw_base(self, painter):
        if not self.show_image:
            return

        img = QtGui.QImage(self.image,
                           self.image.shape[0],
                           self.image.shape[1],
                           QtGui.QImage.Format_Grayscale8)
        self.qimage = img.scaled(self.size(), QtCore.Qt.KeepAspectRatio)
        painter.drawImage(0, 0, self.qimage)

    def __draw_heatmap(self, painter):
        if not self.show_heatmap:
            return

        # Normalize
        min = np.min(self.heatmap)
        max = np.max(self.heatmap)
        heatmap = (self.heatmap - min) / (max - min)

        # Colorize
        heatmap8 = (heatmap * 255).astype(np.uint8)

        # TODO: Document
        if self.show_image:
            rgbas = self.rgbas_alpha
        else:
            rgbas = self.rgbas_noalpha

        # Create
        image = QtGui.QImage(heatmap8.data,
                             heatmap8.shape[0],
                             heatmap8.shape[1],
                             QtGui.QImage.Format_Indexed8)
        self.qheat_map = image.scaled(self.size(), QtCore.Qt.KeepAspectRatio)
        self.qheat_map.setColorTable(rgbas)
        painter.drawImage(0, 0, self.qheat_map)

    def __draw_peaks(self, painter):
        if not self.show_peaks:
            return

        painter.setPen(QtGui.QColor('#f67c25'))
        mindim = min(self.size().height(), self.size().width())
        for (r, c) in self.peaks:
            row = mindim * r
            col = mindim * c
            center = QtCore.QPoint(row, col)
            origin = QtCore.QPoint(row, col - 20)
            lhs    = QtCore.QPoint(row - 5, col - 7)
            rhs    = QtCore.QPoint(row + 5, col - 7)

            painter.drawLine(center, origin)
            painter.drawLine(center, lhs)
            painter.drawLine(center, rhs)

