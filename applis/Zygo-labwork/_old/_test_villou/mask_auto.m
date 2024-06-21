function [Img,mask] = mask_auto(Img1,Img2,Img3,Img4,Img5)

seuil_mask= 13; %difference d'images successives <26 hors interferro 


Imgd1 = double(Img1) ;
Imgd2 = double(Img2) ;
Imgd3 = double(Img3) ;
Imgd4 = double(Img4) ;
Imgd5 = double(Img5) ;

% definition de la zone utile (zone d''interferences) sur les images
% on applique un seuil a la difference en valeur absolue entre img1 et les autres images resp.
% si la variation en un point est toujours inferieure au seuil, l''eclairement du point n''a pas varie entre les differentes images
% et n''est donc pas dans la zone d''interferences

%calcul des differences entre images
Imgddiff1 = abs(Imgd1 - Imgd3) ;
Imgddiff2 = abs(Imgd2 - Imgd4) ;


% mise a 0 des points du masque pour lesquels la difference est toujours inferieure au seuil
[a,b]=size(Imgd1) ;
mask=ones(a,b) ;


mask(Imgddiff1<16 & Imgddiff2<16) = 0 ;
% 
 PSF = fspecial('average',9);
 maskinv = imfilter(1-mask,PSF,'conv');

mask = (maskinv == 0) ;


%affichage du masque en transparence
alpha_mask=0.3 * ones(a,b) ;
alpha_mask(mask) = 1 ;

Img=double(Img1);
Img=Img.*alpha_mask+ones(a,b)-alpha_mask ;