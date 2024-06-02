%impression des resultats 


hf=figure('position', [0 0 900 900])
ha=axes('Parent',hf,'Position',[ 0.1 0.75 0.25 0.25])


%  bonne propri�t� 'Position', un vecteur de 4 nombres [bgx bgy Lx Ly] o� bg signifie bas_gauche et L largeur ou longueur
%  de l'axe en question dans la figure. Par d�faut, ces nombres s'expriment en unit� normalis�e par rapport � la figure
%  (0,0) �tant le bas gauche et (1,1) le haut droit de la figure. La position de l'axe correspond pr�cis�ment au rectangle de trac� des donn�es; 
%  les xlabel, ylabel et title sont en dehors de cette zone. 
%  Le plus simple est peut-�tre d'utiliser hk=subplot(n,m,k) puis de modifier la propri�t� 'Position' de l'axe hk pour l'ajuster � ce que l'on veut...
% Sinon, il faut utiliser la commande bas niveau  de cr�ation d'axes, ha=axes('Parent',hf,'Position',[bgx bgy Lx Ly])...
% 
% Pour imprimer, effectivement le plus simple est probablement de cr�er une nouvelle figure dans laquelle on place les graphiques et textes � imprimer,
% puis de lancer une commande �print -dwinc -v -fh�; -v permet l'ouverture de la bo�te de dialogue d'impression de Windows, 
% -fh o� h est la cha�ne de caract�res repr�sentant le n� de la figure � imprimer, i.e. le handle de la figure en question num2str(hf) 
% permet �ventuellement de pr�ciser la figure en question...  
%     Pour le texte, il est �ventuellement plus simple de le placer dans un subplot avec des commandes text 
% plut�t que d'utiliser un uicontrol de style text dans la figure... (On a plus de contr�le sur la police de caract�res et sa couleur, 
% on peut mettre des caract�res grecs, des indices, ...).   
%     Il peut aussi �tre utile d'avoir pr�alablement positionn� les propri�t�s 'PaperOrientation', 'PaperPosition', 'PaperUnit' de la figure 
