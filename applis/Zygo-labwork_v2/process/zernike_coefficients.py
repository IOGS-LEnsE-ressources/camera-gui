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

from numpy import sqrt, sin, cos
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import numpy as np
from timeit import default_timer as timer

if __name__ == '__main__':
    from polar_cartesian_transformations import *
else:
    from process.polar_cartesian_transformations import *

PI = np.pi

aberrations_type = {
    "piston": [1],
    "tilt": [2, 3]
}

class Zernike:

    def __init__(self, max_order:int = 36):
        self.max_order = max_order
        self.surface = None

        self.corrected_phase = None
        self.coeff_calculated = False  # Zernike coefficients are calculated
        self.coeff_list = [None] * (self.max_order + 1)
        self.polynomials = [None] * (self.max_order + 1)
        self.X = None
        self.Y = None

    def set_surface(self, surface):
        #self.surface = surface.flatten()
        self.surface = surface
        # Dimensions of the surface
        a, b = self.surface.shape

        # Creating coordinate grids
        x = np.linspace(-1, 1, b)
        y = np.linspace(-1, 1, a)
        self.X, self.Y = np.meshgrid(x, y)

        self.corrected_phase = np.zeros_like(self.surface)

    def process_cartesian_polynomials(self, noll_index: int) -> np.ndarray:
        if noll_index == 1:     # Piston
            return np.ones_like(self.X)
        elif noll_index == 2:   # x-Tilt
            return 2*self.X
        elif noll_index == 3:   # y-Tilt
            return 2*self.Y

    def process_zernike_coefficient(self, order: int) -> np.ndarray:
        if order <= self.max_order:
            if self.coeff_list[order] is None:
                Z_nm = self.process_cartesian_polynomials(order)
                np.sum(self.surface * Z_nm) / np.sum(Z_nm ** 2)

                self.coeff_list[order] = np.sum(self.surface * Z_nm) / np.sum(Z_nm ** 2)
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

        '''
        # Affichage des résultats
        fig, axs = plt.subplots(1, 3, figsize=(12, 4))
        im1 = axs[0].imshow(self.surface, cmap='jet')
        axs[0].set_title("Init Surf")
        fig.colorbar(im1, ax=axs[0])

        im2 = axs[1].imshow(self.corrected_phase, cmap='jet')
        axs[1].set_title("Correction")
        fig.colorbar(im2, ax=axs[1])

        im3 = axs[2].imshow(new_surface, cmap='jet')
        axs[2].set_title("New surface")
        fig.colorbar(im3, ax=axs[2])

        plt.show()
        '''


if __name__ == "__main__":
    zer = Zernike(3)

    # Définition de la grille
    N, M = 256, 128  # Taille de la grille
    x = np.linspace(-1, 1, N)
    y = np.linspace(-1, 1, M)
    X, Y = np.meshgrid(x, y)
    # Création d'une surface avec un tilt (pente)
    tilt_x = -0.2  # Amplitude du tilt en x
    tilt_y = 0.05  # Amplitude du tilt en y
    surface = (tilt_x * X + tilt_y * Y)  # Surface avec tilt

    zer.set_surface(surface)
    ab_list = ['tilt']

    correction, new_image = zer.process_surface_correction(ab_list)

    # Affichage des résultats
    fig, axs = plt.subplots(1, 3, figsize=(12, 4))
    im1 = axs[0].imshow(surface, cmap='jet')
    axs[0].set_title("Surface initiale")
    fig.colorbar(im1, ax=axs[0])

    im2 = axs[1].imshow(correction, cmap='jet')
    axs[1].set_title("Correction appliquée")
    fig.colorbar(im2, ax=axs[1])

    im3 = axs[2].imshow(new_image, cmap='jet')
    axs[2].set_title("Surface corrigée")
    fig.colorbar(im3, ax=axs[2])

    plt.show()




