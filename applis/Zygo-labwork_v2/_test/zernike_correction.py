import numpy as np
import matplotlib.pyplot as plt

def zernike_coefficient(surface, Z_nm, mask):
    """Calcule un coefficient de Zernike à partir d'une surface donnée."""
    return np.sum(surface * Z_nm * mask) / np.sum(Z_nm**2 * mask)

# Définition de la grille
N = 256  # Taille de la grille
x = np.linspace(-1, 1, N)
y = np.linspace(-1, 1, N)
X, Y = np.meshgrid(x, y)
R = np.sqrt(X**2 + Y**2)
Theta = np.arctan2(Y, X)
mask = R <= 1  # Pupille circulaire

'''
# Exemple d'une surface aberrée simulée (onde déformée)
surface = np.exp(-5 * R**2) * mask + 0.2 * (2 * R**2 - 1) * mask  # Ajout d'un Z_2^0 (Astigmatisme)

# Définition d'un polynôme de Zernike (n=2, m=0) - Astigmatisme
Z_20 = (2 * R**2 - 1) * mask

# Calcul du coefficient de Zernike
a_20 = zernike_coefficient(surface, Z_20, mask)
print(f"Coefficient Z_2^0 estimé : {a_20}")

# Reconstruction de la surface aberrée à partir du coefficient trouvé
surface_aberration = a_20 * Z_20

# Correction de la surface
surface_corrigée = surface - surface_aberration

# Affichage des résultats
fig, axs = plt.subplots(1, 3, figsize=(12, 4))
im1 = axs[0].imshow(surface * mask, extent=(-1, 1, -1, 1), cmap='jet')
axs[0].set_title("Surface aberrée")
fig.colorbar(im1, ax=axs[0])

im2 = axs[1].imshow(surface_aberration, extent=(-1, 1, -1, 1), cmap='jet')
axs[1].set_title("Correction appliquée")
fig.colorbar(im2, ax=axs[1])

im3 = axs[2].imshow(surface_corrigée * mask, extent=(-1, 1, -1, 1), cmap='jet')
axs[2].set_title("Surface corrigée")
fig.colorbar(im3, ax=axs[2])

plt.show()
'''


# Création d'une surface avec un tilt (pente)
tilt_x = -4  # Amplitude du tilt en x
tilt_y = 12  # Amplitude du tilt en y
surface = (tilt_x * X + tilt_y * Y) * mask  # Surface avec tilt

# Définition des polynômes de Zernike pour le tilt
Z_1m1 = X * mask  # Tilt en x
Z_11 = Y * mask  # Tilt en y

# Calcul des coefficients de tilt
a_1m1 = zernike_coefficient(surface, Z_1m1, mask)
a_11 = zernike_coefficient(surface, Z_11, mask)

print(f"Coefficient Z_1^-1 (Tilt x) estimé : {a_1m1}")
print(f"Coefficient Z_1^1 (Tilt y) estimé : {a_11}")

# Reconstruction de l'aberration (tilt)
surface_aberration = a_1m1 * Z_1m1 + a_11 * Z_11

# Correction de la surface
surface_corrigée = surface - surface_aberration

# Affichage des résultats
fig, axs = plt.subplots(1, 3, figsize=(12, 4))
im1 = axs[0].imshow(surface * mask, extent=(-1, 1, -1, 1), cmap='jet')
axs[0].set_title("Surface avec tilt")
fig.colorbar(im1, ax=axs[0])

im2 = axs[1].imshow(surface_aberration, extent=(-1, 1, -1, 1), cmap='jet')
axs[1].set_title("Correction appliquée")
fig.colorbar(im2, ax=axs[1])

im3 = axs[2].imshow(surface_corrigée * mask, extent=(-1, 1, -1, 1), cmap='jet')
axs[2].set_title("Surface corrigée")
fig.colorbar(im3, ax=axs[2])

plt.show()
