from PyQt6.QtWidgets import (
    QWidget, QGridLayout, QSplitter, QStackedWidget, QApplication
)
from PyQt6.QtCore import Qt
import sys

from views.acquisition import AcquisitionView
from views.camera_params import CameraParamsView
from views.images import ImageDisplayGraph
from views.live_mode import liveWidget
from views.motors_control import MotorControlView


class MainWindow(QWidget):
    def __init__(self, parent = None):
        super().__init__()
        self.parent = parent
        self.tint = 0

        self.image_graph = ImageDisplayGraph(self, '#404040')
        self.live_widget = liveWidget()

        self.image1_widget = ImageDisplayGraph(self, '#909090')
        self.image2_widget = ImageDisplayGraph(self, '#909090')
        self.top_splitter = QSplitter(Qt.Orientation.Horizontal)
        self.top_splitter.addWidget(self.image1_widget)
        self.top_splitter.addWidget(self.image2_widget)

        # Zone dynamique pour image ou live
        self.stack = QStackedWidget()
        self.stack.addWidget(self.live_widget)  # index 0
        self.stack.addWidget(self.image_graph)  # index 1
        self.stack.setCurrentIndex(0)

        self.main_splitter = QSplitter(Qt.Orientation.Vertical)
        self.main_splitter.addWidget(self.top_splitter)
        self.main_splitter.addWidget(self.stack)
        self.main_splitter.setSizes([230,500])

        self.camera = CameraParamsView(self)
        self.acq = AcquisitionView(self)

        #self.start.clicked.connect(self.button_action)
        #self.stop.clicked.connect(self.button_action)

        self.layout = QGridLayout()
        self.setLayout(self.layout)

        self.layout.setColumnStretch(0, 1)
        self.layout.setColumnStretch(1, 3)

        # Configuration des lignes
        self.layout.setRowStretch(0, 1)
        self.layout.setRowStretch(1, 1)
        self.layout.setRowStretch(2, 1)

        self.motors = MotorControlView(self)

        self.layout.addWidget(self.camera, 0, 0)
        self.layout.addWidget(self.acq, 1, 0)
        self.layout.addWidget(self.motors, 2, 0)

        self.layout.addWidget(self.main_splitter, 0, 1, 3, 1)

        self.live = 1

        self.camera.camThread.connect(self.cam_action)
        #self.acq.acqThread.connect(self.acquisition_action)
        #self.motors.motThread.connect(self.motor_action)

    def button_action(self):
        sender = self.sender()
        if sender == self.start and self.live == 1:
            self.live = 0
            print("acquisition démarrée")
            self.stack.setCurrentIndex(1)
        elif sender == self.stop and self.live == 0:
            self.live = 1
            print("acquisition terminée")
            self.stack.setCurrentIndex(0)

    def cam_action(self, event):
        source_event = event.split("=")
        source = source_event[0]
        message = source_event[1]
        if source == "int":
            self.tint = int(message)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    fenetre = MainWindow()
    fenetre.show()
    sys.exit(app.exec())