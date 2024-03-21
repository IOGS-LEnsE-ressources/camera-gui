"""


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

# Initialize library
ids_peak.Library.Initialize()

# Device manager
device_manager = ids_peak.DeviceManager.Instance()
device_manager.Update()
device_descriptors = device_manager.Devices()

# Display devices
for device_desc in device_descriptors:
    print(device_desc.DisplayName())

# Open a device
my_camera = device_descriptors[0].OpenDevice(ids_peak.DeviceAccessType_Exclusive)
print(f'Opened device : {my_camera.DisplayName()}')

# Create a remote of the device (to control it)
my_camera_remote = my_camera.RemoteDevice().NodeMaps()[0]

# Software trigger of the camera
my_camera_remote.FindNode("TriggerSelector").SetCurrentEntry("ExposureStart")
my_camera_remote.FindNode("TriggerSource").SetCurrentEntry("Software")
my_camera_remote.FindNode("TriggerMode").SetCurrentEntry("On")

# First image acquisition
datastream = my_camera.DataStreams()[0].OpenDataStream()
payload_size = my_camera_remote.FindNode("PayloadSize").Value()
for i in range(datastream.NumBuffersAnnouncedMinRequired()):
    buffer = datastream.AllocAndAnnounceBuffer(payload_size)
    datastream.QueueBuffer(buffer)

datastream.StartAcquisition()
my_camera_remote.FindNode("AcquisitionStart").Execute()
my_camera_remote.FindNode("AcquisitionStart").WaitUntilDone()

##### Exposure time
## Set
my_camera_remote.FindNode("ExposureTime").SetValue(20000) # in microseconds
## Get
expo_time = my_camera_remote.FindNode("ExposureTime").Value()
print(f'Expo Time = {expo_time} us')
## Range
# double min = nodeMapRemoteDevice->FindNode<peak::core::nodes::FloatNode>("ExposureTime")->Minimum();
# double inc = nodeMapRemoteDevice->FindNode<peak::core::nodes::FloatNode>("ExposureTime")->Increment();
max_expo_time = my_camera_remote.FindNode("ExposureTime").Maximum()
print(f'Max Expo Time = {max_expo_time/1000.0} ms')

## Pixel Format
# Determine the current entry of PixelFormat (str)
value = my_camera_remote.FindNode("PixelFormat").CurrentEntry().SymbolicValue()
# Get a list of all available entries of PixelFormat
allEntries = my_camera_remote.FindNode("PixelFormat").Entries()
availableEntries = []
for entry in allEntries:
    if (entry.AccessStatus() != ids_peak.NodeAccessStatus_NotAvailable
            and entry.AccessStatus() != ids_peak.NodeAccessStatus_NotImplemented):
        availableEntries.append(entry.SymbolicValue())

# Set PixelFormat to "BayerRG8" (str)
# my_camera_remote.FindNode("PixelFormat").SetCurrentEntry("BayerRG8")

## Flip camera
# my_camera_remote.FindNode("ReverseX").SetValue(False)
# my_camera_remote.FindNode("ReverseY").SetValue(False)

# Grab an image

# trigger image
# require : pip install ids_peak_ipl-1.2.2.1-cp38-cp38-win_amd64.whl
my_camera_remote.FindNode("TriggerSoftware").Execute()
buffer = datastream.WaitForFinishedBuffer(1000)

# convert to RGB
raw_image = ids_ipl.Image.CreateFromSizeAndBuffer(buffer.PixelFormat(), buffer.BasePtr(), buffer.Size(), buffer.Width(), buffer.Height())
color_image = raw_image.ConvertTo(ids_ipl.PixelFormatName_RGB8)
datastream.QueueBuffer(buffer)

picture = color_image.get_numpy_3D()
print(type(picture))

# display the image
from matplotlib import pyplot as plt
plt.figure()
plt.imshow(picture)
plt.show()

# Close all cameras
ids_peak.Library.Close()
