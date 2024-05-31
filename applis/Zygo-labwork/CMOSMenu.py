# -*- coding: utf-8 -*-
"""Menu for CMOS Sensor Analysis GUI

---------------------------------------
(c) 2023 - LEnsE - Institut d'Optique
---------------------------------------

Modifications
-------------
    Creation on 2023/07/02


Authors
-------
    Julien VILLEMEJANE
"""

# Standard Libraries

# Third pary imports
from PyQt6.QtWidgets import QWidget, QComboBox
from PyQt6.QtWidgets import QHBoxLayout, QGridLayout, QVBoxLayout
from PyQt6.QtWidgets import QLabel, QPushButton, QProgressBar, QLineEdit, QMessageBox
from PyQt6.QtCore import QTimer, pyqtSignal, Qt

# Local libraries

# Global Constants
ACTIVE_COLOR = "#45B39D"
INACTIVE_COLOR = "#AF7AC5"

live_run_style = "background:" + ACTIVE_COLOR + "; color:white; font-weight:bold;"
stop_style = "background:" + INACTIVE_COLOR + "; color:white; font-weight:bold;"
no_style = "background:gray; color:white; font-weight:none;"
title_style = "background:darkgray; color:white; font-size:15px; font-weight:bold;"

progress_bar_style = '''
#GreenProgressBar {
    min-height: 24px;
    max-height: 24px;
    border-radius: 6px;
    text-align: center;
    font-weight: bold;
    color: black;
}
'''


class CMOSMenu(QWidget):
    """
    Main menu of the Application.
    Children of QWidget
    ---

    Attributes
    ----------
    menu_mode: str
        Mode of the application :
            "Disabled" (when no camera is connected)
            "Waiting" (when a camera is connected but no acquisition)
            "Acquisition" (when data are acquired)
            "LiveRun" (when camera is connected and acquisition in continuous mode)
    data_ready: bool
        State of the data acquisition - True if data are acquired
    aoi : bool
        True if only Area of Interest is selected, False for the whole frame
    Methods
    -------
    connectCam():
        Initializes the USB connexion to the camera.
    closeEvent(event):
        Closes the application properly.

    """

    # Signal emits when a button is clicked
    menu_signal = pyqtSignal(str)

    def __init__(self):
        super().__init__()  # Constant Colors
        self.menu_mode = "Disabled"
        self.data_ready = False
        self.aoi = False

        self.menu_layout = QVBoxLayout()
        self.menu_layout.setSpacing(0)
        self.setStyleSheet('background:gray;color:white;')

        # # Acquisition
        self.acquisition_label = QLabel('Acquisition')
        self.acquisition_label.setStyleSheet(title_style)
        self.acquisition_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.menu_layout.addWidget(self.acquisition_label)

        self.start_stop_widget = QWidget()
        self.start_stop_layout = QHBoxLayout()
        self.start_stop_widget.setLayout(self.start_stop_layout)
        self.menu_layout.addWidget(self.start_stop_widget)
        # Camera Live Run Button - Display frame and charts in real time
        self.live_run_button = QPushButton('Start')
        self.live_run_button.setEnabled(False)
        self.start_stop_layout.addWidget(self.live_run_button)
        self.live_run_button.clicked.connect(self.live_run_action)
        # Stop Live Button
        self.stop_live_button = QPushButton('Stop')
        self.stop_live_button.setEnabled(False)
        self.start_stop_layout.addWidget(self.stop_live_button)
        self.stop_live_button.clicked.connect(self.stop_live_action)

        self.reset_data_widget = QWidget()
        self.reset_data_layout = QHBoxLayout()
        self.reset_data_widget.setLayout(self.reset_data_layout)
        self.menu_layout.addWidget(self.reset_data_widget)
        # Reset Data
        self.reset_button = QPushButton('Reset')
        self.reset_button.setEnabled(False)
        self.reset_data_layout.addWidget(self.reset_button)
        self.reset_button.clicked.connect(self.reset_action)
        # Save Data
        self.save_data_button = QPushButton('Save Data')
        self.save_data_button.setEnabled(False)
        self.reset_data_layout.addWidget(self.save_data_button)
        self.save_data_button.clicked.connect(self.save_data_action)

        # # Acquisition Parameters
        self.acq_params_widget = QWidget()
        self.acq_params_layout = QHBoxLayout()
        self.acq_params_widget.setLayout(self.acq_params_layout)
        self.menu_layout.addWidget(self.acq_params_widget)
        self.nb_of_points_label = QLabel('Nb of points')
        self.nb_of_points_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.acq_params_layout.addWidget(self.nb_of_points_label)

        self.nb_of_points_value = QComboBox()
        self.nb_of_points_value.addItems([" LIVE ", "50", "100", "200", "500", "1000", "2000"])
        self.nb_of_points_value.setEnabled(False)
        self.acq_params_layout.addWidget(self.nb_of_points_value)
        self.max_progress_value = 0

        self.progress_bar_widget = QWidget()
        self.progress_bar_layout = QHBoxLayout()
        self.progress_bar_widget.setLayout(self.progress_bar_layout)
        self.progress_bar = QProgressBar(self, minimum=0, maximum=100, objectName="GreenProgressBar")
        self.progress_bar_layout.addWidget(self.progress_bar)
        self.menu_layout.addWidget(self.progress_bar_widget)

        self.snap_widget = QWidget()
        self.snap_layout = QHBoxLayout()
        self.snap_widget.setLayout(self.snap_layout)
        self.snap_button = QPushButton('Snap')
        self.snap_button.clicked.connect(self.snap_action)
        self.snap_layout.addWidget(self.snap_button)
        self.save_snap_button = QPushButton('Save Snap')
        self.save_snap_button.clicked.connect(self.save_snap_action)
        self.snap_layout.addWidget(self.save_snap_button)
        self.menu_layout.addWidget(self.snap_widget)

        # AOI
        self.max_width_aoi = 0
        self.max_height_aoi = 0
        self.aoi_label = QLabel('Area of Interest')
        self.aoi_label.setStyleSheet(title_style)
        self.aoi_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.menu_layout.addWidget(self.aoi_label)
        self.aoi_widget = QWidget()
        self.aoi_layout = QGridLayout()
        self.aoi_widget.setLayout(self.aoi_layout)
        self.aoi_x_label = QLabel('X Pos')
        self.aoi_x_text = QLineEdit()
        self.aoi_x_text.setStyleSheet('background:white;color:black;')
        self.aoi_y_label = QLabel('Y Pos')
        self.aoi_y_text = QLineEdit()
        self.aoi_y_text.setStyleSheet('background:white;color:black;')
        self.aoi_layout.addWidget(self.aoi_x_label, 1, 0)
        self.aoi_layout.addWidget(self.aoi_x_text, 1, 1)
        self.aoi_layout.addWidget(self.aoi_y_label, 1, 2)
        self.aoi_layout.addWidget(self.aoi_y_text, 1, 3)
        self.aoi_x_size_label = QLabel('X Size')
        self.aoi_x_size_text = QLineEdit()
        self.aoi_x_size_text.setStyleSheet('background:white;color:black;')
        self.aoi_y_size_label = QLabel('Y Size')
        self.aoi_y_size_text = QLineEdit()
        self.aoi_y_size_text.setStyleSheet('background:white;color:black;')
        self.aoi_layout.addWidget(self.aoi_x_size_label, 2, 0)
        self.aoi_layout.addWidget(self.aoi_x_size_text, 2, 1)
        self.aoi_layout.addWidget(self.aoi_y_size_label, 2, 2)
        self.aoi_layout.addWidget(self.aoi_y_size_text, 2, 3)
        self.all_frame_button = QPushButton('Frame')
        self.aoi_frame_button = QPushButton('AOI')
        self.aoi_center_button = QPushButton('Center')
        self.all_frame_button.clicked.connect(self.all_frame_action)
        self.aoi_frame_button.clicked.connect(self.aoi_frame_action)
        self.aoi_center_button.clicked.connect(self.aoi_center_action)
        self.aoi_layout.addWidget(self.all_frame_button, 3, 0, 1, 2)
        self.aoi_layout.addWidget(self.aoi_frame_button, 3, 2, 1, 2)
        self.aoi_layout.addWidget(self.aoi_center_button, 4, 2, 1, 2)
        self.aoi_y_text.setEnabled(False)
        self.aoi_x_text.setEnabled(False)
        self.aoi_y_size_text.setEnabled(False)
        self.aoi_x_size_text.setEnabled(False)
        self.aoi_frame_button.setEnabled(False)
        self.all_frame_button.setEnabled(False)
        self.aoi_center_button.setEnabled(False)

        self.menu_layout.addWidget(self.aoi_widget)

        self.setLayout(self.menu_layout)

    def live_run_action(self):
        self.data_ready = True
        self.live_run_button.setEnabled(False)
        self.live_run_button.setStyleSheet(live_run_style)
        self.stop_live_button.setEnabled(True)
        self.stop_live_button.setStyleSheet(no_style)
        self.reset_button.setEnabled(False)
        self.save_data_button.setEnabled(False)
        self.snap_button.setEnabled(False)
        self.save_snap_button.setEnabled(False)
        self.all_frame_button.setEnabled(False)
        self.aoi_center_button.setEnabled(False)
        self.aoi_frame_button.setEnabled(False)
        if self.nb_of_points_value.currentText() != ' LIVE ':
            self.menu_mode = "Acquisition"
            self.menu_signal.emit('acquisition')
        else:
            self.menu_mode = "LiveRun"
            self.menu_signal.emit('start')

    def stop_live_action(self):
        self.live_run_button.setEnabled(True)
        self.live_run_button.setStyleSheet(no_style)
        self.stop_live_button.setEnabled(False)
        self.snap_button.setEnabled(True)
        self.save_snap_button.setEnabled(True)
        self.stop_live_button.setStyleSheet(stop_style)
        self.menu_mode = "Waiting"
        if self.data_ready:
            self.reset_button.setEnabled(True)
            self.save_data_button.setEnabled(True)
        else:
            self.reset_button.setEnabled(False)
            self.reset_button.setEnabled(False)
        self.all_frame_button.setEnabled(True)
        self.aoi_center_button.setEnabled(True)
        self.aoi_frame_button.setEnabled(True)
        self.menu_signal.emit('stop')

    def reset_action(self):
        self.data_ready = False
        self.menu_signal.emit('reset')

    def save_data_action(self):
        self.menu_signal.emit('save_data')

    def snap_action(self):
        self.menu_signal.emit('snap')

    def save_snap_action(self):
        self.menu_signal.emit('save_snap')

    def update_progress_bar(self, value):
        if self.max_progress_value != 0:
            self.progress_bar.setValue(int(value))
        else:
            self.progress_bar.setValue(int(value))

    def aoi_center_action(self):
        if not self.aoi:
            self.all_frame_button.setStyleSheet(no_style)
            self.aoi_frame_button.setStyleSheet(stop_style)
            self.aoi_center_button.setStyleSheet(live_run_style)
            self.all_frame_button.setEnabled(True)
            self.aoi_frame_button.setEnabled(False)
            self.aoi_center_button.setEnabled(False)
            self.aoi = True
            self.menu_signal.emit('center')

    def all_frame_action(self):
        if self.aoi:
            self.all_frame_button.setStyleSheet(live_run_style)
            self.aoi_frame_button.setStyleSheet(no_style)
            self.aoi_center_button.setStyleSheet(no_style)
            self.all_frame_button.setEnabled(False)
            self.aoi_frame_button.setEnabled(True)
            self.aoi_center_button.setEnabled(True)
            self.aoi = False
            self.menu_signal.emit('all_frame')

    def aoi_frame_action(self):
        if not self.aoi:
            print('AOI BUTTON')
            error_nb = 0
            x = self.aoi_x_text.text()
            y = self.aoi_y_text.text()
            x_size = self.aoi_x_size_text.text()
            y_size = self.aoi_y_size_text.text()
            # Test if values are numbers
            if not x.isnumeric() or not y.isnumeric():
                error_nb += 1
                print('error  X Y')
            if not x_size.isnumeric() or not y_size.isnumeric():
                error_nb += 1
                print('error SIZE')
            # Test if values are in the good range
            if error_nb == 0:
                x = int(x)
                y = int(y)
                x_size = int(x_size)
                y_size = int(y_size)
                if not (0 <= x < self.max_width_aoi) or not (0 <= y < self.max_height_aoi):
                    error_nb += 1
                    print('error RANGE X/Y')
                if not (0 < x + x_size <= self.max_width_aoi) or not (0 < y + y_size <= self.max_height_aoi):
                    error_nb += 1
                    print('error RANGE Size')

            if error_nb == 0:
                self.all_frame_button.setStyleSheet(no_style)
                self.aoi_frame_button.setStyleSheet(live_run_style)
                self.aoi_center_button.setStyleSheet(stop_style)
                self.all_frame_button.setEnabled(True)
                self.aoi_frame_button.setEnabled(False)
                self.aoi_center_button.setEnabled(False)
                self.aoi = True
                self.menu_signal.emit('aoi')

    def get_aoi_mode(self):
        """
        Return if analysis is on the whole frame or on an AOI
        """
        return self.aoi

    def set_aoi_mode(self, val):
        self.aoi = val

    def get_aoi_size(self):
        """
        Return the position and the size of the area of intereset.

        Returns
        -------
        Tuple of 4 integer values
            X, Y, X Size, Y Size
        """
        if self.aoi:
            return int(self.aoi_x_text.text()), int(self.aoi_y_text.text()), int(self.aoi_x_size_text.text()), int(self.aoi_y_size_text.text())
        else:
            return 0, 0, 0, 0

    def set_max_progress_bar(self):
        """
        Set the maximum value for the progression bar to the selected value

        Returns
        -------
        False if Live mode is activated
        True if max value is set
        """
        val_nb_of_points = self.nb_of_points_value.currentText()
        if val_nb_of_points != ' LIVE ':
            self.max_progress_value = int(val_nb_of_points)
            self.progress_bar.setMaximum(self.max_progress_value)
            return True
        else:
            self.max_progress_value = 0
            return False

    def get_max_progress_bar_value(self):
        return self.max_progress_value

    def set_enable(self):
        self.menu_mode == "Waiting"
        self.live_run_button.setEnabled(True)
        self.stop_live_button.setEnabled(False)
        self.stop_live_button.setStyleSheet(stop_style)
        self.live_run_button.setStyleSheet(no_style)
        self.reset_button.setEnabled(True)
        self.nb_of_points_value.setEnabled(True)
        self.all_frame_button.setStyleSheet(live_run_style)
        if self.data_ready:
            self.save_data_button.setEnabled(True)
        else:
            self.save_data_button.setEnabled(False)
        self.aoi_y_text.setEnabled(True)
        self.aoi_x_text.setEnabled(True)
        self.aoi_y_size_text.setEnabled(True)
        self.aoi_x_size_text.setEnabled(True)
        self.aoi_frame_button.setEnabled(True)
        self.all_frame_button.setEnabled(False)
        self.aoi_center_button.setEnabled(True)
        self.aoi_x_text.setText('0')
        self.aoi_y_text.setText('0')

    def set_width_height_camera(self, w, h):
        self.max_width_aoi = w
        self.aoi_x_size_text.setText(str(w))
        self.max_height_aoi = h
        self.aoi_y_size_text.setText(str(h))

    def get_mode(self):
        return self.menu_mode
