# -*- coding: utf-8 -*-
"""
File: OCT_lab_app.py

This file contains test code for piezo and step motor controlling (Thorlabs).

https://pylablib.readthedocs.io/en/stable/devices/Thorlabs_kinesis.html#stages-thorlabs-kinesis


.. note:: LEnsE - Institut d'Optique - version 1.0

.. moduleauthor:: Julien VILLEMEJANE (PRAG LEnsE) <julien.villemejane@institutoptique.fr>
"""

import time
import struct
from pylablib.devices import Thorlabs

id_number = 0

def init_step_motor(id_num: str):
	# https://github.com/AlexShkarin/pyLabLib/issues/6#issue-1073743642
	step_motor = Thorlabs.BasicKinesisDevice(id_num)
	time.sleep(0.1)
	step_motor.instr.instr._flow = 256
	step_motor.instr.instr._setFlowControl()
	time.sleep(0.1)
	step_motor.instr.instr.flushInput()
	step_motor.instr.instr.flushOutput()
	time.sleep(0.1)
	step_motor.instr.instr._flow = 0
	step_motor.instr.instr._setFlowControl()

	step_motor.send_comm(messageID=0x0434)
	return step_motor
	# https://github.com/AlexShkarin/pyLabLib/issues/74

# %% Example
if __name__ == '__main__':	
	print(Thorlabs.list_kinesis_devices())

	dev = Thorlabs.BasicKinesisDevice("40897338", is_rack_system=True)
	time.sleep(0.1)
	dev.send_comm(0x0443, param1=0x01, param2=0x00, source=0x01,
				  dest=0x21)  # dest=0x22 for channel 2 and 0x23 for channel 3
	time.sleep(0.1)
	dev.close()

	time.sleep(0.1)
	step_motor = Thorlabs.KinesisMotor("40897338", is_rack_system=True)
	step_motor.home(channel=1)


	piezo_motor = Thorlabs.KinesisPiezoController("29501399")

	# "<" means little-endian, and "Hi" means a 2-byte unsigned integer followed by a 4-byte signed integer (see struct documentation)
	data = struct.pack("<Hi", 0, 1000)  # channel 0 and position 10000
	#step_motor.send_comm_data(messageID=0x0443, data=data)

	step_motor.close()
	piezo_motor.close()