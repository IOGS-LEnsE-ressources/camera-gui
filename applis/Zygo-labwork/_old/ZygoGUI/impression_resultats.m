%impression
function impression_resultats(img_interf_NB,phi,PV,RMS,echelle,unit,zernicke,typeacq,wedge,aberrations_soustraites);

PV_str=num2str(PV,3);
RMS_str=num2str(RMS,3);

Titre_text=['Défaut du front d''onde:  PV : ' PV_str ' et  RMS : ' RMS_str];
Entre_ligne_niveau=PV/20;

figure('Resize','off','Color','white','Position',[200,0,800,800],'Name','Utiliser Impression',...
    'PaperPosition',[1 1 18 27]);

subplot(3,2,1,'Position',[0.05 0.5 0.40 0.40]);image(img_interf_NB);axis image,xlabel('Premier interferogramme')

%%%%%Echelle en x et en y
x_image=linspace(0,size(phi,2)*echelle,size(phi,2));
y_image=linspace(0,size(phi,1)*echelle,size(phi,1));

subplot(2,2,2,'Position',[0.5 0.5 0.45 0.45])
contour(x_image,y_image,flipud(phi)*unit,20);axis image

  uicontrol('style','text','BackgroundColor','white','HorizontalAlignment',...
       'left','Position',[300,340,400,20],'FontName','Monospaced','String',Titre_text);
   
%title(Titre_text)
  uicontrol('style','text','BackgroundColor','white','HorizontalAlignment',...
       'left','Position',[400,370,400,20],'FontName','Monospaced','String',[num2str(PV/20,3) ' entre 2 lignes de niveau']);


%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
Wedge_factor_str= ['Wedge factor :  ' num2str(wedge)];
  uicontrol('style','text','BackgroundColor','white','HorizontalAlignment',...
       'left','Position',[50,350,150,10],'FontName','Monospaced','String',Wedge_factor_str);
   
aberrations_soustraites=aberrations_soustraites(aberrations_soustraites~=0);       
N_absoust=length(aberrations_soustraites);
str_ab_soustr=['termes soustraits : '];
if (N_absoust == 1), str_ab_soustr=[str_ab_soustr 'Piston'];
elseif (N_absoust == 3), str_ab_soustr=[str_ab_soustr 'Piston' ', Tilt'];
elseif (N_absoust == 4), str_ab_soustr=[str_ab_soustr 'Piston' ', Tilt' ',sphère'];
elseif (N_absoust == 6), str_ab_soustr=[str_ab_soustr 'Piston' ', Tilt', ', sphère',', Astig'];
elseif (N_absoust == 8), str_ab_soustr=[str_ab_soustr 'Piston' ', Tilt', ', sphère',', Astig.',',Coma'];
elseif (N_absoust == 9), str_ab_soustr=[str_ab_soustr 'Piston' ', Tilt' ', sphère' ', Astig.',', Ab. sphérique'];
end

uicontrol('style','text','BackgroundColor','white','HorizontalAlignment',...
       'left','Position',[400,300,350,30],'FontName','Monospaced','String',str_ab_soustr);
   
       
if typeacq==1
   % subplot(2,2,3,'Position',[0.05 0.05 0.40 0.40])
    set(gca,'visible','off')
    coeff = seidel_imprimables(zernicke);
    coeff=char(coeff);
    uicontrol('style','text','BackgroundColor','white','HorizontalAlignment','left',...
    'Position',[20,10,300,200],'FontName','Monospaced','String',coeff);
      %'PaperPosition',[0.634517 1.34517 20.3046 10.2284],
      
    %subplot(2,2,4,'Position',[0.5 0.05 0.40 0.40])
    set(gca,'visible','off')
    coeff = zernike_imprimables(zernicke);
    coeff=char(coeff);
    %text(0,0.5,coeff)
    uicontrol('style','text','BackgroundColor','white','HorizontalAlignment','left',...
           'Position',[300,10,500,250],'FontName','Monospaced','String',coeff);
            %'PaperPosition',[10.634517 1.34517 20.3046 10.2284],
end

