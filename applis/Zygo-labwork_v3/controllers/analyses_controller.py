# -*- coding: utf-8 -*-
"""*analyses_controller.py* file.

./controllers/analyses_controller.py contains AnalysesController class to manage "analyses" mode.

.. note:: LEnsE - Institut d'Optique - version 1.0

.. moduleauthor:: Julien VILLEMEJANE (PRAG LEnsE) <julien.villemejane@institutoptique.fr>
Creation : march/2025
"""
import sys, os
import threading
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), ".")))
from views.main_structure import MainView
from views.sub_menu import SubMenu
from views.images_display_view import ImagesDisplayView
from views.html_view import HTMLView
from views.analyses_options_view import AnalysesOptionsView
from views.surface_2D_view import Surface2DView
from lensepy import load_dictionary, translate, dictionary
from lensepy.css import *
from lensepy.pyqt6 import *
from PyQt6.QtWidgets import (
    QWidget,
    QFileDialog
)
from models.dataset import DataSetModel
from utils.dataset_utils import generate_images_grid, DataSetState

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from controllers.modes_manager import ModesManager

class AnalysesController:
    """
    Analyses mode manager.
    """

    def __init__(self, manager: "ModesManager"):
        """
        Default constructor.
        :param manager: Main manager of the application (ModesManager).
        """
        self.manager: "ModesManager" = manager
        self.data_set: DataSetModel = self.manager.data_set
        self.main_widget: MainView = self.manager.main_widget
        self.images_loaded = (self.data_set.images_sets.get_number_of_sets() >= 1)
        self.masks_loaded = (len(self.data_set.get_masks_list()) >= 1)
        # Graphical elements
        self.top_left_widget = ImagesDisplayView()     # Display first image of a set
        self.top_right_widget = Surface2DView()              # Display 2D. Default.
        self.bot_right_widget = HTMLView()             # HTML Help on analyses ?
        # Submenu
        self.submenu = SubMenu(translate('submenu_analyses'))
        if __name__ == "__main__":
            self.submenu.load_menu('../menu/analyses_menu.txt')
        else:
            self.submenu.load_menu('menu/analyses_menu.txt')
        self.submenu.menu_changed.connect(self.update_submenu)
        # Option 1
        self.options1_widget = AnalysesOptionsView()        # Analyses Options
        # Option 2
        self.options2_widget = QWidget()        # ??

        # Update menu and view
        self.update_submenu_view("")
        self.init_view()
        # Start Analyses
        ## Where to find set_number ?
        set_number = 1
        thread = threading.Thread(target=self.thread_wrapped_phase_calculation, args=(set_number,))
        thread.start()

    def init_view(self):
        """
        Initializes the main structure of the interface.
        """
        self.main_widget.clear_all()
        self.main_widget.set_sub_menu_widget(self.submenu)
        self.main_widget.set_top_left_widget(self.top_left_widget)
        self.main_widget.set_top_right_widget(self.top_right_widget)
        if __name__ == "__main__":
            self.bot_right_widget.set_url('../docs/html/analyses.html', '../docs/html/styles.css')
        else:
            self.bot_right_widget.set_url('docs/html/analyses.html', 'docs/html/styles.css')
        self.main_widget.set_bot_right_widget(self.bot_right_widget)
        self.main_widget.set_options1_widget(self.options1_widget)
        # Update grid of images
        images = self.data_set.get_images_sets(1)
        g_images = generate_images_grid(images)
        self.top_left_widget.set_image_from_array(g_images)

    def update_submenu_view(self, submode: str):
        """
        Update the view of the submenu to display new options.
        :param submode: Submode name : [open_images, display_images, save_images]
        """
        self.manager.update_menu()
        ## Erase enabled list for buttons
        self.submenu.inactive_buttons()
        for k in range(len(self.submenu.buttons_list)):
            self.submenu.set_button_enabled(k + 1, False)
        ## Activate button depending on data
        if self.data_set.data_set_state == DataSetState.WRAPPED:
            self.submenu.set_button_enabled(1, True)
        if self.data_set.data_set_state == DataSetState.UNWRAPPED:
            self.submenu.set_button_enabled(1, True)
            self.submenu.set_button_enabled(2, True)

    def update_submenu(self, event):
        """
        Update data and views when the submenu is clicked.
        :param event: Sub menu click.
        """
        # Update view
        self.update_submenu_view(event)
        # Update Action
        match event:
            case 'wrappedphase_analyses':
                ## Test 2D or 3D ??
                # Display wrapped in 2D
                self.top_right_widget = Surface2DView()
                self.main_widget.set_top_right_widget(self.top_right_widget)
                wrapped = self.data_set.phase.get_wrapped_phase()
                self.top_right_widget.set_array(wrapped)
                # Activate submenu
                self.submenu.set_activated(1)

            case 'unwrappedphase_analyses':
                ## Test 2D or 3D ??
                # Display unwrapped in 2D
                self.top_right_widget = Surface2DView()
                self.main_widget.set_top_right_widget(self.top_right_widget)
                unwrapped = self.data_set.phase.get_unwrapped_phase()
                self.top_right_widget.set_array(unwrapped)
                # Activate submenu
                self.submenu.set_activated(1)
                self.submenu.set_activated(2)

    def thread_wrapped_phase_calculation(self, set_number: int=1):
        """
        Thread to calculate wrapped phase from 5 images.
        :param set_number: Number of the set to process.
        """
        # TO DO : select the good set of images if multiple acquisition
        k = 0
        if self.data_set.is_data_ready():
            self.data_set.phase.prepare_data()
            # Process Phase
            self.data_set.phase.process_wrapped_phase()
            # End of process
            wrapped = self.data_set.phase.get_wrapped_phase()
            # Update wrapped ?
            thread = threading.Thread(target=self.thread_unwrapped_phase_calculation, args=(set_number,))
            thread.start()

    def thread_unwrapped_phase_calculation(self, set_number: int=1):
        """
        Thread to calculate unwrapped phase from the wrapped phase.
        :param set_number: Number of the set to process.
        """
        if self.data_set.is_data_ready() and self.data_set.data_set_state == DataSetState.WRAPPED:
            # Process Phase
            self.data_set.phase.process_unwrapped_phase()
            # End of process
            unwrapped = self.data_set.phase.get_unwrapped_phase()
            # Update wrapped ?
            self.update_submenu('')
            # Start Zernike coefficients process
            ## TO DO


if __name__ == "__main__":
    from PyQt6.QtWidgets import QApplication
    from controllers.modes_manager import ModesManager
    from views.main_menu import MainMenu

    app = QApplication(sys.argv)
    widget = MainView()
    menu = MainMenu()
    menu.load_menu('')
    widget.set_main_menu(menu)
    data_set = DataSetModel()
    manager = ModesManager(menu, widget, data_set)
    # Update data
    manager.data_set.load_images_set_from_file("../_data/test3.mat")
    manager.data_set.load_mask_from_file("../_data/test3.mat")

    # Test controller
    manager.mode_controller = AnalysesController(manager)
    widget.showMaximized()
    sys.exit(app.exec())