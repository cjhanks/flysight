import numpy as np
from matplotlib import cm
from flysight.client.display_zoom import DisplayZoom
from PySide2 import (
        QtWidgets,
        QtCore,
        QtGui,
        )

class DisplayMain(QtWidgets.QWidget):
    """
    :class DisplayMain:

    This class implements the main display region for heatmaps/image/peaks.
    """
    def __init__(self, parent, client, width: int, height: int):
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
        self.peaks = []
        # }

    def setup_ui(self):
        # {
        # Configure the main window defaults.  It enables mouse tracking to
        # be used by the zoom, and sets a black background.
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
        # }

        # {
        # Pre-compute RGBA values for the two different modes from the `inferno`
        # colormap.
        #
        # self.rgbas_alpha is used when the heatmap is overlayed atop the image.
        # self.rgbas_noalpha is used when no image is displayed.
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

    def set_show_image(self, toggle: bool):
        """
        Toggle whether the image should be showed.
        """
        self.show_image = toggle
        self.update()

    def set_show_peaks(self, toggle: bool):
        """
        Toggle whether the peak arrows should be showed.
        """
        self.show_peaks = toggle
        self.update()

    def set_show_heatmap(self, toggle: bool):
        """
        Toggle whether the heatmap should be showed.
        """
        self.show_heatmap = toggle
        self.update()

    def load_image(self, frame_idx: int, image: np.array):
        """
        Given an RGB image:
        - Convert it to grayscale (assuming uniform channel)
        - Use the ZMQ client to fetch a heatmap/peak solution
        - Refresh the UI
        """
        self.image = image[:, :, 0].copy()
        (self.heatmap, self.peaks) = self.client.detect(self.image)
        self.frame_idx = frame_idx
        self.update()

    def mouseMoveEvent(self, e):
        """
        Handle the mouse move to update the zoom region.
        """
        self.update_zoom(e)

    def update_zoom(self, pos):
        """
        Update the zoom box if it's possible.
        """
        # Compute the bounding region.  If the computed box would fall outside
        # of the display widget, don't bother to update the zoom region.
        x_min = pos.x() - DisplayZoom.ZOOM_DIM
        y_min = pos.y() - DisplayZoom.ZOOM_DIM
        x_max = pos.x() + DisplayZoom.ZOOM_DIM
        y_max = pos.y() + DisplayZoom.ZOOM_DIM

        if not self.rect().contains(QtCore.QPoint(y_min, x_min)) or \
           not self.rect().contains(QtCore.QPoint(y_max, x_max)):
            return

        # Update the actual zoom region.
        screen = QtWidgets.QApplication.primaryScreen()
        region = screen.grabWindow(
                        self.winId(),
                        pos.x() - DisplayZoom.ZOOM_DIM // 2,
                        pos.y() - DisplayZoom.ZOOM_DIM // 2,
                        DisplayZoom.ZOOM_DIM,
                        DisplayZoom.ZOOM_DIM)
        region = region.scaled(128, 128)
        self.p.update_zoom(region)

    def paintEvent(self, e):
        """
        Overloaded paintEvent controlled by QWidget logic.
        """
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

        self.update_zoom(self.mapFromGlobal(QtGui.QCursor.pos()))

    def __draw_base(self, painter):
        """
        If the image is enabled, draw the image data to the display widget.
        """
        if not self.show_image:
            return

        img = QtGui.QImage(self.image,
                           self.image.shape[0],
                           self.image.shape[1],
                           QtGui.QImage.Format_Grayscale8)
        self.qimage = img.scaled(self.size(), QtCore.Qt.KeepAspectRatio)
        painter.drawImage(0, 0, self.qimage)

    def __draw_heatmap(self, painter):
        """
        If the heatmap is enabled...
        - Draw the translucent heatmap over the image (if the image is drawn)
        - Draw the opaque heatmap (if the image is not drawn).
        """
        if not self.show_heatmap:
            return

        # Normalize [0, 1]
        min = np.min(self.heatmap)
        max = np.max(self.heatmap)
        heatmap = (self.heatmap - min) / (max - min)

        # Choose the RGBA colormap
        heatmap8 = (heatmap * 255).astype(np.uint8)
        if self.show_image:
            rgbas = self.rgbas_alpha
        else:
            rgbas = self.rgbas_noalpha

        # Create the image and draw it.
        image = QtGui.QImage(heatmap8.data,
                             heatmap8.shape[0],
                             heatmap8.shape[1],
                             QtGui.QImage.Format_Indexed8)
        self.qheat_map = image.scaled(self.size(), QtCore.Qt.KeepAspectRatio)
        self.qheat_map.setColorTable(rgbas)
        painter.drawImage(0, 0, self.qheat_map)

    def __draw_peaks(self, painter):
        """
        If the peaks are enabled, draw the arrows on the display.
        """
        if not self.show_peaks:
            return

        painter.setPen(QtGui.QColor('#f67c25'))
        mindim = min(self.size().height(), self.size().width())
        for (r, c) in self.peaks:
            row = mindim * r
            col = mindim * c

            # {
            # Draw an arrow.
            center = QtCore.QPoint(row, col)
            origin = QtCore.QPoint(row, col - 20)
            lhs    = QtCore.QPoint(row - 5, col - 7)
            rhs    = QtCore.QPoint(row + 5, col - 7)

            painter.drawLine(center, origin)
            painter.drawLine(center, lhs)
            painter.drawLine(center, rhs)
            # }

