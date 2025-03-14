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
from views import *
from modes_manager import ModesManager
from lensepy import load_dictionary, translate, dictionary
from lensepy.css import *
from lensepy.pyqt6 import *
from PyQt6.QtWidgets import (
    QWidget, QLabel, QPushButton,
    QVBoxLayout
)

class ImagesController:
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
        self.submenu = SubMenu('submenu_images')
        self.submenu.load_menu('../menu/images_menu.txt')

        print('ImagesController / Images Mode')

    def init_view(self):
        """
        Initializes the main structure of the interface.
        """
        self.main_widget.set_sub_menu_widget(self.submenu)



