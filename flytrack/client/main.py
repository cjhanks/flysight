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
from flytrack.client.resource_loader import Resource


class MainDisplay(QtWidgets.QMainWindow):
    """
    :class MainDisplay:

    Implements the main display for the GUI.  This is where the majority of the
    GUI logic lives.
    """
    def __init__(self, video: str):
        super().__init__()

        # Construct the OpenCV video capture object and extract some relevant
        # metadata which can be used to initialize various window sizes.
        self.reader = cv2.VideoCapture(video)
        self.frame_count  = self.reader.get(cv2.CAP_PROP_FRAME_COUNT)
        self.frame_width  = self.reader.get(cv2.CAP_PROP_FRAME_WIDTH)
        self.frame_height = self.reader.get(cv2.CAP_PROP_FRAME_HEIGHT)
        self.resize(self.frame_width - 256, self.frame_height)

        # Initialize the ZMQ socket connection.
        self.client = Client('tcp://127.0.0.1:{}'.format(
                                Config.Instance.networking.port))

        # Configure UI
        self.setup_ui()

        # Initialize to frame 0.
        self.changed_frame_index()

    def setup_ui(self):
        """
        Laborious UI configuration.
        """
        # Initialize the elements directly attached to the central widget and
        # configure the layout.
        self.central = QtWidgets.QWidget(self)
        self.setCentralWidget(self.central)
        self.layout = QtWidgets.QGridLayout(self.central)

        # {
        # Configure the slider which changes the selected frame and the
        # associated LCD display.
        self.slider = QtWidgets.QSlider(self)
        self.slider.setOrientation(QtCore.Qt.Horizontal)
        self.slider.setMaximum(self.frame_count)
        self.slider.setSizePolicy(
                QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum,
                                      QtWidgets.QSizePolicy.Minimum))
        self.slider.setStyleSheet(Resource.Get('slider'))
        self.layout.addWidget(self.slider, 0, 0, 1, 1)

        self.lcd = QtWidgets.QLCDNumber(self)
        self.lcd.setSizePolicy(
                QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed,
                                      QtWidgets.QSizePolicy.Fixed))
        self.lcd.setStyleSheet(Resource.Get('lcd'))
        self.layout.addWidget(self.lcd, 0, 1, 1, 1,
                              QtCore.Qt.AlignCenter)

        self.slider_blocked = False
        self.slider.valueChanged.connect(self.lcd.display)
        # }

        # {
        # Configure the slider signals.  We want to support two different modes
        # of changing the frame; dragging the slider, pressing left/right on the
        # keyboard.
        #
        # Left/right on the keyboard ignores the `sliderReleased`, so you have
        # to use the `valueChanged`.  But if you do that, then changing the
        # slider will try and update the image at every increment making the UI
        # completely unusable.
        #
        # So this blocks the slider updates while the slider is clicked and
        # unblocks it when its released.
        def sighandler1():
            self.slider_blocked = False
            self.changed_frame_index()

        def setblocked():
            self.slider_blocked = True

        self.slider.sliderPressed.connect(setblocked)
        self.slider.sliderReleased.connect(sighandler1)

        def sighandler2(value):
            if not self.slider_blocked:
                self.changed_frame_index()

        self.slider.valueChanged.connect(sighandler2)
        # }

        # Add display zoom
        self.zoom = DisplayZoom(self)
        self.zoom.setSizePolicy(
                QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed,
                                      QtWidgets.QSizePolicy.Fixed))
        self.layout.addWidget(self.zoom, 1, 1, 1, 1, QtCore.Qt.AlignTop)

        # Add the main display.
        self.display = \
                DisplayMain(self, self.client, self.frame_width,
                            self.frame_height)
        self.layout.addWidget(self.display, 1, 0, 1, 1)

        # {
        # Menu bar for the `Command` section.
        menubar = self.menuBar()
        options = menubar.addMenu('Command')
        menu_save = options.addAction('Save')
        menu_save.setShortcut(QtGui.QKeySequence('Ctrl+S'))
        menu_save.triggered.connect(self.save_image)

        menu_help = options.addAction('Help')

        menu_exit = options.addAction('Exit')
        menu_exit.triggered.connect(QtWidgets.QApplication.quit)
        # }

        # {
        # Menu bar for the `Display` section.
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
        """
        When the frame has been changed this SLOT is called.

        Load the image from the LCD value (since it is canonical), and trigger
        a display change.
        """
        frame_idx = int(self.lcd.value())
        self.reader.set(cv2.CAP_PROP_POS_FRAMES, frame_idx)

        (status, image) = self.reader.read()
        if not status:
            print('Failed to read from video stream.')
        else:
            self.display.load_image(frame_idx, image)

    def update_zoom(self, image):
        """
        This is called when the mouse moves on the main screen.  It relays
        down to the zoom object.
        """
        self.zoom.update_image(image)

    def save_image(self):
        """
        Grab the entire `display` element and save it to an image specified
        by a file dialog box.
        """
        frame_idx = int(self.lcd.value())
        (path, _) = QtWidgets.QFileDialog.getSaveFileName(
                        self,
                        'Save: F:xile',
                        'image_%04d.png' % frame_idx,
                        'Images (*.png *.jpg)')
        if not path:
            return

        region = self.display.grab()
        region.save(path)


def main(video: str):
    """
    A localized `main` function for the client application.
    """
    app = QtWidgets.QApplication(["flysight"])
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
