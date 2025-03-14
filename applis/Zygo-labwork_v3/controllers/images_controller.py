# -*- coding: utf-8 -*-
"""*images_controller.py* file.

./controllers/images_controller.py contains ImagesController class to manage "images" mode.

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
    QVBoxLayout,
    QMessageBox, QFileDialog, QDialog
)
from modes_manager import ModesManager
from utils import *

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
        self.images_loaded = (self.manager.data_set.images_sets.get_number_of_sets() >= 1)
        self.masks_loaded = (len(self.manager.data_set.get_masks_list()) >= 1)
        # Graphical elements
        self.top_left_widget = ImagesDisplayView()        # Display first image of a set
        self.top_right_widget = ImagesDisplayView()       # Display grid of images
        self.bot_right_widget = QWidget()       # HTML Help on images
        # Submenu
        self.submenu = SubMenu('submenu_images')
        self.submenu.load_menu('menu/images_menu.txt')
        self.submenu.menu_changed.connect(self.update_submenu)
        # Option 1
        # Option 2

        #Init view
        self.init_view()
        print('ImagesController / Images Mode')

    def init_view(self):
        """
        Initializes the main structure of the interface.
        """
        self.main_widget.set_sub_menu_widget(self.submenu)
        self.main_widget.set_top_left_widget(self.top_left_widget)
        self.main_widget.set_top_right_widget(self.top_right_widget)
        # Images loaded ?
        if self.images_loaded:
            # Display first image in top left
            images = self.manager.data_set.get_images_sets(1)
            self.top_left_widget.set_image_from_array(images[0], 'First Image')
        # Update menu
        self.update_submenu_view("")

    def update_submenu_view(self, submode):
        """

        :param submode:
        :return:
        """
        ## Erase enabled list for buttons
        self.submenu.inactive_buttons()
        for k in range(len(self.submenu.buttons_list)):
            self.submenu.set_button_enabled(k + 1, False)
        self.submenu.set_button_enabled(1, True)
        ## Activate button depending on data
        # Images loaded ?
        if self.images_loaded:
            self.submenu.set_button_enabled(2, True)
        # Data acquired ? Saving images is ok
        ### TO DO
        ## Update menu
        match submode:
            case 'open_images':
                self.submenu.set_activated(1)
            case 'display_images':
                self.submenu.set_activated(2)

    def update_submenu(self, event):
        """

        :param event:
        :return:
        """
        # Update view
        self.update_submenu_view(event)
        # Update Action
        print(event)
        match event:
            case 'open_images':
                self.open_mat_file()
            case 'display_images':
                # Display first image in top left
                images = self.manager.data_set.get_images_sets(1)
                self.top_left_widget.set_image_from_array(images[0])
            case 'save_images':
                pass

    def open_mat_file(self):
        """Action performed when a MAT file has to be loaded."""
        file_dialog = QFileDialog()
        # Check default_path in default_parameters !

        default_path = os.path.expanduser(".") + '/_data/'
        file_path, _ = file_dialog.getOpenFileName(self.main_widget, translate('dialog_open_image'),
                                                   default_path, "Matlab (*.mat)")
        if file_path != '':
            self.images_loaded = self.manager.data_set.images_sets.load_images_set_from_file(file_path)
            if self.images_loaded is False:
                msg = "No images in the files or bad format of data."
                message_box("Warning - No Images Loaded", msg)
            else:
                self.masks_loaded = self.manager.data_set.masks_sets.load_mask_from_file(file_path)
                if self.masks_loaded is False:
                    msg = "No masks in the files."
                    message_box("Warning - No Mask Loaded", msg)
        else:
            msg = "No Image File was loaded..."
            message_box("Warning - No File Loaded", msg)
            self.update_submenu("")
        if self.images_loaded:
            # Display images
            self.update_submenu("display_images")
            pass
