# -*- coding: utf-8 -*-
"""*phase.py* file.

./models/phase.py contains Phase_Model class to manage the phase from Zygo application.

Phase is demodulated by the Hariharan phase demodulation algorithm from a set of 5 images.

.. note:: LEnsE - Institut d'Optique - version 1.0

.. moduleauthor:: Julien VILLEMEJANE (PRAG LEnsE) <julien.villemejane@institutoptique.fr>
Creation : march/2025
"""
import cv2
import numpy as np
from lensepy.images.conversion import crop_images
from models import *
from skimage.restoration import unwrap_phase


class PhaseModel:
    """Class containing phase data and parameters.
    """
    def __init__(self):
        """

        """
        self.images_list = []
        self.mask = None
        self.cropped_phase = None
        self.wrapped_phase = None
        self.unwrapped_phase = None

    def set_images(self, images_set: list[np.ndarray]) -> bool:
        """
        Add a set of 5 images (as list of arrays).
        :param images_set: List of array containing images data
        (for Hariharan phase demodulation algorithm)
        :return: True if images are added.
        """
        if isinstance(images_set, list):
            if len(images_set) == 5:
                self.images_list = images_set
                return True
        self.images_list = []
        return False

    def set_mask(self, mask: np.ndarray) -> bool:
        """
        Add a mask to process data.
        :param mask: 2D array containing mask for image processing.
        :return: True if mask is added.
        """
        # Test size of the mask, compared to image size
        if mask.shape[0] == self.images_list[0].shape[0] and mask.shape[1] == self.images_list[0].shape[1]:
            self.mask = mask
            return True
        self.mask = None
        return False

    def process_wrapped_phase(self):
        """
        Process Hariharan demodulation altorithm on data (set of 5 images).
        :return: True if Hariharan algorithm is processed.
        """
        print(f'L = {len(self.images_list)}')
        if len(self.images_list) != 0 and self.mask is not None:
            self.cropped_phase = []
            for image in self.images_list:
                self.cropped_phase.append(cv2.blur(image, (15, 15)))
            self.wrapped_phase = hariharan_algorithm(self.cropped_phase, self.mask)
            return True
        else:
            self.wrapped_phase = None
            return False

    def get_wrapped_phase(self) -> np.ndarray:
        """
        Return the wrapped phase if calculated
        :return: Wrapped phase as an array in 2D.
        """
        return self.wrapped_phase

    def process_unwrapped_phase(self):
        """
        Process unwrapping algorithm from Skimage-restauration.
        :return: True if Hariharan algorithm is processed. None if not processed.
        """
        if self.wrapped_phase is not None:
            self.unwrapped_phase = unwrap_phase(self.wrapped_phase) / (2 * np.pi)
            return True
        else:
            self.unwrapped_phase = None
            return False

    def get_unwrapped_phase(self) -> np.ndarray:
        """
        Return the unwrapped phase if calculated
        :return: Unwrapped phase as an array in 2D. None if not processed.
        """
        return self.unwrapped_phase


if __name__ == '__main__':
    import sys, os
    from matplotlib import pyplot as plt
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
    from models import *
    from utils import *

    phase_test = PhaseModel()

    nb_of_images_per_set = 5
    file_path = '../_data/test3.mat'
    image_set = ImagesModel(nb_of_images_per_set)
    image_set.load_images_set_from_file(file_path)
    masks_set = MasksModel()
    masks_set.load_mask_from_file(file_path)

    ## Test class
    print(f'Number of sets = {image_set.get_number_of_sets()}')
    if phase_test.set_images(image_set.get_images_set(1)):
        print('Images OK')
    if phase_test.set_mask(masks_set.get_global_mask()):
        print('Mask OK')
    cropped_mask, c_size, c_pos = masks_set.get_global_cropped_mask()
    if phase_test.process_wrapped_phase():
        print('Wrapped Phase OK')
    wrapped = phase_test.get_wrapped_phase()
    if wrapped is not None:
        plt.figure()
        plt.imshow(wrapped, cmap='gray')

    if phase_test.process_unwrapped_phase():
        print('Unwrapped Phase OK')
    unwrapped = phase_test.get_unwrapped_phase()
    if wrapped is not None:
        plt.figure()
        plt.imshow(unwrapped, cmap='gray')



    plt.show()