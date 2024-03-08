Basler Driver
#############

To facilitate the integration of the pypylon API in the different projects, we developped : 

* a *driver* based on the *pypylon* API,
* a set of *widgets* based on *PyQt6*.

This section deals with the **driver**.

|

This driver is based on the `Pypylon Wrapper <https://github.com/basler/pypylon>`_. 
It contains two main files :

* :file:`camera_basler.py` :download:`< <https://github.com/IOGS-LEnsE/camera-gui/blob/main/progs/Basler/camera_basler.py>` including :

	* :class:`CameraBasler` class, 
	* :class:`BaslerERROR` class : to process low-level error when accessing the camera, 
	* :samp:`get_converter_mode(color_mode: str)`
	* :samp:`get_bits_per_pixel(color_mode: str)`

* :file:`camera_list.py` :download:`< <https://github.com/IOGS-LEnsE/camera-gui/blob/main/progs/Basler/camera_list.py>` including the :class:`CameraList` class


List available cameras
**********************

The :class:`CameraList` class, including in the :file:`camera_list.py` file, contains methods to create and to display a list of available Basler cameras.

.. warning::

	The :file:`camera_list.py` must be in the same directory as the Python file containing your script.

Import the CameraList class
===========================
To access :class:`CameraList` class and its functions, import the class in your Python code like this:

.. code-block:: python
	
	from camera_list import CameraList

Example of use
==============

Create a CameraList object
--------------------------

Cameras list is given by an instance of the :class:`CameraList` class. First of all, you need to create an instance of this class like this:

.. code-block:: python
	
	cam_list = CameraList()

Create a string list of the cameras
-----------------------------------

The :samp:`get_cam_list()` method from the :class:`CameraList` class returns a list of a Python :class:`tuple` of 3 values per camera corresponding to : 

* index of the camera (integer)
* serial number of the camera (string)
* name of the camera (string)

You can use this method like this:

.. code-block:: python
	
    cameras_list = cam_list.get_cam_list()

By printing the result of this method, you will obtain something like this:

>>> print(cameras_list)
[[0, 40282239, 'a2A1920-160ucBAS']]


Get a device
------------

You can then access to one of the connected devices by using the :samp:`get_cam_device()` method like this:

.. code-block:: python

	cam_id = 0
	my_cam_dev = cam_list.get_cam_device(cam_id)

The :samp:`cam_id` corresponding to the index of the camera in the list created previously.


Complete example
================

.. code-block:: python

	from camera_list import CameraList
	
	cam_list = CameraList()
	cameras_list = cam_list.get_cam_list()
	
	for cam in cameras_list:
		print(f'ID:{cam[0]} - Name: {cam[2]} - Serial: {cam[1]}')	
	
	cam_id = 'a'
	while cam_id.isdigit() is False:
		cam_id = input('Enter the ID of the camera to connect :')
	cam_id = int(cam_id)
	
	my_cam_dev = cam_list.get_cam_device(cam_id)
	
In this example, a :class:`CameraList` instance is created. The list of available cameras is displayed in the console. User must enter a valid number. Finally, a camera device is created in the :code:`my_cam_dev` variable.
	

Initialize a camera
*******************

The :class:`CameraBasler` class, including in the :file:`camera_basler.py` file, contains methods to setup the camera parameters and to get images from the camera.

>>> my_cam = CameraBasler(cam_dev)

Setup a camera
**************


Get and display images
**********************



Start a continuous shot
***********************

Coming soon...