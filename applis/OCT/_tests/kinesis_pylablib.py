# -*- coding: utf-8 -*-
"""
File: OCT_lab_app.py

This file contains test code for piezo and step motor controlling (Thorlabs).

https://pylablib.readthedocs.io/en/stable/devices/Thorlabs_kinesis.html#stages-thorlabs-kinesis


.. note:: LEnsE - Institut d'Optique - version 1.0

.. moduleauthor:: Julien VILLEMEJANE (PRAG LEnsE) <julien.villemejane@institutoptique.fr>
"""

import sys
import numpy as np
import cv2
from pylablib.devices import Thorlabs

id_number = 0

# %% Example
if __name__ == '__main__':	
	Thorlabs.list_kinesis_devices()
