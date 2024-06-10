if __name__ == '__main__':
    from hariharan_algorithm import *
else:
    from process.hariharan_algorithm import *

def get_phase(camera_widget):
    images = []
    for _ in range(5):
        image = camera_widget.get_image()
        images.append(image)
        # Piezo add phase (wait until it's done)

    import matplotlib.pyplot as plt
    plt.figure()
    plt.title('Raw image')
    plt.imshow(image)
    plt.show()

    plt.figure()
    plt.title('Image * mask')
    plt.imshow(image*mask)
    plt.show()

    return hariharan_algorithm(*images), images