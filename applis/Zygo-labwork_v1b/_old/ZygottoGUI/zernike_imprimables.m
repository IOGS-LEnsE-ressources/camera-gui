function coeff = zernike_imprimables(zernike)
ligne1='';
ligne2='';
ligne3='';
ligne4='';
for j = 1:8
    ligne1 = [ligne1  num2str(zernike(j+1),3) '     '];
    ligne2 = [ligne2  num2str(zernike(j+9),2) '     '];
    ligne3 = [ligne3  num2str(zernike(j+18),2) '     '];
    ligne4 = [ligne4  num2str(zernike(j+27),2) '     '];
end
coeff={'Coefficients de zernicke';...
    'Tilt1   Tilt2  Defoc    Astig1   Astig2   coma1    coma2    ab.spher';
    ligne1;'9-17';ligne2;'18-26';ligne3;'27-35';ligne4};