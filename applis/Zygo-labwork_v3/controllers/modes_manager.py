# -*- coding: utf-8 -*-
"""*modes_manager.py* file.

./controllers/modes_manager.py contains ModesManager class to manage the different modes of the application.

.. note:: LEnsE - Institut d'Optique - version 1.0

.. moduleauthor:: Julien VILLEMEJANE (PRAG LEnsE) <julien.villemejane@institutoptique.fr>
Creation : march/2025
"""
import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

class ModesManager:
    """
    Main modes manager.
    The different modes are loaded from the main menu file (menu/menu.txt)
    """

    def __init__(self, menu):
        """
        Default constructor.
        """
        self.main_mode = None
        self.main_menu = menu
        self.main_menu.menu_changed.connect(self.update_mode)

    def update_mode(self):
        """

        :return:
        """
        print('Menu Changed !!')


