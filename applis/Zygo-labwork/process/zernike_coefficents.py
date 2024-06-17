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

from numpy import sqrt, sin, cos, ndarray
import numpy as np

if __name__ == '__main__':
    from polar_cartesian_transformations import *
else:
    from process.polar_cartesian_transformations import *

PI = np.pi

number_zernike_polynomials = 37

def polar_zernike_coefficients(u: np.ndarray, phi: np.ndarray, osa_index: int) -> np.ndarray:
    """
    Calculate the Zernike polynomial coefficient for given polar coordinates and OSA index.

    Parameters
    ----------
    u : numpy.ndarray
        Radial coordinates, where 0 <= u <= 1.
    phi : numpy.ndarray
        Angular coordinates in radians.
    osa_index : int
        The OSA (Optical Society of America) index of the Zernike polynomial.

    Returns
    -------
    numpy.ndarray
        The values of the Zernike polynomial coefficient for the given u, phi, and osa_index.
        Returns 0 for points where u > 1.

    Notes
    -----
    For more information on Zernike polynomials and their coefficients, refer to:
    https://wp.optics.arizona.edu/jcwyant/wp-content/uploads/sites/13/2016/08/ZernikePolynomialsForTheWeb.pdf
    """
    # Handle points outside the pupil (where u > 1)
    u[u > 1] = 0
    
    if osa_index == 0:
        # Piston
        return 1
    
    elif osa_index == 1:
        # Tilt Y
        return 2 * u * sin(phi)
    
    elif osa_index == 2:
        # Tilt X
        return 2 * u * cos(phi)
    
    elif osa_index == 3:
        # Defocus
        return sqrt(3) * (2 * u**2 - 1)
    
    elif osa_index == 4:
        # Astigmatism 45°
        return sqrt(6) * u**2 * sin(2 * phi)
    
    elif osa_index == 5:
        # Astigmatism 0°
        return sqrt(6) * u**2 * cos(2 * phi)
    
    elif osa_index == 6:
        # Trefoil Y
        return sqrt(8) * u**3 * sin(3 * phi)
    
    elif osa_index == 7:
        # Coma Y
        return sqrt(8) * (3 * u**3 - 2 * u) * sin(phi)
    
    elif osa_index == 8:
        # Coma X
        return sqrt(8) * (3 * u**3 - 2 * u) * cos(phi)
    
    elif osa_index == 9:
        # Trefoil X
        return sqrt(8) * u**3 * cos(3 * phi)
    
    elif osa_index == 10:
        # Spherical aberration
        return sqrt(5) * (6 * u**4 - 6 * u**2 + 1)
    
    elif osa_index == 11:
        # Secondary Astigmatism 45°
        return sqrt(10) * (4 * u**4 - 3 * u**2) * sin(2 * phi)
    
    elif osa_index == 12:
        # Secondary Astigmatism 0°
        return sqrt(10) * (4 * u**4 - 3 * u**2) * cos(2 * phi)
    
    elif osa_index == 13:
        # Tetrafoil Y
        return sqrt(12) * u**4 * sin(4 * phi)
    
    elif osa_index == 14:
        # Secondary Trefoil Y
        return sqrt(12) * (10 * u**5 - 12 * u**3 + 3 * u) * sin(3 * phi)
    
    elif osa_index == 15:
        # Secondary Coma Y
        return sqrt(12) * (10 * u**5 - 12 * u**3 + 3 * u) * sin(phi)
    
    elif osa_index == 16:
        # Secondary Coma X
        return sqrt(12) * (10 * u**5 - 12 * u**3 + 3 * u) * cos(phi)
    
    elif osa_index == 17:
        # Secondary Trefoil X
        return sqrt(12) * u**4 * cos(4 * phi)
    
    elif osa_index == 18:
        # Tetrafoil X
        return sqrt(12) * u**4 * cos(4 * phi)
    
    elif osa_index == 19:
        # Pentafoil Y
        return sqrt(14) * u**5 * sin(5 * phi)
    
    elif osa_index == 20:
        # Tetra-Astigmatism 45°
        return sqrt(14) * (15 * u**6 - 20 * u**4 + 6 * u**2) * sin(2 * phi)
    
    elif osa_index == 21:
        # Tetra-Astigmatism 0°
        return sqrt(14) * (15 * u**6 - 20 * u**4 + 6 * u**2) * cos(2 * phi)
    
    elif osa_index == 22:
        # Pentafoil X
        return sqrt(14) * u**5 * cos(5 * phi)
    
    elif osa_index == 23:
        # Secondary Spherical Aberration
        return sqrt(7) * (20 * u**6 - 30 * u**4 + 12 * u**2 - 1)
    
    elif osa_index == 24:
        # Secondary Astigmatism 0°
        return sqrt(7) * (15 * u**6 - 20 * u**4 + 6 * u**2) * cos(6 * phi)
    
    elif osa_index == 25:
        # Secondary Astigmatism 45°
        return sqrt(7) * (15 * u**6 - 20 * u**4 + 6 * u**2) * sin(6 * phi)
    
    elif osa_index == 26:
        # Hexafoil Y
        return sqrt(16) * u**6 * sin(6 * phi)
    
    elif osa_index == 27:
        # Secondary Pentafoil Y
        return sqrt(16) * (21 * u**7 - 30 * u**5 + 12 * u**3 - u) * sin(5 * phi)
    
    elif osa_index == 28:
        # Secondary Pentafoil X
        return sqrt(16) * (21 * u**7 - 30 * u**5 + 12 * u**3 - u) * cos(5 * phi)
    
    elif osa_index == 29:
        # Secondary Hexafoil Y
        return sqrt(16) * (28 * u**8 - 42 * u**6 + 20 * u**4 - 3 * u**2) * sin(6 * phi)
    
    elif osa_index == 30:
        # Tetra-Pentafoil Y
        return sqrt(18) * u**7 * sin(7 * phi)
    
    elif osa_index == 31:
        # Hexafoil X
        return sqrt(18) * u**6 * cos(6 * phi)
    
    elif osa_index == 32:
        # Tetrafoil X
        return sqrt(18) * (36 * u**8 - 56 * u**6 + 28 * u**4 - 8 * u**2) * cos(4 * phi)
    
    elif osa_index == 33:
        # Tetrafoil Y
        return sqrt(18) * (36 * u**8 - 56 * u**6 + 28 * u**4 - 8 * u**2) * sin(4 * phi)
    
    elif osa_index == 34:
        # Secondary Pentafoil X
        return sqrt(18) * u**7 * cos(7 * phi)
    
    elif osa_index == 35:
        # Secondary Pentafoil Y
        return sqrt(18) * (45 * u**9 - 72 * u**7 + 45 * u**5 - 10 * u**3 + u) * sin(5 * phi)
    
    elif osa_index == 36:
        # Secondary Pentafoil X
        return sqrt(18) * (45 * u**9 - 72 * u**7 + 45 * u**5 - 10 * u**3 + u) * cos(5 * phi)
    
    return 0  # Si l'indice n'est pas dans les 37 premiers, retournez 0

def cartesian_zernike_coefficients(x: np.ndarray, y: np.ndarray, osa_index: int) -> np.ndarray:
    """
    Calculate the Zernike polynomial coefficient for given Cartesian coordinates and OSA index.

    Parameters
    ----------
    x : numpy.ndarray
        Cartesian x coordinates.
    y : numpy.ndarray
        Cartesian y coordinates.
    osa_index : int
        The OSA (Optical Society of America) index of the Zernike polynomial.

    Returns
    -------
    numpy.ndarray
        The values of the Zernike polynomial coefficient for the given Cartesian coordinates (x, y)
        and OSA index.

    Notes
    -----
    This function converts Cartesian coordinates (x, y) to polar coordinates (u, phi),
    where u is the radial coordinate normalized to [0, 1] and phi is the angular coordinate in radians.
    It then calculates the Zernike polynomial coefficient using the polar coordinates.

    For more information on Zernike polynomials and their coefficients, refer to:
    https://wp.optics.arizona.edu/jcwyant/wp-content/uploads/sites/13/2016/08/ZernikePolynomialsForTheWeb.pdf
    """
    u, phi = cartesian_to_polar(x, y)  # Convert Cartesian to polar coordinates
    return polar_zernike_coefficients(u, phi, osa_index)  # Calculate Zernike coefficients

def get_surface_zernike_coefficient(surface: np.ndarray) -> np.ndarray:
    # Parameters
    N = 37 # Degree of the polynomial
    limit = 1e-3 # Below, the coefficients are considered insignificant.
    
    # Dimensions of the surface
    a, b = surface.shape
    
    # Creating coordinate grids
    x = np.linspace(-1, 1, b)
    y = np.linspace(-1, 1, a)
    X, Y = np.meshgrid(x, y)
    
    # Reorganizing the surface
    surface = np.fliplr(surface)
    surface = np.flipud(surface)
    
    # Converting to column vectors
    X = X.flatten()
    Y = Y.flatten()
    surface = surface.flatten()
    
    # Removing NaN values
    X = X[~np.isnan(surface)]
    Y = Y[~np.isnan(surface)]
    surface = surface[~np.isnan(surface)]

    # Normalizing the surface
    phi = surface / (2 * PI)

    # Calculating the matrix M using polar_zernike_coefficients
    M = np.zeros((len(phi), N-1))
    for i in range(2, N+1):
        M[:, i-2] = cartesian_zernike_coefficients(X, Y, i)

    # Calculating Zernike coefficients
    coeff_zernike = np.linalg.lstsq(M, phi, rcond=None)[0]
    coeff_zernike = np.concatenate(([0], coeff_zernike))
    coeff_zernike[coeff_zernike < limit] = 0  # removing insignificant coefficients

    return coeff_zernike

# Exemple d'utilisation
if __name__ == "__main__":
    u = np.array([0.5])
    phi = np.array([0.25])
    for i in range(37):
        # print(f"Zernike coefficient for OSA index {i}: {polar_zernike_coefficients(u, phi, i)}")
        pass

    surf = np.random.randint(0, 255, (10,10))
    print(get_surface_zernike_coefficient(surf))