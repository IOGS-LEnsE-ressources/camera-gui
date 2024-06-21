import numpy as np
from numpy.fft import fftshift, fft2
from scipy.interpolate import RegularGridInterpolator
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

WAVELENGTH = 632.8e-6  # en mm
Ne = 512
zoom_psf = 4
I = complex(0, 1)
PI = np.pi

N_phi = Ne // (2**zoom_psf)
plane_pupil_rate = Ne / N_phi

def ftm(phase, f_number):
    image_radius = WAVELENGTH * f_number

    dim_y, dim_x = phase.shape

    if dim_y <= dim_x:
        xi, yi = np.meshgrid(np.linspace(0, dim_x-1, N_phi), np.linspace(0, dim_y-1, int(np.round(N_phi * dim_y / dim_x))))
    else:
        xi, yi = np.meshgrid(np.linspace(0, dim_x-1, int(np.round(N_phi * dim_x / dim_y))), np.linspace(0, dim_y-1, N_phi))
    
    interpolator = RegularGridInterpolator((np.arange(dim_y), np.arange(dim_x)), phase, bounds_error=False, fill_value=0)
    phi_N_phi = interpolator((yi, xi))

    perfect_pupil = 1 - np.isnan(phi_N_phi).astype(int)
    phi_N_phi[np.isnan(phi_N_phi)] = 0

    perfect_magnitude = fftshift(fft2(perfect_pupil, (Ne, Ne)))
    magnitude = fftshift(fft2(perfect_pupil * np.exp(2 * I * PI * phi_N_phi), (Ne, Ne)))

    perfect_psf = perfect_magnitude * np.conjugate(perfect_magnitude)
    psf = magnitude * np.conjugate(magnitude)

    # Normalisation
    perfect_psf /= perfect_psf.max()
    psf /= psf.max()

    ftm = np.abs(fftshift(fft2(psf)))
    ftm /= ftm.max()

    perfect_ftm = np.abs(fftshift(fft2(perfect_psf)))
    perfect_ftm /= perfect_ftm.max()

    f_coupure = 1 / (WAVELENGTH * f_number)
    x_freq_3D = (plane_pupil_rate / Ne) * f_coupure * np.arange(-round(Ne / plane_pupil_rate), round(Ne / plane_pupil_rate) + 1)
    x_freq = (plane_pupil_rate / Ne) * f_coupure * np.arange(0, round(Ne / plane_pupil_rate) + 1)

    return {
        'perfect_ftm': perfect_ftm,
        'ftm': ftm,
        'f_coupure': f_coupure,
        'x_freq': x_freq,
        'x_freq_3d': x_freq_3D
    }

def display_3d_ftm(freq_3d, ftm):
    start = int(np.round(Ne / 2 - Ne / plane_pupil_rate))
    end = int(np.round(Ne / 2 + Ne / plane_pupil_rate)) + 1

    X, Y = np.meshgrid(freq_3d, freq_3d)
    ftm_cutted = ftm[start:end, start:end]

    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    ax.plot_surface(X, Y, ftm_cutted, cmap='viridis')
    fig.colorbar(ax.plot_surface(X, Y, ftm_cutted, cmap='viridis'))

    plt.show()

def display_ftm_x_cut(x_freq, ftm, perfect_ftm, plane_pupil_rate, Ne):
    start = int(np.round(Ne/2 + 1))
    end = int(np.round(Ne/2 + Ne/plane_pupil_rate) + 2)
    plt.figure()
    plt.plot(x_freq, ftm[start, start:end], label='FTM')
    plt.plot(x_freq, perfect_ftm[start, start:end], 'm--', label='FTM idéale')
    plt.grid(True)
    plt.title('FTM selon Ox')
    plt.xlabel('mm^{-1}')
    plt.legend()
    plt.show()

def display_ftm_y_cut(x_freq, ftm, perfect_ftm, plane_pupil_rate, Ne):
    start = int(np.round(Ne/2 + 1))
    end = int(np.round(Ne/2 + Ne/plane_pupil_rate) + 2)
    plt.figure()
    plt.plot(x_freq, ftm[start:end, start], label='FTM')
    plt.plot(x_freq, perfect_ftm[start:end, start], 'm--', label='FTM idéale')
    plt.grid(True)
    plt.title('FTM selon Oy')
    plt.xlabel('mm^{-1}')
    plt.legend()
    plt.show()

def defoc_phase_map(mask, defoc_lambda):
    y, x = np.indices(mask.shape)
    center = np.array(mask.shape) // 2
    r = np.sqrt((x - center[1])**2 + (y - center[0])**2)
    return defoc_lambda * (r**2 / (mask.shape[0]**2))

def display_ftm_with_defoc(x_freq, ftm_ideal, plane_pupil_rate, Ne, mask, phi_N_phi, ecart_normal, N_defoc_levels=5):
    fig, axes = plt.subplots(2, N_defoc_levels, figsize=(15, 6))
    for i in range(N_defoc_levels):
        defoc_lambda = ecart_normal * (i - 3) / 2
        Z_phase_defoc = defoc_phase_map(mask, defoc_lambda)
        phi_defocalise = phi_N_phi + Z_phase_defoc

        ampl_image_defocalise = fftshift(fft2(mask * np.exp(2 * 1j * np.pi * phi_defocalise), (Ne, Ne)))
        psf_norm_defocalise = ampl_image_defocalise * np.conj(ampl_image_defocalise)
        psf_norm_defocalise /= np.max(np.max(psf_norm_defocalise))

        ftm_defocalise = np.abs(fftshift(fft2(psf_norm_defocalise)))
        ftm_defocalise /= np.max(ftm_defocalise)

        axes[0, i].plot(x_freq, ftm_defocalise[Ne//2, Ne//2:Ne//2 + round(Ne / plane_pupil_rate) + 1])
        axes[0, i].plot(x_freq, ftm_ideal[Ne//2, Ne//2:Ne//2 + round(Ne / plane_pupil_rate) + 1], 'm--')
        axes[0, i].grid(True)
        axes[0, i].set_title(f"FTM coupe X pour Defoc = {defoc_lambda:.2f} mm")

        axes[1, i].plot(x_freq, ftm_defocalise[Ne//2:Ne//2 + round(Ne / plane_pupil_rate) + 1, Ne//2])
        axes[1, i].plot(x_freq, ftm_ideal[Ne//2:Ne//2 + round(Ne / plane_pupil_rate) + 1, Ne//2], 'm--')
        axes[1, i].grid(True)
        axes[1, i].set_title(f"FTM coupe Y pour Defoc = {defoc_lambda:.2f} mm")

    plt.tight_layout()
    plt.show()

if __name__ == '__main__':
    x = y = np.linspace(-5, 5, 100)
    X, Y = np.meshgrid(x, y)
    phase = X + Y

    result = ftm(phase, 5)
    display_3d_ftm(result['x_freq_3d'], result['ftm'])
    display_ftm_x_cut(result['x_freq'], result['ftm'], result['perfect_ftm'], plane_pupil_rate, Ne)
    display_ftm_y_cut(result['x_freq'], result['ftm'], result['perfect_ftm'], plane_pupil_rate, Ne)

if __name__ == '__main__':
    x_freq = np.linspace(-5, 5, 100)
    phi_N_phi = np.random.randn(100, 100)  # Exemple de phase aléatoire
    mask = np.ones_like(phi_N_phi)

    Ne = 512
    zoom_psf = 4
    N_phi = Ne // (2 ** zoom_psf)
    plane_pupil_rate = Ne / N_phi
    ecart_normal = 1.0  # Exemple de décalage normalisé

    ftm_ideal = np.abs(np.fft.fftshift(np.fft.fft2(np.random.randn(Ne, Ne))))  # Exemple de FTM idéale aléatoire

    display_ftm_with_defoc(x_freq, ftm_ideal, plane_pupil_rate, Ne, mask, phi_N_phi, ecart_normal)

