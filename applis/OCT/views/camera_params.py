import cv2
import numpy as np
import sys
from PyQt6.QtWidgets import (
    QWidget, QGridLayout, QVBoxLayout,
    QLabel, QComboBox, QPushButton, QFrame,
    QSizePolicy, QSpacerItem, QMainWindow, QHBoxLayout, QApplication, QSlider, QLineEdit)
from PyQt6.QtCore import Qt, pyqtSignal

class CameraParamsView(QWidget):

    camThread = pyqtSignal(str)

    def __init__(self, parent = None):
        super().__init__()

        self.setWindowTitle("Paramètres Caméra")
        #self.setGeometry(100, 100, 300, 100)
        self.parent = parent

        # Créer un layout vertical
        layout = QVBoxLayout()

        layout_int_time = QHBoxLayout()
        layout_num = QHBoxLayout()

        self.int_time_label = QLabel("temps d'intégration : ")
        self.int_time_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)

        self.int_time_value = QLabel("50 ms")
        self.int_time_value.setFixedWidth(40)  # largeur fixe pour garder l'alignement stable
        self.int_time_value.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)

        layout_int_time.addWidget(self.int_time_label)
        layout_int_time.addWidget(self.int_time_value)

        self.num_label = QLabel("Nombre d'images moyennées ")
        self.num_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)

        self.num_value = QLineEdit("10")
        self.num_value.setEnabled = True
        self.num_value.editingFinished.connect(self.mise_a_jour_num)

        layout_num.addWidget(self.num_label)
        layout_num.addWidget(self.num_value)

        # Créer un slider horizontal
        self.slider = QSlider(Qt.Orientation.Horizontal)
        self.slider.setMinimum(0)
        self.slider.setMaximum(100)
        self.slider.setValue(50)
        self.slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.slider.setTickInterval(10)

        self.slider.valueChanged.connect(self.mise_a_jour_slider)

        # Ajouter le slider au layout
        layout.addLayout(layout_int_time)
        layout.addWidget(self.slider)
        layout.addLayout(layout_num)

        # Appliquer le layout à la fenêtre
        self.setLayout(layout)

    def mise_a_jour_slider(self, tint):
        self.int_time_value.setText(str(tint) + " ms")
        if __name__ == "__main__":
            print("integration time changed")
        self.camThread.emit("int" + str(tint))

    def mise_a_jour_num(self):
        if __name__ == "__main__":
            print("Number of averaged images changed")
        self.camThread.emit("num" + self.num_value.text())


if __name__ == "__main__":
    app = QApplication(sys.argv)
    fenetre = CameraParamsView()
    fenetre.show()
    sys.exit(app.exec())