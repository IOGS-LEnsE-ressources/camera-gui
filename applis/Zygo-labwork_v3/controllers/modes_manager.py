# -*- coding: utf-8 -*-
"""*modes_manager.py* file.

./controllers/modes_manager.py contains ModesManager class to manage the different modes of the application.

.. note:: LEnsE - Institut d'Optique - version 1.0

.. moduleauthor:: Julien VILLEMEJANE (PRAG LEnsE) <julien.villemejane@institutoptique.fr>
Creation : march/2025
"""
import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), ".")))
from enum import Enum
from views.main_structure import MainView
from views.main_menu import MainMenu
from models.dataset import DataSetModel
from controllers.acquisition_controller import AcquisitionController
from controllers.images_controller import ImagesController
from controllers.masks_controller import MasksController
from controllers.analyses_controller import AnalysesController
from controllers.help_controller import HelpController
from utils.initialization_parameters import read_default_parameters

class ModesManager:
    """
    Main modes manager.
    The different modes are loaded from the main menu file (menu/menu.txt)
    """

    def __init__(self, menu: MainMenu, widget: MainView, data_set: DataSetModel):
        """
        Default constructor.
        :param menu: Main menu of the application (MainMenu).
        :param widget: Main widget container of the application (MainView).
        :param dataset: Dataset of the application (DataSetModel).
        """
        # Menu
        self.main_menu: MainMenu = menu
        self.main_menu.menu_changed.connect(self.update_mode)
        self.default_parameters = read_default_parameters('config.txt')
        self.options_list = []
        # Main widget
        self.main_widget = widget
        # Data set
        self.data_set = data_set
        # Modes
        self.main_mode = 'first'
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
        if self.main_mode != 'first':
            nocam = 'nocam' in self.options_list
            nopiezo = 'nopiezo' in self.options_list

        self.options_list = []
        # Check Hardware
        if self.main_mode == 'first':
            if self.data_set.acquisition_mode.is_camera() is False:
                self.options_list.append('nocam')
            if self.data_set.acquisition_mode.is_piezo() is False:
                self.options_list.append('nopiezo')
            self.main_mode = ''
        else:
            # To avoid to check hardware each time
            if nocam:
                self.options_list.append('nocam')
            if nopiezo:
                self.options_list.append('nopiezo')

        # Check dataset
        if self.data_set.is_data_ready() is False:
            self.options_list.append('nodata')
        if self.data_set.images_sets.get_number_of_sets() == 0:
            self.options_list.append('noimages')
        if self.data_set.masks_sets.get_masks_number() == 0:
            self.options_list.append('nomask')
        if self.data_set.phase.is_analysis_ready() is False:
            self.options_list.append('noanalysis')
        # Update menu
        self.main_menu.update_options(self.options_list)

    def update_mode(self, event):
        """

        :return:
        """
        if self.main_mode == 'acquisition':
            self.mode_controller.stop_acquisition()
        self.main_mode = event
        self.main_widget.clear_all()
        self.update_menu()
        match self.main_mode:
            case 'acquisition':
                self.mode_controller = AcquisitionController(self)
            case 'images':
                self.mode_controller = ImagesController(self)
            case 'masks':
                self.mode_controller = MasksController(self)
            case 'analyses':
                self.mode_controller = AnalysesController(self)
            case 'help':
                self.mode_controller = HelpController(self)

        print(self.main_mode)


