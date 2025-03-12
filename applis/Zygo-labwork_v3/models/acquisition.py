# -*- coding: utf-8 -*-
"""*acquisition.py* file.

./models/acquisition.py contains Acquisition_Model class to manage the acquisition of a set of images.

Images are intensity measurements of interferences. All images have the same size.
A set of 5 images is necessary to be demodulated by the Hariharan phase
demodulation algorithm

Data are stored in MAT file, containing "Images" (set of 5 arrays in 2 dimensions)
and "Masks" objects (array(s) in 2 dimensions - same size as images).

.. note:: LEnsE - Institut d'Optique - version 1.0

.. moduleauthor:: Julien VILLEMEJANE (PRAG LEnsE) <julien.villemejane@institutoptique.fr>
Creation : march/2025
"""
import sys, os
import threading, time
import numpy as np
from lensecam.basler.camera_basler import *
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from utils import *
from models import *
from drivers import *

number_of_images = 5


class AcquisitionModel:
    """Class containing images data and parameters.
    Images are stored in sets of N images.
    """
    def __init__(self, set_size: int=5, acq_nb: int=1):
        """Default constructor.
        :param set_size: Size of a set of images.
        """
        # Hardware
        self.camera = CameraBasler()
        self.camera_connected = False
        self.piezo = NIDaqPiezo()
        self.voltages_list = []             # Voltages for piezo movement
        # Data
        self.set_size = set_size            # Number of images of each set
        self.current_images_set = []
        self.images_sets = ImagesModel(set_size)
        self.acquisition_number = acq_nb    # Total number of acquisition to do
        self.acquisition_counter = 0        # To count number of images sets during thread
        self.images_counter = 0             # To count acquired images in a set during thread

        # Init hardware
        self.camera_connected = self.camera.find_first_camera()
        # self.piezo -> set channel and voltages

    def is_possible(self):
        """
        Check if a camera (IDS) and a piezo controller (NIDaqMx) is connected.
        :return: True if acquisition is possible.
        """
        if self.piezo.is_piezo_here() is False:
            return False
        if self.camera_connected is False:
            print('models/acquisition.py - No camera connected')
            return False
        if not self.voltages_list: # Empty list
            print('models/acquisition.py - No voltages set for piezo')
            return False
        return True

    def start(self) -> bool:
        """
        Start the acquisition.
        :return: Return False if acquisition is not possible.
        """
        '''
        if self.is_possible() is False:
            return False
        self.acquisition_counter = 0
        '''
        thread = threading.Thread(target=self.thread_acquisition)
        time.sleep(0.01)
        thread.start()

    def _one_acquisition(self) -> np.ndarray:
        """
        Process one acquisition, depending on index of the sample and index of the set.
        :return: Captured image as an array in 2D.
        """
        # Move piezo
        self.piezo.write_dac(self.voltages_list[self.images_counter])
        # Wait end of movement
        time.sleep(0.5)
        # Acquire image
        image = self.camera.get_images(1)
        time.sleep(0.1)
        return image

    def thread_acquisition(self):
        """
        Thread for acquisition of data.
        """
        if self.acquisition_counter < self.acquisition_number:
            if self.images_counter < self.set_size:
                self.current_images_set.append(self._one_acquisition())
                self.images_counter += 1
            else:
                self.images_sets.add_set_images(self.current_images_set)
                self.current_images_set = []
                self.images_counter = 0
                self.acquisition_counter += 1
            thread = threading.Thread(target=self.thread_acquisition)
            time.sleep(0.01)
            thread.start()

    def set_voltages(self, voltage_list):
        """
        Set the voltages list (for the piezo controller)
        :param voltage_list: List of float - in Volt.
        """
        self.voltages_list = voltage_list

    def reset_all_images(self):
        """Reset all images."""
        self.images_set.reset_all_images()

    def get_number_of_acquisition(self) -> int:
        """Return the number of stored sets of images.
        :return: Number of stored sets of images.
        """
        return self.acquisition_counter

    def get_acquisition_index(self) -> int:
        """
        Return the index of the current sample index.
        :return: Index of the current sample index.
        """
        return self.images_counter

    def get_progress(self):
        """
        Return the progression of the current acquisition. In %.
        """
        maximum = self.acquisition_number * self.set_size
        current = (self.images_counter + 1) + (self.acquisition_counter * self.set_size)
        return round(current * 100 / maximum, 0)

    def get_images_set(self, index: int) -> list[np.ndarray]:
        """Return a set of N images.
        :param index: Index of the set to return.
        :return: List of images from the specified set.
        """
        if index <= self.acquisition_counter:
            return self.images_set.get_images_set(index)
        return None


if __name__ == '__main__':
    from matplotlib import pyplot as plt

    nb_of_images_per_set = 5
    acquisition = AcquisitionModel(nb_of_images_per_set, acq_nb=3)
    volt_list = [0.80,1.62,2.43,3.24,4.05]
    acquisition.set_voltages(volt_list)
    if acquisition.is_possible():
        print('ACQ is possible')
    acquisition.start()

    while acquisition.get_progress() < 100:
        print(f'{acquisition.get_progress()} %')
        time.sleep(0.2)



    image_set = ImagesModel(nb_of_images_per_set)


    ## Test class
    print(f'Number of sets = {image_set.get_number_of_sets()}')
    if image_set.get_number_of_sets() >= 1:
        image_1_1 = image_set.get_images_set(1)
        if isinstance(image_1_1, list):
            plt.figure()
            plt.imshow(image_1_1[0], cmap='gray')
            plt.show()


