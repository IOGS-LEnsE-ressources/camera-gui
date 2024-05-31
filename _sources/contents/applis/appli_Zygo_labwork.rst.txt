Interferometric controls / Labwork
##################################

The source code of the application is in the :file:`applis/Zygo-labwork` directory of the GitHub repository of this project : `Camera GUI <https://github.com/IOGS-LEnsE-ressources/camera-gui>`_.

.. note::

	The :file:`basler/camera_basler_widget.py` and :file:`ids/camera_ids_widget.py` files were modified to include the :code:`supoptools` module.
	
	The importation of this module is done by:
	
	.. code-block:: python
	
		sys.path.append('../supoptools')
		from images.conversion import *
		from pyqt6.widget_slider import WidgetSlider
	
	! To change when SupOpTools will become a package !
	
Goal of the labwork
*******************
	
The goal of the labwork is to ...
	
Needs for the interface
***********************

Capture images from a camera
============================

- Set exposure time, fps and black level of the camera.
- Acquire image from a the camera.

Control a piezo actuator
========================

- Analog output (via Texas Instruments USB-6001 device or Nucleo if no API in Python for TI USB-6001) to control the piezo actuator.


Make some calculations
======================

To complete...