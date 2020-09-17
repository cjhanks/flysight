from argparse import ArgumentParser
import cv2
import numpy as np
from matplotlib import cm
from PySide2 import (
        QtWidgets,
        QtCore,
        QtGui,
        )
from flytrack.client import Client


class MainDisplay(QtWidgets.QMainWindow):
    def __init__(self, args):
        super().__init__()
        #self.setStyleSheet('''
        #background: rgb(246, 124, 37);
        #''')

        self.reader = cv2.VideoCapture(args.video)
        self.client = Client('tcp://127.0.0.1:8003')

        self.frame_count  = self.reader.get(cv2.CAP_PROP_FRAME_COUNT)
        self.frame_width  = self.reader.get(cv2.CAP_PROP_FRAME_WIDTH)
        self.frame_height = self.reader.get(cv2.CAP_PROP_FRAME_HEIGHT)
        self.resize(self.frame_width - 256, self.frame_height)
        self.setup_ui()

    def setup_ui(self):
        self.central = QtWidgets.QWidget(self)
        self.setCentralWidget(self.central)

        self.layout = QtWidgets.QGridLayout(self.central)

        # {
        self.slider = QtWidgets.QSlider(self)
        self.slider.setOrientation(QtCore.Qt.Horizontal)
        self.slider.setMaximum(self.frame_count)
        self.slider.setSizePolicy(
                QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum,
                                      QtWidgets.QSizePolicy.Minimum))
        self.slider.setStyleSheet('''
QSlider::groove:horizontal {
border: 1px solid #bbb;
background: white;
height: 10px;
border-radius: 4px;
}

QSlider::sub-page:horizontal {
background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1,
    stop: 0 #f5c39f, stop: 1 #f67c25);
border: 1px solid #777;
height: 10px;
border-radius: 4px;
}

QSlider::add-page:horizontal {
background: #fff;
border: 1px solid #777;
height: 10px;
border-radius: 4px;
}

QSlider::handle:horizontal {
background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
    stop:0 #404040, stop:1 #404040);
border: 1px solid #777;
width: 13px;
margin-top: -2px;
margin-bottom: -2px;
border-radius: 4px;
}

QSlider::handle:horizontal:hover {
background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
    stop:0 #000000, stop:1 #000000);
border: 1px solid #444;
border-radius: 4px;
}
''')
        self.layout.addWidget(self.slider, 0, 0, 1, 1)

        self.lcd = QtWidgets.QLCDNumber(self)
        self.lcd.setSizePolicy(
                QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed,
                                      QtWidgets.QSizePolicy.Fixed))

        self.lcd.setStyleSheet('''
QLCDNumber{
  background-color: #000000;
  border: 2px solid #404040;
  border-width: 2px;
  border-radius: 10px;
  color: #f67c25;
}
''')
        self.layout.addWidget(self.lcd, 0, 1, 1, 1,
                              QtCore.Qt.AlignCenter)

        self.slider.valueChanged.connect(self.lcd.display)
        self.slider.sliderReleased.connect(self.changed_frame_index)
        # }

        # Add display zoom
        self.zoom = DisplayZoom(self)
        self.zoom.setSizePolicy(
                QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed,
                                      QtWidgets.QSizePolicy.Fixed))
        self.layout.addWidget(self.zoom, 1, 1, 1, 1, QtCore.Qt.AlignTop)

        # Add the display.
        self.display = \
                DisplayTool(self, self.client, self.frame_width,
                            self.frame_height)
        self.layout.addWidget(self.display, 1, 0, 1, 1)

        # {
        menubar = self.menuBar()
        options = menubar.addMenu('Options')
        menu_show_image = options.addAction('Show Image')
        menu_show_image.toggled.connect(self.display.set_show_image)
        menu_show_image.setShortcut(QtGui.QKeySequence('Ctrl+I'))
        menu_show_image.setCheckable(True)
        menu_show_image.setChecked(True)

        menu_show_peaks = options.addAction('Show Peaks')
        menu_show_peaks.toggled.connect(self.display.set_show_peaks)
        menu_show_peaks.setShortcut(QtGui.QKeySequence('Ctrl+P'))
        menu_show_peaks.setCheckable(True)
        menu_show_peaks.setChecked(False)

        menu_show_heatmap = options.addAction('Show HeatMap')
        menu_show_heatmap.toggled.connect(self.display.set_show_heatmap)
        menu_show_heatmap.setShortcut(QtGui.QKeySequence('Ctrl+H'))
        menu_show_heatmap.setCheckable(True)
        menu_show_heatmap.setChecked(True)
        # }

    def changed_frame_index(self):
        frame_idx = int(self.lcd.value())
        self.reader.set(cv2.CAP_PROP_POS_FRAMES, frame_idx)

        (status, image) = self.reader.read()
        if not status:
            print('Failed to read from video stream.')
            return

        self.display.load_image(frame_idx, image)

    def update_zoom(self, image):
        self.zoom.update_image(image)


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


class DisplayTool(QtWidgets.QWidget):
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
        indices = np.linspace(0, 1, 256)
        rgbas = cm.jet(indices)

        # TODO: Document
        if self.show_image:
            rgbas[:,3] *= indices

        rgbas = [QtGui.QColor(
                    int(r * 255),
                    int(g * 255),
                    int(b * 255),
                    int(a * 255)).rgba() for r, g, b, a in rgbas]

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


def main(argv=None):
    argp = ArgumentParser()
    argp.add_argument(
            '--video',
            required=True)
    args = argp.parse_args(argv)

    app = QtWidgets.QApplication([""])
    main = MainDisplay(args)
    main.show()
    app.exec_()

if __name__ == '__main__':
    main()
