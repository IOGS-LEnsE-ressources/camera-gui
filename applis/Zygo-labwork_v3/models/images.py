# -*- coding: utf-8 -*-
"""*images.py* file.

./models/images.py contains Images_Model class to manage sets of images from Zygo application.

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
import scipy
import numpy as np
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from utils import *

number_of_images = 5


def generate_images_grid(images: list[np.ndarray]):
    """Generate a grid with 5 images.
    The 6th image is the mean of the 4 first images.
    :param images: List of 5 images.
    """
    img_height, img_width = images[0].shape
    separator_size = 5
    # Global size
    total_height = 2 * img_height + separator_size  # 2 rows of images
    total_width = 3 * img_width + 2 * separator_size  # 3 columns of images
    # Empty image
    result = np.ones((total_height, total_width), dtype=np.uint8) * 255
    # Add each images
    result[0:img_height, 0:img_width] = images[0]
    result[0:img_height, img_width + separator_size:2 * img_width + separator_size] = images[1]
    result[0:img_height, 2 * img_width + 2 * separator_size:] = images[2]
    result[img_height + separator_size:, 0:img_width] = images[3]
    result[img_height + separator_size:, img_width + separator_size:2 * img_width + separator_size] = images[4]
    sum_image = (images[0] + images[1] + images[2] + images[3])/4
    sum_image = sum_image.astype(np.uint8)
    result[img_height + separator_size:, 2 * img_width + 2 * separator_size:] = sum_image
    return result


class ImagesModel:
    """Class containing images data and parameters.
    Images are stored in sets of N images.
    """
    def __init__(self, set_size: int=5):
        """Default constructor.
        :param set_size: Size of a set of images.
        """
        self.set_size = set_size
        self.images_list = []
        self.images_sets_number = 0

    def add_set_images(self, images: list):
        """Add a new set of images."""
        if isinstance(images, list):
            if len(images) == self.set_size:
                self.images_list.append(images)
                self.images_sets_number += 1

    def reset_all_images(self):
        """Reset all images."""
        self.images_list.clear()
        self.images_sets_number = 0

    def get_number_of_sets(self) -> int:
        """Return the number of stored sets of images.
        :return: Number of stored sets of images.
        """
        return self.images_sets_number

    def get_images_set(self, index: int) -> list[np.ndarray]:
        """Return a set of N images.
        :param index: Index of the set to return.
        :return: List of images from the specified set.
        """
        if index <= self.images_sets_number+1:
            return self.images_list[index-1]
        return None

    def get_image_from_set(self, index: int, set_index: int = 1):
        """Return an image from its index in a specific set.
        :param index: Index of the image to return.
        :param set_index: Index of the set of the image. Default 1.
        """
        return self.images_list[set_index-1][index-1]

    def get_images_as_list(self):
        """Return all the stored images in a single list."""
        list = []
        for i in range(self.images_sets_number):
            set = self.get_images_set(i+1)
            list += set
        return list


    def load_images_set_from_file(self, filename: str = '') -> bool:
        """
        Load sets of images from a MAT file.
        :param filename: Path of the MAT file.
        :return: True if file is loaded.
        """
        if filename != '':
            data_from_mat = read_mat_file(filename)
            # Process images from MAT file
            images_mat = data_from_mat['Images']
            images_d = split_3d_array(images_mat)

            if isinstance(images_d, list):
                if len(images_d) % self.set_size == 0 and len(images_d) > 1:
                    for i in range(int(len(images_d) / 5)):
                        self.add_set_images(images_d[i:i + 5])
                    return True
        return False

    def save_images_set_to_file(self, filename: str = '') -> bool:
        """
        Save sets of images to a MAT file.
        :param filename: Path of the MAT file.
        :return: True if file is saved.
        """
        new_data = np.stack((self.images_list), axis=2).astype(np.uint8)
        data = {
            'Images': new_data
        }
        scipy.io.savemat(filename, data)



if __name__ == '__main__':
    from matplotlib import pyplot as plt

    nb_of_images_per_set = 5
    image_set = ImagesModel(nb_of_images_per_set)

    ## Open MAT file - including 'Images' and 'Masks'
    if image_set.load_images_set_from_file('../_data/test3.mat'):
        print('Images OK')

    ## Test class
    print(f'Number of sets = {image_set.get_number_of_sets()}')
    if image_set.get_number_of_sets() >= 1:
        image_1_1 = image_set.get_images_set(1)
        if isinstance(image_1_1, list):
            plt.figure()
            plt.imshow(image_1_1[0], cmap='gray')
            plt.show()


