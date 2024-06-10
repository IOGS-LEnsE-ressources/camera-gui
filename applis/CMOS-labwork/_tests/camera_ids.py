# -*- coding: utf-8 -*-
"""camera_ids file.

File containing :class::CameraIds
class to communicate with an IDS camera sensor.

.. module:: CameraIds
   :synopsis: class to communicate with an IDS camera sensor.

.. note:: LEnsE - Institut d'Optique - version 0.1

.. moduleauthor:: Julien VILLEMEJANE <julien.villemejane@institutoptique.fr>


.. warning::

    **IDS peak** (2.8 or higher) and **IDS Sofware Suite** (4.95 or higher) softwares
    are required on your computer.

    For old IDS camera, IDS peak must be installed in Custom mode with the Transport Layer option.

    **IDS peak IPL** (Image Processing Library) and **Numpy** are required.

.. note::

    To use old IDS generation of cameras (type UI), you need to install **IDS peak** in **custom** mode
    and add the **uEye Transport Layer** option.

.. note::

    **IDS peak IPL** can be found in the *IDS peak* Python API.

    Installation file is in the directory :file:`INSTALLED_PATH_OF_IDS_PEAK\generic_sdk\ipl\binding\python\wheel\x86_[32|64]`.

    Then run this command in a shell (depending on your python version and computer architecture):

    .. code-block:: bash

        pip install ids_peak_1.2.4.1-cp<version>-cp<version>m-[win32|win_amd64].whl

    Generally *INSTALLED_PATH_OF_IDS_PEAK* is :file:`C:\Program Files\IDS\ids_peak`

@ see : https://www.1stvision.com/cameras/IDS/IDS-manuals/en/index.html
@ See API DOC : C:\Program Files\IDS\ids_peak\generic_sdk\api\doc\html

# >>> ids_peak.Library.Initialize()
# >>> device_manager = ids_peak.DeviceManager.Instance()
# >>> device_manager.Update()
# >>> device_descriptors = device_manager.Devices()
# >>> my_cam_dev = device_descriptors[0].OpenDevice(ids_peak.DeviceAccessType_Exclusive)
# >>> my_cam = CameraIds(my_cam_dev)

"""

import numpy as np
import cv2
from ids_peak import ids_peak
import ids_peak_ipl.ids_peak_ipl as ids_ipl
from lensecam.ids.camera_ids_widget import CameraIdsListWidget

def get_bits_per_pixel(color_mode: str) -> int:
    """Return the number of bits per pixel.

    :param color_mode: color mode.
    :type color_mode: str
    :return: number of bits per pixel.
    :rtype: int

    """
    return {
        'Mono8': 8,
        'Mono10': 10,
        'Mono12': 12,
        'RGB8': 8
    }[color_mode]

def check_value_in(val: int, val_max: int, val_min: int = 0):
    """
    Check if a value is in a range.

    :param val: Value to check.
    :type val: int
    :param val_max: Maximum value of the range.
    :type val: int
    :param val_min: Minimum value of the range. Default 0.
    :type val: int

    :return: true if the coordinates are in the sensor area
    :rtype: bool

    """
    if val_min <= val <= val_max:
        return True
    else:
        return False


class CameraIds:

    def __init__(self, camera_device = None):
        """"""
        self.camera_device = camera_device
        self.camera_connected = False   # A camera device is connected
        self.camera_acquiring = False   # The camera is acquiring
        self.camera_remote = None
        self.data_stream = None

    def list_cameras(self):
        pass

    def find_first_camera(self) -> bool:
        """Create an instance with the first IDS available camera.

        :return: True if an IDS camera is connected.
        :rtype: bool
        """
        # Initialize library
        ids_peak.Library.Initialize()
        # Create a DeviceManager object
        device_manager = ids_peak.DeviceManager.Instance()
        try:
            # Update the DeviceManager
            device_manager.Update()
            # Exit program if no device was found
            if device_manager.Devices().empty():
                print("No device found. Exiting Program.")
                return False
            self.camera_device = device_manager.Devices()[0].OpenDevice(ids_peak.DeviceAccessType_Control)
            self.camera_connected = True
            return True
        except Exception as e:
            print('Exception - find_first_camera : {e}')

    def get_cam_info(self) -> tuple[str, str]:
        """Return the serial number and the name.

        :return: the serial number and the name of the camera
        :rtype: tuple[str, str]

        # >>> my_cam.get_cam_info
        ('40282239', 'a2A1920-160ucBAS')

        """
        serial_no, camera_name = None, None
        try:
            camera_name = self.camera_device.ModelName()
            serial_no = self.camera_device.SerialNumber()
            return serial_no, camera_name
        except Exception as e:
            print("Exception - get_cam_info: " + str(e) + "")

    def get_sensor_size(self) -> tuple[int, int]:
        """Return the width and the height of the sensor.

        :return: the width and the height of the sensor in pixels
        :rtype: tuple[int, int]

        # >>> my_cam.get_sensor_size()
        (1936, 1216)

        """
        try:
            max_height = self.camera_remote.FindNode("HeightMax").Value()
            max_width = self.camera_remote.FindNode("WidthMax").Value()
            return max_width, max_height
        except Exception as e:
            print("Exception - get_sensor_size: " + str(e) + "")

    def init_camera(self):
        """"""
        if self.camera_connected:
            self.camera_remote = device.RemoteDevice().NodeMaps()[0]

    def alloc_memory(self) -> bool:
        """Alloc the memory to get an image from the camera."""
        if self.camera_connected:
            data_streams = device.DataStreams()
            if data_streams.empty():
                print("No datastream available.")
                return False
            self.data_stream = data_streams[0].OpenDataStream()
            # Flush queue and prepare all buffers for revoking
            self.data_stream.Flush(ids_peak.DataStreamFlushMode_DiscardAll)
            # Clear all old buffers
            for buffer in self.data_stream.AnnouncedBuffers():
                self.data_stream.RevokeBuffer(buffer)
            payload_size = self.camera_remote.FindNode("PayloadSize").Value()
            # Get number of minimum required buffers
            num_buffers_min_required = self.data_stream.NumBuffersAnnouncedMinRequired()
            # Alloc buffers
            for count in range(num_buffers_min_required):
                buffer = self.data_stream.AllocAndAnnounceBuffer(payload_size)
                self.data_stream.QueueBuffer(buffer)
            self.camera_remote.FindNode("TriggerSelector").SetCurrentEntry("ExposureStart")
            self.camera_remote.FindNode("TriggerSource").SetCurrentEntry("Software")
            self.camera_remote.FindNode("TriggerMode").SetCurrentEntry("On")
            return True
        else:
            return False

    def free_memory(self) -> None:
        """
        Free memory containing the data stream.
        """
        self.data_stream = None

    def start_acquisition(self):
        """Start acquisition"""
        if self.camera_acquiring is False:
            self.data_stream.StartAcquisition(ids_peak.AcquisitionStartMode_Default)
            self.camera_remote.FindNode("TLParamsLocked").SetValue(1)
            self.camera_remote.FindNode("AcquisitionStart").Execute()
            self.camera_remote.FindNode("AcquisitionStart").WaitUntilDone()
            self.camera_acquiring = True

    def stop_acquisition(self):
        """Stop acquisition"""
        if self.camera_acquiring is True:
            self.camera_remote.FindNode("AcquisitionStop").Execute()
            self.camera_remote.FindNode("AcquisitionStop").WaitUntilDone()
            self.camera_remote.FindNode("TLParamsLocked").SetValue(0)
            self.data_stream.StopAcquisition()
            self.camera_acquiring = False

    def set_mode(self):
        """Set the mode of acquisition : Continuous or SingleFrame"""
        pass

    def get_image(self) -> np.ndarray:
        """Collect an image from the camera."""
        if self.camera_connected and self.camera_acquiring:
            # trigger image
            self.camera_remote.FindNode("TriggerSoftware").Execute()
            buffer = self.data_stream.WaitForFinishedBuffer(1000)
            # convert to RGB
            raw_image = ids_ipl.Image.CreateFromSizeAndBuffer(buffer.PixelFormat(), buffer.BasePtr(),
                                                              buffer.Size(), buffer.Width(), buffer.Height())
            self.data_stream.QueueBuffer(buffer)
            picture = raw_image.get_numpy_3D()
            return picture
        else:
            return None

    def get_exposure(self) -> float:
        """Return the exposure time in microseconds.

        :return: the exposure time in microseconds.
        :rtype: float

        # >>> my_cam.get_exposure()
        5000.0

        """
        try:
            return self.camera_remote.FindNode("ExposureTime").Value()
        except Exception as e:
            print("Exception - get exposure time: " + str(e) + "")

    def get_exposure_range(self) -> tuple[float, float]:
        """Return the range of the exposure time in microseconds.

        :return: the minimum and the maximum value
            of the exposure time in microseconds.
        :rtype: tuple[float, float]

        """
        try:
            exposure_min = self.camera_remote.FindNode("ExposureTime").Minimum()
            exposure_max = self.camera_remote.FindNode("ExposureTime").Maximum()
            return exposure_min, exposure_max
        except Exception as e:
            print("Exception - get range exposure time: " + str(e) + "")

    def set_exposure(self, exposure: float) -> bool:
        """Set the exposure time in microseconds.

        :param exposure: exposure time in microseconds.
        :type exposure: int

        :return: Return true if the exposure time changed.
        :rtype: bool
        """
        try:
            expo_min, expo_max = self.get_exposure_range()
            if check_value_in(exposure, expo_max, expo_min):
                self.camera_remote.FindNode("ExposureTime").SetValue(exposure)
                return True
            return False
        except Exception as e:
            print("Exception - set exposure time: " + str(e) + "")


    def __check_range(self, x: int, y: int) -> bool:
        """Check if the coordinates are in the sensor area.

        :param x: Coordinate to evaluate on X-axis.
        :type x: int
        :param y: Coordinate to evaluate on Y-axis.
        :type y: int

        :return: true if the coordinates are in the sensor area
        :rtype: bool

        """
        if 0 <= x <= self.width_max and 0 <= y <= self.height_max:
            return True
        else:
            return False



from PyQt6.QtCore import QThread, pyqtSignal

class CameraThread(QThread):
    """

    """
    image_acquired = pyqtSignal(np.ndarray)

    def __init__(self):
        super().__init__()
        self.running = False
        self.camera = None

    def set_camera(self, camera: CameraIds):
        """"""
        self.camera = camera

    def stop(self):
        if self.camera.camera_acquiring is True:
            self.running = False
            self.camera.stop_acquisition()
            self.camera.free_memory()

    def run(self):
        """
        Collect data from camera to display images.

        .. warning::

            The image must be in 8 bits mode for displaying !

        """
        try:
            if self.camera.camera_acquiring is False:
                print('First')
                self.camera.init_camera()
                self.camera.alloc_memory()
                self.camera.start_acquisition()
                self.running = True
            while self.running:
                image_array = self.camera.get_image()
                self.image_acquired.emit(image_array)
        except Exception as e:
            print(f'Thread Running - Exception - {e}')

from PyQt6.QtWidgets import QWidget, QPushButton, QLabel, QVBoxLayout, QGridLayout
from lensepy.images.conversion import resize_image_ratio, array_to_qimage

class CameraIdsWidget(QWidget):
    """CameraIdsWidget class, children of QWidget.

    Class to integrate an IDS camera into a PyQt6 graphical interface.

    :param cameras_list_widget: Widget containing a ComboBox with the list of available cameras.
    :type cameras_list_widget: CameraIdsListWidget
    :param main_layout: Main layout container of the widget.
    :type main_layout: QGridLayout
    :param camera: Device to control
    :type camera: CameraIds

    .. note::

        The camera is initialized with the following parameters :

        * Exposure time = 10 ms
        * FPS = 10
        * Black Level = 0
        * Color Mode = 'Mono12' (if possible)

    :param camera_display: Area to display the camera image
    :type camera_display: QLabel
    :param camera_infos: Area to display camera informations (FPS, expotime...)
    :type camera_infos: SmallParamsDisplay
    :param main_timer: timer object to manage display refresh
    :type main_timer: QTimer

    """
    connected = pyqtSignal(str)

    def __init__(self, camera: CameraIds = None, params_disp=False):
        super().__init__(parent=None)
        # Camera
        self.display_params = params_disp
        self.camera = camera
        # GUI
        self.initUI()

    def set_camera(self, camera: CameraIds):
        self.camera = camera

    def initUI(self):
        self.camera_display = QLabel('Image')
        self.layout = QGridLayout()
        self.layout.addWidget(self.camera_display)
        self.setLayout(self.layout)

        if self.camera is None:
            print('No Cam')
            self.cameras_list_widget = CameraIdsListWidget()
            self.layout.addWidget(self.cameras_list_widget, 0, 0)
            # Connect the signal emitted by the ComboList to its action
            self.cameras_list_widget.connected.connect(self.connect_camera)
        else:
            print('Camera OK')
            self.set_camera(camera=self.camera)

    def connect_camera(self, event):
        print(event)


class Remote(QWidget):
    """"""
    transmitted = pyqtSignal(str)

    def __init__(self, camera: CameraIds = None):
        super().__init__(parent=None)
        self.initUI()
        self.camera = camera

    def set_camera(self, camera: CameraIds):
        self.camera = camera
        self.camera.init_camera()
        self.camera.alloc_memory()

    def initUI(self):
        self.get_image_button = QPushButton('Get Image')
        self.get_image_button.clicked.connect(self.action_button)
        self.stop_acq_button = QPushButton('Stop Acq')
        self.stop_acq_button.clicked.connect(self.action_button)
        self.start_acq_button = QPushButton('Start Acq')
        self.start_acq_button.clicked.connect(self.action_button)
        self.expo_button = QPushButton('Expo')
        self.expo_button.clicked.connect(self.action_button)

        self.layout = QVBoxLayout()
        self.layout.addWidget(self.get_image_button)
        self.layout.addWidget(self.start_acq_button)
        self.layout.addWidget(self.stop_acq_button)
        self.layout.addWidget(self.expo_button)

        self.setLayout(self.layout)

    def action_button(self, event):
        button = self.sender()
        if button == self.get_image_button:
            self.transmitted.emit('get')
        if button == self.start_acq_button:
            self.transmitted.emit('start')
        if button == self.stop_acq_button:
            self.transmitted.emit('stop')
        if button == self.expo_button:
            self.transmitted.emit('expo')


from PyQt6.QtWidgets import QMainWindow
from PyQt6.QtGui import QImage, QPixmap

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

        self.camera_thread = CameraThread()
        self.camera_thread.image_acquired.connect(self.update_image)

    def initUI(self):
        self.setWindowTitle("IDS Camera Display")
        self.setGeometry(100, 100, 800, 600)

        self.layout = QGridLayout()
        self.camera_widget = None
        self.remote = Remote()
        self.remote.transmitted.connect(self.action_remote)
        self.layout.addWidget(self.remote, 2, 0)

        self.central_widget = QWidget()
        self.central_widget.setLayout(self.layout)
        self.setCentralWidget(self.central_widget)

    def action_remote(self, event):
        if event == 'get':
            try:
                self.camera_widget.camera.init_camera()
                self.camera_widget.camera.alloc_memory()
                self.camera_widget.camera.start_acquisition()
                raw_array = self.camera_widget.camera.get_image()
                self.camera_widget.camera.stop_acquisition()
                self.camera_widget.camera.free_memory()
                # Depending on the color mode - display only in 8 bits mono
                nb_bits = 8 #get_bits_per_pixel(self.camera.get_color_mode())
                if nb_bits > 8:
                    image_array = raw_array.view(np.uint16)
                    image_array_disp = (image_array / (2 ** (nb_bits - 8))).astype(np.uint8)
                else:
                    image_array = raw_array.view(np.uint8)
                    image_array_disp = image_array.astype(np.uint8)
                frame_width = self.camera_widget.width()
                frame_height = self.camera_widget.height()
                # Resize to the display size
                image_array_disp2 = resize_image_ratio(
                        image_array_disp,
                        frame_width,
                        frame_height)
                # Convert the frame into an image
                image = array_to_qimage(image_array_disp2)
                pmap = QPixmap(image)
                # display it in the cameraDisplay
                self.camera_widget.camera_display.setPixmap(pmap)
            except Exception as e:
                print("Exception - action_get_image: " + str(e) + "")
        elif event == 'start':
            print('Start')
            self.camera_thread.start()
        elif event == 'stop':
            print('Stop')
            self.camera_widget.camera.set_exposure(10000)
            self.camera_thread.stop()
        elif event == 'expo':
            print(f'Expo {self.camera_widget.camera.get_exposure()}')
            self.camera_widget.camera.set_exposure(20000)

    def set_camera(self, camera: CameraIds):
        """

        """
        self.camera_thread.set_camera(camera)
        self.camera_widget = CameraIdsWidget(camera)
        self.layout.addWidget(self.camera_widget, 1, 0)

    def update_image(self, image_array):
        try:
            frame_width = self.camera_widget.width()
            frame_height = self.camera_widget.height()
            # Resize to the display size
            image_array_disp2 = resize_image_ratio(
                image_array,
                frame_width,
                frame_height)
            # Convert the frame into an image
            image = array_to_qimage(image_array_disp2)
            pmap = QPixmap(image)
            # display it in the cameraDisplay
            self.camera_widget.camera_display.setPixmap(pmap)
        except Exception as e:
            print(f'Exception - update_image {e}')

    def closeEvent(self, event):
        self.camera_thread.stop()
        event.accept()

if __name__ == "__main__":
    import sys
    from PyQt6.QtWidgets import QApplication

    camera_ids = CameraIds()
    if camera_ids.find_first_camera():
        print(f'Camera OK')
        device = camera_ids.camera_device

    # Test with a Thread
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.set_camera(camera_ids)
    main_window.show()
    sys.exit(app.exec())


    ''' # Test image by image
    try:
        print(camera_ids.get_cam_info())
        camera_ids.init_camera()
        camera_ids.alloc_memory()

        numberOfImagesToGrab = 2
        camera_ids.start_acquisition()

        for k in range(numberOfImagesToGrab):
            raw_image = camera_ids.get_image()
            color_image = raw_image.ConvertTo(ids_ipl.PixelFormatName_Mono8)
            picture = color_image.get_numpy_3D()
            picture_shape = picture.shape
            # Access the image data.
            print("SizeX: ", picture_shape[1])
            print("SizeY: ", picture_shape[0])
            print("Gray value of first pixel: ", picture[0, 0])

            cv2.imshow('image', picture)
            cv2.waitKey(0)
            cv2.destroyAllWindows()

        camera_ids.stop_acquisition()
        camera_ids.free_memory()

    except Exception as e:
        print("EXCEPTION: " + str(e))

    finally:
        ids_peak.Library.Close()

    '''