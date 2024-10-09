
import numpy as np
import matplotlib.pyplot as plt

N = 1001
x = np.linspace(0, 1, N)
Te = x[1] - x[0]

freq = 13
s = 3 + np.sin(2*np.pi*freq*x) + np.sin(2*np.pi*4*freq*x)

plt.figure()
plt.plot(x,s)

TF_s = np.fft.fft(s)

Fs = 1/Te

xf = np.linspace(0, 1, N, endpoint=False) * Fs

# Modify to -fs/2 to fs/2
condition = xf > Fs/2
xf[condition] = -(Fs - xf[condition])
xf = np.fft.fftshift(xf)


print(f'Man = {xf}')

freqs = np.fft.fftfreq(N, Te)
print(f'NP = {freqs}')


plt.figure()
plt.plot(np.fft.fftshift(freqs), np.fft.fftshift(np.abs(TF_s)))
plt.show()



