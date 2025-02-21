# -*- coding: utf-8 -*-
"""
File: zernike_coefficients.py

This file is associated with a first-year and second year engineering lab in photonics.
First-year subject: http://lense.institutoptique.fr/ressources/Annee1/TP_Photonique/S5-2324-PolyCI.pdf
Second-year subject: https://lense.institutoptique.fr/s8-aberrations/

Development details for this interface:
https://iogs-lense-ressources.github.io/camera-gui/contents/applis/appli_Zygo_labwork.html

.. note:: LEnsE - Institut d'Optique - version 1.0

.. moduleauthor:: Julien VILLEMEJANE (PRAG LEnsE) <julien.villemejane@institutoptique.fr>
.. moduleauthor:: Dorian MENDES (Promo 2026) <dorian.mendes@institutoptique.fr>
"""

import matplotlib.pyplot as plt
import numpy as np
import math

if __name__ == '__main__':
    from polar_cartesian_transformations import *
else:
    from process.polar_cartesian_transformations import *

aberrations_type = {
    "piston": [1],
    "tilt": [2, 3],
    "defocus": [4, 5, 6],
    "coma1": [7, 8, 9, 10],
    "sphere1": [11, 12, 13, 14, 15],
    "coma2": [16, 17, 18, 19, 20, 21],
    "sphere2": [22, 23, 24, 25, 26, 27, 28]
}

class Zernike:
    """
    Notes
    -----
    For more information on Zernike polynomials and their coefficients, refer to:
    https://iopscience.iop.org/article/10.1088/2040-8986/ac9e08/pdf
    """

    def __init__(self, max_order:int = 36):
        self.max_order = max_order
        self.surface = None

        self.corrected_phase = None
        self.coeff_calculated = False  # Zernike coefficients are calculated
        self.coeff_list = [None] * (self.max_order + 1)
        self.polynomials = [None] * (self.max_order + 1)
        self.X = None
        self.Y = None
        self.pow1 = None
        self.pow2 = None

    def set_surface(self, surface):
        self.surface = surface
        # Dimensions of the surface
        a, b = self.surface.shape

        # Creating coordinate grids
        x = np.linspace(-1, 1, b)
        y = np.linspace(-1, 1, a)
        self.X, self.Y = np.meshgrid(x, y)
        self.pow1 = (self.X**2 - self.Y**2)
        self.pow2 = (self.X**2 + self.Y**2)

        self.corrected_phase = np.zeros_like(self.surface)
        print(self.surface)

    def process_cartesian_polynomials(self, noll_index: int) -> np.ndarray:
        if noll_index == 1:     # Piston
            return np.ones_like(self.X)
        elif noll_index == 2:   # x-Tilt
            return 2*self.X
        elif noll_index == 3:   # y-Tilt
            return 2*self.Y
        elif noll_index == 4:   # defocus
            return np.sqrt(3)*(2*(self.X**2 + self.Y**2) - 1)
        elif noll_index == 5:   # defocus / 45d primary astig
            return 2*np.sqrt(6)*(self.X * self.Y)
        elif noll_index == 6:   # defocus / 0d primary astig
            return np.sqrt(6)*(self.X**2 - self.Y**2)
        elif noll_index == 7:   # Primary coma
            return np.sqrt(8)*self.Y*(3*(self.X**2 - self.Y**2)-2)
        elif noll_index == 8:   # Primary coma
            return np.sqrt(8)*self.X*(3*(self.X**2 - self.Y**2)-2)
        elif noll_index == 9:   # Primary coma
            return np.sqrt(8)*self.Y*(3*self.X**2 - self.Y**2)
        elif noll_index == 10:   # Primary coma
            return np.sqrt(8)*self.X*(self.X**2 - 3*self.Y**2)
        elif noll_index == 11:   # Primary Spherical Aber.
            return np.sqrt(5)*(6*self.pow2**2 - 6*self.pow2 + 1)
        elif noll_index == 12:   # Primary Spherical Aber.
            return np.sqrt(10)*self.pow1*(4*self.pow2 - 3)
        elif noll_index == 13:   # Primary Spherical Aber.
            return 2*np.sqrt(10)*self.X*self.Y*(4*self.pow2 - 3)
        elif noll_index == 14:   # Primary Spherical Aber.
            return np.sqrt(10)*(self.pow2**2 - 8*self.X**2*self.Y**2)
        elif noll_index == 15:   # Primary Spherical Aber.
            return 4*np.sqrt(10)*self.X*self.Y*self.pow1
        elif noll_index == 16:   # Secondary coma
            return np.sqrt(12)*self.X*(10*(self.pow2)**2 - 12*(self.pow2) + 3)
        elif noll_index == 17:   # Secondary coma
            return np.sqrt(12)*self.Y*(10*(self.pow2)**2 - 12*(self.pow2) + 3)
        elif noll_index == 18:   # Secondary coma
            return np.sqrt(12)*self.X*(self.X**2 - 3*self.Y**2)*(5*self.pow2 - 4)
        elif noll_index == 19:   # Secondary coma
            return np.sqrt(12)*self.Y*(3 * self.X**2 - self.Y**2)*(5*self.pow2 - 4)
        elif noll_index == 20:   # Secondary coma
            return np.sqrt(12)*self.X*(16*self.X**4 - 20*self.X**2*self.pow2 + 5*self.pow2**2)
        elif noll_index == 21:   # Secondary coma
            return np.sqrt(12)*self.Y*(16*self.Y**4 - 20*self.Y**2*self.pow2 + 5*self.pow2**2)
        elif noll_index == 22:   # Secondary Spherical Aber.
            return np.sqrt(7)*(20*self.pow2**3 - 30*self.pow2**2 + 12*self.pow2 - 1)
        elif noll_index == 23:   # Secondary Spherical Aber.
            return 2*np.sqrt(14)*self.X*self.Y*(15*self.pow2**2 - 20*self.pow2 + 6)
        elif noll_index == 24:   # Secondary Spherical Aber.
            return np.sqrt(14)*self.pow1*(15*self.pow2**2 - 20*self.pow2 + 6)
        elif noll_index == 25:   # Secondary Spherical Aber.
            return 4*np.sqrt(14)*self.X*self.Y*self.pow1*(6*self.pow2 - 5)
        elif noll_index == 26:   # Secondary Spherical Aber.
            return np.sqrt(14)*(self.pow2**2 - 8*self.X**2*self.Y*2)*(6*self.pow2 - 5)
        elif noll_index == 27:   # Secondary Spherical Aber.
            return np.sqrt(14)*self.X*self.Y*(32*self.X**4 - 32*self.X**2*self.pow2 + 6*self.pow2**2)
        elif noll_index == 28:   # Secondary Spherical Aber.
            return np.sqrt(14)*(32*self.X**6 - 48*self.X**4*self.pow2 + 18*self.X**2*self.pow2**2 - self.pow2**3)

    def process_zernike_coefficient(self, order: int) -> np.ndarray:
        if order <= self.max_order:
            if self.coeff_list[order] is None:
                Z_nm = self.process_cartesian_polynomials(order)
                # Mask NaN values
                valid_mask = ~np.isnan(self.surface)
                surface_filtered = self.surface[valid_mask]
                Z_nm_filtered = Z_nm[valid_mask]
                print(surface_filtered.shape)

                self.coeff_list[order] = np.sum(surface_filtered * Z_nm_filtered) / np.sum(Z_nm_filtered ** 2)
                print(f'Z[{order}] = {self.coeff_list[order]}')
        else:
            return None

    def process_surface_correction(self, aberrations: list[str]):
        self.corrected_phase = np.zeros_like(self.surface)
        for k, type_ab in enumerate(aberrations):
            coeffs = aberrations_type[type_ab]
            for c in coeffs:
                if self.coeff_list[c] is None:
                    self.process_zernike_coefficient(c)
                self.corrected_phase += self.coeff_list[c] * self.process_cartesian_polynomials(c)
        # Correction de la surface
        new_surface = self.surface - self.corrected_phase
        return self.corrected_phase, new_surface

def display_3_figures(init, zer, corr):
    """Displaying results."""
    fig, axs = plt.subplots(1, 3, figsize=(12, 4))
    im1 = axs[0].imshow(init, extent=(-1, 1, -1, 1), cmap='jet')
    axs[0].set_title("Initial Surface")
    fig.colorbar(im1, ax=axs[0])

    im2 = axs[1].imshow(zer, extent=(-1, 1, -1, 1), cmap='jet')
    axs[1].set_title("Correction")
    fig.colorbar(im2, ax=axs[1])

    im3 = axs[2].imshow(corr, extent=(-1, 1, -1, 1), cmap='jet')
    axs[2].set_title("Corrected surface")
    fig.colorbar(im3, ax=axs[2])

    plt.show()


def zernike_radial(n, m, r):
    """ Calcule la composante radiale des polynômes de Zernike. """
    R = np.zeros_like(r)
    for k in range((n - abs(m)) // 2 + 1):
        c = (-1)**k * math.factorial(n - k) / (
            math.factorial(k) *
            math.factorial((n + abs(m)) // 2 - k) *
            math.factorial((n - abs(m)) // 2 - k)
        )
        R += c * r**(n - 2*k)
    return R


def zernike(n, m, rho, theta):
    """ Calcule un polynôme de Zernike. """
    if m >= 0:
        return zernike_radial(n, m, rho) * np.cos(m * theta)
    else:
        return zernike_radial(n, -m, rho) * np.sin(-m * theta)


def elliptic_mask(image, cx=0, cy=0, a=0.5, b=0.5):
    """Create elliptic mask on an image.
    :param image: initial image to mask
    :param cx: X-axis center
    :param cy: Y-axis center
    :param a: X-axis dimension
    :param b: Y-axis dimension
    """
    height, width = image.shape
    x = np.linspace(-1, 1, width)
    y = np.linspace(-1, 1, height)
    X, Y = np.meshgrid(x, y)
    return ((X - cx) ** 2) / a ** 2 + ((Y - cy) ** 2) / b ** 2 <= 1


if __name__ == "__main__":
    zer = Zernike(28)

    # Grid definition
    N, M = 256, 128  # Taille de la grille
    x = np.linspace(-1, 1, N)
    y = np.linspace(-1, 1, M)
    X, Y = np.meshgrid(x, y)
    # Circular mask
    R = np.sqrt(X ** 2 + Y ** 2)
    theta = np.arctan2(Y, X)
    mask = R <= 1


    # Surface creation
    tilt_x = -0.27
    tilt_y = 0.35
    surface = tilt_x * X + tilt_y * Y #+ np.exp(-3 * R ** 2) + 0.48 * (2 * R ** 2 - 1)


    mask = elliptic_mask(surface, 0.2, 0, a=0.5)

    # Coma horizontale (Z3^1) et verticale (Z3^-1)
    coma_horizontal = zernike(3, 1, R, theta)  # Z3^1
    coma_vertical = zernike(3, -1, R, theta)  # Z3^-1
    #surface += coma_vertical+coma_vertical

    surface[~mask] = np.nan

    zer.set_surface(surface)
    ab_list = ['tilt'] #,'defocus','coma1','sphere1','coma2','sphere2']

    correction, new_image = zer.process_surface_correction(ab_list)

    display_3_figures(surface, correction, new_image)






