function [Imgd1,phi]=phase_shift(Img1,Img2,Img3,Img4,Img5,mask,wedge)

% calcul de la phase obtenue par algorithme de phase-shift a 5 images
% definit automatiquement la zone utile de l''image
% 1. acquisition des images (decalage de pi/2 par translation de la piezo entre deux images)
% 2. definition de la zone utile
% 3. calcul de la phase par l''algorithme de Hariharan
% 4. deroulement de la phase grace a la fonction unwrap2D
% 5. affichage de la phase

try
    close ('probleme avec le phase_shift')
catch
end

% conversion des images en double
Imgd1 = double(Img1) ;
Imgd2 = double(Img2) ;
Imgd3 = double(Img3) ;
Imgd4 = double(Img4) ;
Imgd5 = double(Img5) ;


[mask,xmin,xmax,ymin,ymax]=selection_surface_utile(mask) ;

Imgd1=Imgd1(xmin:xmax,ymin:ymax) ;
Imgd2=Imgd2(xmin:xmax,ymin:ymax) ;
Imgd3=Imgd3(xmin:xmax,ymin:ymax) ;
Imgd4=Imgd4(xmin:xmax,ymin:ymax) ;
Imgd5=Imgd5(xmin:xmax,ymin:ymax) ;

[a,b] = size(Imgd1) ;
Imgd1(mask==0) = NaN ;
Imgd2(mask==0) = NaN ;
Imgd3(mask==0) = NaN ;
Imgd4(mask==0) = NaN ;
Imgd5(mask==0) = NaN ;


% application de la correction gamma aux images obtenues
gamma=read_config('gamma',1);
Imgd1=Imgd1.^gamma;
Imgd2=Imgd2.^gamma;
Imgd3=Imgd3.^gamma;
Imgd4=Imgd4.^gamma;
Imgd5=Imgd5.^gamma;



%filtrage des images
filtre_conv = fspecial('gaussian',5,3);
Imgd1 = filter2(filtre_conv,Imgd1);
Imgd2 = filter2(filtre_conv,Imgd2);
Imgd3 = filter2(filtre_conv,Imgd3);
Imgd4 = filter2(filtre_conv,Imgd4);
Imgd5 = filter2(filtre_conv,Imgd5);
%calcul de la phase
phi = atan2((2*Imgd3-Imgd5-Imgd1),2*(Imgd2-Imgd4)) ;


% %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
alpha = ((Imgd5-Imgd1)./(2*(Imgd4-Imgd2))) ;
alpha = reshape(alpha(~isnan(alpha)),1,[]) ;
alpha = mod(real(acos(alpha)*180/pi),180) ;
alpha=alpha(~isnan(alpha));

 %h_histo=figure('name', 'histogramme des dephasage');
 %hist(alpha,linspace(45,135,91))
 
 alpha=alpha(alpha<135 & alpha>45);
 moyenne_phase_shift=mean(alpha)
 rms_phase_shift=std(alpha)
 grid

  if  ((moyenne_phase_shift<86)||(moyenne_phase_shift>94)||(rms_phase_shift>8))
     h = warndlg('Il vaut mieux refaire la mesure ou attendre que le laser soit stabilisé','probleme avec le phase_shift');
 end
% phase deroulee et lissee
%waitbar(0.8,wbar,'Deroulement de la phase') ;
phi = unwrap2D(phi) ;

phi=-phi*wedge;

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% filtre_conv = fspecial('gaussian',5,3);
% phi = filter2(filtre_conv,phi);

% Suppression du bord
%waitbar(0.95,wbar,'Suppression du bord de pupille') ;

phi = suppression_bord(phi,3) ;


%supression du piston
phi=phi-mean(mean(phi(~isnan(phi))));

%ff=figure,contour(phi,20),axis image, waitforbuttonpress,close(ff)
%rechantillonnage de la phase sur 200 par 200 points

if (size(phi,1) >400 && size(phi,2) > 400 )
    [xi,yi] = meshgrid(linspace(1,size(phi,2),size(phi,2)/4),linspace(1,size(phi,1),size(phi,1)/4));
elseif  (size(phi,1) > 200 && size(phi,2) > 200 )
    [xi,yi] = meshgrid(linspace(1,size(phi,2),size(phi,2)/2),linspace(1,size(phi,1),size(phi,1)/2));
else
    [xi,yi] = meshgrid(linspace(1,size(phi,2),size(phi,2)),linspace(1,size(phi,1),size(phi,1)));
end

%[xi,yi] = meshgrid(linspace(1,size(phi,2),min(size(phi,2),100)),linspace(1,size(phi,1),min(size(phi,1),100)));
phi = interp2(phi,xi,yi);

%ff=figure,contour(phi,20),axis image, waitforbuttonpress,close(ff)