function trace_spot_diagram(handles) ;

lambda = 632.8e-6 ; %lambda en mm

origines = handles.origines ;
angles = handles.angles ;
N = handles.N ;
f = handles.f ;
r = handles.r ;
deltaf = handles.deltaf ;

axes(handles.axe_spotdiagram) ;

hold off ;

spot = origines + [(f+deltaf-origines(:,3)) (f+deltaf-origines(:,3)) (f+deltaf-origines(:,3))].* angles ; 

%Calcul des coordonnées du barycentre des points
xcenter = mean(spot(:,1)) ;
ycenter = mean(spot(:,2)) ;
plot(xcenter,ycenter,'k+') ;


hold on ;

spot(:,1)=-1e3*spot(:,1);
spot(:,2)=1e3*spot(:,2);

for i=1:length(origines)

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

% Tracé de la tache d'Airy
theta=0:0.05:(2*pi+0.05);
rho_airy = 1.22*lambda*N*1e3 ;
x = xcenter + rho_airy*cos(theta);
y = ycenter + rho_airy*sin(theta);
plot(x,y,'k','LineWidth',2);

hold off ;
axis equal ;
grid on ;

