% Selectionne a l''aide de 3 points un cercle sur une image
% renvoie une matrice valant 1 a l''interieur du cercle et 0 a l''exterieur
% pouvant ensuite servir de masque sur ladite image
% 1. acquisition et affichage de l''image
% 2. selection manuelle de 3 points sur le cercle
% 3. calcul du rayon et du centre du cercle a partir des coordonnees des 3 points
% 4. definition de la matrice masque

function [Img,mask]=mask_cercle(Img);

[sizex,sizey]=size(Img) ;

h = figure('Name','Sélection du masque') ;

imagesc(Img) ;axis image;colormap gray

% selection des 3 points sur le cercle
% et recuperation des coordonnees
hold on
ABC=ones(3,2);
	for gpoint=1:3	
		ABC(gpoint,:)=ginput(1);
		plot(ABC(gpoint,1),ABC(gpoint,2),'r+') 
	end

%ABC coordonnées des 3 points
%calcule du vecteur (xA^2+yA^2;xb^2+yb^2;xc^2+yc^2)
ABC2=ABC(:,1).^2+ABC(:,2).^2;

%on calcule les 4 determinants de la matrice 4*4
% ce qui permettra d''en deduire centre et rayon du cercle

det1=det([ABC ones(3,1)]);
if det1==0,disp('3 Points alignés!!'),return,end

det2=det([ABC2 ABC(:,2) ones(3,1)]);
det3=det([ABC2 ABC(:,1) ones(3,1)]);
det4=det([ABC2 ABC(:,1) ABC(:,2)]);
%eq cercle: (x^2+y^2) + ax + by + c = 0
%calcule de a,b,c
a=-det2/det1;
b=det3/det1;
c=-det4/det1;

centre=[-a/2 -b/2];
rayon=sqrt(-c+0.25*a^2+0.25*b^2);


% definition du masque
% vaut 1 a l''interieur du cercle, et 0 a l''exterieur
mask=zeros(sizex,sizey) ;
alpha_mask=0.3*ones(sizex,sizey) ;
for i=1:sizex
    for j=1:sizey
        if (sqrt((i+b/2)^2+(j+a/2)^2)<=rayon)
            mask(i,j)=1 ;
            alpha_mask(i,j)=1 ;
        end
    end
end

Img=double(Img);
Img=Img.*alpha_mask+ones(sizex,sizey)-alpha_mask ;
%imagesc(Img) ;
close(h) ;