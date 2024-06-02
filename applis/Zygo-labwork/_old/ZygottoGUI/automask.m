function [Img,mask]=automask

wbar = waitbar(0,'Calcul du masque automatique en cours...') ;
set(wbar,'CloseRequestFcn','return')
pause(0.01) ;


daqoutfloat(0) ;
[Img1,status,ErrLoc]=VideoSNAP ;

waitbar(0.2,wbar) ;


daqoutfloat(1.1) ;
[Img2,status,ErrLoc]=VideoSNAP ;

waitbar(0.4,wbar) ;


daqoutfloat(1.8) ;
[Img3,status,ErrLoc]=VideoSNAP ;

waitbar(0.6,wbar) ;


daqoutfloat(2.5) ;
[Img4,status,ErrLoc]=VideoSNAP ;

waitbar(0.8,wbar) ;


daqoutfloat(0) ;


Imgd1 = double(Img1) ;
Imgd2 = double(Img2) ;
Imgd3 = double(Img3) ;
Imgd4 = double(Img4) ;


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
for i=1:a
    for j=1:b
        if (Imgddiff1(i,j)<8 && Imgddiff2(i,j)<8)
            mask(i,j)=0 ;
        end
    end
end

[sizex,sizey]=size(Img1) ;
alpha_mask = 0.3*ones(sizex,sizey) ;

for i=1:sizex
    for j=1:sizey
        if mask(i,j)==1 ;
            alpha_mask(i,j)=1 ;
        end
    end
end

Img=double(Img1);
Img=Img.*alpha_mask+ones(sizex,sizey)-alpha_mask ;


waitbar(1,wbar) ;


set(wbar,'CloseRequestFcn','delete(gcf)')
close(wbar) ;
