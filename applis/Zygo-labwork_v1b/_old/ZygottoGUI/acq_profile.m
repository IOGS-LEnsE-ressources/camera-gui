%acquiere une image video
%demande a l'utilisateur de choisir un profil
%puis trace celui-ci
%la fonction ressort le profil choisi

function [profile,Img]=acq_profile

%acquisition de l'image video
[Img,status,ErrLoc]=VideoSNAP ;

%affichage de l'image
imshow(Img) ;

%choix du profil par l'utilisateur et stockage dans profile
profile = improfile ;

%trace du profil
plot(profile) ;

end