function [Mask_select,xmin,xmax,ymin,ymax] = selection_surface_utile(Mask)

[a,b] = size(Mask) ;

xmin = 1 ;

while ( (sum(Mask(xmin,:))==0) && (xmin<a) )
    xmin = xmin+1 ;
end


xmax = a ;

while ( (sum(Mask(xmax,:))==0) && (xmax>1) )
    xmax = xmax-1 ;
end


ymin = 1 ;

while ( (sum(Mask(:,ymin))==0) && (ymin<b) )
    ymin = ymin+1 ;
end


ymax = b ;

while ((sum(Mask(:,ymax))==0) && (ymax>1) )
    ymax = ymax-1 ;
end


Mask_select = Mask(xmin:xmax,ymin:ymax) ;
