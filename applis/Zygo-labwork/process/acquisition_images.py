if __name__ == '__main__':
    from hariharan_algorithm import *
else:
    from process.hariharan_algorithm import *

def get_phase(parent):
    images = []
    mask = parent.mask
    try:
        parent.camera_thread.stop()
        parent.camera.init_camera()
        parent.camera.alloc_memory()
        parent.camera.start_acquisition()
        for i in range(5):
            print(f'Image {i}')
            raw_array = parent.camera_widget.camera.get_image()
            images.append(raw_array)
            # Piezo add phase (wait until it's done)

    except Exception as e:
        print(f'Exception Phase - {e}')

    import matplotlib.pyplot as plt
    plt.figure()
    plt.title('Raw image')
    plt.imshow(raw_array)
    plt.show()

    plt.figure()
    plt.title('Image * mask')
    plt.imshow(raw_array*mask)
    plt.show()

    parent.camera.stop_acquisition()
    parent.camera.free_memory()
    parent.camera_thread.start()
    return hariharan_algorithm(*images), images