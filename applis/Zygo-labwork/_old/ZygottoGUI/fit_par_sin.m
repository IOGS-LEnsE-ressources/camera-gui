function [x0,decalage,y_fit]=fit_par_sin(x0_ini,largeur_ini,decalage_ini,x_profil,profil_tache);
% Chercher un fit par une sinusoide
% Les parametres_ini sont les paramètres de debut de recherche de la
% courbe sin :
%   * x0_ini 
%   * largeur_ini : periode de la sinusoide
%   * Ampl_ini : la valeur du max
%   * decalage_ini : le decalage de zero 
%  x_profil et profil_tache sont obtenus  
%   par la fonction [x_profil,profil_tache]=profil_moyen;


options=optimset('Display','off','TolFun',1e-8,'TolX',1e-3);
x=x_profil;


param=[x0_ini largeur_ini decalage_ini];
 format long, param=lsqcurvefit('fonct_sinus',param, x, profil_tache);


x0=param(1);
largeur=param(2);
decalage=param(3);


u=2*pi*(x-x0)/(largeur);
y_fit=(sin(u)+1)/2+decalage;

figure
plot(x,profil_tache,'g'),grid on,hold

%waitforbuttonpress
 
 plot(x, y_fit,'r');
 
 hold off
 
end