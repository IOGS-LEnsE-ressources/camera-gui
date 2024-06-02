function Imgdiff=difference_images(Img1,Img2)

%Imgdiff = uint8(double(coupe_image(Img1,550,550)).^(1.2)-double(coupe_image(Img2,550,550)).^(1.2)) ;
Imgd1 = double(Img1) ;
Imgd2 = double(Img2) ;
mx1 = max(max(Imgd1)) ;
mx2 = max(max(Imgd2)) ;
Imgdn1 = Imgd1/mx1 ;
Imgdn2 = Imgd2/mx2 ;
% Imgdiffd = 255*((Imgdn1).^(1)-Imgdn2.^(1)) ;
Imgdiffd = 255*((Imgdn1).^(1/0.46)-Imgdn2.^(1/0.46)) ; % Correction du gamma 
Imgdiff = uint8(Imgdiffd) ;

end