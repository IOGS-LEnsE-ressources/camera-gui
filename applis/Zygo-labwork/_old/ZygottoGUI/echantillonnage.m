function Img_ech = echantillonnage(Img,p)

[a,b] = size(Img) ;

Img_ech=zeros(round(a/p),round(b/p)) ;

x=0 ;
y=0 ;

for i=1:p:a-p
    x=x+1;
    for j=1:p:b-p
        y=y+1 ;
        Img_ech(x,y)=sum(sum(Img(i:i+p,j:j+p)))/((p+1)^2) ;
    end
    y=0 ;
end

Img_ech=Img_ech(1:end-1,1:end-1) ;