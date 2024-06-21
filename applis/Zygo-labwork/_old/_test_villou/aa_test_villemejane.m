% Test Script for unwrapping and interpolation
%   Author : Villemejane Julien / 2024

disp('Test Unwrapping')
load("imgs1.mat")

Img1=uint8(Imgs(:,:,1));
Img2=uint8(Imgs(:,:,2));
Img3=uint8(Imgs(:,:,3));
Img4=uint8(Imgs(:,:,4));
Img5=uint8(Imgs(:,:,5));

[img,mask] = mask_auto(Img1,Img2,Img3,Img4,Img5) ;

%figure();
%imshow(mask);
mask = ones((size(Img1)));

[img_interf,phi]=phase_shift(Img1,Img2,Img3,Img4,Img5, mask);

figure();
imshow(phi)

% unwrap2D()