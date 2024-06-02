function spot = spot_diagram2(phi,N,f,p)

% Paramètre pour indiquer si l'on souhaite avoir une vue 3D du tracé des
% rayons (valeur par défaut : 0)
trace3D = 0 ;
lambda = 632.8e-6 ;
%conversion en écart normal de la surface en mm
phi=phi*lambda ;


%% Spot diagram

[a,b] = size(phi) ;
D = max(a,b) ;
D2 = f/N ; %Plus grande dimension, en mm
r = D2/2 ; %Plus grand rayon, en mm

%phi=flipud(phi);
% Calcul du gradient de la phase non convergente
[gphix,gphiy] = gradient(phi,(D2/b),(D2/a)) ;
%[gphix,gphiy] = gradient(phi,1,1) ;

% Création d'une grille de coordonnées de la pupille
[X,Y] = meshgrid(linspace(-r*b/D,r*b/D,b),linspace(-r*(a/D),r*(a/D),a)) ;

% Ajout d'une phase sphérique convergeant au point focal
phi = phi + f-sqrt(f^2-X.^2-Y.^2) ;

% Sauvegarde de la phase en organisation matricielle au cas où l'on trace
% la vue 3D
if (trace3D ==1)
    phi2 = phi ;
end

% Ajout d'une phase convergente
% On calcule directement le gradient de la partie focalisation pour des
% problèmes de précision de la fonction gradient
Gphix = X./sqrt((f^2)-(X.^2)-(Y.^2)) ;
Gphiy = Y./sqrt((f^2)-(X.^2)-(Y.^2)) ;
% gphix = gphix + Gphix ;
% gphiy = gphiy + Gphiy ;
 gphix = tan(atan(gphix) + atan(Gphix)) ;
 gphiy = tan(atan(gphiy) + atan(Gphiy)) ;
% Suppression des bords à cause d'un problème de bord de la fonction
% gradient
gphix = gphix(2:end-1,2:end-1) ;
gphiy = gphiy(2:end-1,2:end-1) ;
phi = phi(2:end-1,2:end-1) ;
X = X(2:end-1,2:end-1) ;
Y = Y(2:end-1,2:end-1) ;

% Transformation des coordonnées en vecteurs
gphix = reshape(gphix,[],1) ;
gphiy = reshape(gphiy,[],1) ;
X = reshape(X,[],1) ;
Y = reshape(Y,[],1) ;
phi = reshape(phi,[],1) ;


% Sélection des pixels du masque
index = ~isnan(gphix) & ~isnan(gphiy) & ~isnan(phi) ;
gphix = gphix(index) ;
gphiy = gphiy(index) ;
X = X(index) ;
Y = Y(index) ;
phi = phi(index) ;


% Sélection des points à afficher : plus p est grand, et moins il y a de
% points
index = [ones(round(length(phi)/p),1) ; zeros(length(phi)-round(length(phi)/p),1)] ;
p = randperm(length(phi)) ;
index(1:length(phi)) = index(p) ;

X = X(index==1) ;
Y = Y(index==1) ;
phi = phi(index==1) ;
origines = [X Y phi] ; %Origine des rayons du spot diagram
gphix = -gphix(index==1) ;
gphiy = -gphiy(index==1) ;
angles = [ gphix gphiy ones(sum(index),1) ] ; %Angles des rayons

%Coordonnées des points d'impact dans le plan focal
spot = origines + [(f-origines(:,3)) (f-origines(:,3)) (f-origines(:,3))].* angles ; 
%spot = origines + [(f+50-origines(:,3)) (f+50-origines(:,3)) (f+50-origines(:,3))].* angles ; 
%% Tracé des rayons en 3D

if (trace3D == 1)
    
    figure ; hold on ;

    for i=1:length(phi)

        %Selection des coordonnées de départ et d'arrivé des rayons
        x1=origines(i,1) ;
        x1=origines(i,1) ;
        y1=origines(i,2) ;
        z1=origines(i,3) ;
        x2=spot(i,1) ;
        y2=spot(i,2) ;
        z2=spot(i,3) ;

        %Affichage des points suivant un code de couleur
        if ((sqrt(x1^2+y1^2))<(0.2*r))
            plot3(x2,y2,f,'b.') ;
            line([x1;x2],[y1;y2],[z1;z2],'Color','b','LineWidth',0.1) ;
        elseif ((sqrt(x1^2+y1^2))<(0.4*r))
            plot3(x2,y2,f,'c.') ;
            line([x1;x2],[y1;y2],[z1;z2],'Color','c','LineWidth',0.1) ;
        elseif ((sqrt(x1^2+y1^2))<(0.6*r))
            plot3(x2,y2,f,'g.') ;
            line([x1;x2],[y1;y2],[z1;z2],'Color','g','LineWidth',0.1) ;
        elseif ((sqrt(x1^2+y1^2))<(0.8*r))
            plot3(x2,y2,f,'y.') ;
            line([x1;x2],[y1;y2],[z1;z2],'Color','y','LineWidth',0.1) ;
        else
            plot3(x2,y2,f,'r.') ;
            line([x1;x2],[y1;y2],[z1;z2],'Color','r','LineWidth',0.1) ;
        end

    end

    % Affichage de la surface
    [X,Y] = meshgrid(linspace(-r*b/D,r*b/D,b),linspace(-r*(a/D),r*(a/D),a)) ;
    surf(X,Y,phi2) ; shading interp ;
    axis equal ;

    hold off ;
    
end


%% Tracé du spot diagram

figure('name','spot diagramme','Position',[50,20,500,500]), ; 
hold on ;

spot(:,1)=-1e3*spot(:,1);
spot(:,2)=1e3*spot(:,2);
for i=1:length(phi)

    %Selection des coordonnées de départ et d'arrivé des rayons
    x1=origines(i,1) ;
    y1=origines(i,2) ;
    x2=spot(i,1) ;
    y2=spot(i,2) ;

    %Affichage des points suivant un code de couleur
    if ((sqrt(x1^2+y1^2))<(0.2*r))
        plot(x2,y2,'b.') ;
    elseif ((sqrt(x1^2+y1^2))<(0.4*r))
        plot(x2,y2,'c.') ;
    elseif ((sqrt(x1^2+y1^2))<(0.6*r))
        plot(x2,y2,'g.') ;
    elseif ((sqrt(x1^2+y1^2))<(0.8*r))
        plot(x2,y2,'y.') ;
    else
        plot(x2,y2,'r.') ;
    end

end

%Calcul des coordonnées du barycentre des points et tracé du cercle de la
%tache d'Airy
xcenter = mean(spot(:,1)) ;
ycenter = mean(spot(:,2)) ;
theta=0:0.05:(2*pi+0.05);
rho_airy = 1.22*lambda*N*1e3 ;%en microns
x = xcenter + rho_airy*cos(theta);
y = ycenter + rho_airy*sin(theta);
plot(x,y,'k','LineWidth',2);

hold off ;
axis equal ;
grid on ;
xlabel('microns')
ylabel('Cercle noir : rayon du premier anneau noir de la tache d''Airy')
title({'Spot diagram en microns';'Bleu : 0 à 0.2 -- Cyan : 0.2 à 0.4 -- ';'--Vert : 0.4 à 0.6 -- Jaune : 0.6 à 0.8 -- Rouge : 0.8 à 1'}) ;


%% Energie encerclée

%Calcul du nombre de points du spot diagram
nbpts = length(spot(:,1)) ;

%Création du cercle dont on va compter les points qui sont à l'intérieur
rho = 0 ;
deltarho = rho_airy/100 ;

%Nombre de points à l'intérieur du cercle
nbptscercle = 0 ;

i=1 ;

%Calcul des distances des points du spot diagram au centre du cercle
distances = sqrt( (xcenter*ones(nbpts,1)-spot(:,1)).^2 + (xcenter*ones(nbpts,1)-spot(:,1)).^2 ) ;

%Aggrandissement de la taille du cercle, on compte le nombre de points qui
%se trouve à l'intérieur en fonction de la taille
while (nbptscercle ~=nbpts && i<100000)
    
    nbptscercle = sum(distances < rho) ;
    tab_energie(i) = nbptscercle ;
    i=i+1 ;
    rho = rho+deltarho ;
    
end

%Affichage
figure('name','spot diagramme : energie encerclée','Position',[600,20,400,400]) ; 

plot(deltarho*(0:i-2),100*tab_energie/nbpts,'r',[rho_airy rho_airy],[0 100],'b') ;
xlabel('microns')
grid on
legend('Pourcentage de rayons encerclés','Système limité par la diffraction','Location','SE') ;
        

clear all