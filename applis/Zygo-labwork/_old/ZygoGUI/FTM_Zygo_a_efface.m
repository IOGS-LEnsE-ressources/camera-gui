   %6666666    Calcul FTM%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    if rep_menu_principal==6
        if PSF_OK==0 warndlg('Calculer la PSF d''abord!!','!! Warning !!')
        elseif PSF_OK==1
            retourne_menuP=0;
            %Calcul FTM

            FTM=abs(fftshift(fft2(PSF)));
            Max_FTM=max(max(FTM));
            FTM=FTM/Max_FTM;


            FTM_ideale=abs(fftshift(fft2(PSF_ideal)));
            Max_FTM_ideale=max(max(FTM_ideale));
            FTM_ideale=FTM_ideale/Max_FTM_ideale;


            f_coupure=1/(Lambda*foc/Diam_pupille);
            x_freq_3D=(Rapport_pupille_plan /Ne)*f_coupure*(-round(Ne/Rapport_pupille_plan ):round(Ne/Rapport_pupille_plan ));
            x_freq=(Rapport_pupille_plan/Ne)*f_coupure*(0:round(Ne/Rapport_pupille_plan ));

            while  retourne_menuP==0;
                menu_FTM=menu('Menu FTM','FTM 3D','Coupe X','Coupe Y','FTM en présence de defoc','Menu principal');
                %x_image=1e3*(Rayon_image/Rapport_pupille_plan )*(-Ne/2:+Ne/2-1); %axe de l'image echelle en microns
                rotate3D off
                if menu_FTM==1
                    colormap('default')
                    surf(x_freq_3D,x_freq_3D,FTM(round(Ne/2-Ne/Rapport_pupille_plan ):round(Ne/2+Ne/Rapport_pupille_plan ),round(Ne/2-Ne/Rapport_pupille_plan ):round(Ne/2+Ne/Rapport_pupille_plan )))
                    xlabel(['mm^{-1}'])
                    title(['FTM'])
                    rotate3D

                end
                if menu_FTM==3
                    plot(x_freq,FTM(round(Ne/2+1):round(Ne/2+Ne/Rapport_pupille_plan )+1,Ne/2+1))
                    hold on
                    plot(x_freq,FTM_ideale(round(Ne/2+1):round(Ne/2+Ne/Rapport_pupille_plan )+1,Ne/2+1),'m--')
                    hold off
                    title(['FTM selon Oy'])
                    xlabel(['mm^{-1}'])
                end

                if menu_FTM==2
                    plot(x_freq,FTM(Ne/2+1,round(Ne/2+1):round(Ne/2+Ne/Rapport_pupille_plan )+1))
                    hold on
                    plot(x_freq,FTM_ideale(Ne/2+1,round(Ne/2+1):round(Ne/2+Ne/Rapport_pupille_plan )+1),'m--')
                    hold off
                    title(['FTM selon Ox'])
                    xlabel(['mm^{-1}'])
                end

                if menu_FTM==4

                    %configuration echantillonage
                    prompt  = {'Défoc. maximum en mm, par rapport au meilleur foyer?:'};
                    val_def     = {'1'};%mm
                    titre_dialogue   = 'Défocalisation : delta Z';
                    lineNo  = 1;
                    reponse  = inputdlg(prompt,titre_dialogue,lineNo,val_def);

                    if size(reponse,1)~=0
                        delta_Z=str2num(reponse{1});
                        ecart_normal=delta_Z*(1-cos(Rayon_pupille/foc))/Lambda;%en lambda
                    end

                    for Num_defoc=1:5
                        Zern(1,4)= ecart_normal*(Num_defoc-3)/4;%pas de ecart_normal/2 en lambda /2 pour passer an Zernicke
                        [Z,Ampl]=calc_phase_map(Ne,Rapport_pupille_plan,Zern);
                        %calcul de l'amplitude dans le plan pupille
                        Ampl_image=fftshift(fft2(Ampl));
                        %calcul de l'intnsité dans le plan pupille
                        PSF=Ampl_image.*conj(Ampl_image);
                        Max_PSF=max(max(PSF));
                        PSF=PSF/Max_PSF;
                        %calcul de la ftm
                        FTM=abs(fftshift(fft2(PSF)));
                        Max_FTM=max(max(FTM));
                        FTM=FTM/Max_FTM;
                        subplot(2,5,Num_defoc)

                        plot(x_freq,FTM(round(Ne/2+1):round(Ne/2+Ne/Rapport_pupille_plan )+1,Ne/2+1))
                        hold on
                        plot(x_freq,FTM_ideale(round(Ne/2+1):round(Ne/2+Ne/Rapport_pupille_plan )+1,Ne/2+1),'m--')
                        hold off

                        subplot(2,5,5+Num_defoc)
                        plot(x_freq,FTM(Ne/2+1,round(Ne/2+1):round(Ne/2+Ne/Rapport_pupille_plan )+1))
                        hold on
                        plot(x_freq,FTM_ideale(Ne/2+1,round(Ne/2+1):round(Ne/2+Ne/Rapport_pupille_plan )+1),'m--')
                        hold off


                    end
                    subplot(2,5,3)
                    %delta_Z=(Lambda/4)/(1-cos(Rayon_pupille/foc));
                    title([num2str(delta_Z/2,2) 'mm de défoc. entre plans images, soit un ecart normal :' num2str(ecart_normal/2,2) 'lambda'])
                    xlabel(['coupe Y'])

                    subplot(2,5,8)
                    xlabel(['coupe X'])

                    Zern(1,4)=0;%on ramene defoc à zero
                    %on doit recalculer la PSF
                    [Z,Ampl]=calc_phase_map(Ne,Rapport_pupille_plan,Zern);
                    %calcul de l'amplitude dans le plan pupille
                    Ampl_image=fftshift(fft2(Ampl));
                    %calcul de l'intnsité dans le plan pupille
                    PSF=Ampl_image.*conj(Ampl_image);
                    Max_PSF=max(max(PSF));
                    PSF=PSF/Max_PSF;
                    Rapport_de_Strelh=Max_PSF/Max_PSF_ideal;
                end




                if menu_FTM==5
                    retourne_menuP=1;
                end
            end %du elseif
            PSF_OK=0;
            clear FTM,FTM_ideale;
        end %sous menu FTM
    end