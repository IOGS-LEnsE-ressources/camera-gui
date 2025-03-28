# -*- coding: utf-8 -*-
"""*aberrations_options_view.py* file.

./views/aberrations_options_view.py contains AnalysesOptionsView class to display options for analyses mode.

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
    QWidget, QLabel, QProgressBar, QCheckBox,
    QHBoxLayout, QVBoxLayout
)
from PyQt6.QtCore import Qt, pyqtSignal
from views.PVRMS_view import PVRMSView

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from controllers.aberrations_controller import AberrationsController


class AberrationsOptionsView(QWidget):
    """Images Choice."""

    aberrations_changed = pyqtSignal(str)

    def __init__(self, controller: "AberrationsController"=None) -> None:
        """Default constructor of the class.
        :param parent: Parent widget or window of this widget.
        """
        super().__init__()
        self.controller: "AberrationsController" = controller
        #self.data_set = self.controller.data_set
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        ## Title of the widget
        self.label_analyses_options = QLabel(translate("label_aberrations_options"))
        self.label_analyses_options.setStyleSheet(styleH1)
        self.label_analyses_options.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.layout.addWidget(self.label_analyses_options)

        # Wedge factor

        # PV/RMS displayed (for uncorrected phase)
        self.label_pv_rms_uncorrected = QLabel(translate('label_pv_rms_ab_corrected'))
        self.label_pv_rms_uncorrected.setStyleSheet(styleH2)
        self.pv_rms_uncorrected = PVRMSView(vertical=True)
        self.layout.addWidget(self.label_pv_rms_uncorrected)
        self.layout.addWidget(self.pv_rms_uncorrected)
        self.layout.addStretch()

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
    main_widget = AberrationsOptionsView()
    main_widget.setGeometry(100, 100, 700, 500)
    main_widget.show()

    # Class test
    main_widget.set_pv_uncorrected(20.5, 'mm')

    sys.exit(app.exec())