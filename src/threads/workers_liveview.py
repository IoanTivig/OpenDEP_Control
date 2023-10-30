# ------------------------------------------------------
# ----------------- CONVERSION MODULE ------------------
# ------------------------------------------------------
import time

import cv2
from PyQt5.QtCore import QObject, pyqtSignal
from src.classes.webcam_camera_control import *

"""
Live Capture workers script:
This file covers all thread functionality to the Live Capture module
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
                marker_percentage = self.main_ui.pyqt5_dynamic_spinbox_marker_size.value()

                frame = self.video_camera.single_frame_liveview(
                                                                      marker_position=self.marker_position,
                                                                      zoom=crop,
                                                                      zoom_percentage=zoom_percentage,
                                                                      mark=mark,
                                                                      marker_percentage=marker_percentage,
                                                                      )

                self.main_ui.pyqt5_dynamic_label_cameraview.setPixmap(QPixmap.fromImage(frame))

            else:
                print('Finished')
                self.finished.emit()
                break

            time.sleep(0.05)

    def stop_live_view(self):
        self.thread_active = False



