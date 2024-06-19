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
    """
    # Handle points outside the pupil (where u > 1)
    u[u > 1] = 0
    
    if osa_index == 1:
        return np.ones_like(u)

    elif osa_index == 2:
        return u * cos(phi)

    elif osa_index == 3:
        return u * sin(phi)

    elif osa_index == 4:
        return 2 * (u ** 2) - 1

    elif osa_index == 5:
        return u ** 2 * cos(2 * phi)

    elif osa_index == 6:
        return u ** 2 * sin(2 * phi)

    elif osa_index == 7:
        return (3 * u ** 3 - 2 * u) * cos(phi)

    elif osa_index == 8:
        return (3 * u ** 3 - 2 * u) * sin(phi)

    elif osa_index == 9:
        return 6 * u ** 4 - 6 * u ** 2 + 1

    elif osa_index == 10:
        return u ** 3 * cos(3 * phi)

    elif osa_index == 11:
        return u ** 3 * sin(3 * phi)

    elif osa_index == 12:
        return (4 * u ** 4 - 3 * u ** 2) * cos(2 * phi)

    elif osa_index == 13:
        return (4 * u ** 4 - 3 * u ** 2) * sin(2 * phi)

    elif osa_index == 14:
        return (10 * u ** 5 - 12 * u ** 3 + 3 * u) * cos(phi)

    elif osa_index == 15:
        return (10 * u ** 5 - 12 * u ** 3 + 3 * u) * sin(phi)

    elif osa_index == 16:
        return 20 * u ** 6 - 30 * u ** 4 + 12 * u ** 2 - 1

    elif osa_index == 17:
        return u ** 4 * cos(4 * phi)

    elif osa_index == 18:
        return u ** 4 * sin(4 * phi)

    elif osa_index == 19:
        return (5 * u ** 5 - 4 * u ** 3) * cos(3 * phi)

    elif osa_index == 20:
        return (5 * u ** 5 - 4 * u ** 3) * sin(3 * phi)

    elif osa_index == 21:
        return (15 * u ** 6 - 20 * u ** 4 + 6 * u ** 2) * cos(2 * phi)

    elif osa_index == 22:
        return (15 * u ** 6 - 20 * u ** 4 + 6 * u ** 2) * sin(2 * phi)

    elif osa_index == 23:
        return (35 * u ** 7 - 60 * u ** 5 + 30 * u ** 3 - 4 * u) * cos(phi)

    elif osa_index == 24:
        return (35 * u ** 7 - 60 * u ** 5 + 30 * u ** 3 - 4 * u) * sin(phi)

    elif osa_index == 25:
        return 70 * u ** 8 - 140 * u ** 6 + 90 * u ** 4 - 20 * u ** 2 + 1

    elif osa_index == 26:
        return u ** 5 * cos(5 * phi)

    elif osa_index == 27:
        return u ** 5 * sin(5 * phi)

    elif osa_index == 28:
        return (6 * u ** 2 - 5) * u ** 4 * cos(4 * phi)

    elif osa_index == 29:
        return (6 * u ** 2 - 5) * u ** 4 * sin(4 * phi)

    elif osa_index == 30:
        return (21 * u ** 4 - 30 * u ** 2 + 10) * u ** 3 * cos(3 * phi)

    elif osa_index == 31:
        return (21 * u ** 4 - 30 * u ** 2 + 10) * u ** 3 * sin(3 * phi)

    elif osa_index == 32:
        return (56 * u ** 6 - 105 * u ** 4 + 60 * u ** 2 - 10) * u ** 2 * cos(2 * phi)

    elif osa_index == 33:
        return (56 * u ** 6 - 105 * u ** 4 + 60 * u ** 2 - 10) * u ** 2 * sin(2 * phi)

    elif osa_index == 34:
        return (126 * u ** 8 - 280 * u ** 6 + 210 * u ** 4 - 60 * u ** 2 + 5) * u * cos(phi)

    elif osa_index == 35:
        return (126 * u ** 8 - 280 * u ** 6 + 210 * u ** 4 - 60 * u ** 2 + 5) * u * sin(phi)

    elif osa_index == 36:
        return 252 * u ** 10 - 630 * u ** 8 + 560 * u ** 6 - 210 * u ** 4 + 30 * u ** 2 - 1

    elif osa_index == 37:
        return 924 * u ** 12 - 2772 * u ** 10 + 3150 * u ** 8 - 1680 * u ** 6 + 420 * u ** 4 - 42 * u ** 2 + 1
    
    return 0

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

def get_zernike_coefficient(surface: np.ndarray) -> np.ndarray:
    # Parameters
    N = 37 # Degree of the polynomial
    limit = 1e-3 # Below, the coefficients are considered insignificant.
    
    # Dimensions of the surface
    a, b = surface.shape
    
    # Creating coordinate grids
    x = np.linspace(-1, 1, b)
    y = np.linspace(-1, 1, a)
    X, Y = np.meshgrid(x, y)
    
    surface = np.transpose(surface)
    
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
    # m_(i,k) = Z_k(u_i, phi_i)
    M = np.zeros((len(phi), N-1))
    for i in range(2, N+1):
        M[:, i-2] = cartesian_zernike_coefficients(X, Y, i)

    # Calculating Zernike coefficients
    coeff_zernike = np.linalg.lstsq(M, phi, rcond=None)[0]
    coeff_zernike = np.concatenate(([0], coeff_zernike))
    coeff_zernike[np.abs(coeff_zernike) < limit] = 0  # removing insignificant coefficients

    return coeff_zernike.squeeze()

def get_polynomials_basis(x: np.ndarray, y: np.ndarray) -> np.ndarray:
    """ Return Z_i(x, y) """
    polynomials = np.ones((len(x), number_zernike_polynomials))
    for i in range(number_zernike_polynomials):
        polynomials[:, i] = cartesian_zernike_coefficients(x, y, i)
    return polynomials

def remove_aberration(phase: np.ndarray, aberrations_considered: np.ndarray) -> np.ndarray:
    a, b = phase.shape
    normalized_phase = phase / (2 * PI)
    
    print("Normalized phase before correction:")
    print(normalized_phase)
    print(normalized_phase.min(), normalized_phase.max())
    
    x = np.linspace(-1, 1, b)
    y = np.linspace(-1, 1, a)
    X, Y = np.meshgrid(x, y)
    
    coeffs = get_zernike_coefficient(normalized_phase)
    
    print("Zernike coefficients:")
    print(coeffs)

    plt.figure(figsize=(10, 6))
    plt.bar(list(range(len(coeffs))), coeffs**2)
    plt.bar(list(range(len(coeffs))), (coeffs*aberrations_considered)**2, color='red')
    plt.xticks(list(range(len(coeffs))))
    plt.axhline(0, color='black')
    plt.ylabel(r'$C_i^2$')
    plt.title('Zernike coefficients')
    plt.show()
    
    polynomials = get_polynomials_basis(X.flatten(), Y.flatten())
    surface = polynomials.dot((aberrations_considered * coeffs))
    
    normalized_phase -= surface.reshape((a, b))
    print("Normalized phase after correction:")
    print(normalized_phase)
    print(normalized_phase.min(), normalized_phase.max())
    
    return normalized_phase * 2 * PI

if __name__ == '__main__':
    # Dimensions de l'image
    a, b = 100, 300

    # Définir une phase combinée avec piston, tilt et astigmatisme
    X, Y = np.meshgrid(np.linspace(-1, 1, b), np.linspace(-1, 1, a))

    # Piston
    phi_piston = np.ones((a, b)) * 5

    # Tilt
    phi_tilt = 3 * Y

    # Astigmatisme à 45°
    # phi_astigmatism_45 = 2 * np.sqrt(6) * (X**2 - Y**2) * np.sin(2 * np.arctan2(X, Y))

    # Phase totale avec aberrations
    phi = phi_piston + phi_tilt # + phi_astigmatism_45

    # Appliquer la fonction pour retirer les aberrations
    aberrations_considered = np.zeros(37, dtype=int)
    aberrations_considered[1:2] = 1
    print(aberrations_considered)
    corrected_phase = remove_aberration(phi, aberrations_considered)

    # Affichage de la phase initiale
    # Création de la figure et des sous-graphiques en 3D
    fig = plt.figure(figsize=(14, 6))

    # Graphique 1 : Phase initiale avec aberrations
    ax1 = fig.add_subplot(1, 2, 1, projection='3d')
    surf1 = ax1.plot_surface(X, Y, phi, cmap='viridis')
    ax1.set_title('Phase initiale avec aberrations')
    fig.colorbar(surf1, ax=ax1, shrink=0.5, aspect=10)

    # Graphique 2 : Phase corrigée sans aberrations
    ax2 = fig.add_subplot(1, 2, 2, projection='3d')
    surf2 = ax2.plot_surface(X, Y, corrected_phase, cmap='viridis')
    ax2.set_title('Phase corrigée sans aberrations')
    fig.colorbar(surf2, ax=ax2, shrink=0.5, aspect=10)

    # Ajustement des paramètres de la figure
    fig.tight_layout()

    plt.show()