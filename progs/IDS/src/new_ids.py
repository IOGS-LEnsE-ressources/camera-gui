# -*- coding: utf-8 -*-
"""new_ids file.

File containing first tests with IDS Peak API.

.. warning::

    **IDS peak** (2.8 or higher) and **IDS Sofware Suite** (4.95 or higher) softwares
    are required on your computer.

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

"""

# IDS peak API
from ids_peak import ids_peak
import ids_peak_ipl.ids_peak_ipl as ids_ipl

from matplotlib import pyplot as plt
import numpy as np


def list_of_cam():
    try:
        ids_peak.Library.Initialize()
        # Device manager
        device_manager = ids_peak.DeviceManager.Instance()
        # Update the DeviceManager
        device_manager.Update()

        # Exit program if no device was found
        if device_manager.Devices().empty():
            print("No device found. Exiting Program.")
            return -1
        # List
        device_descriptors = device_manager.Devices()
        # Display devices
        for device_desc in device_descriptors:
            print(device_desc.DisplayName())
        return device_descriptors

    except Exception as e:
        print("EXCEPTION: " + str(e))
        ids_peak.Library.Close()
        return -2


def open_cam(id: int, devices: ids_peak.VectorDeviceDescriptor) -> ids_peak.Device:
    try:
        # Open a device
        my_camera = devices[id].OpenDevice(ids_peak.DeviceAccessType_Exclusive)
        print(f'Opened device : {my_camera.DisplayName()}')
        print(type(my_camera))
        return my_camera

    except Exception as e:
        print("EXCEPTION: " + str(e))
        ids_peak.Library.Close()
        return -2


def create_remote(id: int, camera: ids_peak.Device) -> ids_peak.NodeMap:
    try:
        # Create a remote of the device (to control it)
        my_camera_remote = camera.RemoteDevice().NodeMaps()[id]

        # Software trigger of the camera
        my_camera_remote.FindNode("TriggerSelector").SetCurrentEntry("ExposureStart")
        my_camera_remote.FindNode("TriggerSource").SetCurrentEntry("Software")
        my_camera_remote.FindNode("TriggerMode").SetCurrentEntry("On")
        return my_camera_remote

    except Exception as e:
        print("EXCEPTION: " + str(e))
        ids_peak.Library.Close()
        return -2

def get_pixel_format_list(camera_remote: ids_peak.NodeMap):
    ## Pixel Format
    # Determine the current entry of PixelFormat (str)
    value = camera_remote.FindNode("PixelFormat").CurrentEntry().SymbolicValue()
    # Get a list of all available entries of PixelFormat
    allEntries = camera_remote.FindNode("PixelFormat").Entries()
    availableEntries = []
    for entry in allEntries:
        if (entry.AccessStatus() != ids_peak.NodeAccessStatus_NotAvailable
                and entry.AccessStatus() != ids_peak.NodeAccessStatus_NotImplemented):
            availableEntries.append(entry.SymbolicValue())
            print(entry.SymbolicValue())


def open_datastream(camera, camera_remote):
    try:
        datastreams = camera.DataStreams()
        if datastreams.empty():
            print("Error stream")
            '''
                if data_stream:
                # Flush queue and prepare all buffers for revoking
                data_stream.Flush(ids_peak.DataStreamFlushMode_DiscardAll)
                # Clear all old buffers
                for buffer in data_stream.AnnouncedBuffers():
                    data_stream.RevokeBuffer(buffer)
        
                payload_size = node_map_remote_device.FindNode("PayloadSize").Value()
        
                # Get number of minimum required buffers
                num_buffers_min_required = data_stream.NumBuffersAnnouncedMinRequired()
        
                # Alloc buffers
                for count in range(num_buffers_min_required):
                    buffer = data_stream.AllocAndAnnounceBuffer(payload_size)
                    data_stream.QueueBuffer(buffer)
            '''
        data_stream = camera.DataStreams()[0].OpenDataStream()

        payload_size = camera_remote.FindNode("PayloadSize").Value()
        for i in range(data_stream.NumBuffersAnnouncedMinRequired()):
            buffer = data_stream.AllocAndAnnounceBuffer(payload_size)
            data_stream.QueueBuffer(buffer)
        return data_stream
    except Exception as e:
        print("EXCEPTION: " + str(e))
        ids_peak.Library.Close()
        return -2


def start_acquisition(camera_remote, data_stream):
    try:
        data_stream.StartAcquisition()
        camera_remote.FindNode("AcquisitionStart").Execute()
        camera_remote.FindNode("AcquisitionStart").WaitUntilDone()

    except Exception as e:
        print("EXCEPTION: " + str(e))
        ids_peak.Library.Close()
        return -2


def stop_acquisition(camera_remote, data_stream):
    try:
        data_stream.StopAcquisition()
        camera_remote.FindNode("AcquisitionStop").Execute()
        camera_remote.FindNode("AcquisitionStop").WaitUntilDone()

    except Exception as e:
        print("EXCEPTION: " + str(e))
        ids_peak.Library.Close()
        return -2


def get_image(camera, camera_remote, datastream):
    try:
        # trigger image
        camera_remote.FindNode("TriggerSoftware").Execute()
        buffer = datastream.WaitForFinishedBuffer(200)
        # convert to RGB
        raw_image = ids_ipl.Image.CreateFromSizeAndBuffer(
            buffer.PixelFormat(),
            buffer.BasePtr(),
            buffer.Size(),
            buffer.Width(),
            buffer.Height())
        color_image = raw_image.ConvertTo(ids_ipl.PixelFormatName_RGB8)
        datastream.QueueBuffer(buffer)

        picture = color_image.get_numpy_3D()
        return picture

    except Exception as e:
        print("EXCEPTION: " + str(e))
        ids_peak.Library.Close()
        return -2


# Main

try:
    all_devices = list_of_cam()
    cam_id = 0
    my_camera = open_cam(cam_id, all_devices)
    my_camera_remote = create_remote(cam_id, my_camera)
    get_pixel_format_list(my_camera_remote)

    print('DataStream')
    data_stream = open_datastream(my_camera, my_camera_remote)

    print('Start')
    start_acquisition(my_camera_remote, data_stream)
    print('Image')
    image = get_image(my_camera, my_camera_remote, data_stream)
    # stop_acquisition(my_camera_remote, data_stream)

    # display the image
    plt.figure()
    plt.imshow(image)
    plt.show()

except Exception as e:
    print("EXCEPTION: " + str(e))
    ids_peak.Library.Close()


'''
##### Exposure time
## Set
my_camera_remote.FindNode("ExposureTime").SetValue(20000)  # in microseconds
## Get
expo_time = my_camera_remote.FindNode("ExposureTime").Value()
print(f'Expo Time = {expo_time} us')
## Range
# double min = nodeMapRemoteDevice->FindNode<peak::core::nodes::FloatNode>("ExposureTime")->Minimum();
# double inc = nodeMapRemoteDevice->FindNode<peak::core::nodes::FloatNode>("ExposureTime")->Increment();
max_expo_time = my_camera_remote.FindNode("ExposureTime").Maximum()
print(f'Max Expo Time = {max_expo_time / 1000.0} ms')

# Set PixelFormat to "BayerRG8" (str)
# my_camera_remote.FindNode("PixelFormat").SetCurrentEntry("BayerRG8")

## Flip camera
# my_camera_remote.FindNode("ReverseX").SetValue(False)
# my_camera_remote.FindNode("ReverseY").SetValue(False)


# Close all cameras
ids_peak.Library.Close()

'''