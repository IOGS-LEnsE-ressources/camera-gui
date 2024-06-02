function [PV,RMS]=statistique_surface(surf)

PV = max(max(surf))-min(min(surf)) ;
min(min(surf))
max(max(surf))

[a,b]=size(surf) ;

Z=zeros(a*b,1) ;

k=1 ;

for i=1:a
    for j=1:b
        if ~(isnan(surf(i,j)))
            Z(k)=surf(i,j) ;
            k=k+1;
        end
    end
end

Z=Z(1:k-1) ;
RMS = sqrt(var(Z)) ;