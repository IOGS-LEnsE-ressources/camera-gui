function [gamma,periode,y_fit]=fit_par_sinus_gamma(x0_ini,gamma_ini,periode_ini,decalage_ini,x_profil,profil_tache);
% Chercher un fit par un sinus^gamma
% Les parametres_ini sont les paramètres de debut de recherche de la
% courbe sin^gamma :
%   * x0_ini : position en pixel du centre de la tache de % diffraction
%   * gamma_ini : largeur entre les deux premiers zeros
%   * periode_ini : la valeur du max
%   * decalage_ini : le decalage de zero 
%  x_profil et profil_tache sont obtenus  
%   par la fonction [x_profil,profil_tache]=profil_moyen;


options=optimset('Display','off','TolFun',1e-8,'TolX',1e-3);
x=x_profil;


param=[x0_ini gamma_ini periode_ini decalage_ini];
 format long, param=lsqcurvefit('fonct_sinus_gamma',param, x, profil_tache);


x0=param(1);
gamma=param(2);
periode=param(3);
decalage=param(4);


u=2*pi*(x-x0)/(periode);
y_fit=(((sin(u)+1)/2).^(gamma))+decalage;

figure
plot(x,profil_tache,'g'),grid on,hold

%waitforbuttonpress
 
 plot(x, y_fit,'r');
 
 hold off
 
end