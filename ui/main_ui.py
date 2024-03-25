# ------------------------------------------------------
# ------------------ OpenDEP Control -------------------
# ------------------------------------------------------

from PyQt5.QtCore import QThread
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QDialog, QFileDialog
from PyQt5.uic import loadUi
import json

# Local imports #
import src.classes.function_generator_control as func_gen
from src.threads.workers_livecapture import *
from src.threads.workers_liveview import *
from src.classes.video_camera_control import *
from src.classes.opendep_firmware_control import *
from ui.resources.graphical_resources import *  # don't remove this line

'''
OpenDEP Control
    Copyright (C) 2023  Ioan Cristian Tivig

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <https://www.gnu.org/licenses/>.

    You can contact the developer/owner of OpenDEP at "ioan.tivig@gmail.com".
'''


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

        self.live_view_populate_with_cameras()
        self.pyqt5_dynamic_combo_aspect_ratio.setCurrentIndex(1)
        self.live_view_populate_with_resolutions()
        self.pyqt5_dynamic_combo_resolution.setCurrentIndex(2)
        self.resolution = self.resolutions_HD[2]
        self.load_instrument_connection_settings()

        self.firmware = OpenDepFirmware()
        self.generator = func_gen.FunctionGenerator()
        self.video_camera = VideoCamera(main_ui=self)
        self.dsrl_camera = DSRLCamera()
        self.camera_live_view()

        self.dsrl_camera.change_software_path(
            self.pyqt5_dynamic_odsc_entry_folder_location_digicam.text()
        )
        self.pyqt5_dynamic_odsc_entry_output_path.setText(
            os.path.expanduser("~/Desktop")
        )

        # Capture connections
        self.pyqt5_dynamic_odsc_button_start_capture.clicked.connect(self.multi_capture)
        self.pyqt5_dynamic_odsc_button_stop_capture.clicked.connect(self.stop_capture)
        self.pyqt5_dynamic_odsc_button_pause_capture.clicked.connect(self.pause_capture)
        self.pyqt5_dynamic_odsc_button_resume_capture.clicked.connect(
            self.resume_capture
        )
        self.pyqt5_dynamic_odsc_button_check_software.clicked.connect(
            self.verify_software
        )
        self.pyqt5_dynamic_odsc_button_launch_software.clicked.connect(
            self.launch_software
        )
        self.pyqt5_dynamic_odsc_button_reload_cameras.clicked.connect(self.get_cameras)
        self.pyqt5_dynamic_odsc_combo_camera.currentIndexChanged.connect(
            self.select_camera
        )

        # Live View connections

        self.pyqt5_dynamic_label_cameraview.mousePressEvent = self.live_view_click_event
        self.pyqt5_dynamic_combo_aspect_ratio.currentIndexChanged.connect(
            self.live_view_populate_with_resolutions
        )
        self.pyqt5_dynamic_button_refresh_live_view.clicked.connect(
            self.refresh_live_view
        )
        self.pyqt5_dynamic_button_connect_live_view.clicked.connect(
            self.refresh_live_view
        )

        # Generator connections
        self.pyqt5_dynamic_odsc_button_reload_generator.clicked.connect(
            self.get_generators
        )
        self.pyqt5_dynamic_odsc_combo_generators.currentIndexChanged.connect(
            self.select_generator
        )
        self.pyqt5_dynamic_odsc_button_generator_output_on.clicked.connect(
            self.generator_output_on
        )
        self.pyqt5_dynamic_odsc_button_generator_output_off.clicked.connect(
            self.generator_output_off
        )
        self.pyqt5_dynamic_odsc_button_generator_download.clicked.connect(
            self.generator_download_parameters
        )
        self.pyqt5_dynamic_odsc_button_generator_upload.clicked.connect(
            self.generator_upload_parameters
        )

        self.pyqt5_dynamic_button_refresh_live_view.clicked.connect(
            self.camera_live_view
        )

        self.pyqt5_dynamic_odsc_button_loadfolder_output.clicked.connect(
            lambda: self.get_folder_path(self.pyqt5_dynamic_odsc_entry_output_path)
        )

        self.pyqt5_dynamic_odsc_button_folder_location_digicam.clicked.connect(
            lambda: self.get_folder_path(
                self.pyqt5_dynamic_odsc_entry_folder_location_digicam
            )
        )

        self.pyqt5_dynamic_odsc_entry_folder_location_digicam.textChanged.connect(
            lambda: self.dsrl_camera.change_software_path(
                self.pyqt5_dynamic_odsc_entry_folder_location_digicam.text()
            )
        )

        self.pyqt5_dynamic_odsc_button_single_capture.clicked.connect(
            lambda: self.single_capture(
                "single_capture_" + str(self.single_capture_index)
            )
        )
        # Illumination connections
        self.pyqt5_dynamic_odsc_button_illumination_on.clicked.connect(self.firmware.ledON)
        self.pyqt5_dynamic_odsc_button_illumination_off.clicked.connect(self.firmware.ledOFF)
        self.pyqt5_dynamic_odsc_slider_illumination_value.sliderReleased.connect(
            lambda: self.firmware.ledDIM(
                self.pyqt5_dynamic_odsc_slider_illumination_value.value()
            )
        )

        # Camera parameters connections
        self.pyqt5_dynamic_odsc_slider_exposure_value.sliderReleased.connect(
            lambda: self.video_camera.set_parameter_by_percentage(
                "exposure",
                self.pyqt5_dynamic_odsc_slider_exposure_value.value()
            )
        )
        self.pyqt5_dynamic_odsc_slider_brightness_value.sliderReleased.connect(
            lambda: self.video_camera.set_parameter_by_percentage(
                "brightness",
                self.pyqt5_dynamic_odsc_slider_brightness_value.value()
            )
        )
        self.pyqt5_dynamic_odsc_slider_contrast_value.sliderReleased.connect(
            lambda: self.video_camera.set_parameter_by_percentage(
                "contrast",
                self.pyqt5_dynamic_odsc_slider_contrast_value.value()
            )
        )
        self.pyqt5_dynamic_odsc_slider_saturation_value.sliderReleased.connect(
            lambda: self.video_camera.set_parameter_by_percentage(
                "saturation",
                self.pyqt5_dynamic_odsc_slider_saturation_value.value()
            )
        )

        self.pyqt5_dynamic_button_capture_bkgcorrection_image.clicked.connect(self.capture_bkg_image)

        # Console connections
        self.pyqt5_dynamic_odsc_button_console_input.clicked.connect(self.console_input)
        self.pyqt5_dynamic_odsc_button_reload_console_coms.clicked.connect(self.refresh_console_coms)
        self.pyqt5_dynamic_odsc_button_console_connect.clicked.connect(self.connect_instrument)

        # Instrument connections
        self.pyqt5_dynamic_odsc_button_verify_instrument_status.clicked.connect(self.verify_connection)

    # General methods
    def get_folder_path(self, entry):
        folder = QFileDialog.getExistingDirectory(self, "Select output folder")
        entry.setText(folder)

    def get_file_path(self, entry):
        file, check = QFileDialog.getOpenFileName(
            None, "Open file", "", "Image files (*.png *.jpg *.jpeg *.tif *.tiff')"
        )
        if check:
            entry.setText(file)

    def save_instrument_connection_settings(self):
        # Save the current settings for the instruments (camera and OpenDEP connection) into a json file
        settings = {}

        # Add the settings of the camera and OpenDEP connection to the dictionary
        settings['camera'] = {
            'camera_index': self.pyqt5_dynamic_combo_camera_index.currentIndex(),
        }
        settings['opendep'] = {
            'port': self.pyqt5_dynamic_odsc_combo_console_coms.currentText().split(" ")[0],
            'baudrate': self.pyqt5_dynamic_odsc_combo_console_boadrates.currentText(),
        }

        # Use the json.dump() function to write the dictionary to a JSON file
        with open('src/saves/settings.json', 'w') as f:
            json.dump(settings, f, indent=4)

    def load_instrument_connection_settings(self):
        # Load the settings for the instruments (camera and OpenDEP connection) from a json file
        try:
            with open('src/saves/settings.json', 'r') as f:
                settings = json.load(f)

            # Set the camera index
            self.pyqt5_dynamic_combo_camera_index.setCurrentIndex(settings['camera']['camera_index'])

            # Set the OpenDEP connection settings
            self.pyqt5_dynamic_odsc_combo_console_coms.setCurrentText(settings['opendep']['port'])
            self.pyqt5_dynamic_odsc_combo_console_boadrates.setCurrentText(settings['opendep']['baudrate'])
            self.firmware.connect_instrument()
        except:
            print("No settings file found")

    def closeEvent(self, event):
        self.save_instrument_connection_settings()
        print("Settings saved")
        event.accept()

    # Console methods
    def console_input(self):
        input_text = self.pyqt5_dynamic_odsc_entry_console_input.text()
        self.pyqt5_dynamic_odsc_plaintext_console.appendPlainText("COMMAND: " + input_text)
        response_text = self.firmware.send_command(input_text)
        self.pyqt5_dynamic_odsc_plaintext_console.appendPlainText("RESPONSE: " + response_text)
        self.pyqt5_dynamic_odsc_entry_console_input.clear()

    def connect_instrument(self):
        port = self.pyqt5_dynamic_odsc_combo_console_coms.currentText().split(" ")[0]
        baudrate = int(self.pyqt5_dynamic_odsc_combo_console_boadrates.currentText())
        self.firmware.set_baudrate(baudrate)
        self.firmware.set_port(port)
        try:
            self.firmware.connect_instrument()
            time.sleep(2.5)
            response_text = self.firmware.send_command("OPENDEP ID")
            if "OPENDEP_INSTRUMENT" in response_text:
                self.pyqt5_dynamic_odsc_plaintext_console.appendPlainText("OPENDEP INSTRUMENT CONNECTED")
            else:
                self.pyqt5_dynamic_odsc_plaintext_console.appendPlainText(
                    "INSTRUMENT CONNECTED, BUT NOT OPENDEP"
                )
        except:
            self.pyqt5_dynamic_odsc_plaintext_console.appendPlainText(
                "NO INSTRUMENT FOUND / NOT COMPATIBLE / WRONG BAUDRATE / WRONG PORT")

    def verify_connection(self):
        if self.firmware.verify_connection():
            print("Connected")
            self.pyqt5_dynamic_odsc_label_opendep_status.setEnabled(True)
        else:
            print("Not Connected")
            self.pyqt5_dynamic_odsc_label_opendep_status.setEnabled(False)

        #print(self.video_camera.get_camera_exposure())

    def refresh_console_coms(self):
        self.firmware.get_all_ports()
        self.pyqt5_dynamic_odsc_combo_console_coms.clear()
        for i in self.firmware.port_list:
            self.pyqt5_dynamic_odsc_combo_console_coms.addItem(i)

    # Live Capture methods
    def camera_live_view(self):
        self.threads.append(QThread())
        self.thread_live_view = self.threads[-1]
        self.worker_live_view = LiveViewWorker(
            main_ui=self, video_camera=self.video_camera, resolution=self.resolution
        )
        self.worker_live_view.moveToThread(self.thread_live_view)
        self.thread_live_view.started.connect(self.worker_live_view.start_live_view)
        self.worker_live_view.finished.connect(self.thread_live_view.quit)
        self.worker_live_view.finished.connect(self.worker_live_view.deleteLater)
        self.thread_live_view.finished.connect(self.thread_live_view.deleteLater)
        self.thread_live_view.start()

    def refresh_live_view(self):
        camera_index = int(self.pyqt5_dynamic_combo_camera_index.currentIndex())
        local_resolution = get_camera_resolution(self)
        self.worker_live_view.stop_live_view()
        index_changed = self.video_camera.change_input(camera_index)
        if not index_changed:
            self.resolution = local_resolution
            self.camera_live_view()

    def live_view_click_event(self, event):
        x = event.pos().x()
        y = event.pos().y()
        widget_width = self.pyqt5_dynamic_label_cameraview.width()
        widget_height = self.pyqt5_dynamic_label_cameraview.height()

        percentage_x = (x / widget_width) * 100
        percentage_y = (y / widget_height) * 100

        self.worker_live_view.marker_position = (percentage_x, percentage_y)

    def live_view_populate_with_cameras(self):
        camera_list = get_camera_list()
        self.pyqt5_dynamic_combo_camera_index.clear()
        for i in camera_list:
            self.pyqt5_dynamic_combo_camera_index.addItem("Camera " + str(i + 1))

    def live_view_populate_with_resolutions(self):
        index = self.pyqt5_dynamic_combo_aspect_ratio.currentIndex()
        if index == 0:
            self.pyqt5_dynamic_combo_resolution.clear()
            for i in self.resolutions_SD:
                self.pyqt5_dynamic_combo_resolution.addItem(str(i[0]) + "x" + str(i[1]))
        elif index == 1:
            self.pyqt5_dynamic_combo_resolution.clear()
            for i in self.resolutions_HD:
                self.pyqt5_dynamic_combo_resolution.addItem(str(i[0]) + "x" + str(i[1]))

    # Generator methods
    def generator_output_on(self):
        self.generator.start_output()

    def generator_output_off(self):
        self.generator.stop_output()

    def generator_upload_parameters(self):
        try:
            self.generator.set_frequency(
                self.pyqt5_dynamic_odsc_spinbox_generator_frequency.value()
            )
            self.generator.set_voltage(
                self.pyqt5_dynamic_odsc_dspinbox_generator_amplitude.value()
            )
            self.generator.set_sinusoidal()
        except:
            print("No generator connected")

    def generator_download_parameters(self):
        try:
            self.pyqt5_dynamic_odsc_spinbox_generator_frequency.setValue(
                int(float(self.generator.get_frequency()))
            )
            self.pyqt5_dynamic_odsc_dspinbox_generator_amplitude.setValue(
                float(self.generator.get_voltage())
            )
        except:
            print("No generator connected")

    def get_generators(self):
        id_list = self.generator.get_all_instruments()
        self.pyqt5_dynamic_odsc_combo_generators.clear()
        for i in id_list:
            try:
                self.generator.connect_instrument(i)
                self.pyqt5_dynamic_odsc_combo_generators.addItem(i)
            except:
                continue

    # Capture methods
    def verify_software(self):
        print(self.dsrl_camera.verifyDigiCam())

    def launch_software(self):
        if not self.dsrl_camera.verifyDigiCam():
            self.dsrl_camera.launchDigiCam()
            self.get_cameras()

    def get_cameras(self):
        if self.dsrl_camera.verifyDigiCam():
            name_list = []
            self.camera_details_list = self.dsrl_camera.listCamerasDetails()
            self.pyqt5_dynamic_odsc_combo_camera.clear()
            for i in self.camera_details_list:
                name_list.append(i[1])

            if "error" not in name_list[0]:
                for i in name_list:
                    self.pyqt5_dynamic_odsc_combo_camera.addItem(i[1:])
            elif "error" in name_list[0]:
                self.pyqt5_dynamic_odsc_combo_camera.addItem("No available camera")

            self.select_camera()

    def select_camera(self):
        index = self.pyqt5_dynamic_odsc_combo_camera.currentIndex()
        self.dsrl_camera.setCamera(self.camera_details_list[index][0])

    def select_generator(self):
        index = self.pyqt5_dynamic_odsc_combo_generators.currentIndex()
        id = self.pyqt5_dynamic_odsc_combo_generators.itemText(index)
        print(id)
        try:
            self.generator.connect_instrument(id)
        except:
            print("Not compatible")

    def single_capture(self, file_name):
        if self.dsrl_camera.verifyDigiCam():
            self.capture(file_name)
            self.single_capture_index = self.single_capture_index + 1

    def capture(self, file_name):
        if self.pyqt5_dynamic_radio_use_video_camera.isChecked():
            self.capture_video_camera(file_name)
        elif self.pyqt5_dynamic_radio_use_dsrl_camera.isChecked():
            self.capture_dsrl_camera(file_name)

    def capture_bkg_image(self):
        image = self.video_camera.capture_image()
        self.video_camera.bkg_correction_img = image
        cv2.imwrite("src/saves/bkg_corr.jpg", image)
        response = self.firmware.send_command("OPENDEP LIGHT OFF")
        print(response)

        time.sleep(2)
        dark_image = self.video_camera.capture_image()
        self.video_camera.dark_correction_img = dark_image
        cv2.imwrite("src/saves/dark_corr.jpg", dark_image)
        response = self.firmware.send_command("OPENDEP LIGHT ON")
        print(response)


    def capture_dsrl_camera(self, file_name):
        # Check if image was saved and reload it thorough OpenCV
        path = self.pyqt5_dynamic_odsc_entry_output_path.text()
        file_path = os.path.join(path, file_name)
        self.dsrl_camera.setTransfer("Save_to_PC_only")
        self.dsrl_camera.capture(os.path.join(file_path))

        """
        # Check if image was saved and reload it thorough OpenCV
        new_file_path = file_path + ".jpg"
        while not os.path.exists(new_file_path):
            time.sleep(0.1)
        image = cv2.imread(new_file_path)

        time.sleep(0.25)

        # Save image
        cv2.imwrite(new_file_path, image)
        """

    def capture_video_camera(self, file_name):
        path = self.pyqt5_dynamic_odsc_entry_output_path.text()
        file_path = os.path.join(path, file_name)
        file_path = file_path + ".jpg"
        image = self.video_camera.capture_image()
        cv2.imwrite(file_path, image)
        print("hello")

    def multi_capture(self):
        if (
            self.pyqt5_dynamic_radio_use_video_camera.isChecked()
            or self.dsrl_camera.verifyDigiCam()
        ):
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
        self.pyqt5_dynamic_odsc_label_current_frequency.setText("0 Hz")
        self.pyqt5_dynamic_odsc_label_next_frequency.setText("0 Hz")
        self.pyqt5_dynamic_odsc_label_current_point.setText("0")
        self.pyqt5_dynamic_odsc_label_countdown.setText("0")
        if self.pyqt5_dynamic_odsc_checkbox_use_generator.isChecked():
            self.generator.stop_output()
        self.pause_thread = False
        self.stop_thread = True

    def pause_capture(self):
        self.pause_thread = True

    def resume_capture(self):
        self.pause_thread = False
