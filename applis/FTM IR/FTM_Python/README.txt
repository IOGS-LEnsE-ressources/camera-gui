########################### TP Mesure de la FTM d'un objectif en Ge dans l'IR par Foucaultage ####################################

Dans ce fichier vous trouverez un récapitulatif des fonctions et des liens entre l'interface et le programme.


""""""""" Liens """"""""""""

	''' Mouvement transversal '''
Champ xmax - fonction set_xmax
Champ xmin - fonction set_xmin
Champ xpas - fonction set_xpas

	''' Mouvement longitudinal '''
Champ zmax - fonction set_zmax
Champ zmin - fonction set_zmin
Champ zpas - fonction set_zpas

	''' Détection synchrone '''
Champ Sensibilité 	- fonction set_sen
Champ Temps de Coupure 	- fonction set_tc

	''' Boutons accueil '''
Bouton Acquisition 	- fonction acquire_btn -> fonction acquire_fct
       Arrêter		- fonction acquire_btn -> stop_acq = True (-> fonction Extinction)
Bouton Traitement 	- fonction treat_fct

	''' Ouvrir un fichier de mesures '''
Bouton Parcourir	- fonction choix_fichier
Champ température	- variable window.temperature
Bouton Ouvrir		- fonction lance_ouvre_fichier
Bouton Sélection	- fonction affiche_ROI

	''' Configuration '''
Champ diamètre de l'image du trou	- variable window.Diametre_image_trou
Champ Nombre d'ouverture		- variable window.Nombre_ouverture_image

	''' Filtrage des mesures '''
Champ fréquence de coupure	- variable Freq_coupure (dans lance_filtrage)
Case Afficher filtre	 	- Affichage dans fonction lance_filtrage
Bouton Valider			- fonction lance_filtrage

	''' Calcul de la dérivée des profils '''
Bouton Calculer	- fonction lance_derivee

	''' Calcul de la FTM '''
Bouton Calculer		- fonction lance_FTM
fonction lance_FTM	- FTM_Theo_polychromatique

	''' Effet de la défocalisation sur la FTM '''
Bouton Afficher	- fonction lance_defocalisation


"""""""" Fonctions """"""""

	--- Com ---

''' Fonctions DS '''
n = b2int(b):
#Convertit les bytetypes en entiers
	Entrées: - b: bytetype (exemple: b'1256\n')
	Sorties: - n: b converti en entier (exemple: 1256)

ID = CheckID(ser):
    #Demande son ID à la Détection Synchrone
	Entrées: - ser: connexion série avec la DS
	Sorties: - ID: ID de la DS

SEN = Sen_read(ser):
    #Demande sa sensibilité à la DS
	Entrées: - ser: connexion série avec la DS
	Sorties: - SEN: indice de la sensibilité de la DS
Sen_write(ser,SEN):
    #Change la sensibilité de la DS
	Entrées: - ser: connexion série avec la DS
		 - SEN: indice de sensibilité souhaitée
	Sorties:

TC = TC_read(ser):
    #Demande son temps de coupure à la DS
	Entrées: - ser: connexion série avec la DS
	Sorties: - TC: indice du temps de coupure de la DS

TC_write(ser,TC):
    #Change le temps de coupure de la DS
	Entrées: - ser: connexion série avec la DS
		 - TC: indice du temps de coupure souhaité
	Sorties:

mag = DS_read(ser,TC):
    #Lit la valeur de l'amplitude
	Entrées: - ser: connexion série avec la DS
		 - TC: indice du temps de coupure de la DS
	Sorties: - mag: valeur de l'amplitude du signal (dépend de la sensibilité)

''' Fonctions Moteurs '''
zGoTo(client,z):
    #Déplace le moteur longitudinal
	Entrées: - client: connexion TCP/IP avec l'alimentation des moteurs
		 - z: position du moteur longitudinal souhaitée
	Sorties:

xGoTo(client,x):
    #Déplace le moteur transversal
	Entrées: - client: connexion TCP/IP avec l'alimentation des moteurs
		 - x: position du moteur transversal souhaitée
	Sorties:

''' Fonctions Fichier '''
creer_fichier(M,Z,X,nom,TC,SEN):
    #Créer le fichier de mesure (.csv)
	Entrées: - M: matrice des mesures
		 - Z: liste des positions du moteur longitudinal
		 - X: liste des positions du moteur transversal
		 - nom: nom du fichier avec l'extension ".csv"
		 - TC: indice du temps de coupure de la DS
		 - SEN: indice de la sensibilité de la DS
	Sorties: 


	--- InterfaceFTMIR ---

set_xmax(MWindow):
     #Met a jour xmax, le maximum de xmin et xn
	Entrées: - MWindow: fenêtre principale et tous ses paramètres
	Sorties:

set_xmin(MWindow):
     #Met a jour xmin, le minimum de xmax et xn
	Entrées: - MWindow: fenêtre principale et tous ses paramètres
	Sorties:

set_xpas(MWindow):
     #Met a jour xpas et xn
	Entrées: - MWindow: fenêtre principale et tous ses paramètres
	Sorties:

xn_refresh(MWindow):
      #Met à jour l'affichage des échantillons par scan
      #Affiche un message s'il n'y a pas assez d'échantillons pour filtrer
	Entrées: - MWindow: fenêtre principale et tous ses paramètres
	Sorties:

set_zmax(MWindow):
      #Met à jour zmax, le maximum de zmin et zn
	Entrées: - MWindow: fenêtre principale et tous ses paramètres
	Sorties:

set_zmin(MWindow):
      #Met à jour zmin, le minimum de zmax et zn
	Entrées: - MWindow: fenêtre principale et tous ses paramètres
	Sorties:
    
set_zpas(MWindow):
      #Met à jour zpas et zn
	Entrées: - MWindow: fenêtre principale et tous ses paramètres
	Sorties:

set_sen(MWindow,i):
      #Met à jour l'indice de la sensibilité
	Entrées: - MWindow: fençetre principale et tous ses paramètres
		 - i: indice de la sensibilité (entre 0 et 15)
	Sorties:
      
set_tc(MWindow,i):
      #Met à jour l'indice du temps de coupure
	Entrées: - MWindow: fenêtre principale et tous ses paramètres
		 - i: indice du temps de coupure (entre 0 et 13)
	Sorties:

temps_refresh(MWindow):
      #Met à jour l'affichage du temps estimé pour l'acquisition
	Entrées: - MWindow: fenêtre principale et tous ses paramètres
	Sorties:

acquire_btn(MWindow):
      #Gère l'action du bouton acquisition selon son état:
      # 	- "Acquisition": lance l'acquisition en faisant appel à acquire_fct 
      # 			 et change l'état à "Arrêter" jusqu'à la fin de l'acquisition
      # 	- "Arrêter" : arrête de facon non brutale l'acquisition en désactivant le bouton pendant l'arrêt
      # 		      et le remettant en état "Acquisition" à la fin
	Entrées: - MWindow: fenêtre principale et tous ses paramètres
	Sorties:

acquire_fct(MWindow):
      #Fait l'acquisition des mesures
	Entrées: - MWindow: fenêtre principale et tous ses paramètres
	Sorties:

treat_fct(MWindow):
      #Passe l'interface en mode traitement
	Entrées: - MWindow: fenêtre principale et tous ses paramètres
	Sorties:

choix_fichier(MWindow):
      #Ouvre la fenêtre de choix du fichier et ouvre le fichier choisi
	Entrées: - MWindow: fenêtre principale et tous ses paramètres
	Sorties:

lance_ouvre_fichier(MWindow):
      #Ouvre le fichier indiqué sur l'interface, met en forme les données et les affiche.
      #Initialise la région d'intérêt.
	Entrées: - MWindow: fenêtre principale et tous ses paramètres
	Sorties:

affiche_ROI(MWindow):
      #Tronque les données à la région d'intérêt et les affiche.
	Entrées: - MWindow: fenêtre principale et tous ses paramètres
	Sorties:

lance_config(MWindow):
      #Récupère les données entrées sur l'interface pour la configuration optique.
	Entrées: - MWindow: fenêtre principale et tous ses paramètres
	Sorties:

lance_filtrage(MWindow):
      #Filtre les données avec un filtre de Butterworth du 8ème ordre puis affiche les données filtrées.
      #Affiche le filtre dans une nouvelle fenêtre si le choix est marqué.
	Entrées: - MWindow: fenêtre principale et tous ses paramètres
	Sorties:

lance_derivee(MWindow):
      #Calcule les dérivées des données et les affiche.
	Entrées: - MWindow: fenêtre principale et tous ses paramètres
	Sorties:

lance_FTM(MWindow):
      #Calcule les FTM des mesures et les affiche avec la FTM théorique (en faisant appel a FTM_Theo_Polychromatique())
	Entrées: - MWindow: fenêtre principale et tous ses paramètres
	Sorties:

lance_defocalisation(MWindow):
      #Calcul l'abscisse des FTM a 0.2, 0.4, 0.6 et 0.8 en fonction de la position longitudinale du scan et les affiche.
	Entrées: - MWindow: fenêtre principale et tous ses paramètres
	Sorties:

[theo,w] = FTM_Theo_Polychromatique(MWindow,ouv_num):
      #Calcule la FTM théorique polychromatique et la renvoie.
	Entrées: - MWindow: fenêtre principale et tous ses paramètres
		 - ouv_num: ouverture numérique du système
	Sorties: - theo: liste contenant la FTM théorique
		 - w: liste des fréquences associées à theo

figure(MWindow):
      #Efface le contenu du graphique
	Entrées: - MWindow: fenêtre principale et tous ses paramètres
	Sorties:

plot(MWindow, x, y, plotname, color, croix = True):
      #Trace en couleur *color* y en fonction de x sur le graphique, legendé *plotname*,
      #avec des croix sur les points si *croix*==True
	Entrées: - MWindow: fenêtre principale et tous ses paramètres
		 - x: liste des abscisses
		 - y: liste des ordonnées
		 - plotname: nom de la courbe affiché dans la légende
		 - color: couleur de la courbe
		 - croix: booléen qui définit l'affichage des croix (True par défaut)
	Sorties:

closeEvent(MWindow, event):
      #Arrête l'execution du programme si la fenêtre est fermée.
	Entrées: - MWindow: fenêtre principale et tous ses paramètres
		 - event: évènement "la fenêtre est fermée"
	Sorties:

										- Codé par Vincent NOËL et Jesús FERRANDIS TORRÓN
