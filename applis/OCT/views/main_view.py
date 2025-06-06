# -*- coding: utf-8 -*-
"""*main_view.py* file.

.. note:: LEnsE - Institut d'Optique - version 1.0

.. moduleauthor:: Julien VILLEMEJANE (PRAG LEnsE) <julien.villemejane@institutoptique.fr>
"""
import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), ".")))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import numpy as np
from PyQt6.QtWidgets import (
    QMessageBox, QWidget,
    QGridLayout, QHBoxLayout,
    QLabel
)
from PyQt6.QtCore import pyqtSignal
from lensepy import translate
from views.images_display_view import ImagesDisplayView
from views.images import ImageDisplayGraph
from views.title_view import TitleView
from views.acquisition import AcquisitionView
from views.motors_display import MotorControlView
from views.camera_params import CameraParamsView
#from views.live_mode import *


class CameraParamsWidget(QWidget):
    """
    Widget containing camera parameters.
    """
    def __init__(self, parent=None):
        """
        Default Constructor.
        :param parent: Parent widget of the camera parameters widget.
        """
        super().__init__(parent=parent)
        self.parent = parent

        layout = QHBoxLayout()
        label = QLabel('Test Camera')
        layout.addWidget(label)
        self.setLayout(layout)


class MiniCameraWidget(QWidget):
    """
    Widget containing the title and the camera parameters.
    """

    def __init__(self, parent=None):
        """
        Default Constructor.
        :param parent: Parent widget of the title widget.
        """
        super().__init__(parent=parent)
        self.parent = parent
        self.layout = QGridLayout()

        self.title_widget = TitleView(self.parent)
        self.camera_params_widget = CameraParamsView(self.parent)

        self.layout.setRowStretch(0, 1)
        self.layout.setRowStretch(1, 2)

        self.layout.addWidget(self.title_widget, 0, 0)
        self.layout.addWidget(self.camera_params_widget, 1, 0)
        self.setLayout(self.layout)



class MainView(QWidget):
    """
    Main central widget of the application.
    """

    main_signal = pyqtSignal(str)

    def __init__(self, parent=None):
        """
        Default Constructor.
        :param parent: Parent window of the main widget.
        """
        super().__init__(parent=parent)
        self.parent = parent
        # GUI Structure
        self.layout = QGridLayout()
        # Set size of cols and rows
        self.layout.setColumnStretch(0, 1)
        self.layout.setColumnStretch(1, 2)
        self.layout.setRowStretch(0, 1)
        self.layout.setRowStretch(1, 1)
        self.layout.setRowStretch(2, 1)
        # Adding elements in the layout
        self.mini_camera = MiniCameraWidget(self.parent)
        self.layout.addWidget(self.mini_camera, 0, 0)
        self.acquisition_options = AcquisitionView(self.parent)
        self.layout.addWidget(self.acquisition_options, 1, 0)
        self.motors_options = MotorControlView(self.parent)
        self.layout.addWidget(self.motors_options, 2, 0)

        self.image1_widget = ImagesDisplayView()
        #self.layout.addWidget(self.image1_widget, 0, 1)
        self.image2_widget = ImagesDisplayView() #ImageDisplayGraph(self, '#90EE90', zoom=False)
        #self.layout.addWidget(self.image2_widget, 0, 2)

        self.image_oct_graph = ImagesDisplayView()
        #self.image_oct_graph = ImageDisplayGraph(self, '#48D1CC')
        self.live_widget = QWidget() #liveWidget()
        self.layout.addWidget(self.image_oct_graph, 1, 1, 2, 1)
        bits_depth = self.parent.image_bits_depth
        #self.image1_widget.set_bits_depth(bits_depth) - for ImageDispGraph
        #self.image2_widget.set_bits_depth(bits_depth)
        #self.image_oct_graph.set_bits_depth(bits_depth)

        # TO DELETE
        self.horizontalLayout = QHBoxLayout()
        image = np.random.normal(size=(100, 100))
        self.image1_widget.set_image_from_array(image) #, 'Image1')
        self.image2_widget.set_image_from_array(image) #, 'Image2')
        self.image_oct_graph.set_image_from_array(image) #, 'OCT')

        self.horizontalLayout.addWidget(self.image1_widget)
        self.horizontalLayout.addWidget(self.image2_widget)

        self.layout.addLayout(self.horizontalLayout, 0, 1)

        self.setLayout(self.layout)


    def update_size(self, aoi: bool = False):
        """
        Update the size of the main widget.
        """
        new_size = self.parent.size()
        width = new_size.width()
        height = new_size.height()
        wi = width//3
        he = height//3


if __name__ == '__main__':
    from PyQt6.QtWidgets import QApplication, QMainWindow

    class MyWindow(QMainWindow):
        def __init__(self):
            super().__init__()

            self.setWindowTitle(translate("window_title_main_menu_widget"))
            self.setGeometry(100, 200, 800, 600)

            self.central_widget = MainView(self)
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
    main.create_gui()
    main.show()
    sys.exit(app.exec())
