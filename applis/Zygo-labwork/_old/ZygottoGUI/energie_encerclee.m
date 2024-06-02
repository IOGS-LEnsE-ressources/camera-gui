%energie encerclee pour la PSF
function energie_encerclee(PSF,PSF_parfaite,N_ouverture,zoom_psf);

%Calcul de la posiiton du barycentre de la tache
Dim_X=size(PSF,2);
Dim_Y=size(PSF,1);
Dim_max=max(Dim_X, Dim_Y);
vect_x=(1:Dim_X)';

%Position du barycentre
%coordonnee Bar X : Somme PSF(i,j) * OGx = Somme PSF(i,i)* OA(j)
Bar_X=sum(PSF*vect_x)/sum(sum(PSF))

vect_y=(1:Dim_Y)';
Bar_Y=sum(PSF'*vect_y)/sum(sum(PSF))

x=(1:Dim_X);
y=(1:Dim_Y);
[X,Y]=meshgrid(x,y);

X_rep_bary= X-Bar_X*ones(size(X));
Y_rep_bary= Y-Bar_Y*ones(size(Y));
R=sqrt(X_rep_bary.^2+Y_rep_bary.^2);


%%%%%%%%%%%%%Calcul de l'energie encerclee%%%%%%%%%%%%%%%%%
Energie_encerclee =[];
Energie_encerclee_parfaite=[];%initialisation des vecteurs

for rayon=0:1:(Dim_X/2)%on ouvre le rayon de zero a Dim_X/8
    PSF_encerclee = PSF(R<rayon);
    Energie_encerclee =[Energie_encerclee sum(sum(PSF_encerclee))];
end
Energie_encerclee= Energie_encerclee/sum(sum(PSF));

%%%%%%%%%%Comparaison avec limite de diffraction
for rayon=0:1:(Dim_X/2) %on ouvre le rayon de zero a Dim_X/8
    PSF_encerclee_parfaite = PSF_parfaite(R<rayon);
    Energie_encerclee_parfaite =[Energie_encerclee_parfaite sum(sum(PSF_encerclee_parfaite))];
end
Energie_encerclee_parfaite= Energie_encerclee_parfaite/sum(sum(PSF));


%pour l'affichage x,y
Lambda = 632.8*1E-6 %en mm
Rayon_image=Lambda*N_ouverture;
Rapport_pupille_plan = 2^zoom_psf;
r_image=1e3*(Rayon_image/Rapport_pupille_plan )*(0:(Dim_X/2));
figure('name','Energie encerclée'),plot(r_image,Energie_encerclee,'b', r_image,Energie_encerclee_parfaite,'r:')
grid,  xlabel('en microns')
legend('Réponse percussionnelle','Limite de diffraction',0);