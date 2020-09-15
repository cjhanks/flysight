from argparse import ArgumentParser
import cv2
import numpy as np
from matplotlib import cm
from PySide2 import (
        QtWidgets,
        QtCore,
        QtGui
        #QApplication,
        #QDialog,
        #QLineEdit,
        #QPushButton,
        #QWidget,
        )
from flytrack.client import Client


class MainDisplay(QtWidgets.QMainWindow):
    def __init__(self, args):
        super().__init__()
        self.reader = cv2.VideoCapture(args.video)
        self.client = Client('tcp://127.0.0.1:8003')

        self.frame_count  = self.reader.get(cv2.CAP_PROP_FRAME_COUNT)
        self.frame_width  = self.reader.get(cv2.CAP_PROP_FRAME_WIDTH)
        self.frame_height = self.reader.get(cv2.CAP_PROP_FRAME_HEIGHT)
        self.resize(self.frame_width, self.frame_height)

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
                QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding,
                                      QtWidgets.QSizePolicy.Minimum))
        self.layout.addWidget(self.slider, 0, 0, 1, 1)

        self.lcd = QtWidgets.QLCDNumber(self)
        self.lcd.setSizePolicy(
                QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum,
                                      QtWidgets.QSizePolicy.Minimum))
        self.layout.addWidget(self.lcd, 0, 1, 1, 1)

        self.slider.valueChanged.connect(self.lcd.display)
        self.slider.sliderReleased.connect(self.changed_frame_index)
        # }

        # Add the display.
        self.display = \
                DisplayTool(self, self.client, self.frame_width,
                            self.frame_height)

        self.layout.addWidget(self.display, 1, 0, 1, 2)

        # {
        menubar = self.menuBar()
        options = menubar.addMenu('Options')
        menu_show_image = \
                options.addAction('Show Image',
                                  shortcut=QtGui.QKeySequence('Ctrl+I'))
        menu_show_image.setCheckable(True)
        menu_show_image.setChecked(True)

        menu_show_peaks = \
                options.addAction('Show Peaks',
                                  shortcut=QtGui.QKeySequence('Ctrl+P'))
        menu_show_peaks.setCheckable(True)
        menu_show_peaks.setChecked(False)

        menu_show_heatmap = \
                options.addAction('Show HeatMap',
                                  shortcut=QtGui.QKeySequence('Ctrl+H'))
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

        self.display.load_image(image)


class DisplayTool(QtWidgets.QWidget):
    def __init__(self, parent, client, width, height):
        super().__init__(parent)
        self.client = client
        self.resize(width, height)
        self.setup_ui()

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

    @QtCore.Slot('set_show_image')
    def set_show_image(self):
        print('HERE')

    def load_image(self, image):
        self.image = image[:, :, 0].copy()
        (self.heatmap, self.peaks) = self.client.detect(self.image)
        self.update()

    def paintEvent(self, e):
        painter = QtGui.QPainter()
        painter.begin(self)

        if self.image is not None:
            self.__draw_base(painter)

        if self.heatmap is not None:
            self.__draw_heatmap(painter)

        if self.peaks is not None:
            self.__draw_peaks(painter)

        self.image = None
        self.heatmap = None
        self.peaks = None
        painter.end()

    def __draw_base(self, painter):
        img = QtGui.QImage(self.image,
                           self.image.shape[0],
                           self.image.shape[1],
                           QtGui.QImage.Format_Grayscale8)
        self.qimage = img.scaled(self.size(), QtCore.Qt.KeepAspectRatio)
        painter.drawImage(0, 0, self.qimage)

    def __draw_heatmap(self, painter):
        # Normalize
        min = np.min(self.heatmap)
        max = np.max(self.heatmap)
        heatmap = (self.heatmap - min) / (max - min)

        # Colorize
        heatmap8 = (heatmap * 255).astype(np.uint8)
        indices = np.linspace(0, 1, 256)
        rgbas = cm.jet(indices)
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
        painter.setPen(QtCore.Qt.red)
        for (r, c) in self.peaks:
            row = self.qimage.size().height() * r
            col = self.qimage.size().width() * c
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
