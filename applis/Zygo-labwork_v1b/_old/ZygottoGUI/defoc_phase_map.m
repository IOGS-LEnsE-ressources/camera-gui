%Calcul des polynômes du N ieme polynome de zernicke  
function [Z_phase_defoc]=defoc_phase_map(pupille,N_lambda);
%Cree sur la pupille une defoc de N_lambda
%Zern un tableau ligne de valeurs de  Zernicke
 Dim_X = size(pupille,2) ;
 Dim_Y = size(pupille,1) ;
 Dim_max=max( Dim_X, Dim_Y);
 
x=linspace(-1,1, Dim_X);
y=linspace(-1,1, Dim_Y);
[X,Y]=meshgrid(x,y);
R=sqrt(X.^2+Y.^2);
%A=atan2(Y,X);
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
Z_phase_defoc=N_lambda*(R.^2-1/2); %defoc calculee
ihors_pupille=find(R>1.001);
Z_phase_defoc(ihors_pupille)=zeros(size(ihors_pupille));%masquage

     