%Approximation polynomiale sur la base des polynomes de Zernicke
function [coeff_zernicke,Surf_poly]=zern_soustraction(phi,N)

%degré du polynome
%N=37 ;%Modif principale

%Passage en coordonnée polaire [Theta,R]

[a,b] = size(phi) ;

%surf(phi) ; shading interp ;

x=linspace(-1,1,b) ;
y=linspace(-1,1,a) ;
[X,Y]=meshgrid(x,y) ;

%phi=fliplr(phi) ;
%phi=flipud(phi) ;

X=reshape(X,a*b,1) ;
Y=reshape(Y,a*b,1) ;
phi=reshape(phi,a*b,1) ;



X=X(~isnan(phi)) ;
Y=Y(~isnan(phi)) ;
 phi=phi(~isnan(phi)) ;
% 
% phi=phi-mean(mean(phi));

nbre_points=length(phi);
Pts_pol=ones(nbre_points,2);

[Pts_pol(:,2),Pts_pol(:,1)]=cart2pol(X,Y);
phi=phi/(2*pi);

%Calcul de la matrice M par le biais de la fonction agphi1

%préalloc
M=zeros(nbre_points,N-1);

for i=1:N
    M(:,i)=calc_zer(Pts_pol,i);
end


%Calcul des coefficients de la base 
coeff_zernicke=M\phi ;

coeff_zernicke =[coeff_zernicke];



% if (nargin == 2 && affichage_surface == 1)
%     
%     %Calcul de Sigma et de Delta A,PV
%     %Initialisation de la matrice B
%     %Calcul des hauteurs données par l'approximation polynomiale
%     B=ones(nbre_points,1);
%     for j=1:1:nbre_points
%         B(j)=sum(coeff_zernicke.*M(j,:)');
%     end
%     
%     
%     %construction des phi calculés pour représentation
%     x=linspace(-1,+1,200);
%     y=linspace(-1,+1,200);
%     [X,Y]=meshgrid(x,y);
%     
%     
%     
%     %Calcul des valeurs des polynômes en (X,Y)
%     
%     val_Poly1=zern1(X,Y,N);
%     
%     Surf_poly=zeros(length(X(:)),1);
%     
%     
%     for i=3:1:N
%         Surf_poly(:,1)=Surf_poly(:,1)+coeff_zernicke(i,1)*val_Poly1(:,i);
%     end
%     
%     for i=1:40000
%         if Surf_poly(i)==0
%             Surf_poly(i)=NaN ;
%         end
%     end
%     
%     %Reformation de C pour la fonction mesh à venir
%     Surf_poly=reshape(Surf_poly,length(y),length(x));
%     Surf_poly=flipud(Surf_poly);
%     
%     %mesh(Surf_poly);
%     figure ; surfc(Surf_poly);
%     shading interp ;
%     
% end