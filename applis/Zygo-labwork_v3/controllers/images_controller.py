# -*- coding: utf-8 -*-
"""*modes_manager.py* file.

./controllers/images_controller.py contains ImagesController class to manage "images" mode.

.. note:: LEnsE - Institut d'Optique - version 1.0

.. moduleauthor:: Julien VILLEMEJANE (PRAG LEnsE) <julien.villemejane@institutoptique.fr>
Creation : march/2025
"""
import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), ".")))


class ImagesController:
    """
    Images mode manager.
    """

    def __init__(self, manager):
        """
        Default constructor.
        :param manager: Main manager of the application (ModeManager).
        """
        self.manager = manager
        self.main_widget = self.manager.main_widget

        print('ImagesController / Images Mode')

