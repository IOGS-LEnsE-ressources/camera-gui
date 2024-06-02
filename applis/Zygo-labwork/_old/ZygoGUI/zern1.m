%Calcul des polynômes de la base 1
function Phase_calculee=zern1(X,Y,N)



%on calcule les valeurs des polynômes aux positions des points
%digitalisés
X=X(:);
Y=Y(:);

Pts_pol=ones(length(X),2);
[Pts_pol(:,2),Pts_pol(:,1)]=cart2pol(X,Y);



%Initialisation de phi
Phase_calculee=ones(length(X),N);

for i=1:N
Phase_calculee(:,i)=calc_zer(Pts_pol,i);
end



