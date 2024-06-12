# -*- coding: utf-8 -*-
"""*acquisition_menu_widget.py* file.

.. note:: LEnsE - Institut d'Optique - version 1.0

.. moduleauthor:: Julien VILLEMEJANE (PRAG LEnsE) <julien.villemejane@institutoptique.fr>
.. moduleauthor:: Dorian MENDES (Promo 2026) <dorian.mendes@institutoptique.fr>
"""

import sys

import cv2
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

local_system = nidaqmx.system.System.local()
driver_version = local_system.driver_version

# %% Widget
class PiezoCalibrationWidget(QWidget):
   
    def __init__(self, parent=None):
        super().__init__(parent=None)

        self.parent = parent

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
        image_for_all_voltages = []
        number_measures = 3

        start_voltage = 0  # Tension de départ en volts
        end_voltage = 5 # Tension finale en volts
        num_steps = 50  # Nombre de pas dans la rampe

        # Stop thread

        self.parent.camera_thread.stop()
        self.parent.camera.init_camera()
        self.parent.camera.alloc_memory()
        self.parent.camera.start_acquisition()

        # Calcul des paramètres de la rampe
        ramp = np.linspace(start_voltage, end_voltage, num_steps)
        # Créer une tâche pour générer la rampe de tension
        with nidaqmx.Task() as task:
            # Ajouter un canal de sortie analogique
            task.ao_channels.add_ao_voltage_chan("Dev1/ao1", min_val=start_voltage, max_val=end_voltage)

            # Démarrer la tâche
            task.start()

            import matplotlib.pyplot as plt

            n, m, p = (self.parent.camera_widget.camera.get_image().copy()).shape
            x_min, x_max = n // 4, 3 * n // 4
            y_min, y_max = m // 4, 3 * m // 4
            average_for_all_voltages = []

            # Générer la rampe de tension en écrivant chaque valeur successivement
            for i in range(number_measures):
                image_for_all_voltages = []
                for j,voltage in enumerate(ramp):
                    print(f"{i + 1}e mesure | V={voltage}/{end_voltage}")
                    task.write(voltage)
                    time.sleep(0.1)
                    raw_array = self.parent.camera_widget.camera.get_image().copy()[x_min:x_max, y_min:y_max]/number_measures
                    image_for_all_voltages.append(raw_array)
                average_for_all_voltages.append(image_for_all_voltages)
            average_for_all_voltages = np.mean(np.array(average_for_all_voltages), axis=0)

            print(average_for_all_voltages)
            plt.figure()
            plt.imshow(raw_array, 'gray')
            plt.show()
            average_for_all_voltages = np.squeeze(np.array(average_for_all_voltages))
            phi = np.array(list(map(lambda img:1-img/average_for_all_voltages[0], average_for_all_voltages)))
            phase = np.rad2deg(np.arccos(np.mean(np.mean(phi, axis=2), axis=1)/np.max(phi))-PI/2)

            diff_phase = np.diff(phase, prepend=0)
            for i in range(1, len(phase)):
                if diff_phase[i] <0:
                    phase[i] = phase[i-1] - diff_phase[i]
                else:
                    phase[i] = phase[i-1] + diff_phase[i]

            task.write(0)

            # Arrêter la tâche
            task.stop()

        self.parent.camera.stop_acquisition()
        self.parent.camera.free_memory()
        self.parent.camera_thread.start()

        self.graph_calibration.clear_graph()
        self.graph_calibration.set_data(ramp, phase)
        self.graph_calibration.refresh_chart()

        self.button_start_calibration.setStyleSheet(unactived_button)

        eps = 1 # °
        V_1 = np.mean(ramp[np.where(np.abs(phase-0) < eps)])
        V_2 = np.mean(ramp[np.where(np.abs(phase-90) < eps)])
        V_3 = np.mean(ramp[np.where(np.abs(phase-180) < eps)])
        V_4 = np.mean(ramp[np.where(np.abs(phase-270) < eps)])
        V_5 = np.mean(ramp[np.where(np.abs(phase-360) < eps)])

        print(f"V(phi=0)={V_1}")
        print(f"V(phi=90°)={V_2}")
        print(f"V(phi=180°)={V_3}")
        print(f"V(phi=270°)={V_4}")
        print(f"V(phi=180°)={V_5}")

        self.parent.camera_thread.stop()
        self.parent.camera.init_camera()
        self.parent.camera.alloc_memory()
        self.parent.camera.start_acquisition()

        with nidaqmx.Task() as task:
                # Ajouter un canal de sortie analogique
                task.ao_channels.add_ao_voltage_chan("Dev1/ao1", min_val=start_voltage, max_val=end_voltage)

                # Démarrer la tâche
                task.start()

                import matplotlib.pyplot as plt
                plt.figure()
                for i in range(6):
                    plt.subplot(1,6,i+1)
                    plt.title(f"Voltage={i} V")
                    task.write(i)
                    plt.imshow(self.parent.camera_widget.camera.get_image().copy()[x_min:x_max, y_min:y_max], 'gray')
                    time.sleep(0.1)

                task.write(0)
                task.stop()

        self.parent.camera.stop_acquisition()
        self.parent.camera.free_memory()
        self.parent.camera_thread.start()
        plt.show()

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
