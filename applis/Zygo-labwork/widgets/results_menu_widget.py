# -*- coding: utf-8 -*-
"""*results_menu_widget.py* file.

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

if __name__ == '__main__':
    from combobox_bloc import ComboBoxBloc
    from table_from_numpy import TableFromNumpy
else:
    from widgets.combobox_bloc import ComboBoxBloc
    from widgets.table_from_numpy import TableFromNumpy


# %% To add in lensepy library
# Styles
# ------
styleH1 = f"font-size:20px; padding:7px; color:{BLUE_IOGS}; font-weight: bold;"  # Added missing styleH1
styleH2 = f"font-size:15px; padding:7px; color:{BLUE_IOGS}; font-weight: bold;"
styleH3 = f"font-size:15px; padding:7px; color:{BLUE_IOGS};"
styleCheckbox = f"font-size: 12px; padding: 7px; color: {BLUE_IOGS}; font-weight: normal;"

# %% Params
BUTTON_HEIGHT = 30  # px

# %% Widget
class ResultsMenuWidget(QWidget):
    def __init__(self):
        super().__init__(parent=None)
        self.setStyleSheet("background-color: white;")
        self.layout = QVBoxLayout()
        self.layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        self.master_widget = QWidget()
        self.master_layout = QVBoxLayout()
        self.master_widget.setStyleSheet("background-color: white;")
        
        # Title
        # -----
        self.label_title_results = QLabel(translate('label_title_results'))

        # ComboBox
        # --------
        list_choices = [translate('3D_plot')]
        self.combobox_type_output_plot = ComboBoxBloc(translate('label_output_type'), list_choices)

        # Table results
        # -------------
        self.array_no_results = np.array([
            ['', 1, 2, 3, 4, 5, translate('average')],
            ['PV', np.nan, np.nan, np.nan, np.nan, np.nan, np.nan],
            ['RMS', np.nan, np.nan, np.nan, np.nan, np.nan, np.nan]
        ])
        self.table_results = TableFromNumpy(self.array_no_results)

        # Print button
        # ------------
        self.button_print_all_results = QPushButton(translate('button_print_all_results'))
        self.button_print_all_results.setStyleSheet(unactived_button)
        self.button_print_all_results.setFixedHeight(BUTTON_HEIGHT)
        self.button_print_all_results.clicked.connect(self.button_print_all_results_isClicked)

        # Add widgets to the layout
        # -------------------------
        self.layout.addWidget(self.label_title_results)
        self.layout.addWidget(self.combobox_type_output_plot)
        self.layout.addWidget(self.table_results)
        self.layout.addWidget(self.button_print_all_results)

        self.master_widget.setLayout(self.layout)
        self.master_layout.addWidget(self.master_widget)
        self.setLayout(self.master_layout)

    def button_print_all_results_isClicked(self):
        self.button_print_all_results.setStyleSheet(actived_button)
        print('button_print_all_results_isClicked')
        self.button_print_all_results.setStyleSheet(unactived_button)


# %% Example
if __name__ == '__main__':
    from PyQt6.QtWidgets import QApplication

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
            self.setGeometry(300, 300, 500, 500)

            self.central_widget = ResultsMenuWidget()
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