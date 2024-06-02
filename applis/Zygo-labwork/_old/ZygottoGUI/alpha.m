function alpha = alpha(Imgs)


Imgd1 = double(Imgs(:,:,1)) ;
Imgd2 = double(Imgs(:,:,2)) ;
Imgd3 = double(Imgs(:,:,3)) ;
Imgd4 = double(Imgs(:,:,4)) ;
Imgd5 = double(Imgs(:,:,5)) ;

Imgddiff1 = abs(Imgd1 - Imgd3) ;
Imgddiff2 = abs(Imgd2 - Imgd4) ;


% mise a 0 des points du masque pour lesquels la difference est toujours inferieure au seuil
[a,b]=size(Imgd1) ;
mask=ones(a,b) ;

mask(Imgddiff1<8 & Imgddiff2<8) = 0 ;

PSF = fspecial('gaussian',3,5);
mask = imfilter(mask,PSF,'conv');

alpha = ((Imgd5-Imgd1)./(2*(Imgd4-Imgd2))) ;
%alpha = acos(alpha) 
alpha(mask~=1) = NaN ;

alpha = reshape(alpha(~isnan(alpha)),1,[]) ;
alpha = mod(real(acos(alpha)*180/pi),180) ;

hist(alpha,linspace(45,135,91))
grid


index_cond=~isnan(alpha)& (alpha < 120 ) & (alpha > 60 ) ;
mean(alpha(index_cond))
std(alpha(index_cond))