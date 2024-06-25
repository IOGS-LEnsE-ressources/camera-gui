import matplotlib.pyplot as plt
import numpy as np
from scipy.fftpack import fftshift, fft2
import cv2

PI = np.pi
I = 1j

def get_psf(wavefront, zoom, Ne):
    # Calculating necessary parameters
    N_phi = int(Ne // (2 ** zoom))

    phi_reshaped_real_part = cv2.resize(np.real(wavefront), (N_phi, N_phi), interpolation=cv2.INTER_LINEAR)
    phi_reshaped_imaginary_part = cv2.resize(np.imag(wavefront), (N_phi, N_phi), interpolation=cv2.INTER_LINEAR)
    phi_reshaped = phi_reshaped_real_part + I* phi_reshaped_imaginary_part

    phi_reshaped[np.isnan(phi_reshaped)] = 0

    psf = np.abs(fftshift(fft2(phi_reshaped, (Ne, Ne))))**2
    psf /= psf.max()

    threshold_dB = -30
    threshold_gain = 10**(threshold_dB/10)
    psf[psf<threshold_gain] = threshold_gain
    psf = 10*np.log10(psf)
    
    return psf
