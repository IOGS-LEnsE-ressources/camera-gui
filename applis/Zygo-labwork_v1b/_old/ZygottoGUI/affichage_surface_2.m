function [phi2,Surf_poly] = affichage_surface_2(phi,aberrations_soustraites);

pas=5;

[a,b] = size(phi) ;

phi2 = phi/(2*pi) ;


x=linspace(-1,1,b) ;
y=linspace(-1,1,a) ;
[X,Y] = meshgrid(x,y) ;

%phi2=fliplr(phi2) ;
%phi2=flipud(phi2) ;

% figure ; imagesc(phi2),colorbar ;
% figure ; surf(phi2) ; shading interp ;
aberrations_soustraites(aberrations_soustraites~=0);
    
if (nargin~=1)
    
    N=length(aberrations_soustraites) ;% N=3 pour soustraire le tilt 
    
   coeff_zern=zern_soustraction(phi,N) ;
    
    
    val_Poly1=zern1(X,Y,N);

    Surf_poly = zeros(a*b,1) ;

    for i=1:N
        Surf_poly=Surf_poly+aberrations_soustraites(i)*coeff_zern(i,1)*val_Poly1(:,i);
    end
    Surf_poly=reshape(Surf_poly,length(y),length(x));
    
  % figure ; imagesc(Surf_poly),colorbar ;
    %figure ; imagesc(Surf_poly),colorbar ;
 
 
    phi2=phi2-(Surf_poly);
 %figure ; imagesc(phi2),colorbar ;
 
 
 
   % phi2 = suppression_bord(phi2,3) ;
    
   
    %figure ; surf(phi2),colorbar ; shading interp ;

%     for i=1:N
%         if (aberrations_soustraites(i)==1)
%                         
%             phi2=phi2-(coeff_zern(i)*reshape(val_Poly1(:,i),length(y),length(x)))';
%         end
%     end
    
end

