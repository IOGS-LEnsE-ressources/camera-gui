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
import sys
import numpy as np
# IDS peak API
from ids_peak import ids_peak
import ids_peak_ipl.ids_peak_ipl as ids_ipl


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


def get_converter_mode(color_mode: str) -> int:
    """Return the converter display mode.

    :param color_mode: color mode of the camera
        ('Mono8', 'Mono10', 'Mono12' or 'RGB8')
    :type color_mode: str
    :return: corresponding converter display mode
    :rtype: int

    """
    return {
        "Mono8": ids_ipl.PixelFormatName_Mono8,
        "Mono10": ids_ipl.PixelFormatName_Mono10,
        "Mono12": ids_ipl.PixelFormatName_Mono12,
        "RGB8": ids_ipl.PixelFormatName_RGB8
    }[color_mode]


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


class CameraIds:
    """Class to communicate with an IDS camera sensor.

    :param camera: Camera object that can be controlled.
    :type camera: ids_peak.Device

    TO COMPLETE

    .. note::

        In the context of this driver,
        the following color modes are available :

        * 'Mono8' : monochromatic mode in 8 bits raw data
        * 'Mono10' : monochromatic mode in 10 bits raw data
        * 'Mono12' : monochromatic mode in 12 bits raw data
        * 'RGB8' : RGB mode in 8 bits raw data

    """

    def __init__(self, cam_dev: ids_peak.Device) -> None:
        """Initialize the object."""
        # Camera device
        self.camera = cam_dev
        self.camera_remote = self.create_remote()
        self.data_stream = None
        self.is_opened = False
        # Camera informations
        self.serial_no, self.camera_name = self.get_cam_info()
        self.width_max, self.height_max = self.get_sensor_size()

        self.nb_bits_per_pixels: int = 0
        self.color_mode = 'Mono8'  # default
        self.set_color_mode('Mono8')
        # self.set_display_mode('Mono8')

        # AOI size
        self.aoi_x0: int = 0
        self.aoi_y0: int = 0
        self.aoi_width: int = self.width_max
        self.aoi_height: int = self.height_max
        self.set_aoi(self.aoi_x0, self.aoi_y0, self.aoi_width, self.aoi_height)

        if self.alloc_memory():
            print('Alloc OK')
        self.trigger()

    def create_remote(self):
        try:
            remote = self.camera.RemoteDevice().NodeMaps()[0]
            return remote
        except Exception as e:
            print("Exception - create_remote: " + str(e) + "")
            
    def trigger(self):        
        # Software trigger of the camera
        try:
            self.camera_remote.FindNode("TriggerSelector").SetCurrentEntry("ExposureStart")
            self.camera_remote.FindNode("TriggerSource").SetCurrentEntry("Software")
            self.camera_remote.FindNode("TriggerMode").SetCurrentEntry("On")
        except Exception as e:
            print("Exception - trigger: " + str(e) + "")

    def free_memory(self) -> None:
        """
        Free memory containing the data stream.
        """
        self.data_stream = None

    def alloc_memory(self) -> bool:
        """
        Prepare memory for image acquisition.
        """
        try:
            # Preparing image acquisition - buffers
            data_streams = self.camera.DataStreams()
            if data_streams.empty():
                print("No datastream available.")
            self.data_stream = data_streams[0].OpenDataStream()
            nodemapDataStream = self.data_stream.NodeMaps()[0]

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
        except Exception as e:
            print("EXCEPTION - alloc_memory: " + str(e))

    def is_camera_connected(self) -> bool:
        """Return the status of the device.

        :return: true if the device could be opened, and then close the device
        :rtype: bool (or error)

        # >>> my_cam.is_camera_connected()

        """
        try:
            value = self.camera_remote.FindNode("DeviceLinkSpeed").Value()
            if value > 1:
                return True
            else:
                return False
        except Exception as e:
            print("Exception: " + str(e) + "")

    def start_acquisition(self) -> bool:
        """
        Start Acquisition of images.
        """
        try:
            self.data_stream.StartAcquisition(ids_peak.AcquisitionStartMode_Default)
            self.camera_remote.FindNode("TLParamsLocked").SetValue(1)
            self.camera_remote.FindNode("AcquisitionStart").Execute()
            self.camera_remote.FindNode("AcquisitionStart").WaitUntilDone()
            self.is_opened = True
            return True
        except Exception as e:
            str_error = str(e)
            return False

    def stop_acquisition(self) -> bool:
        """Disconnect the camera."""
        try:
            if self.is_opened:
                self.camera_remote.FindNode("AcquisitionStop").Execute()
                self.camera_remote.FindNode("AcquisitionStop").WaitUntilDone()
                self.camera_remote.FindNode("TLParamsLocked").SetValue(0)
                self.data_stream.StopAcquisition()
                self.is_opened = False
            return True
        except Exception as e:
            print("Exception - stop Acq: " + str(e) + "")

    def disconnect(self) -> None:
        """Disconnect the camera.
        """
        self.stop_acquisition()
        self.free_memory()

    def get_cam_info(self) -> tuple[str, str]:
        """Return the serial number and the name.

        :return: the serial number and the name of the camera
        :rtype: tuple[str, str]

        # >>> my_cam.get_cam_info
        ('40282239', 'a2A1920-160ucBAS')

        """
        serial_no, camera_name = None, None
        try:
            camera_name = self.camera.DisplayName()
            serial_no = self.camera_remote.FindNode("DeviceSerialNumber").Value()
            return serial_no, camera_name
        except Exception as e:
            print("Exception - get_info_cam: " + str(e) + "")

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

    def set_display_mode(self, colormode: str = 'Mono8') -> None:
        """Change the color mode of the converter.

        :param colormode: Color mode to use for the device
        :type colormode: str, default 'Mono8'

        """
        '''
        mode_converter = get_converter_mode(colormode)
        try:
            self.converter.OutputPixelFormat = mode_converter
        except:
            raise IdsError("set_display_mode")
        '''
        pass

    def get_color_mode(self):
        """Get the color mode.

        :param colormode: Color mode to use for the device
        :type colormode: str, default 'Mono8'

        # >>> my_cam.get_color_mode()
        'Mono8'

        """
        try:
            # Test if the camera is opened
            if self.is_opened:
                self.stop_acquisition()
            pixel_format = self.camera_remote.FindNode("PixelFormat").CurrentEntry().SymbolicValue()
            self.color_mode = pixel_format
            return pixel_format
        except Exception as e:
            print("Exception - get_color_mode: " + str(e) + "")

    def set_color_mode(self, color_mode: str) -> None:
        """Change the color mode.

        :param color_mode: Color mode to use for the device
        :type color_mode: str, default 'Mono8'

        """
        try:
            if self.is_opened:
                self.stop_acquisition()
            self.camera_remote.FindNode("PixelFormat").SetCurrentEntry(color_mode)
            self.color_mode = color_mode
            self.nb_bits_per_pixels = get_bits_per_pixel(color_mode)
            # self.set_display_mode(color_mode)
        except Exception as e:
            print("Exception - set_color_mode: " + str(e) + "")

    def get_image(self) -> np.ndarray:
        """Get one image.

        :return: Array of the image.
        :rtype: array

        """
        try:
            # trigger image
            self.camera_remote.FindNode("TriggerSoftware").Execute()
            buffer = self.data_stream.WaitForFinishedBuffer(1000)
            # convert to RGB
            raw_image = ids_ipl.Image.CreateFromSizeAndBuffer(
                buffer.PixelFormat(),
                buffer.BasePtr(),
                buffer.Size(),
                buffer.Width(),
                buffer.Height())
            self.data_stream.QueueBuffer(buffer)
            picture = raw_image.get_numpy_3D()
            return picture

        except Exception as e:
            print("EXCEPTION - get_image: " + str(e))
            ids_peak.Library.Close()
            return -2

    def get_images(self, nb_images:int = 1) -> list:
        """Return a list of nb_images images.

        :param nb_images: Number of images to collect. Default 1.
        :type nb_images: int

        """
        images = []
        for i in range(nb_images):
            images.append(self.get_image())
        return images

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

    def set_aoi(self, x0, y0, w, h) -> bool:
        """Set the area of interest (aoi).

        :param x0: coordinate on X-axis of the top-left corner of the aoi must be dividable without rest by Inc = 4.
        :type x0: int
        :param y0: coordinate on X-axis of the top-left corner of the aoi must be dividable without rest by Inc = 4.
        :type y0: int
        :param w: width of the aoi
        :type w: int
        :param h: height of the aoi
        :type h: int
        :return: True if the aoi is modified
        :rtype: bool

        """
        if self.__check_range(x0, y0) is False or self.__check_range(x0 + w, y0 + h) is False:
            return False
        print(f'X0={x0}/Y0={y0} - H={h}/W={w}')
        self.aoi_x0 = x0
        self.aoi_y0 = y0
        self.aoi_width = w
        self.aoi_height = h

        # Get the minimum ROI and set it. After that there are no size restrictions anymore
        x_min = self.camera_remote.FindNode("OffsetX").Minimum()
        y_min = self.camera_remote.FindNode("OffsetY").Minimum()
        w_min = self.camera_remote.FindNode("Width").Minimum()
        h_min = self.camera_remote.FindNode("Height").Minimum()

        self.camera_remote.FindNode("OffsetX").SetValue(x_min)
        self.camera_remote.FindNode("OffsetY").SetValue(y_min)
        self.camera_remote.FindNode("Width").SetValue(w_min)
        self.camera_remote.FindNode("Height").SetValue(h_min)

        # Set the new values
        self.camera_remote.FindNode("OffsetX").SetValue(self.aoi_x0)
        self.camera_remote.FindNode("OffsetY").SetValue(self.aoi_y0)
        self.camera_remote.FindNode("Width").SetValue(self.aoi_width)
        self.camera_remote.FindNode("Height").SetValue(self.aoi_height)
        return True

    def get_aoi(self) -> tuple[int, int, int, int]:
        """Return the area of interest (aoi).

        :return: [x0, y0, width, height] x0 and y0 are the
            coordinates of the top-left corner and width
            and height are the size of the aoi.
        :rtype: tuple[int, int, int, int]

        # >>> my_cam.get_aoi()
        (0, 0, 1936, 1216)

        """
        self.aoi_x0 = self.camera_remote.FindNode("OffsetX").Value()
        self.aoi_y0 = self.camera_remote.FindNode("OffsetY").Value()
        self.aoi_width = self.camera_remote.FindNode("Width").Value()
        self.aoi_height = self.camera_remote.FindNode("Height").Value()
        return self.aoi_x0, self.aoi_y0, self.aoi_width, self.aoi_height

    def reset_aoi(self) -> bool:
        """Reset the area of interest (aoi).

        Reset to the limit of the camera.

        :return: True if the aoi is modified
        :rtype: bool

        # >>> my_cam.reset_aoi()
        True

        """
        self.aoi_x0 = 0
        self.aoi_y0 = 0
        self.aoi_width = self.width_max
        self.aoi_height = self.height_max
        print(self.set_aoi(self.aoi_x0, self.aoi_y0,
                           self.width_max, self.height_max))

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

    def get_frame_rate(self) -> float:
        """Return the frame rate.

        :return: the frame rate.
        :rtype: float

        # >>> my_cam.get_frame_rate()
        100.0

        """
        try:
            return self.camera_remote.FindNode("AcquisitionFrameRate").Value()
        except Exception as e:
            print("Exception - get frame rate: " + str(e) + "")

    def get_frame_rate_range(self) -> tuple[float, float]:
        """Return the range of the frame rate in frames per second.

        :return: the minimum and the maximum value
            of the frame rate in frames per second.
        :rtype: tuple[float, float]

        """
        try:
            frame_rate_min = self.camera_remote.FindNode("AcquisitionFrameRate").Minimum()
            frame_rate_max = self.camera_remote.FindNode("AcquisitionFrameRate").Maximum()
            return frame_rate_min, frame_rate_max
        except Exception as e:
            print("Exception - get range frame rate: " + str(e) + "")

    def set_frame_rate(self, fps: float) -> bool:
        """Set the frame rate in frames per second.

        :param fps: frame rate in frames per second.
        :type fps: float

        :return: Return true if the frame rate changed.
        :rtype: bool
        """
        try:
            fps_min, fps_max = self.get_frame_rate_range()
            if check_value_in(fps, fps_max, fps_min):
                self.camera_remote.FindNode("AcquisitionFrameRate").SetValue(fps)
                return True
            return False
        except Exception as e:
            print("Exception - set frame rate: " + str(e) + "")

    def get_black_level(self) -> float:
        """Return the black level.

        :return: the black level in gray scale.
        :rtype: float

        # >>> my_cam.get_black_level()
        100.0

        """
        try:
            return self.camera_remote.FindNode("BlackLevel").Value()
        except Exception as e:
            print("Exception - get black level: " + str(e) + "")

    def get_black_level_range(self) -> tuple[float, float]:
        """Return the range of the black level in gray scale.

        :return: the minimum and the maximum value
            of the black level in gray scale.
        :rtype: tuple[float, float]

        """
        try:
            bl_min = self.camera_remote.FindNode("BlackLevel").Minimum()
            bl_max = self.camera_remote.FindNode("BlackLevel").Maximum()
            return bl_min, bl_max
        except Exception as e:
            print("Exception - get range black level: " + str(e) + "")

    def set_black_level(self, black_level: int) -> bool:
        """Set the black level of the camera.

        :param black_level: Black level in gray intensity.
        :type black_level: int

        :return: Return true if the black level changed.
        :rtype: bool
        """
        try:
            bl_min, bl_max = self.get_black_level_range()
            if check_value_in(black_level, bl_max, bl_min):
                self.camera_remote.FindNode("BlackLevel").SetValue(black_level)
                return True
            return False
        except Exception as e:
            print("Exception - set frame rate: " + str(e) + "")


if __name__ == "__main__":
    import cv2

    # Initialize library
    ids_peak.Library.Initialize()
    # Device manager
    device_manager = ids_peak.DeviceManager.Instance()
    device_manager.Update()
    device_descriptors = device_manager.Devices()
    # Open a device
    if device_descriptors.empty():
        sys.exit(-1)
    my_cam_dev = device_descriptors[0].OpenDevice(ids_peak.DeviceAccessType_Exclusive)

    my_cam = CameraIds(my_cam_dev)
    my_cam.start_acquisition()
    raw_image = my_cam.get_image()
    cv2.imshow('image', raw_image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

    print(f'isOpened ?? {my_cam.is_opened}')
    print(f'W/H = {my_cam.get_sensor_size()}')
    print(f'isOpened ?? {my_cam.is_opened}')


    if my_cam.stop_acquisition():
        print(f'Acq Stopped')

    # Change exposure time
    print(f'Old Expo = {my_cam.get_exposure()}')
    my_cam.set_exposure(10000)
    print(f'New Expo = {my_cam.get_exposure()}')

    if my_cam.set_aoi(20, 40, 100, 200):
        print('AOI OK')
    my_cam.free_memory()
    my_cam.alloc_memory()
    my_cam.trigger()

    if my_cam.start_acquisition():
        print(f'Acq Started')
    print(f'Run ? {my_cam.is_opened}')
    picture = my_cam.get_image()
    cv2.imshow('image', picture)
    cv2.waitKey(0)
    cv2.destroyAllWindows()


    '''
    print(f'FPS = {my_cam.get_frame_rate()}')
    print(f'FPS_range = {my_cam.get_frame_rate_range()}')
    print(f'FPS change ? {my_cam.set_frame_rate(10)}')
    print(f'FPS = {my_cam.get_frame_rate()}')
    print(f'Black Level = {my_cam.get_black_level()}')
    print(f'Black Level_range = {my_cam.get_black_level_range()}')
    print(f'Black Level change ? {my_cam.set_black_level(25)}')
    print(f'Black Level = {my_cam.get_black_level()}')


    '''
    '''
    # Different exposure time
    my_cam.reset_aoi()
    
    t_expo = np.linspace(t_min, t_max/10000.0, 11)
    for i, t in enumerate(t_expo):
        print(f'\tExpo Time = {t}us')
        my_cam.set_exposure(t)
        images = my_cam.get_images()
        plt.imshow(images[0], interpolation='nearest')
        plt.show()        
    '''

    '''
    from camera_list import CameraList

    # Create a CameraList object
    cam_list = CameraList()
    # Print the number of camera connected
    print(f"Test - get_nb_of_cam : {cam_list.get_nb_of_cam()}")
    # Collect and print the list of the connected cameras
    cameras_list = cam_list.get_cam_list()
    print(f"Test - get_cam_list : {cameras_list}")

    cam_id = 'a'
    while cam_id.isdigit() is False:
        cam_id = input('Enter the ID of the camera to connect :')
    cam_id = int(cam_id)
    print(f"Selected camera : {cam_id}")

    # Create a camera object
    my_cam_dev = cam_list.get_cam_device(cam_id)
    '''