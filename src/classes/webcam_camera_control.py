import os

import cv2
import matplotlib.pyplot as plt
from PyQt5.QtGui import QPixmap
from PyQt5.uic.properties import QtGui
from matplotlib.animation import FuncAnimation


class WebcamController:
    def __init__(self, main_ui):
        self.cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)

        self.start_rect = None
        self.end_rect = None

        self.start_line = None
        self.end_line = None

        self.main_ui = main_ui

        if not self.cap.isOpened():
            raise IOError("Cannot open webcam")

    def start_live_view(self, resolution=(1280, 720)):
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, resolution[0])
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, resolution[1])

        # Initial position of the rectangle and the line (center of the screen)
        self.start_rect = (int(resolution[0] / 2) - 150, int(resolution[1] / 2) - 100)
        self.end_rect = (int(resolution[0] / 2) + 150, int(resolution[1] / 2) + 100)
        self.start_line = (int(resolution[0] / 2), int(resolution[1] / 2) - 25)
        self.end_line = (int(resolution[0] / 2), int(resolution[1] / 2) + 25)

        while True:
            # Capture the frame
            ret, frame = self.cap.read()

            # Add the rectangle and the line to the frame
            cv2.rectangle(frame, self.start_rect, self.end_rect, (255, 255, 0), 2)
            cv2.line(frame, self.start_line, self.end_line, (255, 255, 0), 2)

            # Crop the image
            percentage = 0
            crop_x = int(resolution[1] * percentage / 100)
            crop_y = int(resolution[0] * percentage / 100)
            cropped = frame[crop_x:resolution[1]-crop_x, crop_y:resolution[0]-crop_y]

            # Show the frame to the user
            cv2.imshow('Input', frame)

            # Wait for the user to click on the screen
            cv2.setMouseCallback('Input', self.click_event)

            c = cv2.waitKey(1)
            if c == 27:
                break

        self.cap.release()
        cv2.destroyAllWindows()

    def single_frame(self):
        # Capture the frame
        ret, frame = self.cap.read()

        # Convert frame to QPixmap
        frame = self.convert_cv_qt(frame)

        # Return frame
        return frame

    def capture_image(self, resolution=(1920, 1080)):
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, resolution[0])
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, resolution[1])

        ret, frame = self.cap.read()
        cv2.imwrite(os.path.join(os.getcwd(), '../../tests/test.jpg'), frame)

    def click_event(self, event, x, y, flags, params):
        if event == cv2.EVENT_LBUTTONDOWN:
            print(x, y)
            x = int(x)
            y = int(y)

            self.start_rect = (x - 150, y - 100)
            self.end_rect = (x + 150, y + 100)

            self.start_line = (x, y - 25)
            self.end_line = (x, y + 25)

    def convert_cv_qt(self, cv_img):
        """Convert from an opencv image to QPixmap"""
        rgb_image = cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb_image.shape
        bytes_per_line = ch * w
        convert_to_qt_format = QtGui.QImage(rgb_image.data, w, h, bytes_per_line, QtGui.QImage.Format_RGB888)
        p = convert_to_qt_format.scaled(self.disply_width, self.display_height, Qt.KeepAspectRatio)
        return QPixmap.fromImage(p)


if __name__ == "__main__":
    webcam = WebcamController()
    webcam.capture_image()
    webcam.start_live_view_2()
