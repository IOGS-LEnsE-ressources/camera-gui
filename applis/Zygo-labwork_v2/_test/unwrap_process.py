# -*- coding: utf-8 -*-
"""*unwrap_process.py* file.

This file contains functions to unwrap the phase.

.. note:: LEnsE - Institut d'Optique - version 1.0

.. moduleauthor:: Julien VILLEMEJANE (LEnsE) <julien.villemejane@institutoptique.fr>

"""

import scipy
import matplotlib.pyplot as plt
import numpy as np
from scipy.ndimage import gaussian_filter, uniform_filter
from scipy.interpolate import griddata
from skimage.restoration import unwrap_phase

PI = np.pi

def read_mat_file(file_path):
    data = scipy.io.loadmat(file_path)
    print(data.keys())
    return data

def split_3d_array(array_3d):
    # Ensure the array has the expected shape
    if array_3d.shape[2] != 5:
        raise ValueError("The loaded array does not have the expected third dimension size of 5.")
    
    # Extract the 2D arrays
    arrays = [array_3d[:, :, i].astype(np.float32) for i in range(5)]
    return arrays

def hariharan_algorithm(intensity: list[np.ndarray]) -> np.ndarray:
    """
    Apply the Hariharan phase demodulation algorithm to a set of intensity measurements.

    Parameters
    ----------
    intensity : list[np.ndarray]
        First intensity measurement, I_1 = I_0 * (1 + C * cos(phi)).
        Second intensity measurement, I_2 = I_0 * (1 + C * cos(phi + π/2)).
        Third intensity measurement, I_3 = I_0 * (1 + C * cos(phi + π)).
        Fourth intensity measurement, I_4 = I_0 * (1 + C * cos(phi + 3π/2)).
        Fifth intensity measurement, I_5 = I_0 * (1 + C * cos(phi + 2π)).

    Returns
    -------
    np.ndarray
        The demodulated phase phi array.

    Notes
    -----
    This function calculates the demodulated phase using the Hariharan algorithm, which is a method for phase recovery in interferometry.

    The five intensity measurements are taken with phase shifts of π/2 between them, specifically:
    - I_1 = I_0(1 + C * cos(phi))
    - I_2 = I_0(1 + C * cos(phi + pi/2))
    - I_3 = I_0(1 + C * cos(phi + pi))
    - I_4 = I_0(1 + C * cos(phi + 3*pi/2))
    - I_5 = I_0(1 + C * cos(phi + 2*pi))

    The returned phase values are in radians.

    This algorithm was originally published in:
    P. Hariharan, B. F. Oreb, and T. Eiju, "Digital phase-shifting interferometry: a simple error-compensating phase calculation algorithm," Appl. Opt. 26, 2504-2506 (1987).
    Available at: https://opg.optica.org/ao/fulltext.cfm?uri=ao-26-13-2504&id=168363
    """
    num = 2 * (intensity[3] - intensity[1])
    denum = 2 * intensity[2] - intensity[4] - intensity[0]
    return np.arctan2(num, denum)

def statistique_surface(surface):
    # Calcul de PV (Peak-to-Valley)
    PV = np.nanmax(surface) - np.nanmin(surface)
    RMS = np.nanstd(surface)
    return PV, RMS

## Read data from MatLab file
data = read_mat_file("../_data/imgs2.mat")
images_mat = data['Imgs']
images = split_3d_array(images_mat)

print(images[0].shape)

## Test with NPZ file / To save images after acquiring !

# Sauvegarde dans un fichier .npz
#np.savez('matrices.npz', *images_mat)

# Chargement du fichier .npz
#loaded_data = np.load('matrices.npz')
#images = [loaded_data[f'arr_{i}'] for i in range(len(loaded_data.files))]

print(type(images))

# Display images
'''
for i, img in enumerate(images):
    plt.subplot(1,5,i+1)
    plt.imshow(img, cmap='gray')
    plt.axis('off')
plt.show()
'''

## Mask on the image
mask = np.zeros_like(images[0])
mask[400:1200, 790:1900] = 1
mask[200:400, 950:1600] = 1
mask[300:400, 880:1800] = 1
mask[1200:1400, 1350:1750] = 1

'''
plt.imshow(images[0]*mask, cmap='magma')
plt.show()
'''

## TO DO : test with masks selection by user...

## Gaussian filter on image*
sigma = 10
images_filtered = list(map(lambda x:gaussian_filter(x, sigma), images))

for i, img in enumerate(images_filtered):
    plt.subplot(1,5,i+1)
    plt.imshow(img[400:1200, 750:1900], cmap='gray')
    plt.axis('off')
plt.show()

## Calculation of the phase by Hariharan algorithm
wrapped_phase = hariharan_algorithm(images_filtered)
# Array for displaying data on 3D projection
x = np.arange(wrapped_phase.shape[1])
y = np.arange(wrapped_phase.shape[0])
X, Y = np.meshgrid(x, y)

# Display of the surface
fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')
surface = ax.plot_surface(X[400:1200, 750:1900], Y[400:1200, 750:1900], wrapped_phase[400:1200, 750:1900], cmap='magma')
ax.set_title('Unwrapped surface')
cbar = fig.colorbar(surface, ax=ax, shrink=0.5, aspect=10)
cbar.set_label(r'Default magnitude ($\lambda$)')
plt.show()

## Unwrap phase
unwrapped_phase = unwrap_phase(wrapped_phase)/(2*np.pi)

# Display of the surface
fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')
surface = ax.plot_surface(X[400:1200, 750:1900], Y[400:1200, 750:1900], unwrapped_phase[400:1200, 750:1900], cmap='magma')
ax.set_title('Unwrapped surface')
cbar = fig.colorbar(surface, ax=ax, shrink=0.5, aspect=10)
cbar.set_label(r'Default magnitude ($\lambda$)')
plt.show()


# Statistics
PV, RMS = statistique_surface(unwrapped_phase)
print(f"PV: {PV:.2f} λ | RMS: {RMS:.2f} λ")