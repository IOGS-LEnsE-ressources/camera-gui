# -*- coding: utf-8 -*-
"""*analyses_controller.py* file.

./controllers/analyses_controller.py contains AnalysesController class to manage "analyses" mode.

.. note:: LEnsE - Institut d'Optique - version 1.0

.. moduleauthor:: Julien VILLEMEJANE (PRAG LEnsE) <julien.villemejane@institutoptique.fr>
Creation : march/2025
"""
import sys, os
import threading, time
import numpy as np
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), ".")))
from views.main_structure import MainView
from views.sub_menu import SubMenu
from views.images_display_view import ImagesDisplayView
from views.html_view import HTMLView
from views.analyses_options_view import AnalysesOptionsView
from views.surface_2D_view import Surface2DView
from lensepy import load_dictionary, translate, dictionary
from models.phase import process_statistics_surface
from lensepy.css import *
from lensepy.pyqt6 import *
from PyQt6.QtWidgets import (
    QWidget,
    QFileDialog
)
from models.zernike_coefficients import Zernike
from utils.dataset_utils import generate_images_grid, DataSetState

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from controllers.modes_manager import ModesManager
    from models.dataset import DataSetModel
    from models.phase import PhaseModel

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
        self.phase: "PhaseModel"= self.manager.phase
        self.zernike_coeffs: Zernike = Zernike(self.phase)
        self.main_widget: MainView = self.manager.main_widget
        self.images_loaded = (self.data_set.images_sets.get_number_of_sets() >= 1)
        self.masks_loaded = (len(self.data_set.get_masks_list()) >= 1)
        self.tilt_possible = False
        # Graphical elements
        self.top_left_widget = ImagesDisplayView()     # Display first image of a set
        self.top_right_widget = Surface2DView('Wrapped Phase')              # Display 2D. Default.
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
        if self.phase.get_wrapped_phase() is None:
            time.sleep(0.3)
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
        self.main_widget.set_options_widget(self.options1_widget)
        self.options1_widget.analyses_changed.connect(self.analyses_changed)
        # Update grid of images
        images = self.data_set.get_images_sets(1)
        mask = self.data_set.get_global_mask()
        g_images = images[0]*mask
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
        if self.zernike_coeffs.get_coeff_counter() > 3:
            self.submenu.set_button_enabled(3, True)
        # Activate submenu
        match submode:
            case 'wrappedphase_analyses':
                self.submenu.set_activated(1)
            case 'unwrappedphase_analyses':
                self.submenu.set_activated(1)
                self.submenu.set_activated(2)
            case 'correctedphase_analyses':
                self.submenu.set_activated(1)
                self.submenu.set_activated(2)
                self.submenu.set_activated(3)

    def update_submenu(self, event):
        """
        Update data and views when the submenu is clicked.
        :param event: Sub menu click.
        """
        # Update view
        self.update_submenu_view(event)
        # Update Action
        self.options1_widget.hide_correction()
        match event:
            case 'wrappedphase_analyses':
                self.main_widget.clear_bot_right()
                self.bot_right_widget = HTMLView()
                if __name__ == "__main__":
                    self.bot_right_widget.set_url('../docs/html/analyses.html', '../docs/html/styles.css')
                else:
                    self.bot_right_widget.set_url('docs/html/analyses.html', 'docs/html/styles.css')
                self.main_widget.set_bot_right_widget(self.bot_right_widget)
                ## Test 2D or 3D ??
                wrapped = self.phase.get_wrapped_phase()
                wrapped_array = wrapped.filled(np.nan)
                # Display wrapped in 2D
                self.top_right_widget = Surface2DView('Wrapped Phase')
                self.main_widget.set_top_right_widget(self.top_right_widget)
                self.top_right_widget.set_array(wrapped_array)
                self.options1_widget.erase_pv_rms()

            case 'unwrappedphase_analyses':
                ## Test 2D or 3D ??
                wrapped = self.phase.get_wrapped_phase()
                wrapped_array = wrapped.filled(np.nan)
                # Display wrapped in 2D
                self.top_right_widget = Surface2DView('Wrapped Phase')
                self.main_widget.set_top_right_widget(self.top_right_widget)
                self.top_right_widget.set_array(wrapped_array)
                ## Test 2D or 3D ??
                self.display_2D_unwrapped()

            case 'correctedphase_analyses':
                self.display_2D_unwrapped()
                # Display corrected in 2D in the top right area
                self.display_2D_correction()
                self.options1_widget.show_correction()

    def display_2D_unwrapped(self):
        """
        Display unwrapped phase in 2D at the bottom right corner.
        """
        unwrapped = self.phase.get_unwrapped_phase()
        unwrapped_array = unwrapped.filled(np.nan)
        # Display unwrapped and corrected in 2D
        self.main_widget.clear_bot_right()
        self.bot_right_widget = Surface2DView('Unwrapped Phase')
        self.main_widget.set_bot_right_widget(self.bot_right_widget)
        self.bot_right_widget.set_array(unwrapped_array)
        pv, rms = process_statistics_surface(unwrapped)
        self.options1_widget.set_pv_uncorrected(pv, '\u03BB')
        self.options1_widget.set_rms_uncorrected(rms, '\u03BB')
        if self.tilt_possible:
            self.options1_widget.set_enable_tilt(True)
            self.options1_widget.set_enable_range(True)
        else:
            self.main_widget.clear_bot_right()
            self.bot_right_widget = HTMLView()
            if __name__ == "__main__":
                self.bot_right_widget.set_url('../docs/html/analyses.html', '../docs/html/styles.css')
            else:
                self.bot_right_widget.set_url('docs/html/analyses.html', 'docs/html/styles.css')
            self.main_widget.set_bot_right_widget(self.bot_right_widget)

    def display_2D_correction(self):
        """
        Display correction depending on tilt checkbox value.
        """
        self.main_widget.clear_top_right()
        self.top_right_widget = Surface2DView('Corrected Phase')
        self.main_widget.set_top_right_widget(self.top_right_widget)
        ## TO DO : update colorbar depending on the max range of TOP and BOT right area.
        unwrapped = self.phase.get_unwrapped_phase()
        unwrapped_array = unwrapped.filled(np.nan)

        # Test if tilt !
        if self.options1_widget.is_tilt_checked():
            _, corrected = self.zernike_coeffs.process_surface_correction(['piston','tilt'])
        else:
            corrected = unwrapped
        corrected_array = corrected.filled(np.nan)
        self.top_right_widget.set_array(corrected_array)
        #range = self.bot_right_widget.get_z_range()
        #self.top_right_widget.set_z_range(range)
        self.options1_widget.erase_pv_rms()
        pv, rms = process_statistics_surface(corrected_array)
        self.options1_widget.set_pv_corrected(pv, '\u03BB')
        self.options1_widget.set_rms_corrected(rms, '\u03BB')
        pv, rms = process_statistics_surface(unwrapped_array)
        self.options1_widget.set_pv_uncorrected(pv, '\u03BB')
        self.options1_widget.set_rms_uncorrected(rms, '\u03BB')

    def analyses_changed(self, event):
        """
        Update controller data and views when options changed.
        :param event: Signal that triggers the event.
        """
        print(event)
        change = event.split(',')
        if change[0] == 'tilt':
            self.display_2D_correction()
        if change[0] == 'wedge':
            if change[1].isnumeric():
                print(float(change[1]))

    def thread_wrapped_phase_calculation(self, set_number: int=1):
        """
        Thread to calculate wrapped phase from 5 images.
        :param set_number: Number of the set to process.
        """
        # TO DO : select the good set of images if multiple acquisition
        k = 0
        if self.data_set.is_data_ready():
            self.phase.prepare_data()
            # Process Phase
            self.phase.process_wrapped_phase()
            # End of process
            thread = threading.Thread(target=self.thread_unwrapped_phase_calculation, args=(set_number,))
            thread.start()

    def thread_unwrapped_phase_calculation(self, set_number: int=1):
        """
        Thread to calculate unwrapped phase from the wrapped phase.
        :param set_number: Number of the set to process.
        """
        if self.data_set.is_data_ready() and self.data_set.data_set_state == DataSetState.WRAPPED:
            # Process Phase
            self.phase.process_unwrapped_phase()
            # End of process
            self.update_submenu('')
            # Start Zernike coefficients process
            thread = threading.Thread(target=self.thread_zernike_calculation)
            thread.start()

    def thread_zernike_calculation(self):
        """Process Zernike coefficients for correction."""
        counter = self.zernike_coeffs.get_coeff_counter()
        max_order = 3 # case of tilt only
        if counter == 0:
            if self.zernike_coeffs.set_phase(self.phase):
                time.sleep(0.05)
        if counter == 3:
            # Tilt OK
            self.tilt_possible = True
            self.submenu.set_button_enabled(3, True)
        self.zernike_coeffs.process_zernike_coefficient(counter)
        self.zernike_coeffs.inc_coeff_counter()
        time.sleep(0.01)

        if counter+1 <= max_order:
            thread = threading.Thread(target=self.thread_zernike_calculation)
            time.sleep(0.1)
            thread.start()


if __name__ == "__main__":
    from zygo_lab_app import ZygoApp
    from PyQt6.QtWidgets import QApplication
    from controllers.modes_manager import ModesManager
    from views.main_menu import MainMenu
    from models.dataset import DataSetModel
    from models.phase import PhaseModel

    app = QApplication(sys.argv)
    m_app = ZygoApp()
    data_set = DataSetModel()
    m_app.data_set = data_set
    m_app.phase = PhaseModel(m_app.data_set)
    m_app.main_widget = MainView()
    m_app.main_menu = MainMenu()
    m_app.main_menu.load_menu('')
    manager = ModesManager(m_app)
    # Update data
    manager.data_set.load_images_set_from_file("../_data/test3.mat")
    manager.data_set.load_mask_from_file("../_data/test3.mat")

    # Test controller
    manager.mode_controller = AnalysesController(manager)
    m_app.main_widget.showMaximized()
    sys.exit(app.exec())