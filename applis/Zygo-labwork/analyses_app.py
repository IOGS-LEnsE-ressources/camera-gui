# -*- coding: utf-8 -*-
"""*analysis_app.py* file.

*analysis_app* file that contains :class::AnalysisApp

This file is attached to a 2nd year of engineer training labwork in photonics.
Subject : https://lense.institutoptique.fr/ressources/Annee2/TP_Photonique/S8-2324-PolyAberrations.EN.pdf

More about the development of this interface :
https://iogs-lense-ressources.github.io/camera-gui/

.. note:: LEnsE - Institut d'Optique - version 1.0

.. moduleauthor:: Julien VILLEMEJANE (PRAG LEnsE) <julien.villemejane@institutoptique.fr>
.. moduleauthor:: Dorian MENDES (Promo 2026) <dorian.mendes@institutoptique.fr>
"""

import sys
import numpy as np
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget,
    QVBoxLayout, QGridLayout, QHBoxLayout,
    QLabel, QComboBox, QPushButton, QCheckBox, QDialog,
    QMessageBox
)
from PyQt6.QtCore import pyqtSignal, QTimer, Qt, QSignalMapper
from PyQt6.QtGui import QPixmap, QIcon, QCloseEvent

from lensepy import load_dictionary, translate, dictionary

from widgets.title_widget import TitleWidget
from widgets.analysis_menu_widget import AnalysisMenuWidget
from widgets.display_zernike_widget import *



class AnalysisApp(QWidget):
    """
    /!\ NEED TO RECEIVE DATA TO PROCESS ANALYSIS / phase ? coeff ?
    """

    window_closed = pyqtSignal(str)

    def __init__(self) -> None:
        """Default constructor of the class.
        """
        super().__init__(parent=None)

        self.layout = QGridLayout()
        self.setLayout(self.layout)

        # Columns stretch: 10%, 45%, 45%
        self.layout.setColumnStretch(0, 10)
        self.layout.setColumnStretch(1, 45)
        self.layout.setColumnStretch(2, 45)

        # Rows stretch: 4%, 48%, 48%
        self.layout.setRowStretch(0, 4)
        self.layout.setRowStretch(1, 48)
        self.layout.setRowStretch(2, 48)

        # Permanent Widgets
        # -----------------
        # Title Widget: first row of the grid layout
        self.title_widget = TitleWidget()
        self.title_widget.set_title("Contrôles interférométriques / Analyses poussées")
        self.layout.addWidget(self.title_widget, 0, 0, 1, 3)

        # Analysis Menu Widget: fist column of the grid layout
        self.main_menu_widget = AnalysisMenuWidget()
        self.layout.addWidget(self.main_menu_widget, 1, 0, 2, 1)
        self.main_menu_widget.analysis_selected.connect(self.analysis_is_selected)

    def analysis_is_selected(self, event):
        """
        Manage menu selection.
        Depending on the analysis required, layout is changing.
        """
        if event == 'zernike':
            zernike_coefficients = 2 * np.random.rand(37) - 1
            zernike_display = ZernikeDisplayWidget(zernike_coefficients)
            seidel_display = SeidelDisplayWidget(zernike_coefficients)
            self.layout.addWidget(zernike_display, 1, 1)
            self.layout.addWidget(seidel_display, 1, 2)

    def clear_layout(self, row: int, column: int) -> None:
        """Remove widgets from a specific position in the layout without deleting them.

        :param row: Row index of the layout.
        :type row: int
        :param column: Column index of the layout.
        :type column: int
        """
        item = self.layout.itemAtPosition(row, column)
        if item is not None:
            widget = item.widget()
            if widget:
                widget.deleteLater()

    def closeEvent(self, a0: QCloseEvent) -> None:
        super().closeEvent(a0)
        self.main_menu_widget.reset_menu()
        self.reset_layout()
        self.window_closed.emit('analysis_window_closed')

    def reset_layout(self):
        self.clear_layout(1,1)
        self.clear_layout(1,2)
        self.clear_layout(2,1)
        self.clear_layout(2,2)

    def resizeEvent(self, event):
        """Action performed when the window is resized.
        """
        super().resizeEvent(event)

if __name__ == '__main__':
    from PyQt6.QtWidgets import QApplication


    class MyWindow(QMainWindow):
        def __init__(self):
            super().__init__()

            # Define Window title
            self.setWindowTitle(translate("Zygo-IDS Labwork APP"))
            self.setWindowIcon(QIcon('assets\IOGS-LEnsE-icon.jpg'))
            self.setGeometry(50, 50, 700, 700)

            self.central_widget = AnalysisApp()
            self.setCentralWidget(self.central_widget)

        def closeEvent(self, event):
            """
            closeEvent redefinition. Use when the user clicks
            on the red cross to close the window
            """
            pass
            """reply = QMessageBox.question(self, 'Quit', 'Do you really want to close ?',
                                         QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                                         QMessageBox.StandardButton.No)

            if reply == QMessageBox.StandardButton.Yes:
                if self.central_widget.camera is not None:
                    self.central_widget.camera_widget.disconnect()
                event.accept()
            else:
                event.ignore()"""


    app = QApplication(sys.argv)
    main = MyWindow()
    main.showMaximized()
    sys.exit(app.exec())