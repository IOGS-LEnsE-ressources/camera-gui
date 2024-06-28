#!/usr/bin/env python
# -*- coding: utf-8 -*-
import time
from PySide6 import QtWidgets, QtCore
from PySide6.QtGui import QIcon, QPixmap
from pyparsing import PositionToken
import pyqtgraph as pg
import matplotlib.pyplot as plt
import serial
import os
import ctypes
import platform
import socket
from math import *
import numpy
import scipy as sp
import scipy.signal
from com import *

class MWindow(QtWidgets.QWidget):
    """
    Main window of the interface
    """

    def __init__(self, app):
        super(MWindow, self).__init__()

        """ Initialisation """
        # Parametres de reglage
        self.xpas = 0.01                #pas d'echantillonnage transversal
        self.xn = 41                    #nombre d'echantillons transversaux
        self.xmin = -0.2                #position transversale minimale
        self.xmax = 0.2                 #position transversale maximale

        self.zpas = 0.5                 #pas d'echantillonnage longitudinal
        self.zn = 5                     #nombre d'echantillons longitudinaux
        self.zmin = -1                  #position longitudinale minimale
        self.zmax = 1                   #position longitudinale maximale

        self.TC = 3                     #indice du temps de coupure de la Détection synchrone
        self.SEN = 16                   #indice de la sensibilité de la detection synchrone

        # Couleurs des graphiques
        self.couleurs = ['#FF0000', '#00FF00', '#FFFF00', '#00FFFF', # Red, Green, Yellow, Cyan-Aqua
                         '#FF00FF', '#849FFF', '#0000FF', '#FFA500', # Magenta-fuchsia, Malibu, Blue, Web-orange
                         '#800080', '#FFB0C0', '#A52A2A', '#FFFFFF'] # Fresh eggplant, Sundown, Mexican red, White
        self.nb_couleurs = len(self.couleurs)
        
        # Parametres de connexion
        self.HOST = '10.117.19.5'
        self.PORT = 5001

        """ Mise en place de l'interface """
        self.current_path = os.getcwd()
        self.img_path = os.path.join(self.current_path, 'images')

        # Init const
        self.app = app
        self.session_opened = True
        self.traitement = False
        self.setWindowTitle('FTM IR') # Titre de la fenêtre
        self.setWindowIcon(QIcon(os.path.join(self.img_path,'IOGS-LEnsE-logo-small.jpg')))
        self.frame_rate = 0

        # Layout
        self.lay1 = QtWidgets.QVBoxLayout()
        self.lay2 = QtWidgets.QHBoxLayout()
        self.lay3 = QtWidgets.QVBoxLayout()

        # Layout 1: Titre + layout 2
        self.title = QtWidgets.QLabel("Mesure de la FTM d'un objectif dans l'IR par Foucaultage")
        self.title.setObjectName('Titre')
        self.title.setAlignment(QtCore.Qt.AlignCenter)
        self.lay1.addWidget(self.title,0)
        
        self.lay1.addLayout(self.lay2,1)

        # Layout 2: Schema + barre de chargement + lay3
        self.bdc_lay = QtWidgets.QVBoxLayout()
        self.bdc = QtWidgets.QProgressBar()
        self.bdc.setValue(0)
        self.bdc.setFormat("Progression globale de l'acquisition : 0%")
        self.bdc.setAlignment(QtCore.Qt.AlignCenter)

        self.bds = QtWidgets.QProgressBar()
        self.bds.setValue(0)
        self.bds.setFormat("Scan 1/  : 0%")
        self.bds.setAlignment(QtCore.Qt.AlignCenter)
        
        self.scheme = QtWidgets.QLabel()
        self.pixmap = QPixmap('images\schematest.png')         #adresse de l'image
        self.scheme.setPixmap(self.pixmap)
        self.scheme.setScaledContents(True)
        self.bdc_lay.addWidget(self.scheme,1)
        self.bdc_lay.addWidget(self.bdc,0)
        self.bdc_lay.addWidget(self.bds,0)
        self.lay2.addLayout(self.bdc_lay,1)
        
        self.lay2.addLayout(self.lay3,0)

        # Layout 3: Parametres + acq/treat buttons

        ## Parametres du moteur 1 pour le mouvement transversal
        self.p_x = QtWidgets.QGroupBox("Mouvement transversal (x)")
        self.x_max_edit = QtWidgets.QDoubleSpinBox()
        self.x_max_edit.setLocale(QtCore.QLocale('English')) #Change la virgule par un point pour le séparateur décimal
        self.x_max_edit.setFixedWidth(60)
        self.x_max_edit.setDecimals(3)                       #Nombre de chiffres après la virgule (maintenant un point)
        self.x_max_edit.setMaximum(10)                       #Valeur maximale
        self.x_max_edit.setMinimum(self.xmin)
        self.x_max_edit.setValue(self.xmax)
        self.x_max_edit.setSingleStep(0.001)
        self.x_max_edit.valueChanged.connect(self.set_xmax)  #Quand la valeur change on lance set_xmax() qui met a jour les valeurs de xmax et xn
        
        self.x_min_edit = QtWidgets.QDoubleSpinBox()
        self.x_min_edit.setLocale(QtCore.QLocale('English')) 
        self.x_min_edit.setFixedWidth(60)
        self.x_min_edit.setDecimals(3)                       
        self.x_min_edit.setMaximum(self.xmax)
        self.x_min_edit.setMinimum(-10)                      #Valeur minimale
        self.x_min_edit.setValue(self.xmin)
        self.x_min_edit.setSingleStep(0.001)
        self.x_min_edit.valueChanged.connect(self.set_xmin)  #Quand la valeur change on lance set_xmin() qui met a jour les valeurs de xmin et xn
        
        self.x_pas_edit = QtWidgets.QDoubleSpinBox()
        self.x_pas_edit.setLocale(QtCore.QLocale('English'))
        self.x_pas_edit.setFixedWidth(60)
        self.x_pas_edit.setMaximum(1)
        self.x_pas_edit.setMinimum(0)
        self.x_pas_edit.setValue(self.xpas)
        self.x_pas_edit.setDecimals(3)
        self.x_pas_edit.setSingleStep(0.001)
        self.x_pas_edit.valueChanged.connect(self.set_xpas) #Quand la valeur change on lance set_xpas() qui met a jour les valeurs de xpas et xn
        
        self.xn_lbl = QtWidgets.QLabel(str(self.xn))        #Affiche xn
        self.x_layout = QtWidgets.QGridLayout()
        self.x_max_lbl = QtWidgets.QLabel("Max (en mm):")
        self.x_layout.addWidget(self.x_max_lbl,1,1)
        self.x_layout.addWidget(self.x_max_edit,1,2)
        self.x_min_lbl = QtWidgets.QLabel("Min (en mm):")
        self.x_layout.addWidget(self.x_min_lbl,2,1)
        self.x_layout.addWidget(self.x_min_edit,2,2)
        self.x_pas_lbl = QtWidgets.QLabel("Pas d'échantillonnage (en mm):")
        self.x_layout.addWidget(self.x_pas_lbl,3,1)
        self.x_layout.addWidget(self.x_pas_edit,3,2)
        self.xn_lbl_lbl = QtWidgets.QLabel("Nb d'échantillons:")
        self.x_layout.addWidget(self.xn_lbl_lbl,4,1)
        self.x_layout.addWidget(self.xn_lbl,4,2)
        self.min_points_warning = QtWidgets.QLabel()        #Préviens si le min d'echantillons pour filtrer n'est pas atteint
        self.x_layout.addWidget(self.min_points_warning,5,1,1,2)
        self.x_layout.setAlignment(QtCore.Qt.AlignTop)
        self.p_x.setLayout(self.x_layout)
        
        ## Parametres du moteur 2 pour le mouvement longitudinal
        self.p_z = QtWidgets.QGroupBox("Mouvement longitudinal (z)")
        self.z_max_edit = QtWidgets.QDoubleSpinBox()
        self.z_max_edit.setLocale(QtCore.QLocale('English'))
        self.z_max_edit.setFixedWidth(60)
        self.z_max_edit.setDecimals(2)
        self.z_max_edit.setMaximum(10)                      #Valeur maximale
        self.z_max_edit.setMinimum(self.zmin)
        self.z_max_edit.setValue(self.zmax)
        self.z_max_edit.setSingleStep(0.01)
        self.z_max_edit.valueChanged.connect(self.set_zmax) #Quand la valeur change on lance set_zmax() qui met a jour les valeurs de zmax et zn
        
        self.z_min_edit = QtWidgets.QDoubleSpinBox()
        self.z_min_edit.setLocale(QtCore.QLocale('English'))
        self.z_min_edit.setFixedWidth(60)
        self.z_min_edit.setDecimals(2)
        self.z_min_edit.setMaximum(self.zmax)
        self.z_min_edit.setMinimum(-10)                     #Valeur minimale
        self.z_min_edit.setValue(self.zmin)
        self.z_min_edit.setSingleStep(0.01)
        self.z_min_edit.valueChanged.connect(self.set_zmin) #Quand la valeur change on lance set_zmin() qui met a jour les valeurs de zmin et zn
        
        self.z_pas_edit = QtWidgets.QDoubleSpinBox()
        self.z_pas_edit.setLocale(QtCore.QLocale('English'))
        self.z_pas_edit.setFixedWidth(60)
        self.z_pas_edit.setMaximum(10)
        self.z_pas_edit.setMinimum(0)
        self.z_pas_edit.setValue(self.zpas)
        self.z_pas_edit.setDecimals(2)
        self.z_pas_edit.setSingleStep(0.01)
        self.z_pas_edit.valueChanged.connect(self.set_zpas) #Quand la valeur change on lance set_zpas() qui met a jour les valeurs de zpas et zn
        
        self.zn_lbl = QtWidgets.QLabel(str(self.zn))
        self.z_layout = QtWidgets.QFormLayout()
        self.z_layout.addRow("Max (en mm):", self.z_max_edit)
        self.z_layout.addRow("Min (en mm):", self.z_min_edit)
        self.z_layout.addRow("Pas d'échantillonnage (en mm):", self.z_pas_edit)
        self.z_layout.addRow("Nb de scans:", self.zn_lbl)
        self.p_z.setLayout(self.z_layout)

        ## Parametres de la détection synchrone
        self.p_DS = QtWidgets.QGroupBox("Détection synchrone")
        ###Sensibilité
        self.DS_sen_drop = QtWidgets.QComboBox()
        self.DS_sen_drop.addItems(['100nV','300nV','1μV','3μV','10μV','30μV','100μV','300μV','1mV','3mV','10mV',
            '30mV','100mV','300mV','1V','3V','Auto'])       #Valeurs de la sensibilité (Auto ne correspond pas au mode de la DS mais à notre mode plus efficace)
        self.DS_sen_drop.setFixedWidth(70)
        self.DS_sen_drop.setCurrentIndex(16)
        self.DS_sen_drop.currentIndexChanged.connect(self.set_sen) #Quand la valeur change on lance set_sen() qui met a jour la valeur de SEN
        ###Temps de coupure
        self.DS_tc_drop = QtWidgets.QComboBox()
        self.DS_tc_drop.addItems(['1ms','3ms','10ms','30ms','100ms','300ms','1s','3s','10s','30s','100s','300s','1ks','3ks']) #Valeurs du temps de coupure
        self.DS_tc_drop.setFixedWidth(70)
        self.DS_tc_drop.setCurrentIndex(self.TC)
        self.DS_tc_drop.currentIndexChanged.connect(self.set_tc)    #Quand la valeur change on lance set_tc() qui met a jour la valeur de TC
        
        self.DS_layout = QtWidgets.QFormLayout()
        self.DS_layout.addRow("Sensibilité:", self.DS_sen_drop)
        self.DS_layout.addRow("Temps/échantillon:", self.DS_tc_drop)
        self.p_DS.setLayout(self.DS_layout)

        ## Temps total de l'acquisition

        self.p_temps = QtWidgets.QGroupBox('Acquisition totale')
        self.p_temps.setObjectName('temps')
        self.temps_layout = QtWidgets.QVBoxLayout()
        self.nb_echantillons = QtWidgets.QLabel()
        self.temps_acquisition = QtWidgets.QLabel()
        self.nb_echantillons.setAlignment(QtCore.Qt.AlignCenter)
        self.temps_acquisition.setAlignment(QtCore.Qt.AlignCenter)
        self.temps_refresh()
        self.temps_layout.addWidget(self.nb_echantillons)
        self.temps_layout.addWidget(self.temps_acquisition)
        self.p_temps.setLayout(self.temps_layout)

        ## Boutons
        self.acq_button = QtWidgets.QPushButton("Acquisition")      #Bouton d'acquisition qui lance acquire_fct
        self.acq_button.setCheckable(True)
        self.acq_button.clicked.connect(self.acquire_btn)
        self.stop_acq = False
        self.treat_button = QtWidgets.QPushButton("Traitement")     #Bouton de traitement qui lance treat_fct
        self.treat_button.clicked.connect(self.treat_fct)

        self.lay3.addWidget(self.p_x,1)
        self.lay3.addWidget(self.p_z,1)
        self.lay3.addWidget(self.p_DS,1)
        self.lay3.addWidget(self.p_temps,0)
        self.lay3.addWidget(self.acq_button,1)
        self.lay3.addWidget(self.treat_button,1)

        self.setLayout(self.lay1)

    def set_xmax(self):
        #Mise a jour de xmax, le maximum de xmin et xn
        self.xmax = self.x_max_edit.value()
        self.x_min_edit.setMaximum(self.xmax)
        self.xn_refresh()
        self.temps_refresh()

    def set_xmin(self):
        #Mise a jour de xmin, le minimum de xmax et xn
        self.xmin = self.x_min_edit.value()
        self.x_max_edit.setMinimum(self.xmin)
        self.xn_refresh()
        self.temps_refresh()

    def set_xpas(self):
        #Mise a jour de xpas et xn
        self.xpas = self.x_pas_edit.value()
        self.xn_refresh()
        self.temps_refresh()

    def xn_refresh(self):
        #Affichage du nombre d'echantillons par scan et d'un warning si le filtrage ne pourra pas être effectué
        self.xn = ceil((self.xmax-self.xmin)/self.xpas)+1
        self.xn_lbl.setText(str(self.xn))
        if self.xn<27:
            self.min_points_warning.setText('Les mesures de moins de 27 échantillons\nne peuvent pas être filtrées.')
            self.xn_lbl.setStyleSheet('color: red')
            self.min_points_warning.setStyleSheet('color: red')
        else:
            self.min_points_warning.setText('')
            self.xn_lbl.setStyleSheet('color: black')
            self.min_points_warning.setStyleSheet('color: black')
    
    def set_zmax(self):
        #Mise à jour de zmax, le maximum de zmin et zn
        self.zmax = self.z_max_edit.value()
        self.z_min_edit.setMaximum(self.zmax)
        self.zn = ceil((self.zmax-self.zmin)/self.zpas)+1
        self.zn_lbl.setText(str(self.zn))
        self.temps_refresh()

    def set_zmin(self):
        #Mise à jour de zmin, le minimum de zmax et zn
        self.zmin = self.z_min_edit.value()
        self.z_max_edit.setMinimum(self.zmin)
        self.zn = ceil((self.zmax-self.zmin)/self.zpas)+1
        self.zn_lbl.setText(str(self.zn))
        self.temps_refresh()
    
    def set_zpas(self):
        #Mise à jour de zpas et zn
        self.zpas = self.z_pas_edit.value()
        self.zn = ceil((self.zmax-self.zmin)/self.zpas)+1
        self.zn_lbl.setText(str(self.zn))
        self.temps_refresh()

    def set_sen(self,i):
        #Mise à jour de l'indice de la sensibilité
        self.SEN = i
        self.temps_refresh()

    def set_tc(self,i):
        #Mise à jour de l'indice du temps de coupure
        self.TC = i
        self.temps_refresh()

    def temps_refresh(self):
        #Affichage de l'estimation de temps de l'acquisition
        self.nb_echantillons.setText(str(self.zn*self.xn)+' échantillons')
        temps = 10+(1+((1 + 2*(self.TC%2))*10**(self.TC//2-2)))*self.zn*(self.xn+15*int(self.SEN==16))
        if temps//3600 > 0:
            if (temps%3600)//60 != 1:
                self.temps_acquisition.setText(str(int(temps//3600))+' h ' +str(int((temps%3600)//60))+' mins '+str(int((temps%3600)%60))+' s')
            else:
                self.temps_acquisition.setText(str(int(temps//3600))+' h 1 min '+str(int((temps%3600)%60))+' s')
        elif temps//60 == 0:
            self.temps_acquisition.setText(str(int(temps))+' s')
        elif temps//60 == 1:
            self.temps_acquisition.setText('1 min '+str(int(temps-60))+' s')
        else:
            self.temps_acquisition.setText(str(int(temps//60))+' mins '+str(int(temps%60))+' s')
    
    def acquire_btn(self):
        # Fonction qui gère l'action du bouton acquisition selon son état
        QtCore.QCoreApplication.processEvents()
        if self.acq_button.isChecked():             #On appuie sur lancer l'acquisition
            self.acq_button.setText('Arrêter')      #Le bouton sert maintenant à arreter l'acquisition jusqu'à la fin de celle-ci
            self.acquire_fct()                      #L'acquisition est lancée
        else:                                       #On appuie pendant l'acquisition pour l'arreter
            self.acq_button.setEnabled(False)       #Désactiver le bouton acquisition pendant l'arrêt (anti-spam)
            self.acq_button.setText('Arrêt en cours...')
            self.stop_acq = True                    #On arrête l'acquisition de façon non brutale (reinitialisation des moteurs puis sortie de la fonction acquisition)
        QtCore.QCoreApplication.processEvents()

    def acquire_fct(self):
        # Fonction d'acquisition
        QtCore.QCoreApplication.processEvents()     #Force la mise à jour de la fenêtre
        
        # Variables de stockage de l'acquisition
        self.M = numpy.zeros((self.zn,self.xn))
        self.Z = numpy.linspace(self.zmin,self.zmax,self.zn)
        self.X = numpy.linspace(self.xmin,self.xmax,self.xn)

        # Connexion
        self.DS = serial.Serial('COM3',9600,timeout=5,parity="E",bytesize=7,stopbits=1,write_timeout=5)

        self.moteurs = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.moteurs.connect((self.HOST, self.PORT))

        self.ID = CheckID(self.DS)
        print("ID de la détection synchrone: " + str(self.ID))
        TC_write(self.DS,self.TC)

        # Acquisition
        self.moteurs.send(b'1MO')                       #allumage du moteur 1
        time.sleep(1.5)
        QtCore.QCoreApplication.processEvents()
        
        if self.SEN<16:                                 #si la sensibilité n'est pas en Auto
            Sen_write(self.DS,self.SEN)                 #envoie de la sensibilité à la DS
            for i in range(len(self.Z)):
                if (not self.session_opened) or self.stop_acq:  #si on ferme la fenêtre ou on arrête l'acquisition
                    Extinction(self)                            #on reinitialise les moteurs
                    return                                      #on sort de la fonction acquisition
                zGoTo(self.moteurs,self.Z[i])           #allumage + déplacement + extinction du moteur 2
                self.bds.setFormat("Scan " + str(i+1) + "/" + str(self.zn) + " : 0%")
                self.bds.setValue(0)
                for j in range(len(self.X)):
                    if (not self.session_opened) or self.stop_acq:
                        Extinction(self)
                        return
                    xGoTo(self.moteurs,self.X[j])       #déplacement du moteur 1
                    mag = DS_read(self.DS,self.TC)      #lecture de l'amplitude du signal
                    self.M[i,j] = mag*(1 + 2*(self.SEN%2))*10**(self.SEN//2-7)/10000    #stockage de la valeur convertie en V (avec la sensibilité)
                    self.bdc.setValue((i*self.xn+j+1)/(self.xn*self.zn)*100)            #mise à jour de la barre de chargement
                    self.bdc.setFormat("Progression globale de l'acquisition : " + str(round((i*self.xn+j+1)/(self.xn*self.zn)*100,1)) + "%")
                    self.bds.setFormat("Scan " + str(i+1) + "/" + str(self.zn) + " : " + str(round((j+1)/self.xn*100)) + "%")
                    self.bds.setValue((j+1)/self.xn*100)
                    QtCore.QCoreApplication.processEvents()     #Force la mise à jour de la fenêtre
                    
        else:                                           #si la sensibilité est en Auto
            for i in range(len(self.Z)):
                if (not self.session_opened) or self.stop_acq:
                    Extinction(self)
                    return
                self.SEN = 15                                   #On prend la pire sensibilité
                Sen_write(self.DS,self.SEN)
                zGoTo(self.moteurs,self.Z[i])
                self.bds.setFormat("Scan " + str(i+1) + "/" + str(self.zn) + " : 0%")
                self.bds.setValue(0)
                for j in range(len(self.X)):
                    if (not self.session_opened) or self.stop_acq:
                        Extinction(self)
                        return
                    xGoTo(self.moteurs,self.X[j])
                    mag = DS_read(self.DS,self.TC)
                    print(mag)
                    
                    #Mode Auto
                    while mag<2500 and self.SEN>0 and (self.session_opened and not self.stop_acq):              #On vérifie si on peut mieux lire avec la sensibilité supérieure (mag<2500)
                        self.SEN -=1                                                                            #et qu'on n'est pas arrivés à la meilleure sensibilité
                        Sen_write(self.DS, self.SEN)
                        mag = DS_read(self.DS,self.TC)          #On lit la nouvelle valeur
                        print(mag)
                        QtCore.QCoreApplication.processEvents() #Force la mise à jour de la fenêtre
                    
                    self.M[i,j] = mag*(1 + 2*(self.SEN%2))*10**(self.SEN//2-7)/10000
                    self.bdc.setValue((i*self.xn+j+1)/(self.xn*self.zn)*100)
                    self.bdc.setFormat("Progression globale de l'acquisition : " + str(round((i*self.xn+j+1)/(self.xn*self.zn)*100,1)) + "%")
                    self.bds.setFormat("Scan " + str(i+1) + "/" + str(self.zn) + " : " + str(round((j+1)/self.xn*100)) + "%")
                    self.bds.setValue((j+1)/self.xn*100)
                    QtCore.QCoreApplication.processEvents() #Force la mise à jour de la fenêtre
            self.SEN = 16       #reinitialisation du mode auto
        
        # Déconnexion
        ## Reinitialisation des moteurs
        Extinction(self)

        # Création du fichier d'acquisition
        self.nom_fichier, ok = QtWidgets.QInputDialog.getText(self, 'Nom du fichier', "Entrez nom du fichier d'acquisition:", QtWidgets.QLineEdit.Normal, 'acquisition')
        if self.nom_fichier[-4:] != '.csv':
            self.nom_fichier += '.csv'
        if self.traitement:
            self.menu1_nomfichierlbl.setText(self.nom_fichier)
        self.nom_fichier = os.getcwd() + '\\Acquisitions\\' + self.nom_fichier
        if ok:
            creer_fichier(self.M,self.Z,self.X,self.nom_fichier,self.TC,self.SEN)
        print(self.M)
        
        self.bdc.setValue(0)                #reinitialisation de la barre de chargement
        self.bdc.setFormat("Progression globale de l'acquisition : 0%")
        self.bds.setValue(0)
        self.bds.setFormat("Scan 1/  : 0%")

    def treat_fct(self):
        # Reconfiguration de l'interface
        self.traitement = True
        self.scheme.deleteLater()                       #On enleve le schema pour laisser de la place au menu de traitement
        self.treat_window = QtWidgets.QHBoxLayout()
        self.treat_menu = QtWidgets.QVBoxLayout()
        self.treat_graph = pg.PlotWidget()              #Creation du graphique
        self.treat_graph.showGrid(x=True, y=True)
        self.treat_graph.setBackground('k')
        self.treat_graph.addLegend(offset=(-30,30))
        self.treat_window.addWidget(self.treat_graph,1)
        self.treat_window.addLayout(self.treat_menu,0)
        self.bdc_lay.insertLayout(0,self.treat_window)  #insertion du menu de traitement dans l'interface

        # Configuration du menu de traitement (les boutons sont désactivés en attendant les étapes précédentes)
        ## Menu1: Ouverture du fichier et sélection de la zone d'intérêt (ROI)
        self.menu1 = QtWidgets.QGroupBox('Ouvrir un fichier de mesures')
        self.menu1_params = QtWidgets.QGridLayout()
        
        self.menu1_nomfichierlbl = QtWidgets.QLabel("Choisir un fichier d'acquisition:")
        self.menu1_btnfichier = QtWidgets.QPushButton('Parcourir')
        self.menu1_btnfichier.clicked.connect(self.choix_fichier)
                
        self.menu1_temperature = QtWidgets.QDoubleSpinBox()
        self.menu1_temperature.setLocale(QtCore.QLocale('English'))
        self.menu1_temperature.setFixedWidth(50)
        self.menu1_temperature.setDecimals(1)
        self.menu1_temperature.setValue(22.0)
        self.menu1_temperature.setSingleStep(0.1)
        self.menu1_temperaturelbl = QtWidgets.QLabel("Température de l'objectif (en °C):")
        
        self.menu1_button = QtWidgets.QPushButton('Ouvrir')
        self.menu1_button.clicked.connect(self.lance_ouvre_fichier)
        
        self.menu1_ROI = QtWidgets.QPushButton('Sélection')
        self.menu1_ROI.clicked.connect(self.affiche_ROI)
        self.menu1_ROI.setEnabled(False)
        
        self.menu1_params.addWidget(self.menu1_nomfichierlbl,1,1)
        self.menu1_params.addWidget(self.menu1_btnfichier,1,2)
        self.menu1_params.addWidget(self.menu1_temperaturelbl,2,1)
        self.menu1_params.addWidget(self.menu1_temperature,2,2)
        self.menu1_params.addWidget(self.menu1_button,3,1)
        self.menu1_params.addWidget(self.menu1_ROI,3,2)
        self.menu1.setLayout(self.menu1_params)
        self.treat_menu.addWidget(self.menu1)
        
        ## Menu2: Configuration optique
        self.menu2 = QtWidgets.QGroupBox('Configuration')
        self.menu2_params = QtWidgets.QGridLayout()
        
        self.menu2_trou = QtWidgets.QDoubleSpinBox()
        self.menu2_trou.setLocale(QtCore.QLocale('English'))
        self.menu2_trou.setFixedWidth(50)
        self.menu2_trou.setDecimals(3)
        self.menu2_trou.setValue(0.04)
        self.menu2_trou.setSingleStep(0.001)
        self.menu2_trou.setMinimum(0.001)
        self.menu2_troulbl = QtWidgets.QLabel("Diamètre de l'image du trou source (en mm):")
        
        self.menu2_NO = QtWidgets.QDoubleSpinBox()
        self.menu2_NO.setLocale(QtCore.QLocale('English'))
        self.menu2_NO.setFixedWidth(50)
        self.menu2_NO.setDecimals(3)
        self.menu2_NO.setValue(1/12)
        self.menu2_NO.setSingleStep(0.001)
        self.menu2_NO.setMinimum(0.001)
        self.menu2_NOlbl = QtWidgets.QLabel("Ouverture numérique image:")
        
        self.menu2_button = QtWidgets.QPushButton('Valider')
        self.menu2_button.clicked.connect(self.lance_config)
        self.menu2_button.setEnabled(False)
        
        self.menu2_params.addWidget(self.menu2_troulbl,1,1)
        self.menu2_params.addWidget(self.menu2_trou,1,2)
        self.menu2_params.addWidget(self.menu2_NOlbl,2,1)
        self.menu2_params.addWidget(self.menu2_NO,2,2)
        self.menu2_params.addWidget(self.menu2_button,3,1,1,2)
        self.menu2.setLayout(self.menu2_params)
        self.treat_menu.addWidget(self.menu2)
        
        ## Menu3: Choix et application du filtre
        self.menu3 = QtWidgets.QGroupBox('Filtrage des mesures')
        self.menu3_params = QtWidgets.QGridLayout()
        
        self.menu3_freq = QtWidgets.QDoubleSpinBox()
        self.menu3_freq.setLocale(QtCore.QLocale('English'))
        self.menu3_freq.setFixedWidth(100)
        self.menu3_freq.setMaximum(1000)
        self.menu3_freq.setDecimals(4)
        self.menu3_freqlbl = QtWidgets.QLabel("Fréquence de coupure du filtre passe-bas (en mm-1):")
        
        self.menu3_affichefiltre = QtWidgets.QCheckBox('Afficher filtre de Butterworth')    #choix d'afficher ou non le filtre
    
        self.menu3_button = QtWidgets.QPushButton('Valider')
        self.menu3_button.clicked.connect(self.lance_filtrage)
        self.menu3_button.setEnabled(False)
        
        self.menu3_params.addWidget(self.menu3_freqlbl,1,1,1,2)
        self.menu3_params.addWidget(self.menu3_freq,2,1)
        self.menu3_params.addWidget(self.menu3_affichefiltre,2,2)
        self.menu3_params.addWidget(self.menu3_button,3,1,1,2)
        self.menu3.setLayout(self.menu3_params)
        self.treat_menu.addWidget(self.menu3)
        
        ## Menu4: Calcul de la dérivée
        self.menu4 = QtWidgets.QGroupBox('Calcul de la dérivée des profils')
        self.menu4_params = QtWidgets.QVBoxLayout()
        
        self.menu4_button = QtWidgets.QPushButton('Calculer')
        self.menu4_button.clicked.connect(self.lance_derivee)
        self.menu4_button.setEnabled(False)

        self.menu4_params.addWidget(self.menu4_button)
        self.menu4.setLayout(self.menu4_params)
        self.treat_menu.addWidget(self.menu4)

        ## Menu5: Calcul de la FTM
        self.menu5 = QtWidgets.QGroupBox('Calcul de la FTM')
        self.menu5_params = QtWidgets.QVBoxLayout()
        
        self.menu5_button = QtWidgets.QPushButton('Calculer')
        self.menu5_button.clicked.connect(self.lance_FTM)
        self.menu5_button.setEnabled(False)
        
        self.menu5_params.addWidget(self.menu5_button)
        self.menu5.setLayout(self.menu5_params)
        self.treat_menu.addWidget(self.menu5)
        
        ## Menu6: Calcul de l'effet de la focalisation
        self.menu6 = QtWidgets.QGroupBox('Effet de la défocalisation sur la FTM')
        self.menu6_params = QtWidgets.QVBoxLayout()
        
        self.menu6_button = QtWidgets.QPushButton('Afficher')
        self.menu6_button.clicked.connect(self.lance_defocalisation)
        self.menu6_button.setEnabled(False)
        
        self.menu6_params.addWidget(self.menu6_button)
        self.menu6.setLayout(self.menu6_params)
        self.treat_menu.addWidget(self.menu6)

        self.treat_menu.addStretch()

        self.noms = QtWidgets.QVBoxLayout()

        self.noms_Jesus = QtWidgets.QLabel("Fait par\nJesús FERRANDIS TORRÓN\nVincent NOËL\nPromo 2023")
        self.noms_Jesus.setAlignment(QtCore.Qt.AlignRight)

        self.noms.addWidget(self.noms_Jesus)
        self.treat_menu.addLayout(self.noms,1)

    def choix_fichier(self):
        # Gestion de la fenêtre de choix du fichier
        dlg = QtWidgets.QFileDialog()
        dlg.setFileMode(QtWidgets.QFileDialog.AnyFile)
        dlg.setNameFilter('CSV files (*.csv)')
        dlg.setDirectory(os.getcwd()+'\\Acquisitions')
        filenames = []
        if dlg.exec():
            self.nom_fichier = dlg.selectedFiles()[0]
            i = len(self.nom_fichier)-1
            nom = ''
            while self.nom_fichier[i] != '/' and i >= 0:
                nom += self.nom_fichier[i]
                i -= 1
            nom = nom[::-1]
            if len(nom) > 37:
                nom = nom[:34] + '...'
            self.menu1_nomfichierlbl.setText(nom)

    def lance_ouvre_fichier(self):
        # Reinitialisation des boutons de traitement
        self.menu2_button.setEnabled(False)
        self.menu3_button.setText('Valider')
        self.menu3_button.setEnabled(False)
        self.menu4_button.setEnabled(False)
        self.menu5_button.setEnabled(False)
        self.menu6_button.setEnabled(False)
        
        if self.nom_fichier[-4:] != '.csv':                                  #On rajoute l'extension si elle n'a pas été écrite
            self.nom_fichier += '.csv'
        try:
            df = pandas.read_csv(self.nom_fichier, sep=';')                  #On essaye d'ouvrir le fichier et on affiche un message d'erreur si on ne réussit pas
        except:
            msg = QtWidgets.QMessageBox()
            msg.setIcon(QtWidgets.QMessageBox.Warning)
            msg.setText("Impossible d'ouvrir le fichier précisé.")
            msg.setInformativeText("Vérifiez le nom du fichier.")
            msg.setWindowTitle("Erreur")
            msg.exec()
            
        TableauStr = df.values
        Tableau = []
        for i in TableauStr:                                            #On crée un tableau de valeurs à paritr du fichier
            ligne = []
            for j in i:
                ligne.append(float(j))
            Tableau.append(ligne)
        Tableau = np.array(Tableau)

        # On stocke les données du tableau dans des variables adaptées au traitement
        self.Position_M1 = Tableau[1:,0]
        self.Position_M2 = np.transpose(Tableau[0,1:])
        self.Valeurs_scan = Tableau[1:,1:]

        self.temperature = self.menu1_temperature.value() #On lit la valeur de la température
        str_temperature = str(self.temperature)
        self.text_temperature = str_temperature + ' °C'
        
        # affichage de l'acquisition
        self.figure()
        for i in range(self.Valeurs_scan.shape[1]):
            self.plot(self.Position_M1, self.Valeurs_scan[:,i], round(self.Position_M2[i],2), i)
        self.treat_graph.setTitle('Données brutes (pour les positions longitudinales en mm), Tobj = ' + self.text_temperature)
        self.treat_graph.setLabel('left', 'Tension en mV (proportionnelle au flux total)')
        self.treat_graph.setLabel('bottom', 'Positions du couteau en mm')
        self.treat_graph.autoRange()
        
        
        # Création de la zone d'intérêt
        self.menu1_ROI.setEnabled(True)
        self.ROI = pg.LinearRegionItem()
        self.treat_graph.addItem(self.ROI)
        centre = len(self.Position_M1)//2
        try:
            self.ROI.setRegion((self.Position_M1[centre-15],self.Position_M1[centre+15]))
        except: pass

        msg = QtWidgets.QMessageBox()
        msg.setIcon(QtWidgets.QMessageBox.Information)
        msg.setText("Veuillez sélectionner la zone d'intérêt du graphique puis cliquer sur 'Sélection'.")
        msg.setWindowTitle("Sélectionner ROI")
        msg.exec()

    def affiche_ROI(self):
        # Tronque les mesures à la région d'intérêt
        [d1,d2] = self.ROI.getRegion()
        indices = []
        for i in range(len(self.Position_M1)):
            if (self.Position_M1[i]>=d1) and (self.Position_M1[i]<=d2):
                indices.append(i)
        self.Valeurs_scan = self.Valeurs_scan[indices[0]:indices[-1],:]
        self.Mesures = self.Valeurs_scan
        self.Position_M1 = self.Position_M1[indices[0]:indices[-1]]

        # Affichage des mesures tronquées
        self.figure()
        for i in range(self.Valeurs_scan.shape[1]):
            self.plot(self.Position_M1, self.Valeurs_scan[:,i], str(round(self.Position_M2[i],2)), i)
        self.treat_graph.setTitle('Données brutes (zone selectionée), Tobj = ' + self.text_temperature)
        self.treat_graph.setLabel('left', 'Tension en mV (proportionnelle au flux total)')
        self.treat_graph.setLabel('bottom', 'Positions du couteau en mm')
        self.treat_graph.autoRange()

        # Calcul de la fréquence d'échantillonnage
        Pas_echantillonnage = self.Position_M1[1]-self.Position_M1[0]
        self.Fech = 1 / Pas_echantillonnage #en mm-1
        self.menu3_freq.setValue(self.Fech*0.2)
        self.menu2_button.setEnabled(True)
        self.menu1_ROI.setEnabled(False)

    def lance_config(self):
        # Configuration optique a partir des valeurs entrées
        try:
            if self.Diametre_image_trou != self.menu2_trou.value() or self.ouv_num != self.menu2_NO.value():
                self.Diametre_image_trou = self.menu2_trou.value()
                self.ouv_num = self.menu2_NO.value()        
                self.menu6_button.setEnabled(False)
        except:
            self.Diametre_image_trou = self.menu2_trou.value()
            self.ouv_num = self.menu2_NO.value()
        if self.Mesures.shape[0]<27:
            self.profil_filtre = np.transpose(self.Mesures)
            self.menu4_button.setEnabled(True)
            self.menu3_button.setText("Echantillons insuffisants")
        else:
            self.menu3_button.setEnabled(True)

    def lance_filtrage(self):
        # filtrage des profils
        # Fech = 100mm-1
        try:
            if self.Freq_coupure != self.menu3_freq.value():
                self.Freq_coupure = self.menu3_freq.value()
                self.menu5_button.setEnabled(False)
                self.menu6_button.setEnabled(False)
        except:
            self.Freq_coupure = self.menu3_freq.value()
            
        buttervalue = self.Freq_coupure/self.Fech*2

        #Calcul du filtre (Fc = buttervalue * Fe/2) et application

        [b,a]=scipy.signal.butter(8,buttervalue)
        [w,H]=scipy.signal.freqz(b,a,512)

        self.profil_filtre = scipy.signal.filtfilt(b,a,np.transpose(self.Mesures))
        
##        self.Position_M1 = np.real(w*self.Fech/(2*pi))
##        self.profil_filtre = np.array([abs(H)])

        # Affichage des mesures filtrées
        self.figure()
        for i in range(self.profil_filtre.shape[0]):
            self.plot(self.Position_M1, self.profil_filtre[i], str(round(self.Position_M2[i],2)), i+1)
        self.treat_graph.setTitle('Données filtrées')
        self.treat_graph.setLabel('left', 'Tension en mV (proportionnelle au flux total)')
        self.treat_graph.setLabel('bottom', 'Scan transversal en mm')
        self.treat_graph.autoRange()
        
        self.menu4_button.setEnabled(True)
        
        # Si la case est cochée on affiche le filtre
        if self.menu3_affichefiltre.isChecked():
            plt.figure()
            plt.plot(np.real(w*self.Fech/(2*pi)),abs(H))
            plt.grid(True)
            plt.title('Filtre Butterworth, 8° ordre')
            plt.xlabel('Fréquence de coupure = ' + str(self.Freq_coupure) + ' mm-1')
            plt.show()

    def lance_derivee(self):
        # Calcul des dérivées
        self.Mesures_derivees = -np.diff(self.profil_filtre)
        self.Position_M1_derivees = self.Position_M1[:-1]
        Han = np.hanning(self.Mesures_derivees.shape[1])
        self.fenetree = self.Mesures_derivees# * Han
        for i in self.fenetree:
            i += abs(min(i))
        # Affichage des dérivées
        self.figure()
        for i in range(self.fenetree.shape[0]):
            self.plot(self.Position_M1_derivees, self.fenetree[i], str(round(self.Position_M2[i],2)), i)
        self.treat_graph.setTitle('Dérivée des scans')
        self.treat_graph.setLabel('left', 'Dérivée des signaux')
        self.treat_graph.setLabel('bottom', 'Positions du couteau en mm')
        self.treat_graph.autoRange()

        self.menu5_button.setEnabled(True)

    def lance_FTM(self):
        
        # Calcul des FTMs
        #Calcul de Bessel1 pour la convolution
        #Diam_image = 36.5e-3 #en mm
        u_image = np.array(range(1,1025))
        u_image = u_image * pi * self.Diametre_image_trou * self.Fech / 1024
        TF_im_geo = 2 * sp.special.jv(1,u_image) / u_image
        
        #On evite de deconvoluer quand la fct de bessel est trop faible
        for i in range(len(TF_im_geo)):
            if TF_im_geo[i]<0.3:
                TF_im_geo[i]=1
        
        [theo,w] = self.FTM_Theo_polychromatique(self.ouv_num)

        #calcul de la ftml padding a 1024 points
        echelle_freq = np.fft.fftfreq(1024, 1/self.Fech)

        #nbrevisu le nombre de points a afficher pour la ftm
        #de 0 a la Fc ideale
        nbrevisu = 512

##        for i in range(self.fenetree.shape[0]):
##            ftm = np.fft.fft(self.fenetree[i,:],1024)
##            ftm = ftm[:nbrevisu]
##            #deconvolution (à refaire soigneusement avec la fct scipy.signal.deconvolve())
##            ftmd = -np.diff(ftm)
##            j = np.argmax(ftmd[:256])
##            fit = np.polyfit(range(j,nbrevisu),ftm[j:],10)
##            ftm = np.polyval(fit,range(nbrevisu))
##            ftm = ftm / np.transpose(TF_im_geo)[:nbrevisu]            
##            ftm = np.sqrt(ftm * np.conj(ftm))
##            ftm = ftm / max(ftm)
##            self.tableau_ftm.append(ftm)

##        if deriv.shape[1] < 2*nbrevisu:
##            temp = np.zeros((deriv.shape[0],2*nbrevisu-deriv.shape[1]))
##            deriv = np.append(deriv,temp,axis = 1)
##        self.tableau_ftm = np.abs(np.fft.fft(scipy.signal.wiener(deriv)))
        
        self.tableau_ftm = []
        
        for i in range(self.fenetree.shape[0]):
            four = np.fft.fft(self.fenetree[i,:],1024)
            ftm1 = np.sqrt(four * np.conj(four))
            ftm1 = ftm1[:nbrevisu]
            #deconvolution (à refaire soigneusement avec la fct scipy.signal.deconvolve())
            ftm = ftm1 / np.transpose(TF_im_geo)[:nbrevisu]
            ftm = ftm / max(ftm)
            self.tableau_ftm.append(ftm)

        self.tableau_ftm = np.array(self.tableau_ftm).transpose()
        
        # Affichage
        self.figure()
        self.plot(w,theo,'FTM Limite diffraction',0, False)
        for i in range(self.tableau_ftm.shape[1]):
            self.plot(echelle_freq[:nbrevisu], np.real(self.tableau_ftm[:,i]), str(round(self.Position_M2[i],2)), 1+i%(self.nb_couleurs-1), False)
        self.treat_graph.setTitle('FTM pour les positions de M2, Tobj = ' + self.text_temperature)
        self.treat_graph.setLabel('left', 'FTM mesurées et FTM polychromatique limitée par la diffraction')
        self.treat_graph.setLabel('bottom', 'Fréquence spatiale en mm-1')
        self.treat_graph.setXRange(0,w[-1])
        self.treat_graph.enableAutoRange(axis='y')
        self.treat_graph.setAutoVisible(y=True)

        self.menu6_button.setEnabled(True)

    def lance_defocalisation(self):
        #Calcul l'abscisse des FTM a 0.2, 0.4, 0.6 et 0.8 en fonction de la position longitudinale du scan
        nbre_positions_M2 = self.tableau_ftm.shape[1]

        critere = [0.2,0.4,0.6,0.8]
        tableau_freq_spat_max = np.zeros((nbre_positions_M2,4))
        for i in range(4):
            freq_spat_max = []
            for j in range(nbre_positions_M2):
                kmax = 0
                for k in range(len(self.tableau_ftm[:,j])):
                    if self.tableau_ftm[:,j][k]>=critere[i]: kmax = k
                freq_spat_max.append(kmax*self.Fech/1024)
            tableau_freq_spat_max[:,i] = np.transpose(freq_spat_max)

        # Affichage
        self.figure()
        for i in range(tableau_freq_spat_max.shape[1]):
            self.plot(self.Position_M2, tableau_freq_spat_max[:,i], str(critere[i]), i)
        self.treat_graph.setTitle('Fréquence spatiale maxi telle que FTM >= (0.2 , 0.4 , 0.6 ou 0.8), T = ' + self.text_temperature)
        self.treat_graph.setLabel('left', 'Fréquence spatiale en mm-1')
        self.treat_graph.setLabel('bottom', 'Position longitudinale du couteau en mm')
        self.treat_graph.autoRange()

    def FTM_Theo_polychromatique(self,ouv_num):
        #Calculée par la formule sur 1024 points
        #sommé sur les longueurs d'onde
        #renvoie la FTM theo sur la FTM de 0 a fc

        L = np.array([6,7,8,9,10,11,12]) * 1e-3
        poids = np.array([0,2,3.5,4.5,3.5,2.5,1.5]) #a verifier soigneusement un jour !!!
        #poids = np.array([1,0,0,0,0,0,0]) #Monochromatique

        wc = (2 * ouv_num) / L
        w = np.linspace(0,max(wc),1024)
        theo = np.zeros(1024)

        for i in range(len(wc)):
            for j in range(len(w)):
                if w[j] <= wc[i]:
                    t = j
            theo[:t] += (2/pi)*(np.arccos(w[:t]/wc[i])-(w[:t]/wc[i])*(1-(w[:t]/wc[i])**2)**0.5)*poids[i]
        theo /= sum(poids)
        
        return theo,w

    def figure(self):
        # efface le contenu du graphique
        self.treat_graph.clear()

    def plot(self, x, y, plotname, color, croix = True):
        # fonction d'affichage
        pen = pg.mkPen(color=self.couleurs[color%self.nb_couleurs])
        if croix:
            self.treat_graph.plot(x, y, name=plotname, pen=pen, symbol='x', symbolSize=10, symbolBrush=(self.couleurs[color%self.nb_couleurs]))
        else:
            self.treat_graph.plot(x, y, name=plotname, pen=pen)
    
    def closeEvent(self, event):
        # arrête l'éxecution quand la fenêtre est fermée
        self.session_opened = False
        self.close()

def main():

    app = QtWidgets.QApplication.instance()
    if app == None:
        app = QtWidgets.QApplication([])
    
    app.quitOnLastWindowClosed()

    # Icon to show in task bar for Windows
    if platform.system() == 'Windows':
        myappid = 'FTMIR'
        try:
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
        except:
            pass
    
    window = MWindow(app)
    
    with open("style.qss","r") as f:
        _style = f.read()
        window.setStyleSheet(_style)

    window.showMaximized()
    prev_time = 0
    
    i = 0
    # Start the update loop:
    while window.session_opened:
        i = i+1
        window.update()
        time_ = time.time()
        window.frame_rate = 0.95 * window.frame_rate + 0.05/(0.001+time_-prev_time)
        QtWidgets.QApplication.processEvents()
        prev_time = time_

if __name__ == '__main__':
    print("Qt version:", QtCore.__version__)
    main()
