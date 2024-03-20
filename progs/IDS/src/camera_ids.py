# -*- coding: utf-8 -*-
"""camera_ids file.

File containing :class::CameraIDS
class to communicate with an IDS camera sensor.

.. module:: CameraIDS
   :synopsis: class to communicate with an IDS camera sensor.

.. note:: LEnsE - Institut d'Optique - version 0.1

.. moduleauthor:: Julien VILLEMEJANE <julien.villemejane@institutoptique.fr>

.. warning::

    Couche de transport spéciale « uEye » grâce à laquelle les caméras uEye
    (matchcode « UI- ») sont également utilisables sur la base GenICam
    et bénéficient des nombreux avantages du nouveau SDK.
    
    Veuillez noter qu’en plus d’IDS peak, la dernière version d’IDS Software Suite
    (4.95 minimum) doit être installée.

@see : https://en.ids-imaging.com/techtipp-details/rapid-prototyping-ids-peak.html
@ see : https://www.1stvision.com/cameras/IDS/IDS-manuals/en/index.html
@ See API DOC : C:\Program Files\IDS\ids_peak\generic_sdk\api\doc\html

"""
import numpy as np

# IDS peak API
from ids_peak import ids_peak
# Require IDS peak IPL and Numpy.
# Go to C:\Program Files\IDS\ids_peak\generic_sdk\ipl\binding\python\wheel\x86_[32|64]
# > pip install ids_peak_1.2.4.1-cp<version>-cp<version>m-[win32|win_amd64].whl
import ids_peak_ipl.ids_peak_ipl as ids_ipl


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


class IdsError(Exception):
    """IdsError class, children of Exeption.

    Class to manage error during communication with an IDS camera sensor

    """

    def __init__(self, ERROR_mode="IdsERROR"):
        """Initialize object.

        :param ERROR_mode: Type of error, defaults to "IdsError"
        :type ERROR_mode: str, optional

        """
        self.ERROR_mode = ERROR_mode
        super().__init__(self.ERROR_mode)


class CameraIDS():
    """Class to communicate with an IDS camera sensor.

    :param camera: Camera object that can be controlled.
    :type camera: pylon.TlFactory.InstantCamera

    TO COMPLETE

    .. note::

        In the context of this driver,
        the following color modes are available :

        * 'Mono8' : monochromatic mode in 8 bits raw data
        * 'Mono10' : monochromatic mode in 10 bits raw data
        * 'Mono12' : monochromatic mode in 12 bits raw data
        * 'RGB8' : RGB mode in 8 bits raw data

    """

    '''
# Open a device
my_camera = device_descriptors[0].OpenDevice(ids_peak.DeviceAccessType_Exclusive)
print(f'Opened device : {my_camera.DisplayName()}')
    '''

    def __init__(self, cam_dev: ids_peak.Device) -> None:
        """Initialize the object."""
        # Camera device
        self.camera = cam_dev
        # Create a remote of the device (to control it)
        self.camera_remote = self.camera.RemoteDevice().NodeMaps()[0]  # Is [0] Index of the camera ?

        # Software trigger of the camera
        self.camera_remote.FindNode("TriggerSelector").SetCurrentEntry("ExposureStart")
        self.camera_remote.FindNode("TriggerSource").SetCurrentEntry("Software")
        self.camera_remote.FindNode("TriggerMode").SetCurrentEntry("On")

        # Camera informations
        self.serial_no, self.camera_name = self.get_cam_info()
        self.width_max, self.height_max = self.get_sensor_size()
        self.nb_bits_per_pixels: int = 0
        self.color_mode = 'Mono8'  # default
        self.set_color_mode('Mono8')
        self.set_display_mode('Mono8')
        # AOI size
        self.aoi_x0: int = 0
        self.aoi_y0: int = 0
        self.aoi_width: int = self.width_max
        self.aoi_height: int = self.height_max
        # Test if camera is connected.
        self.is_camera_connected()
        self.set_aoi(self.aoi_x0, self.aoi_y0, self.aoi_width, self.aoi_height)

    def is_camera_connected(self) -> bool:
        """Return the status of the device.

        :return: true if the device could be opened, and then close the device
        :rtype: bool (or error)

        >>> my_cam.is_camera_connected()
        Device is well initialized.
        True

        """
        value = self.camera_remote.FindNode("DeviceLinkSpeed").Value()
        if value > 1:
            return True
        else:
            return False

    def disconnect(self):
        """Disconnect the camera."""
        '''
        ids_peak.Library.Close() ??
        '''
        pass

    def get_cam_info(self) -> tuple[str, str]:
        """Return the serial number and the name.

        :return: the serial number and the name of the camera
        :rtype: tuple[str, str]

        >>> my_cam.get_cam_info
        ('40282239', 'a2A1920-160ucBAS')

        """
        serial_no, camera_name = None, None

        camera_name = self.camera.DisplayName()
        serial_no = self.camera_remote.FindNode("DeviceSerialNumber").Value()
        return serial_no, camera_name

    def get_sensor_size(self) -> tuple[int, int]:
        """Return the width and the height of the sensor.

        :return: the width and the height of the sensor in pixels
        :rtype: tuple[int, int]

        >>> my_cam.get_sensor_size()
        (1936, 1216)

        """
        max_height = self.camera_remote.FindNode("HeightMax").Value()
        max_width = self.camera_remote.FindNode("WidthMax").Value()
        return max_width, max_height

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

        >>> my_cam.get_color_mode()
        'Mono8'

        """
        '''
        try:
            # Test if the camera is opened
            if self.camera.IsOpen():
                pixelFormat = self.camera.PixelFormat.GetValue()
            else:
                self.camera.Open()
                pixelFormat = self.camera.PixelFormat.GetValue()
                self.camera.Close()
            self.color_mode = pixelFormat
            return pixelFormat
        except:
            raise IdsError("get_colormode")
        '''
        pass

    def set_color_mode(self, colormode: str) -> None:
        """Change the color mode.

        :param colormode: Color mode to use for the device
        :type colormode: str, default 'Mono8'

        """
        '''
        try:
            # Test if the camera is opened
            if self.camera.IsOpen():
                self.camera.PixelFormat = colormode
            else:
                self.camera.Open()
                self.camera.PixelFormat = colormode
                self.camera.Close()
            self.color_mode = colormode
            self.nb_bits_per_pixels = get_bits_per_pixel(colormode)
            self.set_display_mode(colormode)
        except:
            raise IdsError("set_colormode")
        '''
        pass

    def get_image(self) -> np.ndarray:
        """Get one image.

        :return: Array of the image.
        :rtype: array

        """
        image = self.get_images()
        return image[0]

    def get_images(self, nb_images: int = 1) -> list:
        """Get a series of images.

        :param nb_images: Number of images to collect
        :type nb_images: int, default 1
        :return: List of images
        :rtype: list

        """
        '''
        try:
            # Test if the camera is opened
            if not self.camera.IsOpen():
                self.camera.Open()
            # Test if the camera is grabbing images
            if not self.camera.IsGrabbing():
                self.camera.StopGrabbing()
            # Create a list of images
            images: list = []
            self.camera.StartGrabbingMax(nb_images)

            while self.camera.IsGrabbing():
                grabResult = self.camera.RetrieveResult(
                    1000,
                    pylon.TimeoutHandling_ThrowException)
                if grabResult.GrabSucceeded():
                    # Access the image data.
                    images.append(grabResult.Array)
                grabResult.Release()
            return images
        except:
            raise IdsError("get_images")
        '''
        pass

    def __check_range(self, x: int, y: int) -> bool:
        """Check if the coordinates are in the sensor area.

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
        if x0 % 4 != 0 or y0 % 4 != 0:
            return False
        self.aoi_x0 = x0
        self.aoi_y0 = y0
        self.aoi_width = w
        self.aoi_height = h
        '''
        try:
            if self.camera.IsOpen():
                self.camera.Width.SetValue(w)
                self.camera.Height.SetValue(h)
                self.camera.OffsetX.SetValue(x0)
                self.camera.OffsetY.SetValue(y0)
            else:
                self.camera.Open()
                self.camera.Width.SetValue(w)
                self.camera.Height.SetValue(h)
                self.camera.OffsetX.SetValue(x0)
                self.camera.OffsetY.SetValue(y0)
                self.camera.Close()
            return True
        except:
            raise IdsError("set_aoi")
        '''
        pass

    def get_aoi(self) -> tuple[int, int, int, int]:
        """Return the area of interest (aoi).

        :return: [x0, y0, width, height] x0 and y0 are the
            coordinates of the top-left corner and width
            and height are the size of the aoi.
        :rtype: tuple[int, int, int, int]

        >>> my_cam.get_aoi()
        (0, 0, 1936, 1216)

        """
        return self.aoi_x0, self.aoi_y0, self.aoi_width, self.aoi_height

    def reset_aoi(self) -> bool:
        """Reset the area of interest (aoi).

        Reset to the limit of the camera.
        
        :return: True if the aoi is modified
        :rtype: bool

        >>> my_cam.reset_aoi()
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

        >>> my_cam.get_exposure()
        5000.0

        """
        return self.camera_remote.FindNode("ExposureTime").Value()

    def get_exposure_range(self) -> tuple[float, float]:
        """Return the range of the exposure time in microseconds.

        :return: the minimum and the maximum value
            of the exposure time in microseconds.
        :rtype: tuple[float, float]

        """
        exposure_min = self.camera_remote.FindNode("ExposureTime").Minimum()
        exposure_max = self.camera_remote.FindNode("ExposureTime").Maximum()
        return exposure_min, exposure_max

    def set_exposure(self, exposure: float) -> None:
        """Set the exposure time in microseconds.

        :param exposure: exposure time in microseconds.
        :type exposure: float

        """
        self.camera_remote.FindNode("ExposureTime").SetValue(exposure)

    def get_frame_rate(self) -> float:
        """Return the frame rate.

        :return: the frame rate.
        :rtype: float

        >>> my_cam.get_frame_rate()
        100.0

        """
        '''
        try:
            if self.camera.IsOpen():
                frameRate = self.camera.AcquisitionFrameRate.GetValue()
            else:
                self.camera.Open()
                frameRate = self.camera.AcquisitionFrameRate.GetValue()
                self.camera.Close()
            return frameRate
        except:
            raise IdsError("get_frame_rate")
        '''
        pass

    def get_frame_rate_range(self):
        """Return the range of the frame rate in frames per second.

        :return: the minimum and the maximum value
            of the frame rate in frames per second.
        :rtype: tuple[float, float]

        """
        '''
        try:
            if self.camera.IsOpen():
                frameRateMin = self.camera.AcquisitionFrameRate.GetMin()
                frameRateMax = self.camera.AcquisitionFrameRate.GetMax()
            else:
                self.camera.Open()
                frameRateMin = self.camera.AcquisitionFrameRate.GetMin()
                frameRateMax = self.camera.AcquisitionFrameRate.GetMax()
                self.camera.Close()
            return frameRateMin, frameRateMax
        except:
            raise IdsError("get_frame_time_range")
        '''
        pass

    def set_frame_rate(self, fps):
        """Set the frame rate in frames per second.

        :param fps: frame rate in frames per second.
        :type fps:

        """
        '''
        try:
            if self.camera.IsOpen():
                self.camera.AcquisitionFrameRateEnable.SetValue(True)
                self.camera.AcquisitionFrameRate.SetValue(fps)
            else:
                self.camera.Open()
                self.camera.AcquisitionFrameRateEnable.SetValue(True)
                self.camera.AcquisitionFrameRate.SetValue(fps)
                self.camera.Close()
        except:
            raise IdsError("set_frame_rate")
        '''
        pass

    def get_black_level(self):
        """Return the blacklevel.

        :return: the black level of the device in ADU.
        :rtype: int

        >>> my_cam.get_black_level()
        0.0

        """
        '''
        try:
            if self.camera.IsOpen():
                BlackLevel = self.camera.BlackLevel.GetValue()
            else:
                self.camera.Open()
                BlackLevel = self.camera.BlackLevel.GetValue()
                self.camera.Close()
            return BlackLevel

        except:
            raise IdsError("get_black_level")
        '''
        pass

    def get_black_level_range(self) -> tuple[int, int]:
        """Return the range of the black level.

        :return: the minimum and the maximum value
            of the frame rate in frames per second.
        :rtype: tuple[int, int]

        """
        '''
        try:
            if self.camera.IsOpen():
                BlackLevelMin = self.camera.BlackLevel.GetMin()
                BlackLevelMax = self.camera.BlackLevel.GetMax()
            elif not self.camera.IsOpen():
                self.camera.Open()
                BlackLevelMin = self.camera.BlackLevel.GetMin()
                BlackLevelMax = self.camera.BlackLevel.GetMax()
                self.camera.Close()
            return BlackLevelMin, BlackLevelMax
        except:
            raise IdsError("get_black_level_range"
        '''
        pass

    def set_black_level(self, black_level) -> bool:
        """Set the blackLevel.

        :param black_level: blackLevel.
        :type black_level: int
        :return: True if the black level is lower than the maximum.
        :rtype: bool

        """
        '''
        if black_level > 2 ** self.nb_bits_per_pixels - 1:
            return False
        try:
            if self.camera.IsOpen():
                self.camera.BlackLevel.SetValue(black_level)
            else:
                self.camera.Open()
                self.camera.BlackLevel.SetValue(black_level)
                self.camera.Close()
            return True
        except:
            raise IdsError("set_black_level")
        '''
        pass


if __name__ == "__main__":
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
    # Initialize library
    ids_peak.Library.Initialize()
    # Device manager
    device_manager = ids_peak.DeviceManager.Instance()
    device_manager.Update()
    device_descriptors = device_manager.Devices()
    # Open a device
    my_cam_dev = device_descriptors[0].OpenDevice(ids_peak.DeviceAccessType_Exclusive)

    my_cam = CameraIDS(my_cam_dev)
    print(my_cam.is_camera_connected())
    print(f'W/H = {my_cam.get_sensor_size()}')

    # Change exposure time
    print(f'Old Expo = {my_cam.get_exposure()}')
    my_cam.set_exposure(40000)
    print(f'New Expo = {my_cam.get_exposure()}')


    # Check the colormode
    print(my_cam.get_color_mode())

    # Change colormode to Mono12
    my_cam.set_color_mode('Mono12')
    my_cam.set_display_mode('Mono12')
    print(my_cam.get_color_mode())

    '''
    # Test to catch one image
    images = my_cam.get_images()
    print(images[0].shape)

    # display image
    from matplotlib import pyplot as plt

    plt.imshow(images[0], interpolation='nearest')
    plt.show()
    '''

    '''
    if my_cam.set_aoi(200, 300, 500, 400):
        print('AOI OK')
        # Test to catch images
        st = time.time()
        images = my_cam.get_images()
        et = time.time()
        
        # get the execution time
        elapsed_time = et - st
        print('\tExecution time:', elapsed_time, 'seconds')  
        print(images[0].shape)      
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
    # Frame Rate
    ft_act = my_cam.get_frame_rate()
    print(f'Actual Frame Time = {ft_act} fps')
    my_cam.set_frame_rate(20)
    ft_act = my_cam.get_frame_rate()
    print(f'New Frame Time = {ft_act} fps')
    
    # BlackLevel
    bl_act = my_cam.get_black_level()
    print(f'Actual Black Level = {bl_act}')
    my_cam.set_black_level(200)
    bl_act = my_cam.get_black_level()
    print(f'New Black Level = {bl_act}')
    '''
