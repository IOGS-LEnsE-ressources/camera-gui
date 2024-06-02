function [Img,mask] = mask_polygon(Img)

h = figure('Name','Sélection du masque') ;

imagesc(Img) ;axis image ,colormap gray

%pause(0.01) ;

mask=roipoly ;

close(h) ;

[sizex,sizey]=size(Img) ;
alpha_mask = 0.3*ones(sizex,sizey) ;

alpha_mask(mask==1) = 1 ; 

Img=double(Img);
Img=Img.*alpha_mask+ones(sizex,sizey)-alpha_mask ;