from fontTools.merge.util import avg_int

from models.motor_control import *
import numpy as np
from lensecam.basler.camera_basler import CameraBasler
import matplotlib.pyplot as plt
import sys
import time

from views import motors_display

from PyQt6.QtWidgets import (
    QWidget, QGridLayout, QVBoxLayout,
    QLabel, QComboBox, QPushButton, QFrame,
    QSizePolicy, QSpacerItem, QMainWindow, QHBoxLayout, QApplication, QSlider, QLineEdit, QFileDialog)
from PyQt6.QtCore import Qt, pyqtSignal

class cameraControl(QWidget):
    def __init__(self, parent = None):
        super().__init__()
        self.parent = parent

        self.cam = CameraBasler()
        #if __name__ == "__main__":
        cam_connected = self.cam.find_first_camera()
        print(cam_connected)

        self.exposure = 1500
        self.piezo = Piezo()
        self.motor = Motor()

        self.cam.set_exposure(self.exposure)

    def capture_image(self):
        image = self.cam.get_image()
        return image

    def avg_images(self, N):
        images = self.cam.get_images(N)
        return np.mean(images, axis = 0)

    def acquisition_sequence(self, step_size, V0, N):
        images_1 = self.avg_images(N)
        self.piezo.set_voltage_piezo(step_size + V0)
        images_2 = self.avg_images(N)
        self.piezo.set_zero_piezo(V0)
        image1 = np.mean(images_1, axis=0)
        image2 = np.mean(images_2, axis=0)

        image = np.sqrt((image1 - image2)**2)
        return image1, image2, image

    def live_sequence(self, step_size = 0.6, V0 = 0):
        self.piezo.set_voltage_piezo(V0)
        image1 = self.capture_image()
        self.piezo.set_voltage_piezo(step_size + V0)
        image2 = self.capture_image()
        image = np.sqrt((image1 - image2) ** 2)
        return image1, image2, image

    def acquisition_update(self,consigne, tolerance = 0.1, timeout = 300):
        self.motor.move_motor(consigne)
        a = 0
        while(self.motor.get_position() - consigne > tolerance and a < timeout):
            a+=1
            time.sleep(0.01)

    def store_acquisition_sequence(self, z_step_size, z0, v_step_size, V0, N, index, num, consigne, tolerance = 0.1, timeout = 300):
        """
        This function performs the entire measurement sequence of
        the OCT protocol, and returns a list containing the resulting
        images.
        :param z_step_size: motor step size
        :param Z: motor position
        :param v_step_size: piezo step size
        :param V0: piezo voltage
        :param N: number of averaged images
        :param num: number of steps
        :rtype: list
        """
        self.acquisition_update(z0 - num / 2 * z_step_size + index * z_step_size, tolerance, timeout)
        image1, image2, image = self.acquisition_sequence(v_step_size, V0, N)
        return image1, image2, image

    def update_exposure(self, exposure):
        self.exposure = exposure
        self.cam.set_exposure(self.exposure)

    def disconnect(self):
        #self.cam.disconnect()
        self.motor.disconnect_motor()
        self.piezo.disconnect_piezo()

    def find_camera(self):
        self.cam.find_first_camera()

    def find_motors(self):
        self.piezo.find_piezo()
        self.motor.find_motor()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    control = cameraControl()
    control.motor.move_motor(3.125)
    control.update_exposure(300)
    fig, axs = plt.subplots(4, 4, figsize=(8, 8))
    control.piezo.set_voltage_piezo(12)
    image1 = control.cam.get_images(5)
    for i, ax in enumerate(axs.flat):
        control.piezo.set_voltage_piezo(12 + 0.1*i)
        image2 = control.cam.get_images(5)

        image = (np.mean(image1, axis=0) - np.mean(image2, axis=0)) ** 2

        #image = np.mean(image2, axis = 0)
        max_image = image.max()

        if max_image > 0:
            image = abs(image / max_image)

        plt.title(f"V = {2*i}")
        ax.imshow(image, cmap= "gray")
    control.disconnect()
    plt.show()