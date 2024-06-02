function y=fonct_sinus_gamma(param,x);
%cree une  fn sinus^gamma entre 0 et 1
%pour fitter un profil 

x0=param(1);
gamma=param(2);
periode=param(3);
decalage=param(4);

u=2*pi*(x-x0)/(periode);
y=(((sin(u)+1)/2).^(gamma))+decalage;

end