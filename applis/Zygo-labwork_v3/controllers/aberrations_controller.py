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
from views.bar_graph_view import BarGraphView
from lensepy import load_dictionary, translate, dictionary
from models.phase import process_statistics_surface
from views.aberrations_options_view import AberrationsOptionsView
from views.aberrations_start_view import AberrationsStartView
from lensepy.css import *
from PyQt6.QtWidgets import (
    QWidget
)
from models.zernike_coefficients import Zernike, aberrations_type, aberrations_list
from utils.dataset_utils import generate_images_grid, DataSetState

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from controllers.modes_manager import ModesManager
    from models.dataset import DataSetModel
    from models.phase import PhaseModel

class AberrationsController:
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
        self.sub_mode = ''
        self.corrected_aberrations_list = ['piston','tilt','defocus']
        self.colors = [None] * (self.zernike_coeffs.max_order + 1)
        # Graphical elements
        self.top_left_widget = QWidget()        # ??
        self.top_right_widget = Surface2DView('Unwrapped Phase')        # ??
        self.bot_right_widget = HTMLView()             # HTML Help on analyses ?
        # Submenu
        self.submenu = SubMenu(translate('submenu_aberrations'))
        if __name__ == "__main__":
            self.submenu.load_menu('../menu/aberrations_menu.txt')
        else:
            self.submenu.load_menu('menu/aberrations_menu.txt')
        self.submenu.menu_changed.connect(self.update_submenu)
        # Option 1
        self.options1_widget = AberrationsStartView(self)        # ??
        # Option 2
        self.options2_widget = QWidget()        # ??

        # Update menu and view
        self.update_submenu_view("")
        self.init_view()


    def init_view(self):
        """
        Initializes the main structure of the interface.
        """
        self.main_widget.clear_all()
        self.main_widget.set_sub_menu_widget(self.submenu)
        self.main_widget.set_top_left_widget(self.top_left_widget)
        self.main_widget.set_top_right_widget(self.top_right_widget)
        if __name__ == "__main__":
            self.bot_right_widget.set_url('../docs/html/aberrations.html', '../docs/html/styles.css')
        else:
            self.bot_right_widget.set_url('docs/html/aberrations.html', 'docs/html/styles.css')
        self.main_widget.set_bot_right_widget(self.bot_right_widget)
        self.main_widget.set_options_widget(self.options1_widget)

        ## Test 2D or 3D ??
        unwrapped = self.phase.get_unwrapped_phase()
        unwrapped_array = unwrapped.filled(np.nan)
        # Display wrapped in 2D
        self.top_right_widget.set_array(unwrapped_array)

        # Process Zernike coefficients
        for k in range(self.zernike_coeffs.max_order + 1):
            self.zernike_coeffs.process_zernike_coefficient(k)
            val_progression = int((k + 1) * 100 / self.zernike_coeffs.max_order)
            self.options1_widget.update_progress_bar(val_progression)
            self.submenu.set_button_enabled(1, True)
            self.submenu.set_button_enabled(2, True)
            self.submenu.set_button_enabled(4, True)
            self.submenu.set_button_enabled(6, True)

    def update_submenu_view(self, submode: str):
        """
        Update the view of the submenu to display new options.
        :param submode: Submode name : [open_images, display_images, save_images]
        """
        self.manager.update_menu()
        self.sub_mode = submode
        ## Erase enabled list for buttons
        self.submenu.inactive_buttons()
        # Activate submenu
        match submode:
            case '':
                for k in range(len(self.submenu.buttons_list)):
                    self.submenu.set_button_enabled(k + 1, False)
            case 'Zernikecoefficients_aberrations':
                self.submenu.set_activated(1)
            case 'Seidelcoefficients_aberrations':
                self.submenu.set_activated(2)
            case 'coefficientscorrection_aberrations':
                self.submenu.set_activated(4)
            case 'aberrationsanalyses_aberrations':
                self.submenu.set_activated(6)

    def update_submenu(self, event):
        """
        Update data and views when the submenu is clicked.
        :param event: Sub menu click.
        """
        # Update view
        self.update_submenu_view(event)
        # Update Action
        self.main_widget.clear_bot_right()
        self.main_widget.clear_options()
        # Update Action
        match event:
            case 'Zernikecoefficients_aberrations':
                self.options1_widget = AberrationsOptionsView()
                self.options1_widget.aberrations_changed.connect(self.aberration_changed)
                self.main_widget.set_options1_widget(self.options1_widget)
                self.display_2D_ab_corrected()
                self.bot_right_widget = HTMLView()
                if __name__ == "__main__":
                    self.bot_right_widget.set_url('../docs/html/aberrations.html', '../docs/html/styles.css')
                else:
                    self.bot_right_widget.set_url('docs/html/aberrations.html', 'docs/html/styles.css')
                self.main_widget.set_bot_right_widget(self.bot_right_widget)
                self.display_bar_graph_coeff()


            case 'Seidelcoefficients_aberrations':
                self.submenu.set_activated(2)
            case 'coefficientscorrection_aberrations':
                self.submenu.set_activated(4)
            case 'aberrationsanalyses_aberrations':
                self.submenu.set_activated(6)

    def display_bar_graph_coeff(self, disp_correct: bool = False, first: bool = False):
        """
        Display the Zernike coefficients in a bargraph, in the top left area.
        :param disp_correct: True if all the coefficients must be displayed.
        :param first: True if only the first coefficients (piston, tilt and defocus) must be set to 0.
        """
        self.main_widget.clear_top_left()
        # Create bargraph
        self.top_left_widget = BarGraphView()
        self.main_widget.set_top_left_widget(self.top_left_widget)
        max_order = self.zernike_coeffs.max_order
        x_axis = np.arange(max_order + 1)
        self.update_color_aberrations()
        # Force to 0 corrected coefficients
        coeffs_disp = self.zernike_coeffs.coeff_list.copy()
        if disp_correct:
            for jj, aberration in enumerate(self.corrected_aberrations_list):
                for k in aberrations_type[aberration]:
                    coeffs_disp[k] = 0
        if first:
            options = ['piston','tilt','defocus']
            for jj, aberration in enumerate(options):
                for k in aberrations_type[aberration]:
                    coeffs_disp[k] = 0

        y_axis = np.array(coeffs_disp)
        self.top_left_widget.set_data(x_axis, y_axis, color_x=self.colors)

    def display_2D_ab_corrected(self):
        """
        Display tilt and piston corrected phase in the top right corner.
        """
        self.main_widget.clear_top_right()
        # Display wrapped in 2D
        self.top_right_widget = Surface2DView('Tilt and Piston Corrected Phase')
        self.main_widget.set_top_right_widget(self.top_right_widget)
        # Correction of the phase with tilt and piston
        wedge_factor = self.phase.get_wedge_factor()
        _, corrected = self.zernike_coeffs.process_surface_correction(self.corrected_aberrations_list)
        unwrapped_array = corrected * wedge_factor
        unwrapped_array = unwrapped_array.filled(np.nan)
        # Statistics
        self.top_right_widget.set_array(unwrapped_array)
        pv, rms = process_statistics_surface(unwrapped_array)
        self.options1_widget.set_pv_uncorrected(pv, '\u03BB')
        self.options1_widget.set_rms_uncorrected(rms, '\u03BB')

    def update_color_aberrations(self):
        """
        Return a list of color to apply on Zernike bar graph.
        Orange : corrected value, blue : order 1, ...
        """
        self.colors = [None] * (self.zernike_coeffs.max_order + 1)
        #
        for k, ab_type in enumerate(aberrations_list):
            if '3' in ab_type:
                for jj in aberrations_type[ab_type]:
                    self.colors[jj] = '#0f4d7a'
            elif '5' in ab_type:
                for jj in aberrations_type[ab_type]:
                    self.colors[jj] = '#1567a5'
            elif '7' in ab_type:
                for jj in aberrations_type[ab_type]:
                    self.colors[jj] = '#1a82cf'
            elif '9' in ab_type:
                for jj in aberrations_type[ab_type]:
                    self.colors[jj] = '#1f9cfa'
            else:
                for jj in aberrations_type[ab_type]:
                    self.colors[jj] = '#051725'

        for jj, aberration in enumerate(self.corrected_aberrations_list):
            for k in aberrations_type[aberration]:
                self.colors[k] = ORANGE_IOGS

        if self.colors[k] is None:
            self.colors[k] = BLUE_IOGS

    def aberration_changed(self, event):
        """
        Action to perform when an option in the aberrations options view changed.
        """
        if 'wedge' in event:
            d = event.split(',')
            wedge_factor = float(d[1])
            print(wedge_factor)
            # Display 2D correction with new wegde factor

        elif 'correct_disp' in event:
            if 'True' in event:
                self.display_bar_graph_coeff(disp_correct=True)
            else:
                self.display_bar_graph_coeff(disp_correct=False)

        elif 'correct_first' in event:
            if 'True' in event:
                self.display_bar_graph_coeff(first=True)
            else:
                self.display_bar_graph_coeff(first=False)


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
    manager.phase.prepare_data()
    manager.phase.process_wrapped_phase()
    manager.phase.process_unwrapped_phase()

    # Test controller
    manager.mode_controller = AberrationsController(manager)
    m_app.main_widget.showMaximized()
    sys.exit(app.exec())