# ------------------------------------------------------
# ---------------- LIVE CAPTURE MODULE -----------------
# ------------------------------------------------------
import os
import time
import numpy as np

from PyQt5.QtCore import QThread
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QDialog, QFileDialog
from PyQt5.uic import loadUi
from PyQt5 import QtGui

# Local imports #
import src.classes.dsrl_camera_control as dccp
import src.classes.function_generator_control as func_gen
from src.threads.workers_livecapture import *
from src.threads.workers_liveview import *
from src.classes.webcam_camera_control import *
from ui.resources.graphical_resources import *

"""
LiveCapture UI script:
This file covers all UI related functionality to the live Capture module
All buttons and widgets are connected and run either directly scripts found
in src/conversion module for short running scripts or in a thread (in this case
the thread setup can be found in src/threads/workers_livecapture.py)
"""


class MainUI(QDialog):
    def __init__(self):
        QDialog.__init__(self)
        loadUi("ui/main.ui", self)
        self.setWindowTitle("OpenDEP Control")
        self.setWindowIcon(QIcon("icon.png"))

        self.resolutions_SD = [(800, 600), (1024, 768), (1440, 1080), (1920, 1440)]
        self.resolutions_HD = [(854, 480), (1280, 720), (1920, 1080), (2560, 1440)]

        self.threads = []

        self.camera_details_list = []
        self.single_capture_index = 0
        self.stop_thread = False
        self.pause_thread = False

        self.generator = func_gen.FunctionGenerator()
        self.video_camera = VideoCamera(main_ui=self)
        self.camera_live_view()

        self.live_view_populate_with_resolutions()

        #self.camera.change_software_path(self.pyqt5_dynamic_odsc_entry_folder_location_digicam.text())
        self.pyqt5_dynamic_odsc_entry_output_path.setText(os.path.expanduser("~/Desktop"))

        # Capture connections
        self.pyqt5_dynamic_odsc_button_start_capture.clicked.connect(self.multi_capture)
        self.pyqt5_dynamic_odsc_button_stop_capture.clicked.connect(self.stop_capture)
        self.pyqt5_dynamic_odsc_button_pause_capture.clicked.connect(self.pause_capture)
        self.pyqt5_dynamic_odsc_button_resume_capture.clicked.connect(self.resume_capture)
        self.pyqt5_dynamic_odsc_button_check_software.clicked.connect(self.verifySoftware)
        self.pyqt5_dynamic_odsc_button_launch_software.clicked.connect(self.launchSoftware)
        self.pyqt5_dynamic_odsc_button_reload_cameras.clicked.connect(self.get_cameras)
        self.pyqt5_dynamic_odsc_combo_camera.currentIndexChanged.connect(self.select_camera)

        # Live View connections
        #self.worker_live_view.image_update.connect(self.live_view_slot)

        self.pyqt5_dynamic_label_cameraview.mousePressEvent = self.live_view_click_event
        self.pyqt5_dynamic_combo_aspect_ratio.currentIndexChanged.connect(self.live_view_populate_with_resolutions)
        self.pyqt5_dynamic_button_refresh_live_view.clicked.connect(self.refresh_live_view)

        # Generator connections
        self.pyqt5_dynamic_odsc_button_reload_generator.clicked.connect(self.get_generators)
        self.pyqt5_dynamic_odsc_combo_generators.currentIndexChanged.connect(self.select_generator)
        self.pyqt5_dynamic_odsc_button_generator_output_on.clicked.connect(self.generator_output_on)
        self.pyqt5_dynamic_odsc_button_generator_output_off.clicked.connect(self.generator_output_off)
        self.pyqt5_dynamic_odsc_button_generator_download.clicked.connect(self.generator_download_parameters)
        self.pyqt5_dynamic_odsc_button_generator_upload.clicked.connect(self.generator_upload_parameters)

        self.pyqt5_dynamic_button_refresh_live_view.clicked.connect(self.camera_live_view)

        self.pyqt5_dynamic_odsc_button_loadfolder_output.clicked.connect(
            lambda: self.getFolderPath(self.pyqt5_dynamic_odsc_entry_output_path)
        )

        self.pyqt5_dynamic_odsc_button_folder_location_digicam.clicked.connect(
            lambda: self.getFolderPath(self.pyqt5_dynamic_odsc_entry_folder_location_digicam)
        )

        self.pyqt5_dynamic_odsc_entry_folder_location_digicam.textChanged.connect(
            lambda: self.camera.change_software_path(self.pyqt5_dynamic_odsc_entry_folder_location_digicam.text()))

        self.pyqt5_dynamic_odsc_button_single_capture.clicked.connect(
            lambda: self.single_capture('single_capture_' + str(self.single_capture_index))
        )

    def live_view_slot(self, image):
        self.pyqt5_dynamic_label_cameraview.setPixmap(QPixmap.fromImage(image))

    def camera_live_view(self, resolution=resolutions_SD[2]):
        self.threads.append(QThread())
        self.thread_live_view = self.threads[-1]
        self.worker_live_view = LiveViewWorker(main_ui=self,
                                               video_camera=self.video_camera,
                                               resolution=resolution)

        self.worker_live_view.moveToThread(self.thread_live_view)
        self.thread_live_view.started.connect(self.worker_live_view.start_live_view)
        self.worker_live_view.finished.connect(self.thread_live_view.quit)
        self.worker_live_view.finished.connect(self.worker_live_view.deleteLater)
        self.thread_live_view.finished.connect(self.thread_live_view.deleteLater)
        self.thread_live_view.start()

    def refresh_live_view(self):
        camera_index = int(self.pyqt5_dynamic_combo_camera_index.currentIndex())
        if self.pyqt5_dynamic_combo_aspect_ratio.currentIndex() == 0:
            local_resolution = self.resolutions_SD[self.pyqt5_dynamic_combo_resolution.currentIndex()]
        elif self.pyqt5_dynamic_combo_aspect_ratio.currentIndex() == 1:
            local_resolution = self.resolutions_HD[self.pyqt5_dynamic_combo_resolution.currentIndex()]

        self.worker_live_view.stop_live_view()
        time.sleep(0.5)
        index_changed = self.video_camera.change_input(camera_index)
        if not index_changed:
            self.camera_live_view(resolution=resolutions_SD[2])

    def live_view_click_event(self, event):
        x = event.pos().x()
        y = event.pos().y()
        widget_width = self.pyqt5_dynamic_label_cameraview.width()
        widget_height = self.pyqt5_dynamic_label_cameraview.height()

        percentage_x = (x / widget_width) * 100
        percentage_y = (y / widget_height) * 100

        self.worker_live_view.marker_position = (percentage_x, percentage_y)

    def live_view_populate_with_resolutions(self):
        index = self.pyqt5_dynamic_combo_aspect_ratio.currentIndex()
        if index == 0:
            self.pyqt5_dynamic_combo_resolution.clear()
            for i in self.resolutions_SD:
                self.pyqt5_dynamic_combo_resolution.addItem(str(i[0]) + 'x' + str(i[1]))
        elif index == 1:
            self.pyqt5_dynamic_combo_resolution.clear()
            for i in self.resolutions_HD:
                self.pyqt5_dynamic_combo_resolution.addItem(str(i[0]) + 'x' + str(i[1]))



    def getFolderPath(self, entry):
        folder = QFileDialog.getExistingDirectory(self, "Select output folder")
        entry.setText(folder)

    def getFilePath(self, entry):
        file, check = QFileDialog.getOpenFileName(
            None, "Open file", "", "Image files (*.png *.jpg *.jpeg *.tif *.tiff')"
        )
        if check:
            entry.setText(file)

    def generator_output_on(self):
        self.generator.start_output()

    def generator_output_off(self):
        self.generator.stop_output()

    def generator_upload_parameters(self):
        try:
            self.generator.set_frequency(self.pyqt5_dynamic_odsc_spinbox_generator_frequency.value())
            self.generator.set_voltage(self.pyqt5_dynamic_odsc_dspinbox_generator_amplitude.value())
            self.generator.set_sinusoidal()
        except:
            print('No generator connected')

    def generator_download_parameters(self):
        try:
            self.pyqt5_dynamic_odsc_spinbox_generator_frequency.setValue(int(float(self.generator.get_frequency())))
            self.pyqt5_dynamic_odsc_dspinbox_generator_amplitude.setValue(float(self.generator.get_voltage()))
        except:
            print('No generator connected')

    def get_generators(self):
        id_list = self.generator.get_all_instruments()
        self.pyqt5_dynamic_odsc_combo_generators.clear()
        for i in id_list:
            try:
                self.generator.connect_instrument(i)
                self.pyqt5_dynamic_odsc_combo_generators.addItem(i)
            except:
                continue

    def verifySoftware(self):
        print(self.camera.verifyDigiCam())

    def launchSoftware(self):
        if not self.camera.verifyDigiCam():
            self.camera.launchDigiCam()
            self.get_cameras()

    def get_cameras(self):
        if self.camera.verifyDigiCam():
            name_list = []
            self.camera_details_list = self.camera.listCamerasDetails()
            self.pyqt5_dynamic_odsc_combo_camera.clear()
            for i in self.camera_details_list:
                name_list.append(i[1])

            if 'error' not in name_list[0]:
                for i in name_list:
                    self.pyqt5_dynamic_odsc_combo_camera.addItem(i[1:])
            elif 'error' in name_list[0]:
                self.pyqt5_dynamic_odsc_combo_camera.addItem("No available camera")

            self.select_camera()

    def select_camera(self):
        index = self.pyqt5_dynamic_odsc_combo_camera.currentIndex()
        self.camera.setCamera(self.camera_details_list[index][0])

    def select_generator(self):
        index = self.pyqt5_dynamic_odsc_combo_generators.currentIndex()
        id = self.pyqt5_dynamic_odsc_combo_generators.itemText(index)
        print(id)
        try:
            self.generator.connect_instrument(id)
        except:
            print('Not compatible')

    def single_capture(self, file_name):
        if self.camera.verifyDigiCam():
            self.capture(file_name)
            self.single_capture_index = self.single_capture_index + 1

    def capture(self, file_name):
        # Check if image was saved and reload it thorough OpenCV
        path = self.pyqt5_dynamic_odsc_entry_output_path.text()
        file_path = os.path.join(path, file_name)
        self.camera.setTransfer("Save_to_PC_only")
        self.camera.capture(os.path.join(file_path))

        # Check if image was saved and reload it thorough OpenCV
        new_file_path = file_path + '.jpg'
        while not os.path.exists(new_file_path):
            time.sleep(0.1)
        image = cv2.imread(new_file_path)

        # Transform image in black and white
        #image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        time.sleep(0.25)

        # Rotate image
        if self.pyqt5_dynamic_odsc_checkbox_rotate.isChecked():
            image = self.rotate_image(image, self.pyqt5_dynamic_odsc_combo_rotation.currentText())

        # Crop image
        if self.pyqt5_dynamic_odsc_checkbox_crop.isChecked():
            image = self.crop_image(image, self.pyqt5_dynamic_odsc_entry_crop.text())

        # Add image to UI Graph
        self.GraphWidgetLiveCapture.refresh_UI(image)

        # Save image
        cv2.imwrite(new_file_path, image)

    def multi_capture(self):
        if self.camera.verifyDigiCam():
            # Live Timed Multi Capture#
            # Step 1: Set some parameters
            self.stop_thread = False
            self.pause_thread = False
            self.pyqt5_dynamic_odsc_button_start_capture.setDisabled(True)
            self.pyqt5_dynamic_odsc_button_stop_capture.setDisabled(False)
            # Step 2: Create a QThread  and worker object
            self.thread = QThread()
            self.worker = LiveCaptureWorker()

            # Setp 3: Set arguments
            self.worker.live_capture_UI = self

            # Step 4: Move worker to the thread
            self.worker.moveToThread(self.thread)
            # Step 5: Connect signals and slots
            self.thread.started.connect(self.worker.multi_capture_process)
            # Step 6: Start the thread
            self.worker.finished.connect(self.thread.quit)
            self.worker.finished.connect(self.worker.deleteLater)
            self.thread.finished.connect(self.thread.deleteLater)
            self.thread.start()

    def stop_capture(self):
        self.pyqt5_dynamic_odsc_button_start_capture.setDisabled(False)
        self.pyqt5_dynamic_odsc_button_stop_capture.setDisabled(True)
        self.pyqt5_dynamic_odsc_label_current_frequency.setText('0 Hz')
        self.pyqt5_dynamic_odsc_label_next_frequency.setText('0 Hz')
        self.pyqt5_dynamic_odsc_label_current_point.setText('0')
        self.pyqt5_dynamic_odsc_label_countdown.setText('0')
        if self.pyqt5_dynamic_odsc_checkbox_use_generator.isChecked():
            self.generator.stop_output()
        self.pause_thread = False
        self.stop_thread = True

    def pause_capture(self):
        self.pause_thread = True

    def resume_capture(self):
        self.pause_thread = False

    def crop_image(self, image, percentage):
        vertical = (image.shape[0] / 100 * int(
            percentage)) / 2
        horizontal = (image.shape[1] / 100 * int(
            percentage)) / 2
        cropped_image = image[int(vertical):int(image.shape[0] - vertical),
                        int(horizontal):int(image.shape[1] - horizontal)]
        return cropped_image

    def rotate_image(self, image, rotation):
        if str(rotation) == "90":
            rotated_image = cv2.rotate(image, cv2.ROTATE_90_CLOCKWISE)
        elif str(rotation) == "180":
            rotated_image = cv2.rotate(image, cv2.ROTATE_180)
        elif str(rotation) == "270":
            rotated_image = cv2.rotate(image, cv2.ROTATE_90_COUNTERCLOCKWISE)
        else:
            rotated_image = image
        return rotated_image