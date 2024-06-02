function [valeurs_moy,tensions] = recherche_dephasage

Vmin = 0 ;
Vmax = 8 ;
pas = 0.1 ;
nbechantillons = round((Vmax - Vmin)/pas)+1 ;
nbmesures = 1 ;

valeurs = zeros(nbmesures,nbechantillons) ;

wbar = waitbar(0,'Calibration en cours...','color',[0.2 0.357 0.6],'name','Progression') ;
set(wbar,'CloseRequestFcn','return')
pause(0.5) ;






for k=1:nbmesures
    
    disp(['Mesure ',int2str(k),'/',int2str(nbmesures)]) ;
 
    Img=videosnap;
   
    i=1 ;
    
    clear Imgs ;
    
sizeimg=videosnap;
vert=size(sizeimg,1);
hor=size(sizeimg,2);

Imgs = zeros(vert,hor,nbechantillons+1) ;
    
    
    for V=Vmin:pas:Vmax
        daqoutfloat(V);
        Imgs(:,:,i)=videosnap ;
        i=i+1 ;
        waitbar((k-1)/nbmesures+(V-Vmin)/(2*nbmesures * (Vmax-Vmin)),wbar) ;
    end
    
    daqoutfloat(0) ;
    
    %Img = Img(200:300,200:300) ;
   Imgs = Imgs(200:300,200:300,:) ;
    
    for j=11:nbechantillons
        valeurs(k,j) = mean(mean(double(difference_images(Imgs(:,:,11),Imgs(:,:,j))))) ;
        waitbar((k-1)/nbmesures + 0.5/nbmesures + j/(2*nbmesures * nbechantillons),wbar) ;
    end
    
    waitbar(k/nbmesures,wbar) ;

end

% figure ; plot(valeurs(1,:)) ;

figure ; plot(Vmin:pas:Vmax,valeurs) ;



for j=1:nbechantillons
    valeurs_moy(j)=mean(valeurs(:,j)) ;
end


[b a]=butter(2,0.25,'low');
valeurs_moy=filtfilt(b,a,valeurs_moy);

hold on
plot (Vmin:pas:Vmax,valeurs_moy,'m'), title('avec butter');
hold off

size(valeurs_moy)

%figure ; plot(Vmin:pas:Vmax,valeurs_moy) ;

hold on

Vx0=0 ;
Vy0=0 ;
plot(0,0,'+m')

[Vy2,Vx2]=max(valeurs_moy(11:26)) ;
Vx2 = Vx2+9 ;
Vy2
plot(Vx2/10,valeurs_moy(Vx2+1),'+m')

[Vy4,Vx4]=min(valeurs_moy(27:41)) ;
Vx4 = Vx4+25 ;
plot(Vx4/10,valeurs_moy(Vx4+1),'+m')

Vy1 = (Vy0+Vy2)/2 ;
Vy3 = Vy1 ;

for i=1:(Vx2-1)
    if (valeurs_moy(i)<=Vy1 && Vy1<=valeurs_moy(i+1))
        if (Vy1-valeurs_moy(i))<(valeurs_moy(i+1)-Vy1)
            Vx1 = i - 1 ;
        else
            Vx1 = i ;
        end
        plot(Vx1/10,valeurs_moy(Vx1+1),'+m')
        break
    end
end

for i=Vx2:(Vx4-1)
    if (valeurs_moy(i)>=Vy3 && Vy3>=valeurs_moy(i+1))
        if (valeurs_moy(i)-Vy3)<(Vy3-valeurs_moy(i+1))
            Vx3 = i - 1 ;
        else
            Vx3 = i ;
        end
        plot(Vx3/10,valeurs_moy(Vx3+1),'+m')
        break
    end
end

Vx3=Vx4-1;

waitbar(1,wbar) ;
set(wbar,'CloseRequestFcn','delete(gcf)')
close(wbar) ;

disp('Méthode 1')
tensions = [Vx0,Vx1,Vx2,Vx3,Vx4]/10

hold off





% % Méthode n°2 
% 
tensions_appliquees = 1:pas:Vmax ;
valeurs_moy=valeurs_moy(11:end) ;
Nb_pts=length(tensions_appliquees)-1;




Am=max(max(valeurs_moy)); %amplitude sinusoide

tensions_appliquees2=tensions_appliquees(1:Nb_pts); %il faut enlever le dernier point!

dephasages=180*asin(valeurs_moy/Am)/pi ; %en degré phi/2
 
%figure,  plot(dephasages);

der_deph=diff(dephasages) ; % on calcul la derivee
i=find(0>der_deph) ; % points à derivee negative 
dephasages(i)=90+(90-dephasages(i)) ; % attention deroulement avec une seulement deux arches ???

%il faut enlever le dernier point!
dephasages=2*dephasages(1:Nb_pts);

for i=1:Nb_pts-1
    if dephasages(i+1)<dephasages(i)
        dephasages(i+1:end) = dephasages(i+1:end)+360 ;
    end
end

figure ; plot(tensions_appliquees2,dephasages) ;

dephasages_commande = [0 90 180 270 360] ;

disp('Méthode 2')
tensions_commande=interp1(dephasages,tensions_appliquees2,dephasages_commande,'spline')

save_config('calibpiezo_tensions',tensions_appliquees)
save_config('calibpiezo_valeurs',valeurs_moy)
save_config('Tensions',tensions_commande)

%hold on ; plot(tensions_commande,dephasages_commande,'m+') ; hold off