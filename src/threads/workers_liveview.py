# External imports #
import time
import cv2

# Local imports #
from PyQt5.QtCore import QObject, pyqtSignal
from src.classes.video_camera_control import *

"""
Live View worker script:
This file covers all thread functionality to the Live View
This is specific for the long-running functions available in Live Capture module
"""


class LiveViewWorker(QObject):
    finished = pyqtSignal()
    thread_active = bool

    def __init__(self, main_ui, video_camera, resolution):
        super().__init__()
        self.main_ui = main_ui
        self.video_camera = video_camera
        self.resolution = resolution
        self.marker_position = None

    def start_live_view(self):
        print(self.resolution)
        resolution_width = self.resolution[0]
        resolution_height = self.resolution[1]
        self.video_camera.cap.set(cv2.CAP_PROP_FRAME_WIDTH, resolution_width)
        self.video_camera.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, resolution_height)

        self.thread_active = True

        while True:
            if self.thread_active:
                crop = self.main_ui.pyqt5_dynamic_checkbox_zoom.isChecked()
                zoom_percentage = self.main_ui.pyqt5_dynamic_spinbox_zoom.value()

                mark = self.main_ui.pyqt5_dynamic_checkbox_marker.isChecked()
                marker_percentage = (
                    self.main_ui.pyqt5_dynamic_spinbox_marker_size_width.value(),
                    self.main_ui.pyqt5_dynamic_spinbox_marker_size_height.value(),
                )

                frame = self.video_camera.single_frame_live_view(
                    marker_position=self.marker_position,
                    zoom=crop,
                    zoom_percentage=zoom_percentage,
                    mark=mark,
                    marker_percentage=marker_percentage,
                    grey_scale=self.main_ui.pyqt5_dynamic_odsc_checkbox_greyscale.isChecked(),
                    bkg_subtraction=self.main_ui.pyqt5_dynamic_odsc_checkbox_bkgcorrection.isChecked()
                )

                # get size of the qt label
                size = self.main_ui.pyqt5_dynamic_label_cameraview.size()
                frame = frame.scaled(size.width(), size.height(), Qt.KeepAspectRatio)
                self.main_ui.pyqt5_dynamic_label_cameraview.setPixmap(
                    QPixmap.fromImage(frame)
                )

            else:
                print("Finished")
                self.finished.emit()
                break

            time.sleep(0.05)

    def stop_live_view(self):
        self.thread_active = False
