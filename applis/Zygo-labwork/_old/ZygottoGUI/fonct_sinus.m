function y=fonct_sinus(param,x);
%cree une  fn sinus entre 0 et 1
%pour fitter un profil

x0=param(1);
periode=param(2);
decalage=param(3);

u=2*pi*(x-x0)/(periode);
y=(sin(u)+1)/2+decalage;

end