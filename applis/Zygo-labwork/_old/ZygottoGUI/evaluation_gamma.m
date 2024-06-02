%calcul de la correction gamma
%acquiere de profil d'une image video
%calcul a partir de celle-ci la correction gamma a apporter
%realise pour cela un fit a un sinus^gamma
%puis corrige l'intensite mesuree d'une puissance 1/gamma

function gamma=evaluation_gamma

%acquisition du profil a traiter
[profile,Img]=acq_profile;

%filtrage du profil afin de supprimer la composante continue (filtre
%passe-haut)
[b,a] = butter(2,0.01,'high') ;
profile_filt = filtfilt(b,a,profile) ;

%lissage du profil (sinon c'est moche)
profile_filt_moy=lissage(profile_filt,6);
%on centre le profil sur zero
profile_filt_moy=profile_filt_moy - mean(profile_filt_moy) ;

%recherche des zeros du profil
%afin d'obtenir la periode
profile_zeros=recherchezeros(profile_filt_moy);

%calcul des periodes donnees par les ecarts entre les ie et i+2e zeros
n=size(profile_zeros,2) ;
j=1 ;
for i=1:2:n-2
    profile_zeros_ecarts(j) = (profile_zeros(i+2)-profile_zeros(i)) ;
    j=j+1 ;
end
%periode utilisee par la suite = moyenne des periodes calculees au dessus
T = mean(profile_zeros_ecarts) ;

%on ramene le profil entre 0 et 1
mx = max(profile_filt_moy) ;
mn = min(profile_filt_moy) ;
profile_filt_moy =(profile_filt_moy +mx)/(mx-mn) ;

%fit par une sinusoide
%on obtient de cette facon certains parametres a utiliser pour le fit par
%le sinus^gamma
m=size(profile_filt_moy,2)
[x0,decalage,sinus_fit] = fit_par_sin(0,T,0,1:m,profile_filt_moy);

%fit par sinus^gamma
%on obtient la valeur de gamma en sortie de la fonction
[gamma,periode,gamma_fit] = fit_par_sinus_gamma(x0,0.5,T,0,1:m,profile_filt_moy);

%correction de l'intensite du profil de depart d'une puissance 1/gamma
profile_corrige=(profile).^(1/gamma) ;

%trace du profil et du profil corrige
figure ; plot(1:size(profile),profile/max(profile),1:size(profile),profile_corrige/max(profile_corrige)) ;

figure ; imagesc(double(Img)) ; figure ; Imagesc(double(Img).^(1/gamma)) ;

end