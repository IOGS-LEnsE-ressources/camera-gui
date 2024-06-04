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

    # print(len(local_system.devices))

    import sys
    import numpy as np
    from PyQt6.QtWidgets import QApplication, QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget

    # Créer une application PyQt6
    app = QApplication(sys.argv)

    # Créer un tableau numpy
    data = np.array([[1, 2, 3], [4, 5, 6], [7, 8, 9]])

    # Créer un widget de tableau
    table_widget = QTableWidget()

    # Définir le nombre de lignes et de colonnes du tableau
    table_widget.setRowCount(data.shape[0])
    table_widget.setColumnCount(data.shape[1])

    # Remplir les cellules du tableau avec les données du tableau numpy
    for i in range(data.shape[0]):
        for j in range(data.shape[1]):
            table_widget.setItem(i, j, QTableWidgetItem(str(data[i, j])))

    # Créer un widget principal
    main_widget = QWidget()

    # Créer une mise en page verticale pour le widget principal
    layout = QVBoxLayout()

    # Ajouter le widget de tableau à la mise en page
    layout.addWidget(table_widget)

    # Définir la mise en page pour le widget principal
    main_widget.setLayout(layout)

    # Afficher le widget principal
    main_widget.show()

    # Exécuter l'application PyQt6
    sys.exit(app.exec())

    '''
    for device in local_system.devices:
        print(
            "Device Name: {0}, Product Category: {1}, Product Type: {2}".format(
                device.name, device.product_category, device.product_type
            )
        )
    '''