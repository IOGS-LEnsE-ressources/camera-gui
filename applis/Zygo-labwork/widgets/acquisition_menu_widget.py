# -*- coding: utf-8 -*-
"""*acquisition_menu_widget.py* file.

.. note:: LEnsE - Institut d'Optique - version 1.0

.. moduleauthor:: Julien VILLEMEJANE (PRAG LEnsE) <julien.villemejane@institutoptique.fr>
.. moduleauthor:: Dorian MENDES (Promo 2026) <dorian.mendes@institutoptique.fr>
"""

import sys, os
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
sys.path.append(parent_dir)

from PyQt6.QtWidgets import (
    QMainWindow, QWidget,
    QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QComboBox, QPushButton, QCheckBox,
    QMessageBox
)
from PyQt6.QtCore import pyqtSignal, QTimer, Qt
from PyQt6.QtGui import QPixmap
import numpy as np
from scipy.interpolate import griddata

from lensepy import load_dictionary, translate
from lensepy.css import *

from process.unwrap import unwrap2D, suppression_bord
from process.acquisition_images import get_phase, check_alpha
from process.surface_statistics import statistique_surface

if __name__ == '__main__':
    from lineedit_bloc import LineEditBloc
else:
    from widgets.lineedit_bloc import LineEditBloc

PI = np.pi

# %% To add in lensepy library
# Styles
# ------
styleH1 = f"font-size:20px; padding:7px; color:{BLUE_IOGS}; font-weight: bold;"  # Added missing styleH1
styleH2 = f"font-size:15px; padding:7px; color:{BLUE_IOGS}; font-weight: bold;"
styleH3 = f"font-size:15px; padding:7px; color:{BLUE_IOGS};"
styleCheckbox = f"font-size: 12px; padding: 7px; color: {BLUE_IOGS}; font-weight: normal;"

# %% Params
BUTTON_HEIGHT = 30  # px

# %% Auxiliary widget
class RemoveFaultsWidget(QWidget):
    def __init__(self):
        super().__init__(parent=None)

        self.setStyleSheet(f"background-color: {ORANGE_IOGS};")
        self.layout = QVBoxLayout()

        self.master_widget = QWidget()
        self.master_layout = QVBoxLayout()
        
        self.label_title_remove_faults_menu = QLabel("Soustraitre les défauts")
        self.label_title_remove_faults_menu.setStyleSheet(styleH1)
        
        self.subwidget_faults = QWidget()
        self.sublayout_faults = QHBoxLayout()

        # First col
        # ---------
        self.subwidget_left = QWidget()
        self.sublayout_left = QVBoxLayout()

        self.checkbox_remove_tilt = QCheckBox("Retirer le tilt")
        self.checkbox_remove_tilt.setStyleSheet(styleCheckbox)

        self.checkbox_remove_defocus = QCheckBox("Retirer l'autofocus")
        self.checkbox_remove_defocus.setStyleSheet(styleCheckbox)

        self.checkbox_remove_spherical_aberration = QCheckBox("Retirer l'abération sphérique")
        self.checkbox_remove_spherical_aberration.setStyleSheet(styleCheckbox)
        
        self.sublayout_left.addWidget(self.checkbox_remove_tilt)
        self.sublayout_left.addWidget(self.checkbox_remove_defocus)
        self.sublayout_left.addWidget(self.checkbox_remove_spherical_aberration)
        self.sublayout_left.setContentsMargins(0, 0, 0, 0)
        self.subwidget_left.setLayout(self.sublayout_left)
        
        # Second col
        # ----------
        self.subwidget_right = QWidget()
        self.sublayout_right = QVBoxLayout()
        
        self.checkbox_remove_astigmatism = QCheckBox("Retirer l'astigmatisme")
        self.checkbox_remove_astigmatism.setStyleSheet(styleCheckbox)

        self.checkbox_remove_coma = QCheckBox("Retirer la coma")
        self.checkbox_remove_coma.setStyleSheet(styleCheckbox)


        self.sublayout_right.addWidget(self.checkbox_remove_astigmatism)
        self.sublayout_right.addWidget(self.checkbox_remove_coma)
        self.sublayout_right.setContentsMargins(0, 0, 0, 0)
        self.subwidget_right.setLayout(self.sublayout_right)
        
        # Combined
        # --------
        self.sublayout_faults.addWidget(self.subwidget_left)
        self.sublayout_faults.addWidget(self.subwidget_right)
        self.sublayout_faults.setContentsMargins(0, 0, 0, 0)
        self.subwidget_faults.setLayout(self.sublayout_faults)
        
        self.layout.addWidget(self.label_title_remove_faults_menu)
        self.layout.addWidget(self.subwidget_faults)

        self.master_widget.setLayout(self.layout)
        self.master_layout.addWidget(self.master_widget)
        self.setLayout(self.master_layout)

# %% Widget
class AcquisitionMenuWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent=None)

        self.parent = parent

        if self.parent is None or not hasattr(self.parent, 'wedge_factor'):
            self.wedge_factor = 1
        else:
                self.wedge_factor = self.parent.wedge_factor

        self.layout = QVBoxLayout()
        self.layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        self.master_widget = QWidget()
        self.master_layout = QVBoxLayout()
        self.master_widget.setStyleSheet("background-color: white;")
        
        # Title
        # -----
        self.label_title_acquisition_menu = QLabel("Acquisition")
        self.setStyleSheet(styleH1)
        
        # Subwidget to start acquisition
        # ------------------------------
        self.subwidget_start_acquisiton = QWidget()
        self.sublayout_start_acquisiton = QHBoxLayout()

        self.button_simple_acquisition = QPushButton("Acquisition unique")
        self.button_simple_acquisition.setStyleSheet(unactived_button)
        self.button_simple_acquisition.setFixedHeight(BUTTON_HEIGHT)
        self.button_simple_acquisition.clicked.connect(self.button_simple_acquisition_isClicked)

        self.button_repeated_acquisition = QPushButton("Acquisition répétée")
        self.button_repeated_acquisition.setStyleSheet(unactived_button)
        self.button_repeated_acquisition.setFixedHeight(BUTTON_HEIGHT)
        self.button_repeated_acquisition.clicked.connect(self.button_repeated_acquisition_isClicked)

        self.sublayout_start_acquisiton.addWidget(self.button_simple_acquisition)
        self.sublayout_start_acquisiton.addWidget(self.button_repeated_acquisition)
        self.sublayout_start_acquisiton.setContentsMargins(0, 0, 0, 0)
        self.subwidget_start_acquisiton.setLayout(self.sublayout_start_acquisiton)

        # Wedge factor entry
        #-------------------
        self.lineedit_wedge_factor = LineEditBloc("Wedge factor", txt=str(self.wedge_factor))
        self.lineedit_wedge_factor.keyPressEvent = self.wedge_factor_is_modified

        # Remove faults menu
        # ------------------
        self.submenu_remove_faults = RemoveFaultsWidget()

        # Subwidget to save acquisition
        # ------------------------------
        self.subwidget_save_acquisiton = QWidget()
        self.sublayout_save_acquisiton = QHBoxLayout()

        self.button_see_and_save_images = QPushButton("Voir et enregistrer les images")
        self.button_see_and_save_images.setStyleSheet(unactived_button)
        self.button_see_and_save_images.setFixedHeight(BUTTON_HEIGHT)
        self.button_see_and_save_images.clicked.connect(self.button_see_and_save_images_isClicked)

        self.button_save_phase = QPushButton("Enregistrer la phase")
        self.button_save_phase.setStyleSheet(unactived_button)
        self.button_save_phase.setFixedHeight(BUTTON_HEIGHT)
        self.button_save_phase.clicked.connect(self.button_save_phase_isClicked)

        self.sublayout_save_acquisiton.addWidget(self.button_see_and_save_images)
        self.sublayout_save_acquisiton.addWidget(self.button_save_phase)
        self.sublayout_save_acquisiton.setContentsMargins(0, 0, 0, 0)
        self.subwidget_save_acquisiton.setLayout(self.sublayout_save_acquisiton)
        
        # Add widgets to the layout
        # -------------------------
        self.layout.addWidget(self.label_title_acquisition_menu)
        self.layout.addWidget(self.lineedit_wedge_factor)
        self.layout.addWidget(self.subwidget_start_acquisiton)
        self.layout.addWidget(self.submenu_remove_faults)
        self.layout.addWidget(self.subwidget_save_acquisiton)

        self.master_widget.setLayout(self.layout)

        self.master_layout.addWidget(self.master_widget)
        self.setLayout(self.master_layout)

    def wedge_factor_is_modified(self, event):
        if (event.key() == Qt.Key.Key_Return) or (event.key() == Qt.Key.Key_Enter):
            try:
                self.wedge_factor = float(self.lineedit_wedge_factor.text())
                msg_box = QMessageBox()
                msg_box.setStyleSheet(styleH3)
                msg_box.information(self, "Information", "Le wedge factor a bien été modifié.")
            except ValueError:
                msg_box = QMessageBox()
                msg_box.setStyleSheet(styleH3)
                msg_box.warning(self, "Erreur", "Le wedge factor doit être un nombre réel.")

        elif event.key() == Qt.Key.Key_Escape:
            self.lineedit_wedge_factor.clearFocus()
        else:
            # Laissez le QLineEdit gérer les autres touches
            super().keyPressEvent(event)

    def button_simple_acquisition_isClicked(self):
        self.button_simple_acquisition.setStyleSheet(actived_button)
        print('button_simple_acquisition_isClicked')
        if self.parent is not None:
            try:
                mask = self.parent.mask
                if mask is None:
                    msg_box = QMessageBox()
                    msg_box.setStyleSheet(styleH3)
                    msg_box.warning(self, "Erreur", "Vous devez définir un masque.")
                    self.button_simple_acquisition.setStyleSheet(unactived_button)  
                    return None

                wrapped_phase, images = get_phase(self.parent, sigma_gaussian_filter=3)
                average_alpha, std_alpha = check_alpha(images)
                
                if average_alpha<86 or average_alpha>94 or std_alpha>8:
                    msg_box = QMessageBox()
                    msg_box.setStyleSheet(styleH3)
                    msg_box.warning(self, "Erreur", f"α={average_alpha} °: il vaut mieux reprendre la mesure ou attendre que le laser se stabilise.")
                    self.button_simple_acquisition.setStyleSheet(unactived_button)  
                    return None
                else:
                    unwrapped_phase = unwrap2D(wrapped_phase)[0]
                    unwrapped_phase = suppression_bord(unwrapped_phase, 3)
                    unwrapped_phase = unwrapped_phase - np.nanmean(unwrapped_phase)

                self.phase = unwrapped_phase/(2*PI)

                PV, RMS = statistique_surface(self.phase)
                
                array = np.array([
                    ['', 1, 2, 3, 4, 5, 'Moyenne'],
                    ['PV (λ)', round(PV, 4), np.nan, np.nan, np.nan, np.nan, round(PV, 4)],
                    ['RMS (λ)', round(RMS, 4), np.nan, np.nan, np.nan, np.nan, round(RMS, 4)]
                ])

                self.parent.results_menu_widget.array = array
                self.parent.results_menu_widget.table_results.update_table(array)

                self.display_phase_3d(self.phase)

            except Exception as e:
                print(f'Exception - button_simple_acquisition_isClicked {e}')
        self.button_simple_acquisition.setStyleSheet(unactived_button)

    

    def button_repeated_acquisition_isClicked(self):
        self.button_repeated_acquisition.setStyleSheet(actived_button)
        print('button_repeated_acquisition_isClicked')

        if self.parent is not None:
            try:
                mask = self.parent.mask
                if mask is None:
                    msg_box = QMessageBox()
                    msg_box.setStyleSheet(styleH3)
                    msg_box.warning(self, "Erreur", "Vous devez définir un masque.")
                    self.button_repeated_acquisition.setStyleSheet(unactived_button)  
                    return None

                all_PV = []
                all_RMS = []

                for i in range(5):
                    wrapped_phase, images = get_phase(self.parent, sigma_gaussian_filter=3)
                    average_alpha, std_alpha = check_alpha(images)
                    
                    if average_alpha<86 or average_alpha>94 or std_alpha>8:
                        msg_box = QMessageBox()
                        msg_box.setStyleSheet(styleH3)
                        msg_box.warning(self, "Erreur", f"α={average_alpha} °: il vaut mieux reprendre la mesure ou attendre que le laser se stabilise.")
                        self.button_repeated_acquisition.setStyleSheet(unactived_button)  
                        return None
                    else:
                        unwrapped_phase = unwrap2D(wrapped_phase)[0]
                        unwrapped_phase = suppression_bord(unwrapped_phase, 3)
                        unwrapped_phase = unwrapped_phase - np.nanmean(unwrapped_phase)

                    self.phase = unwrapped_phase/(2*PI)

                    PV, RMS = statistique_surface(self.phase)

                    all_PV.append(PV)
                    all_RMS.append(RMS)

                self.display_phase_3d(self.phase)
                    
                array = np.array([
                    ['', 1, 2, 3, 4, 5, 'Moyenne'],
                    ['PV (λ)', round(all_PV[0], 4), round(all_PV[1], 4), round(all_PV[2], 4), round(all_PV[3], 4), round(all_PV[4], 4), round(np.mean(all_PV), 4)],
                    ['RMS (λ)', round(all_RMS[0], 4), round(all_RMS[1], 4), round(all_RMS[2], 4), round(all_RMS[3], 4), round(all_RMS[4], 4), round(np.mean(all_RMS), 4)]
                ])

                self.parent.results_menu_widget.array = array
                self.parent.results_menu_widget.table_results.update_table(array)

                self.display_phase_3d(self.phase)

            except Exception as e:
                print(f'Exception - button_simple_acquisition_isClicked {e}')

        self.button_repeated_acquisition.setStyleSheet(unactived_button)
    
    def button_see_and_save_images_isClicked(self):
        self.button_see_and_save_images.setStyleSheet(actived_button)
        print('button_see_and_save_images_isClicked')
        self.button_see_and_save_images.setStyleSheet(unactived_button)

    def button_save_phase_isClicked(self):
        self.button_save_phase.setStyleSheet(actived_button)
        print('button_save_phase_isClicked')
        self.button_save_phase.setStyleSheet(unactived_button)

    def display_phase_3d(self, phase):
        import matplotlib.pyplot as plt
        not_nan_indices = np.where(~np.isnan(phase))

        values = phase[not_nan_indices]
        x = not_nan_indices[0]
        y = not_nan_indices[1]

        x_grid, y_grid = np.meshgrid(np.linspace(0, phase.shape[1], 300), np.linspace(0, phase.shape[0], 300))

        interpolated_values = griddata((x, y), values, (x_grid, y_grid), method='cubic')

        fig = plt.figure()
        ax = fig.add_subplot(111, projection='3d')

        x = np.arange(interpolated_values.shape[0])
        y = np.arange(interpolated_values.shape[1])
        x, y = np.meshgrid(x, y)

        ax.plot_surface(x, y, interpolated_values, cmap='magma')
        plt.show()

# %% Example
if __name__ == '__main__':
    from PyQt6.QtWidgets import QApplication
    from ids_peak import ids_peak

    class MyWindow(QMainWindow):
        def __init__(self):
            super().__init__()

            # Translation
            dictionary = {}
            # Load French dictionary
            # dictionary = load_dictionary('../lang/dict_FR.txt')
            # Load English dictionary
            dictionary = load_dictionary('../lang/dict_EN.txt')

            self.setWindowTitle(translate("window_title_main_menu_widget"))
            self.setGeometry(300, 300, 800, 200)

            self.central_widget = AcquisitionMenuWidget()
            self.setCentralWidget(self.central_widget)

        def closeEvent(self, event):
            """
            closeEvent redefinition. Use when the user clicks
            on the red cross to close the window
            """
            reply = QMessageBox.question(self, 'Quit', 'Do you really want to close ?',
                                         QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                                         QMessageBox.StandardButton.No)

            if reply == QMessageBox.StandardButton.Yes:
                event.accept()
            else:
                event.ignore()


    app = QApplication(sys.argv)
    main = MyWindow()
    main.show()
    sys.exit(app.exec())
