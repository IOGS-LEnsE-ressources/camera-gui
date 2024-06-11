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

if __name__ == '__main__':
    from x_y_chart_widget import XYChartWidget
else:
    from widgets.x_y_chart_widget import XYChartWidget

from lensepy import load_dictionary, translate, dictionary
from lensepy.css import *
from lensepy.images.conversion import array_to_qimage, resize_image_ratio

import nidaqmx
import time

# %% To add in lensepy library
# Styles
# ------
styleH1 = f"font-size:20px; padding:7px; color:{BLUE_IOGS}; font-weight: bold;"  # Added missing styleH1
styleH2 = f"font-size:15px; padding:7px; color:{BLUE_IOGS}; font-weight: bold;"
styleH3 = f"font-size:15px; padding:7px; color:{BLUE_IOGS};"
styleCheckbox = f"font-size: 12px; padding: 7px; color: {BLUE_IOGS}; font-weight: normal;"

# %% Params
BUTTON_HEIGHT = 30  # px

local_system = nidaqmx.system.System.local()
driver_version = local_system.driver_version

# %% Widget
class PiezoCalibrationWidget(QWidget):
   
    def __init__(self, parent=None):
        super().__init__(parent=None)

        # Layout
        # ------
        self.layout = QVBoxLayout()
        self.layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        # Master
        # ------
        self.master_widget = QWidget()
        self.master_layout = QVBoxLayout()
        self.master_widget.setStyleSheet("background-color: white;")
        
        # Title
        # -----
        self.label_title_calibration_menu = QLabel(translate('label_title_calibration_menu'))
        self.setStyleSheet(styleH1)

        # Graph
        # -----
        self.graph_calibration = XYChartWidget()
        self.graph_calibration.set_background('white')
        self.graph_calibration.set_x_label('Voltage (V)')
        self.graph_calibration.set_y_label('Phase (°)')
        self.graph_calibration.refresh_chart()

        # Button
        # ------
        self.button_start_calibration = QPushButton(translate('button_start_calibration'))
        self.button_start_calibration.setStyleSheet(unactived_button)
        self.button_start_calibration.clicked.connect(self.button_start_calibration_isClicked)

        # Add widgets to the main layout
        self.layout.addWidget(self.label_title_calibration_menu)
        self.layout.addWidget(self.graph_calibration)
        self.layout.addWidget(self.button_start_calibration)

        self.master_widget.setLayout(self.layout)

        self.master_layout.addWidget(self.master_widget)
        self.setLayout(self.master_layout)

    def button_start_calibration_isClicked(self):
        self.button_start_calibration.setStyleSheet(actived_button)
        self.images = []

        start_voltage = 0  # Tension de départ en volts
        end_voltage = 5 # Tension finale en volts
        num_steps = 100  # Nombre de pas dans la rampe
        duration = 4  # Durée totale de la rampe en secondes

        # Calcul des paramètres de la rampe
        step_duration = duration / num_steps
        ramp = np.linspace(start_voltage, end_voltage, num_steps)

        # Créer une tâche pour générer la rampe de tension
        with nidaqmx.Task() as task:
            # Ajouter un canal de sortie analogique
            task.ao_channels.add_ao_voltage_chan("Dev1/ao1", min_val=start_voltage, max_val=end_voltage)

            # Démarrer la tâche
            task.start()

            # Générer la rampe de tension en écrivant chaque valeur successivement
            for voltage in ramp:
                task.write(voltage)
                self.parent.camera_thread.stop()
                self.parent.camera.init_camera()
                self.parent.camera.alloc_memory()
                self.parent.camera.start_acquisition()
                raw_array = self.parent.camera_widget.camera.get_image().copy()
                self.images.append(raw_array)
                self.parent.camera.stop_acquisition()
                self.parent.camera.free_memory()
                time.sleep(step_duration)
            # Arrêter la tâche
            task.stop()

        

# %% Example
if __name__ == '__main__':
    from PyQt6.QtWidgets import QApplication
    from ids_peak import ids_peak

    class MyWindow(QMainWindow):
        def __init__(self):
            super().__init__()

            self.setWindowTitle('Test - Piezo calibration')
            self.setGeometry(300, 300, 1000, 600)

            self.central_widget = PiezoCalibrationWidget()
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
