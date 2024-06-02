function FTM_Zygo(phi,N_ouverture);
%%

%55555555  Calcul des PSF%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%if rep_menu_principal==5

%FFT calcule sur 512 x 512
Ne = 512;
%choix du zoom_psf
%1 : Ne = 512 N_Phi 256
%2 : Ne = 512 N_Phi 128
%3 : Ne = 512 N_Phi 64
%4 : Ne = 512 N_Phi 32
%5 : Ne = 512 N_Phi 16

%valeur par défaut 2
zoom_psf = 4;

val_def_echant    = {'512','4'}; %pour la boite de dialogue

%pour l'affichage x,y
Lambda = 632.8*1E-6 %en mm
Rayon_image=Lambda*N_ouverture;

re_calcul_tout=0;
%tant qu'on change pas la configuration echantillonnage
while  re_calcul_tout==0;

    retourne_menuP=0;   %quite la fonction PSF
    %obligatoire pour la fft


    %dimension de reechantillonge de phi
    N_Phi= Ne/(2^zoom_psf);
    Rapport_pupille_plan=Ne/N_Phi; %taille du cadre sur taille de la pupille
    %Rapport_pupille_plan = 2^zoom_psf
    %%%%%%%%%%On recupere la plus grande dimension de phi
    Dim_X = size(phi,2) ;
    Dim_Y = size(phi,1) ;

    %On reechantillonnne en gardant bien le rapport d'aspect
    if ( Dim_Y <= Dim_X)
        [xi,yi] = meshgrid(linspace(1,Dim_X,N_Phi),linspace(1,Dim_Y,round(N_Phi* Dim_Y/Dim_X)));
    elseif  ( Dim_Y > Dim_X)
        [xi,yi] = meshgrid(linspace(1,Dim_X,round(N_Phi* Dim_X/Dim_Y)),linspace(1,Dim_Y, N_Phi));
    end


    phi_N_phi = interp2(phi,xi,yi);
    %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%


    mask = ~isnan(phi_N_phi) ; %mask est la pupille parfait sans defaut de front d''onde

    phi_N_phi(isnan(phi_N_phi))=0 ; %transforme les NaN en 0

    Ampl_image_parfaite = fftshift(fft2(mask,Ne,Ne)) ; %fft avec zero padding pour la tache Airy
    Ampl_image = fftshift(fft2(mask.*exp(i*2*pi*phi_N_phi),Ne,Ne)) ;%fft avec zero padding pour la PSF ?2 *pi
    %clear phi mask Ampl_pupille ;
    PSF_parfaite = Ampl_image_parfaite.*conj(Ampl_image_parfaite) ;
    PSF_norm = Ampl_image.*conj(Ampl_image) ;

    PSF_norm = PSF_norm/(max(max(PSF_parfaite))) ; %Normalisation à la tache d'airy
    PSF_parfaite = PSF_parfaite/(max(max(PSF_parfaite))) ;

    %Rapport_de_Strelh=max(max(PSF_norm));
    %titre des PSF
    %str_Strehl=['PSF :        Strehl ratio =' num2str(Rapport_de_Strelh,3)];
    %PSF_OK=1;%psf calculé
    FTM=abs(fftshift(fft2(PSF_norm)));
    Max_FTM=max(max(FTM));
    FTM=FTM/Max_FTM;


    FTM_ideale=abs(fftshift(fft2(PSF_parfaite)));
    Max_FTM_ideale=max(max(FTM_ideale));
    FTM_ideale=FTM_ideale/Max_FTM_ideale;


    f_coupure=1/(Lambda*N_ouverture);
    x_freq_3D=(Rapport_pupille_plan /Ne)*f_coupure*(-round(Ne/Rapport_pupille_plan ):round(Ne/Rapport_pupille_plan ));
    x_freq=(Rapport_pupille_plan/Ne)*f_coupure*(0:round(Ne/Rapport_pupille_plan ));

    while  retourne_menuP==0;
        menu_FTM=menu('Menu FTM','FTM 3D','Coupe X','Coupe Y','FTM en présence de defoc','Configuration échantillonnage','Quitter menu FTM');
        %x_image=1e3*(Rayon_image/Rapport_pupille_plan )*(-Ne/2:+Ne/2-1); %axe de l'image echelle en microns
        %rotate3D off
        if menu_FTM==1
            figure('name','FTM')
            colormap('default')
            surf(x_freq_3D,x_freq_3D,FTM(round(Ne/2-Ne/Rapport_pupille_plan ):round(Ne/2+Ne/Rapport_pupille_plan ),round(Ne/2-Ne/Rapport_pupille_plan ):round(Ne/2+Ne/Rapport_pupille_plan )))
            xlabel(['mm^{-1}'])
            title(['FTM'])
            rotate3d

        end

        if menu_FTM==2
            figure('name','FTM coupe X')
            plot(x_freq,FTM(Ne/2+1,round(Ne/2+1):round(Ne/2+Ne/Rapport_pupille_plan )+1))
            hold on
            plot(x_freq,FTM_ideale(Ne/2+1,round(Ne/2+1):round(Ne/2+Ne/Rapport_pupille_plan )+1),'m--')
            hold off
            grid
            title(['FTM selon Ox'])
            xlabel(['mm^{-1}'])
            legend('FTM','FTM ideale',0);
        end

        if menu_FTM==3
             figure('name','FTM coupe Y')
            plot(x_freq,FTM(round(Ne/2+1):round(Ne/2+Ne/Rapport_pupille_plan )+1,Ne/2+1))
            hold on
            plot(x_freq,FTM_ideale(round(Ne/2+1):round(Ne/2+Ne/Rapport_pupille_plan )+1,Ne/2+1),'m--')
            hold off
            grid
            title(['FTM selon Oy'])
            xlabel(['mm^{-1}'])
            legend('FTM','FTM ideale',0);
        end


       % coupe quelconque
      
        if menu_FTM==4

            %FTM avec defoc
            prompt  = {'Défoc. maximum en mm, par rapport au meilleur foyer?:'};
            val_def     = {'1'};%mm
            titre_dialogue   = 'Défocalisation : delta Z';
            lineNo  = 1;
            reponse  = inputdlg(prompt,titre_dialogue,lineNo,val_def);



            if size(reponse,1)~=0
                delta_Z=str2num(reponse{1});
                ecart_normal=delta_Z*(1-cos(1/(2*N_ouverture)))/Lambda;%en lambda
            end
            figure('name','FTM avec défocalistion','position',[100 200 1000 400]);


            for Num_defoc=1:5
                 Defoc_en_lambda = ecart_normal*(Num_defoc-3)/2;%pas de ecart_normal/2 en lambda
                [Z_phase_defoc]=defoc_phase_map(mask,Defoc_en_lambda);
                phi_defocalise = phi_N_phi + Z_phase_defoc;

                %Ampl_image_parfaite = fftshift(fft2(mask,Ne,Ne)) ; %fft avec zero padding pour la tache Airy
                Ampl_image_defocalise = fftshift(fft2(mask.*exp(i*2*pi*phi_defocalise),Ne,Ne)) ;%fft avec zero padding pour la PSF ?2 *pi
                PSF_norm_defocalise = Ampl_image_defocalise.*conj(Ampl_image_defocalise) ;
                PSF_norm_defocalise = PSF_norm_defocalise/(max(max(PSF_parfaite))) ; %Normalisation à la tache d'airy


                %calcul de la ftm
                FTM_defocalise=abs(fftshift(fft2(PSF_norm_defocalise)));
                Max_FTM_defocalise=max(max(FTM_defocalise));
                FTM_defocalise=FTM_defocalise/Max_FTM_defocalise; %normalisation à 1


                %verticale
                subplot(2,5,Num_defoc)
                plot(x_freq,FTM_defocalise(round(Ne/2+1):round(Ne/2+Ne/Rapport_pupille_plan )+1,Ne/2+1))
                hold on
                plot(x_freq,FTM_ideale(round(Ne/2+1):round(Ne/2+Ne/Rapport_pupille_plan )+1,Ne/2+1),'m--')
                hold off
                grid
                %FTM horizontale
                subplot(2,5,5+Num_defoc)
                plot(x_freq,FTM_defocalise(Ne/2+1,round(Ne/2+1):round(Ne/2+Ne/Rapport_pupille_plan )+1))
                hold on
                plot(x_freq,FTM_ideale(Ne/2+1,round(Ne/2+1):round(Ne/2+Ne/Rapport_pupille_plan )+1),'m--')
                hold off
                grid
            end
            subplot(2,5,3)
            %delta_Z=(Lambda/4)/(1-cos(Rayon_pupille/foc));
            title([num2str(delta_Z/2,2) 'mm de défoc. entre plans images, soit un ecart normal :' num2str(ecart_normal/2,2) 'lambda'])
            xlabel(['coupe Y'])
            subplot(2,5,8)
            xlabel(['coupe X'])

        end






        %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

        if menu_FTM==5
            % configuration echantillonnage Ne et zoom_PSF
            prompt  = {'Nombre d''échantillons, Ne :128, 256, 512 ou 1024','Zoom de la PSF : 1, 2 , 3 , 4 ou 5 '};%
            %Rapport plan pupille = 2^zoom
            val_echant    =    val_def_echant;
            titre_dialogue   = 'Configuration de l''échantillonnage';
            lineNo  = 1;
            reponse  = inputdlg(prompt,titre_dialogue,lineNo,val_echant);
            val_def_echant =reponse;

            if size(reponse,1)~=0
                Ne=str2num(reponse{1});
                zoom_psf =str2num(reponse{2});
                %re_calcul_tout=1;
                retourne_menuP=1; %re_calcul_tout
            end

        end

        if menu_FTM==6
            re_calcul_tout=1;
            retourne_menuP=1;
        end
    end %menu PSF

end %recalcul tout

