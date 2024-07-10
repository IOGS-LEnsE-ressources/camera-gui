function phi2 = suppression_bord(phi,p)

[a,b] = size(phi) ;

phi2 = NaN*ones(a+20,b+20) ;
phi2(11:a+10,11:b+10)=phi ;

MatrixNaN = 100*isnan(phi2) ;

H = fspecial('average',p);
maskinverse = imfilter(MatrixNaN,H);

for i=1:a+20
    for j=1:b+20
        if maskinverse(i,j)~=0
            phi2(i,j)=NaN ;
        end
    end
end

MatrixNotNaN = ~isnan(phi2) ;

[mask,xmin,xmax,ymin,ymax] = selection_surface_utile(MatrixNotNaN) ;

phi2 = phi2(xmin:xmax,ymin:ymax) ;