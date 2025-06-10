import numpy as np

class fileManager:
    def __init__(self, parent = None):
        self.parent = parent
        self.files = []
        self.directory = ""
        self.name = "\\"

    def sendTo(self, file, i):
        np.save(self.directory + self.name + str(i) + ".png", file)

    def changeDirectory(self, directory:str):
        self.dirtectory = directory

    def changeName(self, name:str):
        self.name = "\\" + name