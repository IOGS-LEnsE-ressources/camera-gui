function tensions_commande = calcul_tensions(N, theta)

tensions = read_config('calibpiezo_tensions',1) ;
valeurs = read_config('calibpiezo_valeurs',1) ;

figure,plot(tensions,valeurs)

Nb_pts=length(tensions)-1;
Am=max(max(valeurs)); %amplitude sinusoide

tensions2=tensions(1:Nb_pts); %il faut enlever le dernier point!

dephasages=180*asin(valeurs/Am)/pi ; %en degré phi/2

figure, plot(dephasages)

der_deph=diff(dephasages) ; % on calcule la derivee
i=find(0>der_deph) ; % points à derivee negative 
dephasages(i)=90+(90-dephasages(i)) ; % attention deroulement avec une seulement deux arches ???

%il faut enlever le dernier point!
dephasages=2*dephasages(1:Nb_pts);

figure,plot(dephasages)






% for i=1:Nb_pts-1
%     if dephasages(i+1)<dephasages(i)
%         dephasages(i+1:end) = dephasages(i+1:end)+360 ;
%     end
% end

dephasages_commande = theta * (0:(N-1)) + 45 

tensions_commande=interp1(dephasages,tensions2,dephasages_commande,'spline') ;



figure ; plot(tensions2,dephasages) ;
hold on ; plot(tensions_commande,dephasages_commande,'m+') ; hold off

