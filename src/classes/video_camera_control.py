# External imports #
import cv2
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.uic.properties import QtGui

# Local imports #
from src.funcs.camera_functions import *

resolutions_SD = [(800, 600), (1024, 768), (1440, 1080), (1920, 1440)]
resolutions_HD = [(854, 480), (1280, 720), (1920, 1080), (2560, 1440)]
resolutions_photo = [(1080, 720), (1200, 800), (1620, 1080), (3840, 2160)]


class VideoCamera:
    def __init__(self, main_ui=None):
        self.cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)

        exposure = self.cap.get(cv2.CAP_PROP_EXPOSURE)
        print(f"Current Exposure: {exposure}")

        self.cap.set(cv2.CAP_PROP_EXPOSURE, -100)
        exposure = self.cap.get(cv2.CAP_PROP_EXPOSURE)
        print(f"Current MIN Exposure: {exposure}")

        self.cap.set(cv2.CAP_PROP_EXPOSURE, 100)
        exposure = self.cap.get(cv2.CAP_PROP_EXPOSURE)
        print(f"Current MAX Exposure: {exposure}")

        # self.cap.set(cv2.CAP_PROP_EXPOSURE, 0.01)
        # self.cap.set(cv2.CAP_PROP_BRIGHTNESS, 0.5)

        self.start_rect = None
        self.end_rect = None

        self.start_line = None
        self.end_line = None

        self.main_ui = main_ui

        if not self.cap.isOpened():
            raise IOError("Cannot open webcam")

    def start_live_view(self, resolution=(resolutions_SD[3])):
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
            cropped = frame[
                crop_x : resolution[1] - crop_x, crop_y : resolution[0] - crop_y
            ]

            # Show the frame to the user
            cv2.imshow("Input", frame)

            # Wait for the user to click on the screen
            cv2.setMouseCallback("Input", self.click_event)

            c = cv2.waitKey(1)
            if c == 27:
                break

        self.cap.release()
        cv2.destroyAllWindows()

    def change_input(self, index):
        self.cap.release()
        self.cap = cv2.VideoCapture(index, cv2.CAP_DSHOW)
        if not self.cap.isOpened():
            return False

    def single_frame_live_view(
        self,
        marker_position,
        zoom=False,
        zoom_percentage=0,
        mark=False,
        marker_percentage=0,
    ):
        # Capture the frame
        ret, frame = self.cap.read()
        qt_img = None

        if ret:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)


            # Crop image
            if zoom:
                frame = crop_image(frame, scale=1 - zoom_percentage / 100)

            # Add Marker to the frame
            if mark:
                if marker_position is None:
                    marker_position = (frame.shape[1] / 2, frame.shape[0] / 2)
                else:
                    marker_position = convert_location_percentage_to_cv(
                        marker_position, frame
                    )
                frame = mark_image(
                    frame, marker_percentage, marker_position, frame.shape
                )

            # Convert to QImage
            flipped_img = cv2.flip(frame, 1)
            #flipped_img = frame
            qt_img = QImage(
                flipped_img.data, frame.shape[1], frame.shape[0], QImage.Format_RGB888
            )
            # qt_img = qt_img.scaled(640, 480, Qt.KeepAspectRatio)

        # Return frame
        return qt_img

    def capture_image(self):
        ret, frame = self.cap.read()
        if ret:
            return frame

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
        convert_to_qt_format = QtGui.QImage(
            rgb_image.data, w, h, bytes_per_line, QtGui.QImage.Format_RGB888
        )
        p = convert_to_qt_format.scaled(
            self.disply_width, self.display_height, Qt.KeepAspectRatio
        )
        return QPixmap.fromImage(p)

    def subtract_background(self, frame, background):
        # Convert the images to grayscale
        gray_background = cv2.cvtColor(background, cv2.COLOR_BGR2GRAY)
        gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # Subtract the background from the current frame
        diff = cv2.absdiff(gray_background, gray_frame)

        # Apply a threshold to the subtracted image
        _, bkg_sub_image = cv2.threshold(diff, 30, 255, cv2.THRESH_BINARY)

        return bkg_sub_image


if __name__ == "__main__":
    video_camera = VideoCamera()
    # video_camera.capture_image()
    video_camera.start_live_view()
