# -*- coding: utf-8 -*-
"""*zygo_lab_app.py* file.

*zygo_lab_app* file that contains :class::ZygoLabApp

This file is attached to a 1st year of engineer training labwork in photonics.
Subject : http://lense.institutoptique.fr/ressources/Annee1/TP_Photonique/S5-2324-PolyCI.pdf

More about the development of this interface :
https://iogs-lense-ressources.github.io/camera-gui/

.. note:: LEnsE - Institut d'Optique - version 1.0

.. moduleauthor:: Dorian MENDES (Promo 2026) <dorian.mendes@institutoptique.fr>
.. moduleauthor:: Julien VILLEMEJANE (PRAG LEnsE) <julien.villemejane@institutoptique.fr>

.. version:: 3.0
"""
import sys
from models import *
from utils import *

version_app = '3.0'


class ZygoApp:

    def __init__(self):
        """Constructor of the application."""
        self.images_set = ImagesModel()
        self.masks_set = MasksModel()


if __name__ == "__main__":
    print(f'Zygo App - Version {version_app}')
    zygo_app = ZygoApp()