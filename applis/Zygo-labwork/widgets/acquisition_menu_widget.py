# -*- coding: utf-8 -*-
"""*acquisition_menu_widget.py* file.

.. note:: LEnsE - Institut d'Optique - version 1.0

.. moduleauthor:: Julien VILLEMEJANE (PRAG LEnsE) <julien.villemejane@institutoptique.fr>
.. moduleauthor:: Dorian MENDES (Promo 2026) <dorian.mendes@institutoptique.fr>
"""

import sys
from PyQt6.QtWidgets import (
    QMainWindow, QWidget,
    QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QComboBox, QPushButton, QCheckBox,
    QMessageBox
)
from PyQt6.QtCore import pyqtSignal, QTimer, Qt
from PyQt6.QtGui import QPixmap
import numpy as np
from lensepy import load_dictionary, translate
from lensepy.css import *

from lineedit_bloc import LineEditBloc

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
        
        self.label_title_remove_faults_menu = QLabel(translate('label_title_remove_faults_menu'))
        self.label_title_remove_faults_menu.setStyleSheet(styleH1)
        
        self.subwidget_faults = QWidget()
        self.sublayout_faults = QHBoxLayout()

        # First col
        # ---------
        self.subwidget_left = QWidget()
        self.sublayout_left = QVBoxLayout()

        self.checkbox_remove_tilt = QCheckBox(translate('checkbox_remove_tilt'))
        self.checkbox_remove_tilt.setStyleSheet(styleCheckbox)

        self.checkbox_remove_defocus = QCheckBox(translate('checkbox_remove_defocus'))
        self.checkbox_remove_defocus.setStyleSheet(styleCheckbox)

        self.checkbox_remove_spherical_aberration = QCheckBox(translate('checkbox_remove_spherical_aberration'))
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
        
        self.checkbox_remove_astigmatism = QCheckBox(translate('checkbox_remove_astigmatism'))
        self.checkbox_remove_astigmatism.setStyleSheet(styleCheckbox)

        self.checkbox_remove_coma = QCheckBox(translate('checkbox_remove_coma'))
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
    def __init__(self):
        super().__init__(parent=None)

        self.layout = QVBoxLayout()
        self.layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        self.master_widget = QWidget()
        self.master_layout = QVBoxLayout()
        self.master_widget.setStyleSheet("background-color: white;")
        
        # Title
        # -----
        self.label_title_acquisition_menu = QLabel(translate('label_title_acquisition_menu'))
        self.setStyleSheet(styleH1)
        
        # Subwidget to start acquisition
        # ------------------------------
        self.subwidget_start_acquisiton = QWidget()
        self.sublayout_start_acquisiton = QHBoxLayout()

        self.button_simple_acquisition = QPushButton(translate('button_simple_acquisition'))
        self.button_simple_acquisition.setStyleSheet(unactived_button)
        self.button_simple_acquisition.setFixedHeight(BUTTON_HEIGHT)
        self.button_simple_acquisition.clicked.connect(self.button_simple_acquisition_isClicked)

        self.button_repeated_acquisition = QPushButton(translate('button_repeated_acquisition'))
        self.button_repeated_acquisition.setStyleSheet(unactived_button)
        self.button_repeated_acquisition.setFixedHeight(BUTTON_HEIGHT)
        self.button_repeated_acquisition.clicked.connect(self.button_repeated_acquisition_isClicked)

        self.sublayout_start_acquisiton.addWidget(self.button_simple_acquisition)
        self.sublayout_start_acquisiton.addWidget(self.button_repeated_acquisition)
        self.sublayout_start_acquisiton.setContentsMargins(0, 0, 0, 0)
        self.subwidget_start_acquisiton.setLayout(self.sublayout_start_acquisiton)

        # Wedge factor entry
        #-------------------
        self.lineedit_wedge_factor = LineEditBloc('label_wedge_factor', txt='0.5')
        self.lineedit_wedge_factor.keyPressEvent = self.wedge_factor_is_modified

        # Remove faults menu
        # ------------------
        self.submenu_remove_faults = RemoveFaultsWidget()

        # Subwidget to save acquisition
        # ------------------------------
        self.subwidget_save_acquisiton = QWidget()
        self.sublayout_save_acquisiton = QHBoxLayout()

        self.button_see_and_save_images = QPushButton(translate('button_see_and_save_images'))
        self.button_see_and_save_images.setStyleSheet(unactived_button)
        self.button_see_and_save_images.setFixedHeight(BUTTON_HEIGHT)
        self.button_see_and_save_images.clicked.connect(self.button_see_and_save_images_isClicked)

        self.button_save_phase = QPushButton(translate('button_save_phase'))
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
                msg_box.information(self, translate('information'), translate('message_wedge_factor_updated'))
            except ValueError:
                msg_box = QMessageBox()
                msg_box.setStyleSheet(styleH3)
                msg_box.warning(self, translate('error'), translate('message_wedge_factor_error'))

        elif event.key() == Qt.Key.Key_Escape:
            self.lineedit_wedge_factor.clearFocus()
        else:
            # Laissez le QLineEdit gérer les autres touches
            super().keyPressEvent(event)

    def button_simple_acquisition_isClicked(self):
        self.button_simple_acquisition.setStyleSheet(actived_button)
        print('button_simple_acquisition_isClicked')
        self.button_simple_acquisition.setStyleSheet(unactived_button)
        print(self.camera.get_image())

    def button_repeated_acquisition_isClicked(self):
        self.button_repeated_acquisition.setStyleSheet(actived_button)
        print('button_repeated_acquisition_isClicked')
        self.button_repeated_acquisition.setStyleSheet(unactived_button)
    
    
    def button_see_and_save_images_isClicked(self):
        self.button_see_and_save_images.setStyleSheet(actived_button)
        print('button_see_and_save_images_isClicked')
        self.button_see_and_save_images.setStyleSheet(unactived_button)

    def button_save_phase_isClicked(self):
        self.button_save_phase.setStyleSheet(actived_button)
        print('button_save_phase_isClicked')
        self.button_save_phase.setStyleSheet(unactived_button)

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
