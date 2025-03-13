# -*- coding: utf-8 -*-
"""*dataset.py* file.

./models/dataset.py contains DataSetModel class to manage sets of images and masks
from Zygo application.

Images are intensity measurements of interferences. All images have the same size.
A set of 5 images is necessary to be demodulated by the Hariharan phase
demodulation algorithm

Data are stored in MAT file, containing "Images" (set of 5 arrays in 2 dimensions),
"Masks" objects (array(s) in 2 dimensions - same size as images) and
"Masks_Type" list.

.. note:: LEnsE - Institut d'Optique - version 1.0

.. moduleauthor:: Julien VILLEMEJANE (PRAG LEnsE) <julien.villemejane@institutoptique.fr>
Creation : march/2025
"""
import sys, os
import scipy
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from models import *
from utils import *


class DataSetModel:
    """Class containing images data and parameters.
    Images are stored in sets of N images.
    """
    def __init__(self, set_size: int=5):
        """Default constructor.
        :param set_size: Size of a set of images.
        """
        self.set_size = set_size
        self.images_sets = ImagesModel(set_size)
        self.masks_sets = MasksModel()

    def add_set_images(self, images: list):
        """
        Add a new set of images.
        :param images: List of images to add.

        """
        self.images_sets.add_set_images(images)

    def get_images_sets(self, index: int=1) -> list[np.ndarray]:
        """
        Return the list of images of a specific set of images.
        :param index: Index of the set to get images list.
        :return: List of images of a specific set of images.
        """
        return self.images_sets.get_images_set(index)

    def get_masks_list(self) -> list[np.ndarray]:
        """
        Return the list of the masks.
        :return: List of 2D-array.
        """
        return self.masks_sets.get_mask_list()

    def get_global_mask(self) -> np.ndarray:
        """
        Return the global resulting mask.
        :return: 2D-array.
        """
        return self.masks_sets.get_global_mask()

    def get_global_cropped_mask(self) -> np.ndarray:
        """
        Return the global resulting mask.
        :return: 2D-array.
        """
        return self.masks_sets.get_global_cropped_mask()


if __name__ == '__main__':

    number_of_images = 5
    data_set = DataSetModel(number_of_images)

    images_set = ImagesModel(number_of_images)
    if images_set.load_images_set_from_file('../_data/test3.mat'):
        print('Images OK')
        data_set.add_set_images(images_set.get_images_set(1))

    print(f'Number of sets = {data_set.images_sets.get_number_of_sets()}')
    if data_set.images_sets.get_number_of_sets() >= 1:
        image_1_1 = data_set.get_images_sets(1)
        if isinstance(image_1_1, list):
            plt.figure()
            plt.imshow(image_1_1[0], cmap='gray')
            plt.show()


