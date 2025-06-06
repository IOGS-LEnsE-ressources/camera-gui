import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), ".")))
import time
import numpy as np
import threading
from PyQt6.QtCore import QThread
from PyQt6.QtWidgets import QFileDialog
from models.images_acquisition import ImageAcquisition

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from oct_lab_app import MainWindow

class ModesController:
    """
    Modes manager.
    """

    def __init__(self, main_app: "MainWindow"):
        """
        Default constructor.
        :param manager: Main manager of the application (ModesManager).
        """
        self.main_app: "MainWindow" = main_app
        # For image processing and displaying / Thread
        self.thread = QThread()
        self.worker = None

        # Signals management
        camera_widget = self.main_app.central_widget.mini_camera.camera_params_widget
        camera_widget.camera_exposure_changed.connect(self.handle_camera_exposure)
        motor_widget = self.main_app.central_widget.motors_options
        motor_widget.motor_changed.connect(self.handle_stepper_move)
        acq_widget = self.main_app.central_widget.acquisition_options
        acq_widget.filename_changed.connect(self.handle_folder)

        # Variables
        self.stepper_z_step = int(self.main_app.stepper_step) * 0.001

        # Start first mode : Live
        self.mode = 'live'
        self.start_live()


    def start_live(self):
        self.worker = ImageAcquisition(self.main_app)
        self.worker.moveToThread(self.thread)

        # Connexions
        self.thread.started.connect(self.worker.run)
        self.worker.images_ready.connect(self.display_live_images)
        self.worker.finished.connect(self.thread.quit)
        self.thread.start()


    def display_live_images(self):
        """
        Display images for live mode in the main_view
        """
        image_view = self.main_app.central_widget
        piezo = self.main_app.piezo
        camera = self.main_app.camera
        if piezo is not None and self.main_app.camera_connected:
            image_view.image1_widget.set_image_from_array(self.main_app.image1, 'Image 1')
            image_view.image2_widget.set_image_from_array(self.main_app.image2, 'Image 2')
            image_view.image_oct_graph.set_image_from_array(self.main_app.image_oct, 'OCT')
        else:
            black = np.random.normal(size=(100, 100))
            image_view.image1_widget.set_image_from_array(black, "No Piezo or camera")
            image_view.image2_widget.set_image_from_array(black, "No Piezo or camera")
            image_view.image_oct_graph.set_image_from_array(black, "No Piezo or camera")

    def handle_camera_exposure(self, event):
        """Action performed when camera exposure time slider changed."""
        source_event = event.split("=")
        source = source_event[0]
        message = source_event[1]
        if source == "int":
            self.main_app.camera.set_exposure(int(message))
        if source == "num":
            self.main_app.number_avgd_images = int(message)


    def handle_stepper_move(self, event):
        """Action performed when Up or Down button is clicked."""
        print(event)
        motors = self.main_app.central_widget.motors_options
        source_event = event.split("=")
        source = source_event[0]
        message = source_event[1]
        if source == "stepz":
            self.stepper_z_step = float(message) * 0.001
        elif source == "up":
            self.main_app.step_motor.set_motor_displacement(1, self.stepper_z_step)
            new_position = np.round(self.main_app.step_motor.get_position(), 3)
            motors.changeZ(new_position)
            # Update widget ?
        elif source == "down":
            self.main_app.step_motor.set_motor_displacement(0, self.stepper_z_step)
            new_position = np.round(self.main_app.step_motor.get_position(), 3)
            motors.changeZ(new_position)
        elif source == "deltaV":
            self.v_step = float(message)


    def handle_folder(self, event):
        """Action performed when Up or Down button is clicked."""
        print(event)
        acquisition = self.main_app.central_widget.acquisition_options
        source_event = event.split("=")
        source = source_event[0]
        message = source_event[1]
        if source == "request":
            folder_request = QFileDialog.getExistingDirectory(None, "Choisir un fichier")
            if folder_request:
                acquisition.directory.setText(folder_request)
                if acquisition.name.text() != '':
                    acquisition.set_start_enabled(True)
        if source == "name":
            if acquisition.directory.text() != '':
                acquisition.set_start_enabled(True)
