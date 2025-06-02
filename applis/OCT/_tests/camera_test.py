from lensecam.basler.camera_basler import CameraBasler
import matplotlib.pyplot as plt

def find_camera():
    cam = CameraBasler()
    cam_connected = cam.find_first_camera()
    print(cam_connected)
    return cam

exposure = 100

cam = find_camera()
cam.set_exposure(exposure)
image = cam.get_image()


plt.figure()
plt.imshow(image, cmap='gray')
plt.show()