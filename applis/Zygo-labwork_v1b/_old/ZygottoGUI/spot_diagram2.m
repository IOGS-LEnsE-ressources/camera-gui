function spot = spot_diagram2(phi,N,f,p)

% A FAIRE : inclure le wedge factor ?

lambda = 632.8e-6 ;

%phi en phase pure

%Suppression du tilt
%coeff_zernicke = zern(phi) ;
%phi = affichage_surface(phi,coeff_zernicke,[1,1,1]) ;

phi=phi*lambda/(2*pi) ;

[a,b] = size(phi) ;
D = max(a,b) ;
D2 = f/N ;
r = D2/2 ;

for i=1:a
    for j=1:b
        phi(i,j)=phi(i,j)+f-sqrt(f^2-(D2/D*(i-(a+1)/2))^2-(D2/D*(j-(b+1)/2))^2) ;
    end
end


angles=zeros(round(a*b/p^2),3) ;
origines=zeros(round(a*b/p^2),3) ;

n=1 ;
p2 = round(p/2) ;
 
M=zeros((2*p2+1)^2,3) ;
selection2=zeros((2*p2+1)^2,1) ;

for i=(1+p2):p:(a-p2)

    for j=(1+p2):p:(b-p2)

        selection=phi((i-p2):(i+p2),(j-p2):(j+p2)) ;

        if (sum(isnan(selection))==0)

            m=1 ;

            for k=1:(2*p2+1)
                for l=1:(2*p2+1)
                    M(m,:)=[(k*D2/D) (l*D2/D) 1] ;
                    selection2(m)=selection(k,l) ;
                    m = m+1 ;
                end
            end

            angles(n,:)=M\selection2 ;
            origines(n,:)=[(i-a/2)*D2/D (j-b/2)*D2/D phi(i,j)] ;
            n=n+1 ;
        
        end
    end
end

angles = (angles(1:n-1,:)) ;
origines = origines(1:n-1,:) ;

angles = [-angles(:,1) -angles(:,2) ones(n-1,1)] ;

spot = origines + [(f-origines(:,3)) (f-origines(:,3)) (f-origines(:,3))].* angles ;


% figure ; hold on ; 
% 
% for i=1:n-1
%     
%     x1=origines(i,1) ;
%     y1=origines(i,2) ;
%     z1=origines(i,3) ;
%     x2=spot(i,1) ;
%     y2=spot(i,2) ;
%     z2=spot(i,3) ;
%     
%     if ((sqrt(x1^2+y1^2))<(0.2*r))
%         plot3(x2,y2,f,'b.') ;
%         line([x1;x2],[y1;y2],[z1;z2],'Color','b','LineWidth',0.1) ;
%     elseif ((sqrt(x1^2+y1^2))<(0.4*r))
%         plot3(x2,y2,f,'c.') ;
%         line([x1;x2],[y1;y2],[z1;z2],'Color','c','LineWidth',0.1) ;
%     elseif ((sqrt(x1^2+y1^2))<(0.6*r))
%         plot3(x2,y2,f,'g.') ;
%         line([x1;x2],[y1;y2],[z1;z2],'Color','g','LineWidth',0.1) ;
%     elseif ((sqrt(x1^2+y1^2))<(0.8*r))
%         plot3(x2,y2,f,'y.') ;
%         line([x1;x2],[y1;y2],[z1;z2],'Color','y','LineWidth',0.1) ;
%     else
%         plot3(x2,y2,f,'r.') ;
%         line([x1;x2],[y1;y2],[z1;z2],'Color','r','LineWidth',0.1) ;
%     end
% 
% end
% 
% x=linspace(-a*D2/(2*D),a*D2/(2*D),a) ;
% y=linspace(-b*D2/(2*D),b*D2/(2*D),b) ;
% X=zeros(a,b) ;
% Y=zeros(a,b) ;
% 
% for i=1:a
%     for j=1:b
%         X(i,j)=x(i) ;
%         Y(i,j)=y(j) ;
%     end
% end
% 
% surf(X,Y,phi) ;
% shading flat ;
% 
% hold off ;
% axis equal ;

figure ; 

hold on ;


for i=1:n-1
    
    x1=origines(i,1) ;
    y1=origines(i,2) ;
    x2=spot(i,1) ;
    y2=spot(i,2) ;
    
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

xcenter = mean(spot(:,1));
ycenter = mean(spot(:,2));
theta=0:0.05:(2*pi+0.05);
rho_airy = 1.22*lambda*N ;
x = xcenter + rho_airy*cos(theta);
y = ycenter + rho_airy*sin(theta);
plot(x,y);

hold off ;
axis equal ;



%% Energie encerclée

nbpts = length(spot(:,1)) ;
nbptscercle = 0 ;
rho = 0 ;
deltarho = rho_airy/1000 ;
i=1 ;


distances = sqrt( (xcenter*ones(nbpts,1)-spot(:,1)).^2 + (xcenter*ones(nbpts,1)-spot(:,1)).^2 ) ;

while (nbptscercle ~=nbpts && i<100000)
    
    nbptscercle = sum(distances < rho) ;
    tab_energie(i) = nbptscercle ;
    i=i+1 ;
    rho = rho+deltarho ;
    
end

figure ; plot(deltarho*(0:i-2),100*tab_energie/nbpts,'r',[rho_airy rho_airy],[0 100],'b') ;
legend('Pourcentage d''energie encerclée (x en µm)','Système limité par la diffraction','Location','SE') ;
        