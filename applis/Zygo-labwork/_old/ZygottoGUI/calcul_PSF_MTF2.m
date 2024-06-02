function calcul_PSF_MTF2(phi,N)

% A FAIRE : rentrer coeff_zernicke et WegdgeFactor en arguments

%lambda en mm
lambda = 632e-6 ;

Nbpts = 2048 ;


%Suppression du tilt
%coeff_zernicke = zern(phi) ;
%phi = affichage_surface(phi,coeff_zernicke,[1,1,1]) ; 

[a,b] = size(phi) ;
D = max(a,b) ;

mask = ~isnan(phi) ;

phi(isnan(phi))=0 ;


i=sqrt(-1) ;

%% Calcul de la PSF

Ampl_image_parfaite = fftshift(fft2(mask,Nbpts,Nbpts)) ;
Ampl_image = fftshift(fft2(mask.*exp(i*phi),Nbpts,Nbpts)) ;

clear phi mask Ampl_pupille ;

PSF_parfaite = Ampl_image_parfaite.*conj(Ampl_image_parfaite) ;
PSF_norm = Ampl_image.*conj(Ampl_image) ;

clear Ampl_image_parfaite Ampl_image ;

PSF_norm = PSF_norm/(max(max(PSF_parfaite))) ;
PSF_parfaite = PSF_parfaite/(max(max(PSF_parfaite))) ;

a = (Nbpts-D)/2+1 ;
b = (Nbpts+D)/2 ;

PSF_parfaite_reduite = PSF_parfaite(a:b,a:b) ;
PSF_norm_reduite = PSF_norm(a:b,a:b) ;


%% Profile sur la TF

borne_PSF = N*1E3*lambda*(D^2)/(2*Nbpts) ;
figure('Name','Sélectionner la direction d''analyse') ; imagesc(linspace(-borne_PSF,borne_PSF,D),linspace(-borne_PSF,borne_PSF,D),PSF_norm_reduite) ;
[cx,cy,profile_PSF,cxi,cyi] = improfile ;
index_profile1 = -sqrt(cxi(1)^2+cyi(1)^2) ;
index_profile2 = sqrt(cxi(2)^2+cyi(2)^2) ;
pente = (cyi(2) - cyi(1))/(cxi(2) - cxi(1)) ;
taille_profile = length(profile_PSF) ;
index_profile = linspace(index_profile1,index_profile2,taille_profile) ;

figure('Name','PSF') ; plot(index_profile, profile_PSF,'r') ;
legend('PSF (µm)') ;
title(strcat('Rapport de Strehl :',num2str(max(max(PSF_norm_reduite))/max(max(PSF_parfaite_reduite)),'%1.3f'))) ;


%% Calcul de la MTF

MTF_norm = abs(fftshift(fft2(PSF_norm,Nbpts,Nbpts))) ;
MTF_parfaite = abs(fftshift(fft2(PSF_parfaite,Nbpts,Nbpts))) ;

MTF_norm = MTF_norm/(max(max(MTF_parfaite))) ;
MTF_parfaite = MTF_parfaite/(max(max(MTF_parfaite))) ;


%% Profile de la MTF

a = (Nbpts-2*D)/2+1 ;
b = (Nbpts+2*D)/2 ;

MTF_norm_reduite = MTF_norm(a:b,a:b) ;
MTF_parfaite_reduite = MTF_parfaite(a:b,a:b) ;

borne_MTF = 1/(lambda*N) ;

cx_profile_MTF = [-borne_MTF borne_MTF] * cos(atan(pente))
cy_profile_MTF = [-borne_MTF borne_MTF] * sin(atan(pente))

% if (pente <= 1)
%      cx_profile_MTF = [-borne_MTF borne_MTF] ;
%      cy_profile_MTF = [-borne_MTF borne_MTF]*pente ;
% else
%     cx_profile_MTF = [-borne_MTF borne_MTF]/pente ;
%     cy_profile_MTF = [-borne_MTF borne_MTF] ;
% end

MTF_norm_profile = improfile(linspace(-borne_MTF,borne_MTF,D),linspace(-borne_MTF,borne_MTF,D),MTF_norm_reduite,cx_profile_MTF,cy_profile_MTF) ;
MTF_parfaite_profile = improfile(linspace(-borne_MTF,borne_MTF,D),linspace(-borne_MTF,borne_MTF,D),MTF_parfaite_reduite,cx_profile_MTF,cy_profile_MTF) ;

% MTF_norm(round((end+1)/2):end,round(end/2)) ;
% MTF_parfaite_profile = MTF_parfaite(round((end+1)/2):end,round(end/2)) ;
% 
% MTF_norm_profile = MTF_norm_profile(1:D) ;
% MTF_parfaite_profile = MTF_parfaite_profile(1:D) ;

figure('Name','FTM') ; plot(linspace(-borne_MTF,borne_MTF,length(MTF_parfaite_profile)),MTF_parfaite_profile,'b',...
    linspace(-borne_MTF,borne_MTF,length(MTF_norm_profile)),MTF_norm_profile,'r') ;
legend('MTF parfaite (mm-1)','MTF (mm-1)') ;

%%



%PSF_parfaite = PSF_parfaite((size(PSF_parfaite,1)*(Rapport_objet_pupille-1)/2+1):size(PSF_parfaite,1)*((Rapport_objet_pupille-1)/2+1)) ;

%%


% %borne = D*N*1E3*lambda/(2*Rapport_objet_pupille) ;
% figure ; plot( linspace(-borne_PSF,borne_PSF,D) , PSF_parfaite_profile, 'b',...
%     linspace(-borne_PSF,borne_PSF,D), PSF_norm_profile,'r') ;
% legend('PSF parfaite (µm)','PSF (µm)') ;
% title(strcat('Rapport de Strehl : ',num2str(max(max(PSF_norm_profile))/max(max(PSF_parfaite_profile)),'%1.3f'))) ;






%borne = Rapport_objet_pupille /(2*lambda*N) ;



