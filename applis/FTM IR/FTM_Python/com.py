import time
import pandas
import numpy as np
from PySide6 import QtWidgets, QtCore

''' Fonctions DS '''

def b2int(b):
    #Convertit les bytetypes en entiers
    g = b.decode()
    n = int(g)
    return n

def CheckID(ser):
    #Demande son ID à la Détection Synchrone
    ser.write(b'id\r\n')
    time.sleep(0.1)
    ser.readline()
    ID = ser.readline()
    ser.reset_output_buffer()
    ser.reset_input_buffer()
    return b2int(ID)

def Sen_read(ser):
    #Demande sa sensibilité à la DS
    ser.write(b'sen')
    time.sleep(0.1)
    ser.write(b'\r\n')
    time.sleep(0.1)
    ser.readline()
    SEN = ser.readline()
    ser.reset_output_buffer()
    ser.reset_input_buffer()
    return b2int(SEN)

def Sen_write(ser,SEN):
    #Change la sensibilité de la DS
    # SEN entre 0 et 15
    ser.write(b'sen ')
    time.sleep(0.1)
    v = str(SEN)+'\r\n'
    ser.write(v.encode())
    time.sleep(0.1)
    ser.readline()
    ser.reset_output_buffer()
    ser.reset_input_buffer()

def TC_read(ser):
    #Demande son temps de coupure à la DS
    ser.write(b'tc')
    time.sleep(0.1)
    ser.write(b'\r\n')
    time.sleep(0.1)
    ser.readline()
    TC = ser.readline()
    ser.reset_output_buffer()
    ser.reset_input_buffer()
    return b2int(TC)

def TC_write(ser,TC):
    #Change le temps de coupure de la DS
    # TC entre 0 et 13
    ser.write(b'tc ')
    time.sleep(0.1)
    v = str(TC)+'\r\n'
    ser.write(v.encode())
    time.sleep(0.1)
    ser.readline()
    ser.reset_output_buffer()
    ser.reset_input_buffer()

def DS_read(ser,TC):
    #Lit la valeur de l'amplitude
    time.sleep((1 + 2*(TC%2))*10**(TC//2-2))    #Attente de 10 fois le temps de coupure
    ser.write(b'mag')
    time.sleep(0.1)
    ser.write(b'\r\n')
    time.sleep(0.1)
    ser.readline()
    mag = ser.readline()
    return b2int(mag)

''' Fonctions Moteurs '''

def zGoTo(client,z):
    #Déplace le moteur longitudinal
    client.send(b'2MO') #Allumage
    time.sleep(1.5)
    u = '2PA'+str(z)
    u = u.encode()
    client.send(u)      #Déplacement
    time.sleep(0.1)
    c = 0
    while c==0:         #Attente de fin de déplacement
        QtCore.QCoreApplication.processEvents()
        client.send(b'2MD?')
        p = client.recv(3)
        c = int(p.decode())
        time.sleep(0.1)
    time.sleep(0.1)
    client.send(b'2MF') #Extinction

def xGoTo(client,x):
    #Déplace le moteur transversal
    time.sleep(0.2)
    u = '1PA'+str(x)    #Déplacement
    u = u.encode()
    client.send(u)
    c = 0
    while c==0:         #Attente de fin de déplacement
        QtCore.QCoreApplication.processEvents()
        client.send(b'1MD?')
        p = client.recv(3)
        c = int(p.decode())
        time.sleep(0.1)

def creer_fichier(M,Z,X,nom,TC,SEN):
    #Créer le fichier de mesure (.csv)
    (l,w) = M.shape

    #Création de l'en-tête
    #de la forme M1\M2; TC = *valeur; SEN = *valeur;
    h = [str(i) for i in range(l+1)]    
    if l >= 2:
        h[0] = 'M1\M2'
        h[1] = 'TC = ' + str((1+2*(TC%2))*10**(TC//2-3)) + ' s'
        if SEN<16 :
            h[2] = 'SEN = ' + str((1+2*(SEN%2))*10**(SEN//2-7)) + ' V'
        else :
            h[2] = 'SEN Auto'

    T = np.zeros((l+1,w+1)) 
    T[1:,1:] = M        #Corps du fichier (mesures)
    T[1:,0] = Z         #Première Colonne (positions du moteur longitudinal)
    T[0,1:] = X         #Deuxième Ligne (positions du moteur transversal)
    T = np.transpose(T)
    
    df = pandas.DataFrame(T)
    df.to_csv(nom,sep=';', header=h, index=False)   #écriture du fichier

def Extinction(self):
    xGoTo(self.moteurs,0)
    zGoTo(self.moteurs,0)
    self.moteurs.send(b'1MF')
    self.DS.close()
    self.moteurs.close()
    
    self.stop_acq = False
    
    self.bdc.setValue(0)                #reinitialisation de la barre de chargement
    self.bdc.setFormat("Progression globale de l'acquisition : 0%")
    self.bds.setValue(0)
    self.bds.setFormat("Scan 1/  : 0%")
    self.acq_button.setEnabled(True)
    self.acq_button.setChecked(False)
    self.acq_button.setText('Acquisition')
    
