# -*- coding: utf-8 -*-
"""*initialization_parameters.py* file.

...

This file is attached to a 1st year of engineer training labwork in photonics.
Subject : http://lense.institutoptique.fr/ressources/Annee1/TP_Photonique/S5-2324-PolyCI.pdf

.. note:: LEnsE - Institut d'Optique - version 1.0

.. moduleauthor:: Julien VILLEMEJANE (PRAG LEnsE) <julien.villemejane@institutoptique.fr>
.. moduleauthor:: Dorian MENDES (Promo 2026) <dorian.mendes@institutoptique.fr>

"""

def read_default_parameters(file):
    default_parameters = {}
    with open(file, 'r') as f:
        for line in f:
            if line.startswith('#'):
                continue
            key, value = line.strip().split('; ')
            default_parameters[key.strip()] = value.strip()
    return default_parameters

def modify_parameter_value(file, parameter, new_value):
    parameter_found = False
    with open(file, 'r') as f:
        lines = f.readlines()

    with open(file, 'w') as f:
        for line in lines:
            if line.startswith('#'):
                f.write(line)
                continue

            key, value = line.strip().split('; ')
            if key == parameter:
                f.write(f"{key}; {new_value}\n")
                parameter_found = True
            else:
                f.write(line)

    if not parameter_found:
        print(f"The parameter '{parameter}' was not found in the file.")
