# -*- coding: utf-8 -*-
"""*analyses_options_view.py* file.

./views/analyses_options_view.py contains AnalysesOptionsView class to display options for analyses mode.

.. note:: LEnsE - Institut d'Optique - version 1.0

.. moduleauthor:: Julien VILLEMEJANE (PRAG LEnsE) <julien.villemejane@institutoptique.fr>
Creation : march/2025
"""
import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), ".")))
from lensepy import load_dictionary, translate, dictionary
from lensepy.css import *
from lensepy.pyqt6 import *
from PyQt6.QtWidgets import (
    QWidget, QLabel, QPushButton, QProgressBar, QCheckBox,
    QHBoxLayout, QVBoxLayout
)
from PyQt6.QtCore import Qt, pyqtSignal

MINIMUM_WIDTH = 75

class AnalysesOptionsView(QWidget):
    """Images Choice."""

    analyses_changed = pyqtSignal(str)

    def __init__(self, controller=None) -> None:
        """Default constructor of the class.
        :param parent: Parent widget or window of this widget.
        """
        super().__init__()
        self.controller = controller
        #self.data_set = self.controller.data_set
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        ## Title of the widget
        self.label_analyses_options = QLabel(translate("label_analyses_options"))
        self.label_analyses_options.setStyleSheet(styleH1)
        self.label_analyses_options.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.layout.addWidget(self.label_analyses_options)

        # Progression Bar
        self.label_progress_bar = QLabel(translate('label_progress_bar'))
        self.label_progress_bar.setStyleSheet(styleH2)
        self.progress_bar = QProgressBar(self)
        self.progress_bar.setObjectName("IOGSProgressBar")
        self.progress_bar.setStyleSheet(StyleSheet)
        self.progress_bar.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.layout.addWidget(self.label_progress_bar)
        self.layout.addWidget(self.progress_bar)

        # 2D/3D display
        self.widget_2D_3D = QWidget()
        self.layout_2D_3D = QHBoxLayout()
        self.widget_2D_3D.setLayout(self.layout_2D_3D)
        self.checkbox_2D_3D_choice = QCheckBox()
        self.checkbox_2D_3D_choice.stateChanged.connect(self.display_changed)
        self.label_2D_3D_choice = QLabel(translate('label_2D_3D_choice'))
        self.layout_2D_3D.addWidget(self.checkbox_2D_3D_choice)
        self.layout_2D_3D.addWidget(self.label_2D_3D_choice)
        self.layout_2D_3D.addStretch()
        self.checkbox_2D_3D_choice.setEnabled(False)
        self.checkbox_2D_3D_choice.setChecked(False)
        self.layout.addWidget(self.widget_2D_3D)

        # PV/RMS displayed (for uncorrected phase)
        self.label_pv_rms_uncorrected = QLabel(translate('label_pv_rms_uncorrected'))
        self.label_pv_rms_uncorrected.setStyleSheet(styleH2)
        self.pv_rms_uncorrected = PVRMSView()
        self.layout.addWidget(self.label_pv_rms_uncorrected)
        self.layout.addWidget(self.pv_rms_uncorrected)

        ## Only when corrected button in analyses is clicked.
        # PV/RMS displayed (for corrected phase)
        self.label_pv_rms_corrected = QLabel(translate('label_pv_rms_corrected'))
        self.label_pv_rms_corrected.setStyleSheet(styleH2)
        ## Checkbox for TILT
        self.widget_tilt = QWidget()
        self.layout_tilt = QHBoxLayout()
        self.widget_tilt.setLayout(self.layout_tilt)
        self.checkbox_tilt_choice = QCheckBox()
        self.checkbox_tilt_choice.stateChanged.connect(self.tilt_changed)
        self.label_tilt_choice = QLabel(translate('label_tilt_choice'))
        self.layout_tilt.addWidget(self.checkbox_tilt_choice)
        self.layout_tilt.addWidget(self.label_tilt_choice)
        self.layout_tilt.addStretch()
        self.checkbox_tilt_choice.setEnabled(False)
        self.checkbox_tilt_choice.setChecked(False)

        self.pv_rms_corrected = PVRMSView()
        self.layout.addWidget(self.label_pv_rms_corrected)
        self.layout.addWidget(self.widget_tilt)
        self.layout.addWidget(self.pv_rms_corrected)
        self.layout.addStretch()

        self.hide_correction()

    def hide_correction(self):
        """
        Hide the corrected option part of the widget.
        """
        self.checkbox_tilt_choice.hide()
        self.label_tilt_choice.hide()
        self.label_pv_rms_corrected.hide()
        self.pv_rms_corrected.hide()

    def show_correction(self):
        """
        Show the corrected option part of the widget.
        ## Only when corrected button in analyses is clicked.
        """
        self.checkbox_tilt_choice.show()
        self.label_tilt_choice.show()
        self.label_pv_rms_corrected.show()
        self.pv_rms_corrected.show()

    def update_progress_bar(self, value: int):
        """
        Update the progress bar value.
        :param value: Value to update to the progress bar.
        """
        self.progress_bar.setValue(value)

    def set_enable_2D_3D(self, value: bool):
        """
        Set enable the 2D/3D display checkbox.
        :param value: True or False.
        """
        self.checkbox_2D_3D_choice.setEnabled(value)

    def set_enable_tilt(self, value: bool):
        """
        Set enable the 2D/3D display checkbox.
        :param value: True or False.
        """
        self.checkbox_tilt_choice.setEnabled(value)

    def is_tilt_checked(self):
        """
        Return if the tilt checkbox is checked.
        :return: True if checked.
        """
        return self.checkbox_tilt_choice.isChecked()

    def is_3D_checked(self):
        """
        Return if the 3D checkbox is checked.
        :return: True if checked.
        """
        return self.checkbox_2D_3D_choice.isChecked()

    def display_changed(self):
        """
        Action performed when the 2D/3D checkbox is checked.
        """
        state = self.checkbox_2D_3D_choice.isChecked()
        self.analyses_changed.emit(f'3D,{state}')

    def tilt_changed(self):
        """
        Action performed when the 2D/3D checkbox is checked.
        """
        state = self.checkbox_tilt_choice.isChecked()
        self.analyses_changed.emit(f'tilt,{state}')

    def set_pv_uncorrected(self, value: float, unit: str = '\u03BB'):
        """
        Update the value and the unit of the PV value.
        :param value: value of the peak-to-valley.
        :param unit: Unit of the PV value.
        """
        self.pv_rms_uncorrected.set_pv(value, unit)

    def set_rms_uncorrected(self, value: float, unit: str = '\u03BB'):
        """
        Update the value and the unit of the RMS value.
        :param value: value of the RMS.
        :param unit: Unit of the RMS value.
        """
        self.pv_rms_uncorrected.set_rms(value, unit)

    def set_pv_corrected(self, value: float, unit: str = '\u03BB'):
        """
        Update the value and the unit of the PV value.
        :param value: value of the peak-to-valley.
        :param unit: Unit of the PV value.
        """
        self.pv_rms_corrected.set_pv(value, unit)

    def set_rms_corrected(self, value: float, unit: str = '\u03BB'):
        """
        Update the value and the unit of the RMS value.
        :param value: value of the RMS.
        :param unit: Unit of the RMS value.
        """
        self.pv_rms_corrected.set_rms(value, unit)

    def _clear_layout(self, row: int, column: int) -> None:
        """Remove widgets from a specific position in the layout.

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
            else:
                self.layout.removeItem(item)

    def erase_pv_rms(self):
        """
        Erase PV and RMS values.
        """
        self.pv_rms_uncorrected.erase_pv_rms()
        self.pv_rms_corrected.erase_pv_rms()


class PVRMSView(QWidget):
    """
    Class to display PV (Peak-to-Valley) and RMS value of a wavefront.
    """

    def __init__(self):
        """
        Default constructor.
        """
        super().__init__()
        self.layout = QHBoxLayout()
        self.setLayout(self.layout)

        styleL = f"font-size:14px; padding:0px; color:{ORANGE_IOGS}; font-weight: bold;"
        styleT = f"font-size:14px; padding:5px; font-weight: bold; background-color: white;"
        self.label_PV = QLabel(translate('label_PV'))
        self.label_PV.setStyleSheet(styleL)
        self.text_PV = QLabel()
        self.text_PV.setStyleSheet(styleT)
        self.text_PV.setMinimumWidth(MINIMUM_WIDTH)
        self.text_PV.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.unit_PV = QLabel()
        self.unit_PV.setMinimumWidth(MINIMUM_WIDTH)
        self.label_RMS = QLabel(translate('label_RMS'))
        self.label_RMS.setStyleSheet(styleL)
        self.text_RMS = QLabel()
        self.text_RMS.setStyleSheet(styleT)
        self.text_RMS.setMinimumWidth(MINIMUM_WIDTH)
        self.text_RMS.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.unit_RMS = QLabel()
        self.unit_RMS.setMinimumWidth(MINIMUM_WIDTH)
        self.layout.addWidget(self.label_PV)
        self.layout.addWidget(self.text_PV)
        self.layout.addWidget(self.unit_PV)
        self.layout.addStretch()
        self.layout.addWidget(self.label_RMS)
        self.layout.addWidget(self.text_RMS)
        self.layout.addWidget(self.unit_RMS)
        self.layout.addStretch()

    def set_pv(self, value: float, unit: str = ''):
        """
        Update the value and the unit of the PV value.
        :param value: value of the peak-to-valley.
        :param unit: Unit of the PV value.
        """
        self.text_PV.setText(str(value))
        self.unit_PV.setText(unit)

    def set_rms(self, value: float, unit: str = ''):
        """
        Update the value and the unit of the RMS value.
        :param value: value of the RMS.
        :param unit: Unit of the RMS value.
        """
        self.text_RMS.setText(str(value))
        self.unit_RMS.setText(unit)

    def erase_pv_rms(self):
        """
        Erase PV and RMS values.
        """
        self.text_PV.setText('')
        self.unit_PV.setText('')
        self.text_RMS.setText('')
        self.unit_RMS.setText('')


if __name__ == "__main__":
    from PyQt6.QtWidgets import QApplication
    '''
    from controllers.analyses_controller import AnalysesController, ModesManager
    manager = ModesManager()
    controller = AnalysesController()
    '''

    def analyses_changed(value):
        print(value)

    app = QApplication(sys.argv)
    main_widget = AnalysesOptionsView()
    main_widget.setGeometry(100, 100, 700, 500)
    main_widget.show()

    # Class test
    main_widget.update_progress_bar(50)
    main_widget.set_enable_2D_3D(True)
    main_widget.set_enable_tilt(True)
    main_widget.set_pv_uncorrected(20.5, 'mm')
    main_widget.analyses_changed.connect(analyses_changed)
    main_widget.show_correction()

    sys.exit(app.exec())