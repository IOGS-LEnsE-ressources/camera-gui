# -*- coding: utf-8 -*-
"""*modes_manager.py* file.

./controllers/modes_manager.py contains ModesManager class to manage the different modes of the application.

.. note:: LEnsE - Institut d'Optique - version 1.0

.. moduleauthor:: Julien VILLEMEJANE (PRAG LEnsE) <julien.villemejane@institutoptique.fr>
Creation : march/2025
"""
import sys, os
from enum import Enum
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), ".")))
from images_controller import *
from models import *
from views import *

class ModesManager:
    """
    Main modes manager.
    The different modes are loaded from the main menu file (menu/menu.txt)
    """

    def __init__(self, menu: MainMenu, widget: MainView, dataset: DataSetModel):
        """
        Default constructor.
        :param menu: Main menu of the application (MainMenu).
        :param widget: Main widget container of the application (MainView).
        :param dataset: Dataset of the application (DataSetModel).
        """
        # Menu
        self.main_menu = menu
        self.main_menu.menu_changed.connect(self.update_mode)
        self.options_list = []
        # Main widget
        self.main_widget = widget
        # Data set
        self.data_set = dataset
        # Modes
        self.main_mode = None
        self.mode_controller = None
        # Hardware
        self.piezo_connected = False
        self.camera_connected = False

        # First update
        self.update_menu()

    def update_menu(self):
        """

        :return:
        """
        self.options_list = []
        # Check Hardware
        if self.data_set.acquisition_mode.is_camera() is False:
            self.options_list.append('nocam')
        if self.data_set.acquisition_mode.is_piezo() is False:
            self.options_list.append('nopiezo')
        # Check dataset
        if self.data_set.is_data_ready() is False:
            self.options_list.append('nodata')
        if self.data_set.phase.is_analysis_ready() is False:
            self.options_list.append('noanalysis')


        # Update menu
        self.main_menu.update_options(self.options_list)
        pass

    def update_mode(self, event):
        """

        :return:
        """
        self.main_mode = event
        match self.main_mode:
            case 'images':
                self.mode_controller = ImagesController(self)

        print(self.main_mode)

    def create_enum_from_file(self, filename: str):
        with open(filename, "r", encoding="utf-8") as file:
            items = [line.strip() for line in file if line.strip()]  # Delete empty lines
        return Enum("VehicleType", {item: item for item in items})  # Creating enumeration



