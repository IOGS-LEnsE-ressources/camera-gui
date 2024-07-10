function seidel = conversion_zernike2seidel(zern) ;

seidel=zeros(5,2) ;

%Tilt
seidel(1,1) = sqrt(zern(2)^2+zern(3)^2) ;
seidel(1,2) = atan2(zern(3),zern(2))*(180/pi) ;%degre

%Focus
seidel(2,1) = 2*zern(4) ;

%Astigmatisme
seidel(3,1) = 2*sqrt(zern(5)^2+zern(6)^2) ;
seidel(3,2) = 180*atan2(zern(6),zern(5))/2/pi ;

%Coma
seidel(4,1) = 3*sqrt(zern(7)^2+zern(8)^2) ;
seidel(4,2) =180*atan2(zern(8),zern(7))/pi ;

%Aberration sphérique
seidel(5,1) = 6*zern(9) ;