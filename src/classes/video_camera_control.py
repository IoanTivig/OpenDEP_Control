# External imports #
import cv2
from cv2_rolling_ball import subtract_background_rolling_ball
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.uic.properties import QtGui
import numpy as np


# Local imports #
from src.funcs.camera_functions import *

resolutions_SD = [(800, 600), (1024, 768), (1440, 1080), (1920, 1440)]
resolutions_HD = [(854, 480), (1280, 720), (1920, 1080), (2560, 1440)]
resolutions_photo = [(1080, 720), (1200, 800), (1620, 1080), (3840, 2160)]


class VideoCamera:
    def __init__(self, main_ui=None):
        self.cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
        self.main_ui = main_ui

        # Variables for Marker
        self.start_rect = None
        self.end_rect = None
        self.start_line = None
        self.end_line = None

        # Bkg image for BKG subtraction
        self.bkg_correction_img = cv2.imread("src/saves/bkg_corr.jpg")
        self.dark_correction_img = cv2.imread("src/saves/dark_corr.jpg")

        # Get camera parameters ranges
        self.get_all_parameters_min_max()

        if not self.cap.isOpened():
            raise IOError("Cannot open webcam")

    # Parameters methods for the camera
    def get_all_parameters_min_max(self):
        local_brightness = self.cap.get(cv2.CAP_PROP_BRIGHTNESS)
        local_contrast = self.cap.get(cv2.CAP_PROP_CONTRAST)
        local_saturation = self.cap.get(cv2.CAP_PROP_SATURATION)
        local_exposure = self.cap.get(cv2.CAP_PROP_EXPOSURE)

        self.absolute_brightness_range = self.find_min_max_of_parameter(cv2.CAP_PROP_BRIGHTNESS)
        self.absolute_contrast_range = self.find_min_max_of_parameter(cv2.CAP_PROP_CONTRAST)
        self.absolute_saturation_range = self.find_min_max_of_parameter(cv2.CAP_PROP_SATURATION)
        self.absolute_exposure_range = self.find_min_max_of_parameter(cv2.CAP_PROP_EXPOSURE)

        self.cap.set(cv2.CAP_PROP_BRIGHTNESS, local_brightness)
        self.cap.set(cv2.CAP_PROP_CONTRAST, local_contrast)
        self.cap.set(cv2.CAP_PROP_SATURATION, local_saturation)
        self.cap.set(cv2.CAP_PROP_EXPOSURE, local_exposure)

        local_percentage_brightness = np.interp(local_brightness, self.absolute_brightness_range, [0, 100])
        local_percentage_contrast = np.interp(local_contrast, self.absolute_contrast_range, [0, 100])
        local_percentage_saturation = np.interp(local_saturation, self.absolute_saturation_range, [0, 100])
        local_percentage_exposure = np.interp(local_exposure, self.absolute_exposure_range, [0, 100])

        self.main_ui.pyqt5_dynamic_odsc_slider_brightness_value.setValue(int(local_percentage_brightness))
        self.main_ui.pyqt5_dynamic_odsc_slider_contrast_value.setValue(int(local_percentage_contrast))
        self.main_ui.pyqt5_dynamic_odsc_slider_saturation_value.setValue(int(local_percentage_saturation))
        self.main_ui.pyqt5_dynamic_odsc_slider_exposure_value.setValue(int(local_percentage_exposure))

    def set_parameter_by_percentage(self, parameter, value):
        if parameter == "brightness":
            brightness = np.interp(value, [0, 100], self.absolute_brightness_range)
            print("Brightness: ", brightness)
            self.cap.set(cv2.CAP_PROP_BRIGHTNESS, brightness)
        elif parameter == "contrast":
            contrast = np.interp(value, [0, 100], self.absolute_contrast_range)
            print("Contrast: ", contrast)
            self.cap.set(cv2.CAP_PROP_CONTRAST, contrast)
        elif parameter == "saturation":
            saturation = np.interp(value, [0, 100], self.absolute_saturation_range)
            print("Saturation: ", saturation)
            self.cap.set(cv2.CAP_PROP_SATURATION, saturation)
        elif parameter == "exposure":
            exposure = np.interp(value, [0, 100], self.absolute_exposure_range)
            print("Exposure: ", exposure)
            self.cap.set(cv2.CAP_PROP_EXPOSURE, exposure)

    def find_min_max_of_parameter(self, parameter):
        center_value = 0
        actual_min, actual_max = None, None

        value = center_value
        while True:
            result = self.try_set_property(parameter, value)
            if result == value:
                actual_max = value
                value += 1
            else:
                break

        value = center_value
        while True:
            result = self.try_set_property(parameter, value)
            if result == value:
                actual_min = value
                value -= 1
            else:
                break

        return actual_min, actual_max

    def try_set_property(self, prop_id, value):
        self.cap.set(prop_id, value)
        # Some cameras may need a slight delay here
        return self.cap.get(prop_id)

    def flat_field_correction(self, image, flat_field_image, dark_frame_image):
        # Load the raw, flat-field, and dark-frame images
        image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        flat_field = cv2.cvtColor(flat_field_image, cv2.COLOR_BGR2GRAY)
        dark_frame = cv2.cvtColor(dark_frame_image, cv2.COLOR_BGR2GRAY)

        # Perform flat-field correction
        denominator = np.clip(flat_field - dark_frame, 1e-5, np.max(flat_field - dark_frame))
        corrected_image = (image - dark_frame) / denominator

        # Normalize corrected image to the 0-255 range and convert to uint8
        corrected_image = cv2.normalize(corrected_image, None, 0, 255, cv2.NORM_MINMAX)
        corrected_image = np.clip(corrected_image, 0, 255).astype(np.uint8)

        # Optionally apply smoothing to reduce noise
        corrected_image = cv2.GaussianBlur(corrected_image, (5, 5), 0)

        return corrected_image

    # Camera image acquisition methods
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
        grey_scale=False,
        bkg_subtraction=False
    ):
        # Capture the frame
        ret, frame = self.cap.read()
        qt_img = None

        if ret:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            # Background subtraction
            if bkg_subtraction:
                frame = self.flat_field_correction(
                    image=frame,
                    flat_field_image=self.bkg_correction_img,
                    dark_frame_image=self.dark_correction_img
                )

            # Greyscale or RGB
            if grey_scale:
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

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

            if grey_scale or bkg_subtraction:
                qt_img = QImage(
                    flipped_img.data, frame.shape[1], frame.shape[0], QImage.Format_Grayscale8
                )
            else:
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


if __name__ == "__main__":
    video_camera = VideoCamera()
    # video_camera.capture_image()
    video_camera.start_live_view()
