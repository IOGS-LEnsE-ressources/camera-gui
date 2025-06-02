from models.motor_control import *
from _tests.camera_test import *
import numpy as np

exposure = 1000
N = 10
n=  5
delta_z = 0.1

P = Piezo()
M = Motor()

cam = find_camera()
cam.set_exposure(exposure)

for i in range(n):
    image1 = cam.get_images(N)
    P.set_voltage_piezo(2)
    image2 = cam.get_images(N)

    image = (np.mean(image1, axis=0) - np.mean(image2, axis=0))**2

    plt.figure()
    plt.imshow(image, cmap='gray')
    M.move_motor(0.1+delta_z*i)

plt.show()