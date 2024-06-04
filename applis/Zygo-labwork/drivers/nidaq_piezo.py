# -*- coding: utf-8 -*-
"""*nidaq_piezo.py* file.

*nidaq_piezo file that contains :class::NIDaqPiezo

This file is attached to a 1st year of engineer training labwork in photonics.
Subject : http://lense.institutoptique.fr/ressources/Annee1/TP_Photonique/S5-2324-PolyCI.pdf

More about the development of this interface :
https://iogs-lense-ressources.github.io/camera-gui/contents/applis/appli_Zygo_labwork.html

.. note:: LEnsE - Institut d'Optique - version 1.0

.. moduleauthor:: Julien VILLEMEJANE (PRAG LEnsE) <julien.villemejane@institutoptique.fr>
.. moduleauthor:: Dorian MENDES (Promo 2026) <dorian.mendes@institutoptique.fr>
"""

import nidaqmx
class CameraIds:
    """Class to communicate with a DAQ module from NI.

    """

    def __init__(self) -> None:
        """Initialize the object."""
        # Camera device
        pass