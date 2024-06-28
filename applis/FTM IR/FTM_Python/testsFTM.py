import matplotlib.pyplot as plt
from math import *
import numpy as np
import scipy as sp
import scipy.signal

coupe = 100
points = 2048

u_image = np.array(range(1,points+1))
u_image = 100* u_image * pi * 0.04 * 100 / points
airy = (2*sp.special.jv(1,u_image)/u_image)**2
airy = airy[:-coupe]
Airy = np.concatenate((airy[::-1],[1],airy))

TF = np.absolute((np.fft.fft(Airy,8192)))
TF /= max(TF)
mesureTheo = []
for i in range(len(Airy)):
    mesureTheo.append(Airy[i:].sum())

ouv_num = 1/12

L = np.array([6,7,8,9,10,11,12]) * 1e-3
poids = np.array([0,2,3.5,4.5,3.5,2.5,1.5]) #a verifier soigneusement un jour !!!

wc = (2 * ouv_num) / L
w = np.linspace(0,max(wc),1024)
theo = np.zeros(1024)

for i in range(len(wc)):
    for j in range(len(w)):
        if w[j] <= wc[i]:
            t = j
    theo[:t] += (2/pi)*(np.arccos(w[:t]/wc[i])-(w[:t]/wc[i])*(1-(w[:t]/wc[i])**2)**0.5)*poids[i]
theo /= sum(poids)
truc = np.abs(np.fft.fftshift(np.fft.ifft(np.concatenate((theo[::-2],theo)))))
truc /= max(truc)
f = np.fft.fftfreq(8192,0.01)

x_truc = np.linspace(-len(truc)/2,len(truc)/2,len(truc))
x_airy= np.linspace(-len(Airy)/2,len(Airy)/2+1,len(Airy))

plt.plot(x_truc,truc)
plt.plot(x_airy,Airy)
plt.figure()
plt.plot(f,TF)
plt.plot(w,theo)
plt.show()

##Mesures_derivees = np.array([-np.diff(mesureTheo)])
##
####TF = np.abs(np.fft.fftshift(np.fft.fft(derivee)))
####
####plt.figure()
####plt.plot(TF)
####plt.show()
##
### Calcul des FTMs
###Calcul de Bessel1 pour la convolution
###Diam_image = 36.5e-3 #en mm
###calcul de la ftml padding a 1024 points
##echelle_freq = np.linspace(0,100,1024)
##
##tableau_ftm = []
##nbrevisu = 512
##Han = np.hanning(Mesures_derivees.shape[1])
##fenetree = Mesures_derivees * Han
##
##for i in range(fenetree.shape[0]):
##    ftm = np.fft.fft(fenetree[i,:],1024)
##    ftm = ftm[:nbrevisu]
##    #deconvolution (à refaire soigneusement avec la fct scipy.signal.deconvolve())
##    ftm = np.sqrt(ftm * np.conj(ftm))
##    ftmd = -np.diff(ftm)
##    j = np.argmax(ftmd[:256])
##    fit = np.polyfit(range(j,nbrevisu),ftm[j:],10)
##    ftm = np.polyval(fit,range(nbrevisu))
##    ftm = ftm / max(ftm)
##    tableau_ftm.append(ftm)
##
##tableau_ftm = np.array(tableau_ftm).transpose()[:nbrevisu,:]
##
##ouv_num = 1/12
##
##L = np.array([6,7,8,9,10,11,12]) * 1e-3
##poids = np.array([0,2,3.5,4.5,3.5,2.5,1.5]) #a verifier soigneusement un jour !!!
##
##wc = (2 * ouv_num) / L
##w = np.linspace(0,max(wc),1024)
##theo = np.zeros(1024)
##
##for i in range(len(wc)):
##    for j in range(len(w)):
##        if w[j] <= wc[i]:
##            t = j
##    theo[:t] += (2/pi)*(np.arccos(w[:t]/wc[i])-(w[:t]/wc[i])*(1-(w[:t]/wc[i])**2)**0.5)*poids[i]
##theo /= sum(poids)
##
### Affichage
##plt.figure()
##plt.plot(w,theo)
##for i in range(tableau_ftm.shape[1]):
##    plt.plot(echelle_freq[:nbrevisu], np.real(tableau_ftm[:,i]))
##plt.show()
##
