"""
CameraBaslerWidget class to integrate a Basler camera into a PyQt6 graphical interface.

.. module:: CameraBaslerWidget
   :synopsis: class to integrate a Basler camera into a PyQt6 graphical interface.

.. note:: LEnsE - Institut d'Optique - version 0.1

.. moduleauthor:: Julien VILLEMEJANE <julien.villemejane@institutoptique.fr>
"""

import sys
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget,
    QVBoxLayout,
    QLabel, QComboBox, QPushButton
)
from PyQt6.QtCore import pyqtSignal

from camera_list import CameraList
from camera_basler import CameraBasler, BaslerERROR, get_bits_per_pixel, get_converter_mode


class CameraBaslerListWidget(QWidget):
    """
    TO COMPLETE    
    
    :param cam_list: CameraList object that lists available cameras.
    :type cam_list: CameraList
    :param cameras_list: list of the available Basler Camera.
    :type cameras_list: list[tuple[int, str, str]]
    :param cameras_nb: Number of available cameras.
    :type cameras_nb: int
    :param cameras_list_combo: A QComboBox containing the list of the available cameras
    :type cameras_list_combo: QComboBox
    :param main_layout: Main layout container of the widget.
    :type main_layout: QVBoxLayout
    :param title_label: title displayed in the top of the widget.
    :type title_label: QLabel
    :param bt_connect: Graphical button to connect the selected camera
    :type bt_connect: QPushButton
    :param bt_refresh: Graphical button to refresh the list of available cameras.
    :type bt_refresh: QPushButton
    """
    
    connected_signal = pyqtSignal(str)
    
    def __init__(self) -> None:
        """
        Default constructor of the class.
        """
        super().__init__(parent=None) 
        # Objects linked to the CameraList object
        self.cam_list = CameraList()
        self.cameras_list = self.cam_list.get_cam_list()
        self.cameras_nb = self.cam_list.get_nb_of_cam()
        
        # Graphical list as QComboBox 
        self.cameras_list_combo = QComboBox()
        
        # Graphical elements of the interface
        self.main_layout = QVBoxLayout()    
    
        self.title_label = QLabel('Available cameras')
        
        self.bt_connect = QPushButton('Connect')
        self.bt_connect.clicked.connect(self.send_signal_connected)
        self.bt_refresh = QPushButton('Refresh')
        self.bt_refresh.clicked.connect(self.refresh_cameras_list_combo)
        
        if self.cameras_nb == 0:
            self.bt_connect.setEnabled(False)
        self.main_layout.addWidget(self.title_label)
        self.main_layout.addWidget(self.cameras_list_combo)
        self.main_layout.addWidget(self.bt_connect)
        self.main_layout.addWidget(self.bt_refresh)
        
        self.setLayout(self.main_layout)
        self.refresh_cameras_list_combo()

    
    def refresh_cameras_list(self):
        """
        Refresh the list of available cameras.
        
        Update the cameras_list parameter of this class.
        """       
        self.cam_list.refresh_list()
        self.cameras_list = self.cam_list.get_cam_list()
        self.cameras_nb = self.cam_list.get_nb_of_cam()
        if self.cameras_nb == 0:
            self.bt_connect.setEnabled(False)
        else:            
            self.bt_connect.setEnabled(True)
            
    
    def refresh_cameras_list_combo(self):
        """
        Refresh the combobox list of available cameras.
        
        Update the cameras_list_combo parameter of this class.
        """
        self.refresh_cameras_list()
        self.cameras_list_combo.clear()
        for cam in self.cameras_list:
            self.cameras_list_combo.addItem(f'BAS-{cam[1]}')

    def get_selected_camera_dev(self):
        """
        Return the device object from pypylon wraper of the selected camera.
        
        :return: the index number of the selected camera.
        :rtype: pylon.TlFactory
        """
        cam_id = self.cameras_list_combo.currentIndex()
        dev = self.cam_list.get_cam_device(cam_id)
        return dev
        
    def send_signal_connected(self):
        """
        Send a signal when a camera is selected to be used.
        """
        self.connected_signal.emit('C')


class CameraBaslerWidget(QWidget):
    """CameraBaslerWidget class, children of QWidget.
    
    Class to integrate a Basler camera into a PyQt6 graphical interface.
 
    :param cameras_list_widget: Widget containing a ComboBox with the list of available cameras.
    :type cameras_list_widget: CameraBaslerListWidget
    :param main_layout: Main layout container of the widget.
    :type main_layout: QVBoxLayout
    :param camera: Device to control
    :type camera: 
    
    .. note::
        
        The camera is initialized with the following parameters :
            
        * Exposure time = 
        * FPS = 
        * Black Level = 
        * Color Mode = 'Mono12' (if possible)
       
    TO DO : on the camera display : FPS + ExpoTime + BL + ColorMode  
     
    """
    
    def __init__(self) -> None:
        """
        Default constructor of the class.
        """
        super().__init__(parent=None)
        # List of the availables camera
        self.cameras_list_widget = CameraBaslerListWidget()
        self.main_layout = QVBoxLayout()
        self.main_layout.addWidget(self.cameras_list_widget)
        
        # Connect the signal emitted by the ComboList to its action
        self.cameras_list_widget.connected_signal.connect(self.connect_camera)

        # Camera
        self.camera = None

        self.setLayout(self.main_layout)    
        
    def connect_camera(self):
        """
        Triggered action by a connected signal from the combo list.
        """
        # Get the index of the selected camera
        cam_dev = self.cameras_list_widget.get_selected_camera_dev() 
        # Create Camera object
        self.camera = CameraBasler(cam_dev)
        # Initialize the camera with default parameters
        # Clear layout with combo list
        # Include the widget with the camera display
        print('Connected')

    def quit_application(self) -> None:
        """
        Quit properly the PyQt6 application window.
        """
        QApplication.instance().quit()



class MyMainWindow(QMainWindow):
    """MyMainWindow class, children of QMainWindow.
    
    Class to test the previous widget.

    """
    def __init__(self) -> None:
        """
        Default constructor of the class.
        """
        super().__init__()
        self.setWindowTitle("CameraBaslerWidet Test Window")
        self.setGeometry(100, 100, 400, 300)
        self.central_widget = CameraBaslerWidget()
        self.setCentralWidget(self.central_widget)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_window = MyMainWindow()
    main_window.show()
    sys.exit(app.exec())