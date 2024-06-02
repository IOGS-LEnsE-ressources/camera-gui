%impression des resultats 


hf=figure('position', [0 0 900 900])
ha=axes('Parent',hf,'Position',[ 0.1 0.75 0.25 0.25])


%  bonne propriété 'Position', un vecteur de 4 nombres [bgx bgy Lx Ly] où bg signifie bas_gauche et L largeur ou longueur
%  de l'axe en question dans la figure. Par défaut, ces nombres s'expriment en unité normalisée par rapport à la figure
%  (0,0) étant le bas gauche et (1,1) le haut droit de la figure. La position de l'axe correspond précisément au rectangle de tracé des données; 
%  les xlabel, ylabel et title sont en dehors de cette zone. 
%  Le plus simple est peut-être d'utiliser hk=subplot(n,m,k) puis de modifier la propriété 'Position' de l'axe hk pour l'ajuster à ce que l'on veut...
% Sinon, il faut utiliser la commande bas niveau  de création d'axes, ha=axes('Parent',hf,'Position',[bgx bgy Lx Ly])...
% 
% Pour imprimer, effectivement le plus simple est probablement de créer une nouvelle figure dans laquelle on place les graphiques et textes à imprimer,
% puis de lancer une commande «print -dwinc -v -fh»; -v permet l'ouverture de la boîte de dialogue d'impression de Windows, 
% -fh où h est la chaîne de caractères représentant le n° de la figure à imprimer, i.e. le handle de la figure en question num2str(hf) 
% permet éventuellement de préciser la figure en question...  
%     Pour le texte, il est éventuellement plus simple de le placer dans un subplot avec des commandes text 
% plutôt que d'utiliser un uicontrol de style text dans la figure... (On a plus de contrôle sur la police de caractères et sa couleur, 
% on peut mettre des caractères grecs, des indices, ...).   
%     Il peut aussi être utile d'avoir préalablement positionné les propriétés 'PaperOrientation', 'PaperPosition', 'PaperUnit' de la figure 
