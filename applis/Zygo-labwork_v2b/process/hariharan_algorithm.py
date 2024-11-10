# -*- coding: utf-8 -*-
"""*hariharan_algorithm.py* file.

This file is attached to a 1st year of engineer training labwork in photonics.

.. note:: LEnsE - Institut d'Optique - version 1.0

.. moduleauthor:: Dorian Mendes (Promo 2026) <dorian.mendes@institutoptique.fr>

"""

import numpy as np
from matplotlib import pyplot as plt

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


def display_wrapped_phase(wrapped_phase: np.ndarray):
    """Display a 3D surface."""
    # Array for displaying data on 3D projection
    x = np.arange(wrapped_phase.shape[1])
    y = np.arange(wrapped_phase.shape[0])
    X, Y = np.meshgrid(x, y)

    # Display of the surface
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    # [400:1200, 750:1900]
    surface = ax.plot_surface(X, Y, wrapped_phase,
                              cmap='magma')
    ax.set_title('Unwrapped surface')
    cbar = fig.colorbar(surface, ax=ax, shrink=0.5, aspect=10)
    cbar.set_label(r'Default magnitude ($\lambda$)')
    plt.show()


