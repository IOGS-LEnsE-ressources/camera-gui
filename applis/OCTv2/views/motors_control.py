import cv2
import numpy as np
import sys
from PyQt6.QtWidgets import (
    QWidget, QGridLayout, QVBoxLayout,
    QLabel, QComboBox, QPushButton, QFrame,
    QSizePolicy, QSpacerItem, QMainWindow, QHBoxLayout, QApplication, QSlider, QLineEdit, QFileDialog)
from PyQt6.QtCore import Qt, pyqtSignal

class MotorControlView(QWidget):

    motThread = pyqtSignal(str)

    def __init__(self, parent = None):
        super().__init__()

        self.parent = parent
        self.setWindowTitle("Contrôle Moteur")
        self.Z = 0

        layout = QVBoxLayout()

        stepper_layout = QHBoxLayout()
        step_z_layout = QHBoxLayout()
        piezo_layout = QHBoxLayout()
        step_v_layout = QHBoxLayout()

        ### Direction du moteur

        self.stepper_label = QLabel("Stepper Motor")
        self.stepper_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)

        self.stepper_down = QPushButton("DOWN")
        self.stepper_down.setStyleSheet("""
                            QPushButton {
                                background-color: #ee0000; 
                                color: white;                
                                border-radius: 5px;
                                padding: 8px 16px;
                            }
                            QPushButton:hover {
                                background-color: #ce0000;
                            }
                            QPushButton:pressed {
                                background-color: #ae0000;
                            }
                        """)

        self.stepper_up = QPushButton("UP")
        self.stepper_up.setStyleSheet("""
                            QPushButton {
                                background-color: #ee0000; 
                                color: white;                
                                border-radius: 5px;
                                padding: 8px 16px;
                            }
                            QPushButton:hover {
                                background-color: #ce0000;
                            }
                            QPushButton:pressed {
                                background-color: #ae0000;
                            }
                        """)

        stepper_layout.addWidget(self.stepper_label)
        stepper_layout.addWidget(self.stepper_down)
        stepper_layout.addWidget(self.stepper_up)

        ### Pas en z du moteur

        self.step_z_label = QLabel("Pas \u0394z (\u03bcm)")
        self.step_z_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)

        self.step_z_section = QLineEdit("2")
        self.step_z_section.setEnabled = True

        self.z_value = QLabel(f"Z = {self.Z} \u03bcm")
        self.z_value.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)

        step_z_layout.addWidget(self.step_z_label)
        step_z_layout.addWidget(self.step_z_section)
        step_z_layout.addWidget(self.z_value)

        ### Valeur tension Piezo

        self.v0_section = QLabel("Piezo Motor - V0 = ")
        self.v0_section.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)

        self.v0_value = QLineEdit("2")
        self.v0_value.setEnabled = True

        self.v0_unit = QLabel("V")
        self.v0_unit.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)

        piezo_layout.addWidget(self.v0_section)
        piezo_layout.addWidget(self.v0_value)
        piezo_layout.addWidget(self.v0_unit)

        ### Valeur pas en tension

        self.delta_v_section = QLabel("Pas \u0394V (V)")
        self.delta_v_section.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)

        self.delta_v_value = QLineEdit("2")
        self.delta_v_value.setEnabled = True

        step_v_layout.addWidget(self.delta_v_section)
        step_v_layout.addWidget(self.delta_v_value)

        layout.addLayout(stepper_layout)
        layout.addLayout(step_z_layout)
        layout.addSpacing(20)
        layout.addLayout(piezo_layout)
        layout.addLayout(step_v_layout)

        self.setLayout(layout)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    fenetre = MotorControlView()
    fenetre.show()
    sys.exit(app.exec())