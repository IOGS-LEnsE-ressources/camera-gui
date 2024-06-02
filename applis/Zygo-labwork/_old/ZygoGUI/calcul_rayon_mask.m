function R=calcul_rayon_mask(mask)

pts = bwboundaries(mask) ;
pts = pts{1} ;

[a,b] = size(pts) ;

C = [ones(a,1)*(min(pts(:,1))+max(pts(:,1)))/2 ones(a,1)*(min(pts(:,2))+max(pts(:,2)))/2] ;


distances = abs(pts - C) ;

distances = sqrt(distances(:,1).^2 + distances(:,2).^2) ;

R = max(distances) ;