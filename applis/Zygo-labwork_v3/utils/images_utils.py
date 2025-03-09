# -*- coding: utf-8 -*-
"""*images_utils.py* file.

./utils/images_utils.py contains tools for images processing.

.. note:: LEnsE - Institut d'Optique - version 1.0

.. moduleauthor:: Julien VILLEMEJANE (PRAG LEnsE) <julien.villemejane@institutoptique.fr>
Creation : march/2025
"""
import numpy as np
import scipy

def read_mat_file(file_path: str) -> dict:
    """
    Load data and masks from a .mat file.
    The file must contain a set of 5 images (Hariharan algorithm) in a dictionary key called "Images".
    Additional masks can be included in a dictionary key called "Masks".

    :param file_path: Path and name of the file to load.
    :return: Dictionary containing at least np.ndarray including in the "Images"-key object.
    """
    data = scipy.io.loadmat(file_path)
    return data


def write_mat_file(file_path, images: np.ndarray, masks: np.ndarray = None, masks_type: list = []):
    """
    Load data and masks from a .mat file.
    The file must contain a set of 5 images (Hariharan algorithm) in a dictionary key called "Images".
    Additional masks can be included in a dictionary key called "Masks".

    :param file_path: Path and name of the file to write.
    :param images: Set of images to save.
    :param masks: Set of masks to save. Default None.
    :param masks_type: Type of the masks to save. Default [].
    """
    data = {
        'Images': images
    }
    if masks is not None:
        data['Masks'] = masks
    if len(masks_type) != 0:
        data['Masks_Type'] = masks_type
    scipy.io.savemat(file_path, data)


def split_3d_array(array_3d, size: int = 5):
    # Ensure the array has the expected shape
    if array_3d.shape[2]%size != 0:
        raise ValueError(f"The loaded array does not have the expected third dimension size of {size}.")
    # Extract the 2D arrays
    arrays = [array_3d[:, :, i].astype(np.float32) for i in range(array_3d.shape[2])]
    return arrays