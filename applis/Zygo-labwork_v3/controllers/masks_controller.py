# -*- coding: utf-8 -*-
"""*masks_controller.py* file.

./controllers/masks_controller.py contains MasksController class to manage "masks" mode.

.. note:: LEnsE - Institut d'Optique - version 1.0

.. moduleauthor:: Julien VILLEMEJANE (PRAG LEnsE) <julien.villemejane@institutoptique.fr>
Creation : march/2025
"""
import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), ".")))
from views import *
from lensepy import load_dictionary, translate, dictionary
from lensepy.css import *
from lensepy.pyqt6 import *
from PyQt6.QtWidgets import (
    QWidget, QLabel, QPushButton,
    QVBoxLayout
)

from modes_manager import ModesManager

class MasksController:
    """
    Images mode manager.
    """

    def __init__(self, manager: ModesManager):
        """
        Default constructor.
        :param manager: Main manager of the application (ModeManager).
        """
        self.manager: ModesManager = manager
        self.main_widget: MainView = self.manager.main_widget
        # Graphical elements
        self.top_left_widget = QWidget()        # Display first image of a set
        self.top_right_widget = QWidget()       # Display grid of images
        self.bot_right_widget = QWidget()       # HTML Help on images
        self.submenu = SubMenu('submenu_masks')
        self.submenu.load_menu('menu/masks_menu.txt')

        self.init_view()
        print('MasksController / Masks Mode')

    def init_view(self):
        """
        Initializes the main structure of the interface.
        """
        self.main_widget.set_sub_menu_widget(self.submenu)



