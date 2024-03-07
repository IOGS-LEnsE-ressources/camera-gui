"""
CameraBaslerWidget class to integrate a Basler camera into a PyQt6 graphical interface.

.. module:: CameraBaslerWidget
   :synopsis: class to integrate a Basler camera into a PyQt6 graphical interface.

.. note:: LEnsE - Institut d'Optique - version 0.1

.. moduleauthor:: Julien VILLEMEJANE <julien.villemejane@institutoptique.fr>
"""

import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget


class CameraBaslerWidget(QWidget):
    """CameraBaslerWidget class, children of QWidget.
    
    Class to integrate a Basler camera into a PyQt6 graphical interface.
    

    """
    
    def __init__(self) -> None:
        """
        Default constructor of the class.
        """
        super().__init__(parent=None)
        
        

    def quit_application(self) -> None:
        """
        Quit properly the PyQt6 application window.
        """
        QApplication.instance().quit()



class MyMainWindow(QMainWindow):
    """MyMainWindow class, children of QMainWindow.
    
    Class to test the previous widget.

    """
    def __init__(self) -> None:
        """
        Default constructor of the class.
        """
        super().__init__()
        self.setWindowTitle("CameraBaslerWidet Test Window")
        self.setGeometry(100, 100, 400, 300)
        self.central_widget = CameraBaslerWidget()
        self.setCentralWidget(self.central_widget)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_window = MyMainWindow()
    main_window.show()
    sys.exit(app.exec())