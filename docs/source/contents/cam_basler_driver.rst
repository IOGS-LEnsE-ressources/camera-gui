Basler / Driver
###############

The **driver** is based on the `Pypylon Wrapper <https://github.com/basler/pypylon>`_. 

The source is in the :file:`camera_basler.py` :download:`< <https://github.com/IOGS-LEnsE/camera-gui/blob/main/progs/Basler/camera_basler.py>` file including :

* :class:`CameraBasler` class, 
* :class:`BaslerERROR` class : to process low-level error when accessing the camera, 
* :samp:`get_converter_mode(color_mode: str)`
* :samp:`get_bits_per_pixel(color_mode: str)`


.. warning::

	The :file:`camera_basler.py` must be in the same directory as the Python file containing your script.
	
Import the CameraBasler class
*****************************

To access :class:`CameraBasler` class and its functions, import the class in your Python code like this:

.. code-block:: python
	
	from camera_basler import CameraBasler


Initialize a camera
*******************

Device object
=============

First of all, you need to create a device from the :samp:`pypylon` module like this:

.. code-block:: python

	from pypylon import pylon
	my_cam_dev = pylon.InstantCamera(pylon.TlFactory.GetInstance().CreateFirstDevice())
	
This script gets the first Basler connected device. If no device is connected, it returns an error.

You can also use the :class:`CameraList` class, as shown in the previous section. The :samp:`get_cam_device()` method returns a device object that is the same type as the :samp:`pypylon` module.

Camera object
=============

An instance of the :class:`CameraBasler` class creates an object able to communicate with the device.

To use our driver, you have to create an instance of the :class:`CameraBasler` class like this:

.. code-block:: python

	my_cam = CameraBasler(my_cam_dev)

When you use this constructor, a well-initialized message is written in the console (if the camera is correctly connected and recognized by the system.

>>> my_cam = CameraBasler(my_cam_dev)
Device is well initialized.

Connected camera
================

The :code:`is_camera_connected()` method returns the status of the camera, in other words it says if the camera could be opened or not.
	
To check if the camera is well connected, you can use this command:

>>> my_cam.is_camera_connected()
Device is well initialized.
True

If the camera is well initialized, you will obtain a success message in the console, following by :samp:`True`. 

Get information from the camera
*******************************

Different kind of informations are available on Basler camera. You can get the name, the serial number, the frame rate, the exposure time... of the camera.

Camera general informations
===========================

Serial Number and name
----------------------

.. autofunction:: camera_basler.CameraBasler.get_cam_info
	:no-index:



Sensor size
-----------

.. autofunction:: camera_basler.CameraBasler.get_sensor_size
	:no-index:

Camera parameters
=================

Color mode
----------

Exposure Time
-------------

Frame Rate
----------

Area of interest
----------------

Black Level
-----------


Setup a camera
**************


Get and display images
**********************

Images format
=============

Get a set of images
===================

Complete example
================

.. code-block:: python

    from matplotlib import pyplot as plt
	
	my_cam_dev = pylon.InstantCamera(pylon.TlFactory.GetInstance().CreateFirstDevice())
	
    my_cam = CameraBasler(my_cam_dev)

    # Check the colormode
    print(my_cam.get_color_mode())

    # Change colormode to Mono12
    my_cam.set_color_mode('Mono12')
    my_cam.set_display_mode('Mono12')
    print(my_cam.get_color_mode())
    
    # Test to catch one image
    images = my_cam.get_images()    
    print(images[0].shape)
    
    # display image
    plt.imshow(images[0], interpolation='nearest')
    plt.show()



Start a continuous shot
***********************

Coming soon...