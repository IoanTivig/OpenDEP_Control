# ------------------------------------------------------
# ----------------- CONVERSION MODULE ------------------
# ------------------------------------------------------
import cv2
from PyQt5.QtCore import QObject, pyqtSignal

"""
Live Capture workers script:
This file covers all thread functionality to the Live Capture module
This is specific for the long-running functions available in Live Capture module
"""


class LiveViewWorker(QObject):
    finished = pyqtSignal()
    progress = pyqtSignal(int)
    main_ui = None
    resolution = (1440, 1080)

    def live_view(self):
        self.main_ui.webcam.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.resolution[0])
        self.main_ui.webcam.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.resolution[1])

        # Add rectangle to the matplotlib widget

        while True:
            frame = self.main_ui.webcam.single_frame()
            self.main_ui.pyqt5_dynamic_label_cameraview.setPixmap(frame)
        self.finished.emit()


