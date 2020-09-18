from argparse import ArgumentParser
import cv2
import numpy as np
from PySide2 import (
        QtWidgets,
        QtCore,
        QtGui,
        )
from flytrack.config import Config
from flytrack.client import Client
from flytrack.client.display_main import DisplayMain
from flytrack.client.display_zoom import DisplayZoom


class MainDisplay(QtWidgets.QMainWindow):
    def __init__(self, video):
        super().__init__()
        #self.setStyleSheet('''
        #background: #00000000;
        #''')

        self.reader = cv2.VideoCapture(video)
        self.client = Client('tcp://127.0.0.1:{}'.format(
                                Config.Instance.networking.port))

        self.frame_count  = self.reader.get(cv2.CAP_PROP_FRAME_COUNT)
        self.frame_width  = self.reader.get(cv2.CAP_PROP_FRAME_WIDTH)
        self.frame_height = self.reader.get(cv2.CAP_PROP_FRAME_HEIGHT)
        self.resize(self.frame_width - 256, self.frame_height)
        self.setup_ui()

        # Initialize to frame 0.
        self.changed_frame_index()

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

        self.slider_blocked = False
        self.slider.valueChanged.connect(self.lcd.display)

        # -- {
        def sighandler1():
            self.slider_blocked = False
            self.changed_frame_index()

        def setblocked():
            self.slider_blocked = True

        self.slider.sliderPressed.connect(setblocked)
        self.slider.sliderReleased.connect(sighandler1)
        # -- }

        # -- {
        def sighandler2(value):
            if not self.slider_blocked:
                self.changed_frame_index()

        self.slider.valueChanged.connect(sighandler2)
        # -- }

        # Add display zoom
        self.zoom = DisplayZoom(self)
        self.zoom.setSizePolicy(
                QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed,
                                      QtWidgets.QSizePolicy.Fixed))
        self.layout.addWidget(self.zoom, 1, 1, 1, 1, QtCore.Qt.AlignTop)

        # Add the display.
        self.display = \
                DisplayMain(self, self.client, self.frame_width,
                            self.frame_height)
        self.layout.addWidget(self.display, 1, 0, 1, 1)

        # {
        menubar = self.menuBar()
        options = menubar.addMenu('Command')
        menu_save = options.addAction('Save')
        menu_save.setShortcut(QtGui.QKeySequence('Ctrl+S'))

        menu_help = options.addAction('Help')

        menu_exit = options.addAction('Exit')
        menu_exit.triggered.connect(QtWidgets.QApplication.quit)
        # }

        # {
        options = menubar.addMenu('Display')
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




def main(video):
    app = QtWidgets.QApplication([""])
    main = MainDisplay(video)
    main.show()
    app.exec_()

if __name__ == '__main__':
    argp = ArgumentParser()
    argp.add_argument(
            '--video',
            required=True)
    args = argp.parse_args(argv)

    main(args.video)
