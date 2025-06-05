import cv2
import numpy as np
import sys
from PyQt6.QtWidgets import (
    QWidget, QGridLayout, QVBoxLayout,
    QLabel, QComboBox, QPushButton, QFrame,
    QSizePolicy, QSpacerItem, QMainWindow, QHBoxLayout, QApplication, QSlider, QLineEdit, QFileDialog)
from PyQt6.QtCore import Qt, pyqtSignal


class AcquisitionView(QWidget):

    acqThread = pyqtSignal(str)

    def __init__(self, parent = None):
        super().__init__()

        self.setWindowTitle("Acquisition")
        self.parent = parent

        layout = QVBoxLayout()

        directory_layout = QHBoxLayout()
        name_layout = QHBoxLayout()
        step_size_layout = QHBoxLayout()
        step_num_layout = QHBoxLayout()
        buttons_layout = QHBoxLayout()

        ### Destination

        self.directory_label = QLabel("Destination : ")
        self.directory_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)

        self.directory = QLineEdit("")
        self.directory.setEnabled = True
        self.directory.editingFinished.connect(self.directory_action)

        self.search = QPushButton("Parcourir")
        self.search.clicked.connect(self.directory_action)

        directory_layout.addWidget(self.directory_label)
        directory_layout.addWidget(self.directory)
        directory_layout.addWidget(self.search)

        ### Nom du fichier

        self.name_label = QLabel("Nom : ")
        self.name_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)

        self.name = QLineEdit("")
        self.name.setEnabled = True
        self.name.editingFinished.connect(self.directory_action)

        name_layout.addWidget(self.name_label)
        name_layout.addWidget(self.name)

        ### Pas

        self.step_size_label = QLabel("Pas : p(\u03bcm)")
        self.step_size_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)

        self.step_size = QLineEdit("5")
        self.step_size.setEnabled = True
        self.step_size.editingFinished.connect(self.step_action)

        step_size_layout.addWidget(self.step_size_label)
        step_size_layout.addWidget(self.step_size)

        ### Nombre de pas

        self.step_num_label = QLabel("Nombre de pas : ")
        self.step_num_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)

        self.step_num = QLineEdit("5")
        self.step_num.setEnabled = True
        self.step_num.editingFinished.connect(self.step_action)

        step_num_layout.addWidget(self.step_num_label)
        step_num_layout.addWidget(self.step_num)

        ### start/stop

        self.start_button = QPushButton("Start")
        self.start_button.setStyleSheet("""
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
        self.start_button.clicked.connect(self.step_action)

        self.stop_button = QPushButton("Stop")
        self.stop_button.setStyleSheet("""
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

        self.stop_button.clicked.connect(self.step_action)

        buttons_layout.addWidget(self.start_button)
        buttons_layout.addWidget(self.stop_button)

        layout.addLayout(directory_layout)
        layout.addLayout(name_layout)
        layout.addLayout(step_size_layout)
        layout.addLayout(step_num_layout)
        layout.addLayout(buttons_layout)
        layout.addSpacing(40)

        self.setLayout(layout)

    def directory_action(self):
        sender = self.sender()
        if sender == self.directory:
            self.acqThread.emit("dir=" + self.directory.text())
            print("the file directory has been modified")
        elif sender == self.search:
            self.acqThread.emit("request=")
        elif sender == self.name:
            self.acqThread.emit("name=" + self.name.text())
            print(f"the name of the file will be {self.name.text()}")

    def step_action(self):
        sender = self.sender()
        if sender == self.step_size:
            self.acqThread.emit("StepSize=" + self.step_size.text())
            print(f"the step size has been updated")
        elif sender == self.step_num:
            self.acqThread.emit("StepNum=" + self.step_num.text())
            print(f"the number of steps has been updated")
        elif sender == self.start_button:
            self.acqThread.emit("Start=")
            print(f"the acquisition has begun")
        elif sender == self.stop_button:
            self.acqThread.emit("Stop=")
            print(f"the acquisition has been stopped")

    def directory(self):
        folder_request = QFileDialog.getExistingDirectory(self, "Choisir un fichier")
        if folder_request:
            self.acqThread.emit("dir=" + folder_request)
            print(f"the new destination is {folder_request}")
            self.directory.setText(folder_request)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    fenetre = AcquisitionView()
    fenetre.show()
    sys.exit(app.exec())