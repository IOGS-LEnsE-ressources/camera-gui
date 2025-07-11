from PyQt6.QtWidgets import (
    QWidget, QApplication, QFileDialog, QHBoxLayout, QPushButton
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
import sys


ancien_test = 0

class mainWindow(QWidget):
    def __init__(self, parent = None):
        super().__init__()
        self.parent = parent

        self.layout = QHBoxLayout()

        self.widget = secondWidget()
        self.layout.addWidget(self.widget)

        if ancien_test:
            self.widget.thread.connect(self.action)
        else:
            self.widget.button.clicked.connect(self.get_file)

        self.setLayout(self.layout)

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(500)

    def update_frame(self):
        print("update")
        self.widget.change_state()
        return None

    def get_file(self):
        self.timer.stop()
        print("open")
        folder = QFileDialog.getExistingDirectory(None, "choisir un fichier")
        if folder:
            print(f"the new destination is {folder}")
        else:
            print("closed")
        self.timer.start(500)

    def action(self, event):
        folder = QFileDialog.getExistingDirectory(None, "choisir un fichier")
        if folder:
            print(f"the new destination is {folder}")


class secondWidget(QWidget):

    thread = pyqtSignal(str)

    def __init__(self, parent = None):
        super().__init__()
        self.parent = parent

        self.layout = QHBoxLayout()
        self.button = QPushButton("Push me")
        self.button.setStyleSheet("background-color: red; color: white;")
        self.layout.addWidget(self.button)

        self.setLayout(self.layout)

        self.button.clicked.connect(self.action)

        self.state = 1

    def action(self):
        self.thread.emit("request")

    def change_state(self):
        self.state = not self.state
        if self.state:
            self.button.setStyleSheet("background-color: red; color: white;")
        else:
            self.button.setStyleSheet("background-color: green; color: white;")



if __name__ == "__main__":
    app = QApplication(sys.argv)
    fenetre = mainWindow()
    fenetre.show()
    sys.exit(app.exec())
