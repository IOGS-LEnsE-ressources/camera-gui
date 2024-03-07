"""
camera_basler_widget file that contains :

    * :class::CameraBaslerWidget to integrate a Basler camera into a PyQt6 graphical interface.
    * :class::CameraBaslerListWidget to generate a Widget including the list of available camerasintegrate a Basler camera into a PyQt6 graphical interface.
    * :class::CameraBaslerParamsWidget to display the parameters of a camera.
    * :class::SmallParamsDisplay to ...

.. module:: CameraBaslerWidget
   :synopsis: class to integrate a Basler camera into a PyQt6 graphical interface.

.. note:: LEnsE - Institut d'Optique - version 0.1

.. moduleauthor:: Julien VILLEMEJANE <julien.villemejane@institutoptique.fr>
"""

import sys
import time
import numpy as np
import cv2

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget,
    QVBoxLayout, QGridLayout,
    QLabel, QComboBox, QPushButton,
    QMessageBox
)
from PyQt6.QtCore import pyqtSignal, QTimer
from PyQt6.QtGui import QImage, QPixmap

from camera_list import CameraList
from camera_basler import CameraBasler, get_bits_per_pixel


class CameraBaslerListWidget(QWidget):
    """
    Generate a Widget including the list of available cameras and two buttons :
        * connect : to connect a selected camera ;
        * refresh : to refresh the list of available cameras.
    
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



class CameraBaslerParamsWidget(QWidget):
    """CameraBaslerWidget class, children of QWidget.
    
    Class to display and to change the available parameters of a camera.
    
    :param parent: Parent widget of this widget.
    :type parent: SmallParamsDisplay
    :param camera: Device to control
    :type camera: pylon.TlFactory    
    
    """
    def __init__(self, parent):
        """
        Default constructor of the class.
        
        :param parent: Parent widget of this widget.
        :type parent: SmallParamsDisplay
        """
        super().__init__(parent=None)
        self.parent = parent
        # Camera device
        self.camera = None
        # Main layout
        self.main_layout = QVBoxLayout()
        # Graphical objects
        self.test_label = QLabel('NEW WINDOW !!')
        self.main_layout.addWidget(self.test_label)
        
        self.setFixedSize(400, 300)
        self.setLayout(self.main_layout)


    def set_camera(self, camera) -> None:
        """
        Set the camera device to setup.
        
        :param camera: Device to control
        :type camera: pylon.TlFactory        
        """
        self.camera = camera
        
        
    def closeEvent(self, event):
        """
        closeEvent redefinition. Use when the user clicks 
        on the red cross to close the window
        """
        reply = QMessageBox.question(self, 'Quit', 'Do you really want to close ?', 
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, 
                                     QMessageBox.StandardButton.No)

        if reply == QMessageBox.StandardButton.Yes:
            event.accept()  # L'utilisateur a confirmé la fermeture
        else:
            event.ignore()  # L'utilisateur a annulé la fermeture


class SmallParamsDisplay(QWidget):
    """
    Area to display main parameters of the camera.
    
    :param parent: Parent widget of this widget.
    :type parent: CameraBaslerWidget
    :param camera: Device to control
    :type camera: pylon.TlFactory
    :param small_layout: Layout of the widget
    :type small_layout: QGridLayout
    :param camera_name_label: Label to display the name of the camera.
    :type camera_name_label: QLabel
    :param camera_colormode_label: Label to display the color mode of the camera.
    :type camera_colormode_label: QLabel
    :param camera_expotime_label: Label to display the exposure time of the camera.
    :type camera_expotime_label: QLabel
    :param camera_fps_label: Label to display the frame rate of the camera.
    :type camera_fps_label: QLabel    
    """
    def __init__(self, parent) -> None:
        """
        Default constructor of the class.
        
        :param parent: Parent widget of this widget.
        :type parent: CameraBaslerWidget
        """
        super().__init__(parent=None)
        self.parent = parent
        # Camera device
        self.camera = None
        # Layout Grid
        self.small_layout = QGridLayout()
        self.small_layout.setSpacing(20)
        # Internal Widgets
        self.camera_name_label = QLabel('Name')
        self.camera_colormode_label = QLabel('ColorMode')
        self.camera_expotime_label = QLabel('Exposure')
        self.camera_fps_label = QLabel('FPS')
        self.params_button = QPushButton('Parameters')
        self.params_button.clicked.connect(self.params_button_action)
        # Add widgets to the layout
        self.small_layout.addWidget(self.camera_name_label, 0, 0, 1, 2)
        self.small_layout.addWidget(self.params_button, 0, 2)
        self.small_layout.addWidget(self.camera_colormode_label, 1, 0)
        self.small_layout.addWidget(self.camera_expotime_label, 1, 1)
        self.small_layout.addWidget(self.camera_fps_label, 1, 2)
        # All the grid box have the same width
        for i in range(self.small_layout.columnCount()):
            self.small_layout.setColumnStretch(i, 1)
        
        self.setLayout(self.small_layout)
    
    def set_camera(self, camera) -> None:
        """
        Set the camera device to setup.
        
        :param camera: Device to control
        :type camera: pylon.TlFactory        
        """
        self.camera = camera
    
    def update_params(self) -> None:
        """
        Update the display of the parameters
        """
        _, name = self.camera.get_cam_info()
        name = 'Camera : '+name 
        self.camera_name_label.setText(name)
        colormode = self.camera.get_color_mode()
        self.camera_colormode_label.setText(colormode)
        expo = str(self.camera.get_exposure()/1000)+' ms'
        self.camera_expotime_label.setText(expo)
        fps = str(self.camera.get_frame_rate())+' fps'
        self.camera_fps_label.setText(fps)
        print('Update Params')
    
    def params_button_action(self):
        """
        Call when the parameters button is clicked.
        Open a new window to modify the camera parameters.
        """
        print('PARAMS')
        self.params_window = CameraBaslerParamsWidget(self)
        self.params_window.set_camera(self.camera)
        self.params_window.show()


class CameraBaslerWidget(QWidget):
    """CameraBaslerWidget class, children of QWidget.
    
    Class to integrate a Basler camera into a PyQt6 graphical interface.
 
    :param cameras_list_widget: Widget containing a ComboBox with the list of available cameras.
    :type cameras_list_widget: CameraBaslerListWidget
    :param main_layout: Main layout container of the widget.
    :type main_layout: QGridLayout
    :param camera: Device to control
    :type camera: pylon.TlFactory
    
    .. note::
        
        The camera is initialized with the following parameters :
            
        * Exposure time = 100 ms
        * FPS = 20
        * Black Level = 0
        * Color Mode = 'Mono12' (if possible)
     
    :param camera_display: Area to display the camera image
    :type camera_display: QLabel
    :param camera_infos: Area to display camera informations (FPS, expotime...)
    :type camera_infos: SmallParamsDisplay
    :param main_timer: timer object to manage display refresh
    :type main_timer: QTimer
    
    """
    
    def __init__(self) -> None:
        """
        Default constructor of the class.
        """
        super().__init__(parent=None)
        # List of the availables camera
        self.cameras_list_widget = CameraBaslerListWidget()
        self.main_layout = QGridLayout()
        self.main_layout.addWidget(self.cameras_list_widget, 0, 0)
        
        # Connect the signal emitted by the ComboList to its action
        self.cameras_list_widget.connected_signal.connect(self.connect_camera)

        # Camera
        self.camera = None
        
        # Graphical objects
        self.camera_display = QLabel('Test')
        self.camera_infos = SmallParamsDisplay(self)
        
        # Time management
        self.main_timer = QTimer()
        self.main_timer.stop()
        self.main_timer.setInterval(100) # in ms
        self.main_timer.timeout.connect(self.refresh)

        self.setLayout(self.main_layout)    
        
        
    def connect_camera(self) -> None:
        """
        Trigger action when a connected signal from the combo list is emitted.
        """
        # Get the index of the selected camera
        cam_dev = self.cameras_list_widget.get_selected_camera_dev() 
        # Create Camera object
        self.camera = CameraBasler(cam_dev)
        # Initialize the camera with default parameters
        self.camera.set_exposure(100000)
        self.camera.set_color_mode('Mono8')
        self.camera.set_frame_rate(20)
        self.camera.set_black_level(0)
        # Clear layout with combo list
        self.clear_layout()
        # Include the widget with the camera display
        self.main_layout.addWidget(self.camera_display, 0, 0)
        self.main_layout.setRowStretch(0, 4)
        self.main_layout.addWidget(self.camera_infos, 1, 0)
        self.main_layout.setRowStretch(1, 1)
        self.camera_infos.set_camera(self.camera)
        self.camera_infos.update_params()
        # Start main timer
        fps = self.camera.get_frame_rate()
        time_ms = int(1000/fps + 10) # 10 ms extra time
        self.main_timer.setInterval(time_ms) # in ms
        self.main_timer.start()
        self.refresh()
        print('Connected')
        
        
    def is_connected(self) -> bool:
        """
        Test if a camera is connected.
        
        :return: True if a camera is connected.
        :rtype: bool
        """
        if self.camera is None:
            return False
        else:
            return True
    
    
    def clear_layout(self) -> None:
        """
        Clear the main layout of the Widget.
        
        .. note::
            
            This function is used to display camera image instead of the camera
            list when a camera is selected and the user clicks on the connect
            button.
            
        """
        count = self.main_layout.count()
        for i in reversed(range(count)):
            item = self.main_layout.itemAt(i)
            widget = item.widget()
            widget.deleteLater()
    
    
    def resize_image(self, im_array: numpy.ndarray, new_width: int, new_height: int) ->  numpy.ndarray:
        """
        Resize array containing image at a new size.

        :param im_array: Initial array to resize.
        :type im_array: numpy.ndarray
        :param new_width: Width of the new array.
        :type new_width: int        
        :param new_height: Height of the new array.
        :type new_height: int
        :return: Resized array.
        :rtype: numpy.ndarray

        """
        resized_image = cv2.resize(im_array, 
                        dsize=(new_width, new_height), 
                        interpolation=cv2.INTER_CUBIC)
        return resized_image
    
    
    def array_to_qimage(self, array: numpy.ndarray) -> QImage:
        """
        Transcode an array to a QImage.
        
        :param array: Array containing image data.
        :type array: numpy.ndarray
        :return: Image to display.
        :rtype: QImage

        """
        shape_size = len(array.shape)
        if shape_size == 2:
            height, width = array.shape
        else:
            height, width, _ = array.shape
        print(f'W={width}')
        bytes_per_line = width # only in 8 bits gray 
    
        return QImage(array, width, height, bytes_per_line, QImage.Format.Format_Grayscale8)
        

    def refresh(self) -> None:
        """
        Refresh the image from camera.
        
        .. note::
            
            This function is called by a QTimer event
            according to the FPS rate.
        
        """
        
        if self.is_connected() :
            # Get raw image
            image_array = self.camera.get_images()[0]
            # Get widget size
            frame_width = self.width() - 30
            frame_height = self.height() - 120
            print(f'FW={frame_width} * FH={frame_height}')
            
            # Depending on the color mode - display only in 8 bits mono
            nb_bits = get_bits_per_pixel(self.camera.get_color_mode())
            print(f'Nb bits = {nb_bits}')
            if nb_bits > 8:
                image_array = image_array.view(np.uint16)
                image_array_disp = (image_array / (2**(nb_bits-8))).astype(np.uint8)
            else:
                image_array = image_array.view(np.uint8)
                image_array_disp = image_array.astype(np.uint8)
            
            print(type(image_array_disp[0,0]))
            
            # Resize to the display size
            image_array_disp2 = self.resize_image(
                image_array_disp, 
                frame_width, 
                frame_height)
            # Convert the frame into an image
            image = self.array_to_qimage(image_array_disp2)
            print(f'W = {image.width()}')
            pmap = QPixmap(image)

            # display it in the cameraDisplay
            self.camera_display.setPixmap(pmap)
        else:
            self.camera_display.setText('No Camera Connected')



    def quit_application(self) -> None:
        """
        Quit properly the PyQt6 application window.
        """
        if self.main_timer.isActive():
            self.main_timer.stop()
            print('OK STOP')
        time.sleep(0.5)
        self.camera.disconnect()
        print('DISCONNECTED')
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


    def closeEvent(self, event):
        """
        closeEvent redefinition. Use when the user clicks 
        on the red cross to close the window
        """
        reply = QMessageBox.question(self, 'Quit', 'Do you really want to close ?', 
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, 
                                     QMessageBox.StandardButton.No)

        if reply == QMessageBox.StandardButton.Yes:
            self.central_widget.quit_application()
            event.accept()  # L'utilisateur a confirmé la fermeture
        else:
            event.ignore()  # L'utilisateur a annulé la fermeture



if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_window = MyMainWindow()
    main_window.show()
    sys.exit(app.exec())