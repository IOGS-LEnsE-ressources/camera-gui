function coeff = seidel_imprimables(zernike)
seidel=conversion_zernike2seidel(zernike);

ligne1 = [num2str(seidel(1,1),3) '         ' num2str(seidel(1,2),3)];
ligne2 = [num2str(seidel(2,1),3) '           -      '];
ligne3 = [num2str(seidel(5,1),3) '           -      '];
ligne4 = [num2str(seidel(3,1),3) '         ' num2str(seidel(3,2),3)];
ligne5 = [num2str(seidel(4,1),3) '         ' num2str(seidel(4,2),3)];
coeff={'Coefficients de Seidel';'';'Amplitude    Angle en degrés';'Tilt';ligne1;...
    'Defocus';ligne2;'Aberration Sphérique';ligne3;'Astigmatisme';ligne4;'Coma';ligne5};