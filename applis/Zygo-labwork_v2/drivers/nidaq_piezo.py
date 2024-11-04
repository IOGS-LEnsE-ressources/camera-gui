# -*- coding: utf-8 -*-
"""*nidaq_piezo.py* file.

*nidaq_piezo file that contains :class::NIDaqPiezo

This file is attached to a 1st year of engineer training labwork in photonics.
Subject : http://lense.institutoptique.fr/ressources/Annee1/TP_Photonique/S5-2324-PolyCI.pdf

More about the development of this interface :
https://iogs-lense-ressources.github.io/camera-gui/contents/applis/appli_Zygo_labwork.html

.. note:: LEnsE - Institut d'Optique - version 1.0

.. moduleauthor:: Julien VILLEMEJANE (PRAG LEnsE) <julien.villemejane@institutoptique.fr>
.. moduleauthor:: Dorian MENDES (Promo 2026) <dorian.mendes@institutoptique.fr>
"""

import nidaqmx
class NIDaqPiezo:
    """Class to communicate with a DAQ module from NI.

    """

    def __init__(self) -> None:
        """Initialize the object."""
        # Camera device
        pass

    def read_adc(self, chan: str = "Dev1/ai0"):
        result = None
        with nidaqmx.Task() as task:
            task.ai_channels.add_ai_voltage_chan("Dev1/ai0")
            result = task.read()
        return result

if __name__ == '__main__':
    local_system = nidaqmx.system.System.local()
    driver_version = local_system.driver_version
    print(driver_version)


    for device in local_system.devices:
        print(
            "Device Name: {0}, Product Category: {1}, Product Type: {2}".format(
                device.name, device.product_category, device.product_type
            )
        )
        
    device_first = local_system.devices[0]
    device_first_name = device_first.name
    print(device_first_name)