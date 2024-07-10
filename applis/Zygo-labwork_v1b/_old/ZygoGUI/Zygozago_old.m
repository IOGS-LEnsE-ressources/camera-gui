function varargout = Zygozago(varargin)

% Last Modified by GUIDE v2.5 16-Jul-2014 14:03:41

%%
%--------------------------------------------------------------------------
% INITIALISATION
%--------------------------------------------------------------------------
% Begin initialization code - DO NOT EDIT
gui_Singleton = 1;
gui_State = struct('gui_Name',       mfilename, ...
    'gui_Singleton',  gui_Singleton, ...
    'gui_OpeningFcn', @Zygozago_OpeningFcn, ...
    'gui_OutputFcn',  @Zygozago_OutputFcn, ...
    'gui_LayoutFcn',  [] , ...
    'gui_Callback',   []);
if nargin && ischar(varargin{1})
    gui_State.gui_Callback = str2func(varargin{1});
end

if nargout
    [varargout{1:nargout}] = gui_mainfcn(gui_State, varargin{:});
else
    gui_mainfcn(gui_State, varargin{:});
end
% End initialization code - DO NOT EDIT
%%
%--------------------------------------------------------------------------
% CREATION, OUVERTURE ET DESTRUCTION
%--------------------------------------------------------------------------
function Zygozago_OpeningFcn(hObject, eventdata, handles, varargin)
% Choose default command line output for Zygozago
handles.output = hObject;
% Update handles structure
guidata(hObject, handles);

% etude = 0 : etude de surface
% etude = 1 : etude d'aberrations
handles.etude = read_config('etude',0);
panel_surface=findobj('Tag','panel_infos_surface');
panel_aberrations=findobj('Tag','panel_infos_aberrations');
panel_NF=findobj('Tag','panel_infos_NF');
switch handles.etude
    case 0
        set(panel_surface,'Visible','on');
        set(panel_aberrations,'Visible','off');
        set(panel_NF,'Visible','off');
    case 1
        set(panel_surface,'Visible','off');
        set(panel_aberrations,'Visible','on');
        set(panel_NF,'Visible','on');
end


% N : ouverture, F: focale
handles.N = read_config('N',4);
handles.F = read_config('F',100);

set(handles.valeur_fnumber,'String',num2str(handles.N));
set(handles.valeur_focale,'String',num2str(handles.F));
set(handles.edit_config_N,'String',num2str(handles.N));
set(handles.edit_config_f,'String',num2str(handles.F));

% unit = 1 : lambda, =632.8 : nm
a = read_config('unit',0);
switch a
    case 0
        handles.unit = 1;
    case 1
        handles.unit = 632.8;
end

%gamma,wedge factor
handles.gamma = read_config('gamma',2.7);
set(handles.edit_config_gammavalue,'String',num2str(handles.gamma));
handles.wedge = read_config('wedge',0.5);
set(handles.edit_config_wedgevalue,'String',num2str(handles.wedge));
set(handles.text_wedge_value,'String',num2str(handles.wedge));

%typeacq = 0 : nouvelle acquisition
%typeacq = 1 : charger images existantes
handles.typeacq = read_config('typeacq',1);
handles.acqpath = read_config('acqpath','');

text_imgpath=findobj('Tag','text_config_imgpath');

handles.img_interf_NB = [];
%chargement des images si un chemin est specifie
if(handles.typeacq==1)
    if(exist(handles.acqpath))
        load(handles.acqpath);
        handles.img1=Imgs(:,:,1);
        handles.img2=Imgs(:,:,2);
        handles.img3=Imgs(:,:,3);
        handles.img4=Imgs(:,:,4);
        handles.img5=Imgs(:,:,5);

        img = handles.img1 ;
        handles.img_interf_NB = repmat(img/max(max(img)),[1,1,3]);
    else
        set(text_imgpath,'String','aucun fichier sélectionné');
        handles.img1=[];
        handles.img2=[];
        handles.img3=[];
        handles.img4=[];
        handles.img5=[];
    end
else
    img = videosnap();
    handles.img_interf_NB = repmat(img/max(max(img)),[1,1,3]);
    handles.img1=[];
    handles.img2=[];
    handles.img3=[];
    handles.img4=[];
    handles.img5=[];
end


%set(text_imgpath,'String','aucun fichier sélectionné');
if (strcmp(handles.acqpath,'')==0)
    set(text_imgpath,'String',handles.acqpath);
else
    set(text_imgpath,'String','aucun fichier sélectionné');
end

%definition des elements des menus
tousmenus=[
    'panel_config           ';
    'panel_resume           ';
    'panel_mesure           ';
    'image_video            ';
    'image_surface          ';
    'button_menu_maskcirc   ';
    'button_menu_maskpoly   ';
    'button_menu_annulmask  ';
    'button_menu_automask   ';
    'buttongroup_mask       ';
    'buttongroup_mesure     ';
    'button_menu_visuimg    ';
    'buttongroup_analyse    '
    ];
handles.tousmenus=cellstr(tousmenus);
menuconfig=['panel_config'];
handles.menuconfig=cellstr(menuconfig);
menumasque=[
    'button_menu_maskcirc ';
    'button_menu_maskpoly ';
    'button_menu_annulmask';
    'button_menu_automask ';
    'panel_mesure         ';
    'panel_resume         ';
    'buttongroup_mask     '
    ];
handles.menumasque=cellstr(menumasque);
menumesure=[
    'buttongroup_mesure ';
    'panel_mesure       ';
    'panel_resume       ';
    'button_menu_visuimg'
    ];
handles.menumesure=cellstr(menumesure);
menuanalyse=[
    'panel_mesure        ';
    'panel_resume        ';
    'buttongroup_analyse '
    ];
handles.menuanalyse=cellstr(menuanalyse);

%type de graphe de la surface
%1: mesh
%2:contour
%3:profil
handles.typeplot=1;
%nombre de lignes de contour par defaut
handles.nbcont = 20;
%initialisation de la surface
handles.surface=[];
%initialisation du masque
handles.mask=[];
set(handles.txt_mask_value,'String','Automatique');
%initialisation des aberrations soustraites
handles.surface_absoustr=[];
handles.absoustr=[1 0 0 0 0 0 0 0 0]; %piston soustrait
%initialisation des coefficients de zernike
handles.coeff_zernike=zeros(1,37) ;
%Echelle x y en pixel au depart
handles.conversionechelle=1;
%%%%%%%type d'etude par defaut
handles.etude=1;
% Update handles structure
guidata(hObject, handles);
% --- Executes just before Zygozago is made visible.
function Zygozago_CreateFcn(hObject, eventdata, handles, varargin)
% This function has no output args, see OutputFcn. Ne pas effacer
function main_CreateFcn(hObject, eventdata, handles, varargin)
% --- Executes when main is resized.
function main_ResizeFcn(hObject, eventdata, handles)
% hObject    handle to main (see GCBO)
% --- Outputs from this function are returned to the command line.
function varargout = Zygozago_OutputFcn(hObject, eventdata, handles)
% Get default command line output from handles structure
varargout{1} = handles.output;
%%
%--------------------------------------------------------------------------
%CONFIGURATION
%--------------------------------------------------------------------------

% --- Executes on button press in button_menu_config.
% --- Affichage du menu de configuration
function button_menu_config_Callback(hObject, eventdata, handles)

%masquage des axes et des graphes contenus
set(handles.image_surface,'visible','off');
img = get(handles.image_surface,'Children');
set(img,'visible','off');

set(handles.panel_config_calibrations,'visible','on');
%masquage autres menus et affichage du menu de config
affichagemenu(handles.tousmenus,handles.menuconfig);

%lecture de la config
handles.etude = read_config('etude',0);
set(handles.radio_config_surface,'Value',1-handles.etude);
set(handles.radio_config_aberrations,'Value',handles.etude);

handles.typeacq= read_config('typeacq',0);
set(handles.radio_config_acquisition,'Value',1-handles.typeacq);
set(handles.radio_config_images,'Value',handles.typeacq);

switch handles.unit
    case 632.8
        set(handles.radio_config_lambda,'Value',0);
        set(handles.radio_config_nano,'Value',1);
    case 1
        set(handles.radio_config_lambda,'Value',1);
        set(handles.radio_config_nano,'Value',0);
end
%save
guidata(hObject, handles);

% --- Executes on button press in button_calibpiezo.
% --- Lancement d'une calibration de la piezo
%%%%%%%%%%%%%%%%%%A
%%%%%%%%%%%%%%%%%%TESTER%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%%%%%%%%%%%%%%%%%%
function button_menu_calibpiezo_Callback(hObject, eventdata, handles)
valeurs=recherche_dephasage;

% --- Executes on button press in button_menu_calibgamma.
% -- Lance evaluation du gamma
function button_menu_calibgamma_Callback(hObject, eventdata, handles)
handles.gamma = evaluation_gamma;
guidata(hObject, handles);
%%%%%%%%%%%%%%%%%%%%NON FAIT%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%


% --- Executes on button press in push_config_gamma.
% --- bouton de calibration du gamma
function push_config_gamma_Callback(hObject, eventdata, handles)
% --- Executes on button press in push_config_piezo.
% --- bouton de calibration de la cale piezo

function push_config_piezo_Callback(hObject, eventdata, handles)

valeurs=recherche_dephasage;

%%%%%%%%%%%%%%%%%%%%%%%%%%%%Non fait%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%


% --- Sauvegarde de la configuration selectionnee
function push_config_valider_Callback(hObject, eventdata, handles)
% Lecture des boutons selectionnes, puis sauvegarde
% type d'etude
handles.etude = 1 - get(handles.radio_config_surface,'Value');
panel_surface=findobj('Tag','panel_infos_surface');
panel_aberrations=findobj('Tag','panel_infos_aberrations');
panel_NF=findobj('Tag','panel_infos_NF');
switch handles.etude
    case 0
        set(panel_surface,'Visible','on');
        set(panel_aberrations,'Visible','off');
        set(panel_NF,'Visible','off');
    case 1
        set(panel_surface,'Visible','off');
        set(panel_aberrations,'Visible','on');
        set(panel_NF,'Visible','on');
end
save_config('etude',handles.etude);

% type d'acquisition
handles.typeacq = 1 - get(handles.radio_config_acquisition,'Value');
save_config('typeacq',handles.typeacq);
save_config('acqpath',handles.acqpath);

% unite lambda ou nanometre
a = 1 - get(handles.radio_config_lambda,'Value');
switch a
    case 0
        handles.unit = 1;
    case 1
        handles.unit = 632.8;
end
save_config('unite',handles.unit);

% N,F N_ouverture et focale
handles.N = str2double(get(handles.edit_config_N,'string'));
handles.F = str2double(get(handles.edit_config_f,'string'));
save_config('N',handles.N);
save_config('F',handles.F);

% wedge factor
handles.wedge = str2double(get(handles.edit_config_wedgevalue,'string'));
save_config('wedge',handles.wedge);
guidata(hObject, handles);

% --- Ouvre une boîte de dialogue permettant de selectionner un fichier
function push_config_parcourir_Callback(hObject, eventdata, handles)
set(handles.radio_config_acquisition,'Value',0);
set(handles.radio_config_images,'Value',1);
% ouverture boite de dialogue permettant la selection d'un fichier .mat
[FileName,PathName] = uigetfile('*.mat');
% concatenation des chemin et nom de fichier
handles.acqpath = strcat(PathName,FileName);
% chargement du fichier choisi
S = load(handles.acqpath);
% affichage du chemin de fichier choisi
if (strcmp(handles.acqpath,'')==0)
    set(handles.text_config_imgpath,'String',handles.acqpath);
else
    set(handles.text_config_imgpath,'String','aucun fichier sélectionné');
end

%stockage du chemin dans le fichier de config
save_config('acqpath',handles.acqpath);
% stockage des images contenues par S dans la structure handle
handles.img1 = S.Imgs(:,:,1);
handles.img2 = S.Imgs(:,:,2);
handles.img3 = S.Imgs(:,:,3);
handles.img4 = S.Imgs(:,:,4);
handles.img5 = S.Imgs(:,:,5);
%save
guidata(hObject,handles);

%%%modif du wedge factor
function edit_config_wedgevalue_Callback(hObject, eventdata, handles)
handles.wedge = str2double(get(handles.edit_config_wedgevalue,'string'));
save_config('wedge',handles.wedge);
set(handles.text_wedge_value,'String',num2str(handles.wedge));
guidata(hObject, handles);

% --- champ de valeur du wedge value
function edit_config_wedgevalue_CreateFcn(hObject, eventdata, handles)
if ispc && isequal(get(hObject,'BackgroundColor'), get(0,'defaultUicontrolBackgroundColor'))
    set(hObject,'BackgroundColor','white');
end


% --- champ de valeur du nombre d'ouverture
% --- s'exécute par appui sur Enter
function edit_config_N_Callback(hObject, eventdata, handles)
handles.N = str2double(get(handles.edit_config_N,'string'));
save_config('N',handles.N);
set(handles.valeur_fnumber,'String',num2str(handles.N));
guidata(hObject, handles);


% --- Executes during object creation, after setting all properties.
% --- champ de valeur du nombre d'ouverture
function edit_config_N_CreateFcn(hObject, eventdata, handles)
if ispc && isequal(get(hObject,'BackgroundColor'), get(0,'defaultUicontrolBackgroundColor'))
    set(hObject,'BackgroundColor','white');
end

% --- champ de valeur du nombre d'ouverture
% --- s'exécute par appui sur Enter
function valeur_fnumber_Callback(hObject, eventdata, handles)
handles.N = str2double(get(handles.valeur_fnumber,'string'));
save_config('N',handles.N);
set(handles.edit_config_N,'String',num2str(handles.N));
guidata(hObject, handles);

% --- Executes during object creation, after setting all properties.
function valeur_fnumber_CreateFcn(hObject, eventdata, handles)

% --- champ de valeur de la focale (panneau de config)
% --- s'exécute par appui sur Enter
function edit_config_f_Callback(hObject, eventdata, handles)
handles.F = str2double(get(handles.edit_config_f,'string'));
save_config('F',handles.F);
set(handles.valeur_focale,'String',num2str(handles.F));
guidata(hObject, handles);

% --- Executes on button press in button_changescale.
% --- A FAIRE : permet de choisir l'échelle (pour une étude de surface)
function button_changescale_Callback(hObject, eventdata, handles)
%%%%%
% --Changement d'echelle en x et y
function push_change_scale_Callback(hObject, eventdata, handles)
% hObject    handle to push_change_scale (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)
if(~isempty(handles.img_interf_NB))
    h = figure('name','Tracer un ligne de longueur connue,par clique gauche ouis droit');
    imagesc(handles.surface_absoustr);
    axis image
    %choisit un profil dont oon indique la longueur en mm
    Long_pix = length(improfile);
    answer = inputdlg('Entrer la dimension correspondante (en mm) :')
    close(h);
    dimension = str2double(answer);
    handles.conversionechelle = dimension/Long_pix ;
    guidata(hObject, handles); %mise a jour pour les figures
else
    errordlg('Aucune image à exploiter','Erreur de chargement de l''image');
end

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%


% --- champ de valeur de la focale
% --- s'exécute par appui sur Enter
function valeur_focale_Callback(hObject, eventdata, handles)
handles.F = str2double(get(handles.valeur_focale,'string'));
save_config('F',handles.F);
set(handles.edit_config_f,'String',num2str(handles.F));
guidata(hObject, handles);

% --- champ de valeur de la focale
function valeur_focale_CreateFcn(hObject, eventdata, handles)
if ispc && isequal(get(hObject,'BackgroundColor'), get(0,'defaultUicontrolBackgroundColor'))
    set(hObject,'BackgroundColor','white');
end

% --- Executes on button press in radio_config_surface.
function radio_config_surface_Callback(hObject, eventdata, handles)
handles.etude = 0;
panel_surface=findobj('Tag','panel_infos_surface');
panel_aberrations=findobj('Tag','panel_infos_aberrations');
panel_NF=findobj('Tag','panel_infos_NF');
set(panel_surface,'Visible','on');
set(panel_aberrations,'Visible','off');
set(panel_NF,'Visible','off');
save_config('etude',handles.etude);
guidata(hObject, handles);

% --- Executes on button press in radio_config_surface.
function radio_config_aberrations_Callback(hObject, eventdata, handles)
handles.etude = 1;
panel_surface=findobj('Tag','panel_infos_surface');
panel_aberrations=findobj('Tag','panel_infos_aberrations');
panel_NF=findobj('Tag','panel_infos_NF');
set(panel_surface,'Visible','off');
set(panel_aberrations,'Visible','on');
set(panel_NF,'Visible','on');
save_config('etude',handles.etude);
guidata(hObject, handles);
%%
%--------------------------------------------------------------------------
%MASQUES
%--------------------------------------------------------------------------
% --- AFFICHAGE DU MENU MASQUES
function button_menu_masques_Callback(hObject, eventdata, handles)
% affichage du menu Masques
affichagemenu(handles.tousmenus,handles.menumasque);
set(handles.panel_config_calibrations,'visible','off');
% affichage d'une image video permettant la selection du masque
%affichage_imgvideo(handles);
% save
%%%%modif !!!guidata(hObject, handles);

% --- SELECTION D'UN MASQUE CIRCULAIRE
function button_menu_maskcirc_Callback(hObject, eventdata, handles)

% affichage de l'image video permettant la selection du masque
img = affichage_imgvideo(handles);
[img,mask]=mask_cercle(img);
% imagesc(img);
img_interf_NB=repmat(img/max(max(img)),[1,1,3]);
handles.img_interf_NB = img_interf_NB;
grph=image(img_interf_NB,'ButtonDownFcn',{@image_video_ButtonDownFcn, handles});
handles.mask=mask;
set(handles.txt_mask_value,'String','Circulaire');
guidata(hObject,handles);

% --- SELECTION D'UN MASQUE POLYGONAL
function button_menu_maskpoly_Callback(hObject, eventdata, handles)
img = affichage_imgvideo(handles);

[img,mask]=mask_polygon(img);

img_interf_NB=repmat(img/max(max(img)),[1,1,3]);
handles.img_interf_NB = img_interf_NB;
image(img_interf_NB);
handles.mask=mask;
set(handles.txt_mask_value,'String','Polygonal');
guidata(hObject,handles);

% --- CALCUL D'UN MASQUE AUTOMATIQUE
function button_menu_automask_Callback(hObject, eventdata, handles)
affichage_imgvideo(handles);
switch handles.typeacq
    case 0
        Imgs=acquisition_images;
        img1=Imgs(:,:,1);
        img2=Imgs(:,:,2);
        img3=Imgs(:,:,3);
        img4=Imgs(:,:,4);
        img5=Imgs(:,:,5);
    case 1
        img1 = handles.img1;
        img2 = handles.img2;
        img3 = handles.img3;
        img4 = handles.img4;
        img5 = handles.img5;

end

[img,mask]=mask_auto(img1,img2,img3,img4,img5);
imagesc(img);
img_interf_NB=repmat(img/max(max(img)),[1,1,3]);
handles.img_interf_NB = img_interf_NB;
image(img_interf_NB);
handles.mask = [];
guidata(hObject,handles);

% --- Executes on button press in button_menu_annulmask.
% --- REINITIALISE LE MASQUE
function button_menu_annulmask_Callback(hObject, eventdata, handles)

affichage_imgvideo(handles);
handles.mask=[];
set(handles.txt_mask_value,'String','Automatique');
guidata(hObject,handles);

%%
%--------------------------------------------------------------------------
%MESURES
%--------------------------------------------------------------------------

% --- AFFICHAGE DU MENU DE MESURE et MISE A JOUR DE L'AFFICHAGE
function button_menu_mesure_Callback(hObject, eventdata, handles)
%affichage du menu de mesure
affichagemenu(handles.tousmenus,handles.menumesure);
set(handles.panel_config_calibrations,'visible','off');

%si une mesure a déjà été faite, les valeurs sont mises à jour (changement
%d'unité dans la configuration, p.ex)
phi=handles.surface_absoustr;
if(~isempty(phi))
    %mise à jour PV et RMS
    [PV,RMS]=statistique_surface(phi*handles.unit) ;
    [stringPV, errmsg] = sprintf('%.3g',PV);
    [stringRMS, errmsg] = sprintf('%.3g',RMS);
    set(handles.valeur_pv,'string',stringPV) ;
    set(handles.valeur_rms,'string',stringRMS) ;
end
guidata(hObject, handles);

% --- Executes on button press in push_mesure_lancer.
% --- LANCE LE CALCUL DE MESURE DE PHASE SHIFT ET AFFICHE LE RESULTAT
function push_mesure_lancer_Callback(hObject, eventdata, handles)
%pause(1);
%acquisition ou definition des 5 images
switch handles.typeacq
    case 0
        Imgs=acquisition_images;

        Img1=Imgs(:,:,1);
        Img2=Imgs(:,:,2);
        Img3=Imgs(:,:,3);
        Img4=Imgs(:,:,4);
        Img5=Imgs(:,:,5);

        handles.img1 = Img1;
        handles.img2 = Img2;
        handles.img3 = Img3;
        handles.img4 = Img4;
        handles.img5 = Img5;

    case 1

        if (isempty(handles.mask))
            load(handles.acqpath);
            handles.img1=Imgs(:,:,1);
            handles.img2=Imgs(:,:,2);
            handles.img3=Imgs(:,:,3);
            handles.img4=Imgs(:,:,4);
            handles.img5=Imgs(:,:,5);
        end

        Img1 = handles.img1;
        Img2 = handles.img2;
        Img3 = handles.img3;
        Img4 = handles.img4;
        Img5 = handles.img5;

end

%phase shift
if (isempty(handles.mask))
    [img,handles.mask] = mask_auto(Img1,Img2,Img3,Img4,Img5) ;
end
[img_interf,phi]=phase_shift(Img1,Img2,Img3,Img4,Img5,handles.mask,handles.wedge);

%affichage de l'interferogramme n° 1
axes(handles.image_video);
img_interf=img_interf/max(max(img_interf));
img_interf_NB=repmat(img_interf/max(max(img_interf)),[1,1,3]);
handles.img_interf_NB = img_interf_NB;
image(img_interf_NB);axis image

%affichage front d'onde
axes(handles.image_surface);
handles.surface=phi;
set(gca,'Color','black');

%calcul des coefficients de Zernike
coeff_zernike=zern(phi) ;
handles.coeff_zernike=coeff_zernike ;

%soustraction des aberrations
absoustr = handles.absoustr ;
absoustr(2) = get(handles.check_absoustr_tilt,'Value') ;
absoustr(3) = get(handles.check_absoustr_tilt,'Value') ;
absoustr(4) = get(handles.check_absoustr_defocus,'Value') ;
absoustr(5) = get(handles.check_absoustr_astig,'Value') ;
absoustr(6) = get(handles.check_absoustr_astig,'Value') ;
absoustr(7) = get(handles.check_absoustr_coma,'Value') ;
absoustr(8) = get(handles.check_absoustr_coma,'Value') ;
absoustr(9) = get(handles.check_absoustr_abspher,'Value') ;
handles.absoustr = absoustr ;

phi= affichage_surface_2(phi,absoustr);
handles.surface_absoustr=phi ;
guidata(hObject, handles);

%%%%%Echelle en x et en y
x_image=linspace(0,size(phi,2)*handles.conversionechelle,size(phi,2));
y_image=linspace(0,size(phi,1)*handles.conversionechelle,size(phi,1));
%affichage du graphe
switch handles.typeplot
    case 1
       % axis(handles.image_surface,'auto');
        grph=mesh(x_image,y_image,flipud(phi)*handles.unit);set(grph,'ButtonDownFcn',{@image_surface_ButtonDownFcn, handles});view(-45,60)
        set(handles.image_surface,'Color','black','XColor','white', 'YColor','white', 'ZColor','white');
    case 2
       % axis(handles.image_surface,'auto');
        [C,h]=contour(flipud(phi)*handles.unit);,axis xy,axis equal, colorbar;set(h,'HitTestArea','on');set(h,'ButtonDownFcn',{@image_surface_ButtonDownFcn, handles});
        set(handles.image_surface,'Color','black','XColor','white', 'YColor','white', 'ZColor','white');
    case 3
        grph=imagesc(x_image,y_image,phi*handles.unit);axis(handles.image_surface,'equal');
        handles.img_phi=grph;
        [px,py,p,xi,yi] = improfile;
        handles.profile_xi=xi;
        handles.profile_yi=yi;
        grph=plot(linspace(0,size(p,1)*handles.conversionechelle,size(p,1)),p);set(grph,'ButtonDownFcn',{@image_surface_ButtonDownFcn,handles});
        set(handles.image_surface,'Color','black','XColor','white', 'YColor','white', 'ZColor','white');
        grid
    case 4
        grph=imagesc(x_image,y_image,phi*handles.unit);axis(handles.image_surface,'equal');
        set(handles.image_surface,'Color','black','XColor','white', 'YColor','white', 'ZColor','white');
end

%calcul des PV et RMS
[PV,RMS]=statistique_surface(phi*handles.unit) ;
[stringPV, errmsg] = sprintf('%.3g',PV);
[stringRMS, errmsg] = sprintf('%.3g',RMS);
set(handles.valeur_pv,'string',stringPV) ;
set(handles.valeur_rms,'string',stringRMS) ;

%affichage Seidel et Zernike
seidel = get(handles.panel_aff_seidel,'visible');
zernike = get(handles.panel_aff_zernike,'visible');

if strcmp(seidel,'on')==1
    affichage_seidel(handles,coeff_zernike);
end
if strcmp(zernike,'on')==1
    affichage_zernike(handles,coeff_zernike);
end

guidata(hObject, handles);


% --- Executes on button press in push_mesure_visuimg.
% --- AFFICHAGE DES IMAGES ACQUISES DANS UNE NOUVELLE FENETRE
function push_mesure_visuimg_Callback(hObject, eventdata, handles)
img1=handles.img1;
img2=handles.img2;
img3=handles.img3;
img4=handles.img4;
img5=handles.img5;
img_moyenne=(img1+img2+img3+img4)/4;
figure('color',[0.2 0.357 0.6],'Name','Interférogrammes');
subplot(2,3,1,'Position',[0.05 0.6 0.3 0.4]);imshow(uint8(img1));Xlabel('Premier interferogramme')
subplot(2,3,2,'Position',[0.36 0.6 0.3 0.4]);imshow(uint8(img2));Xlabel('Déphasage de 90°')
subplot(2,3,3,'Position',[0.67 0.6 0.3 0.4]);imshow(uint8(img3));Xlabel('Déphasage de 180°')
subplot(2,3,4,'Position',[0.05 0.1 0.3 0.4]);imshow(uint8(img4));Xlabel('Déphasage de 270°')
subplot(2,3,5,'Position',[0.36 0.1 0.3 0.4]);imshow(uint8(img5));Xlabel('Déphasage de 360°')
subplot(2,3,6,'Position',[0.67 0.1 0.3 0.4]);imshow(uint8(img_moyenne));Xlabel('moyenne de 4 images')

% --- Executes on button press in push_mesure_saveimages.
% --- SAUVEGARDE LE PHASE MAP DANS UN FICHIER .MAT
function push_mesure_savephasemap_Callback(hObject, eventdata, handles)
[FileName,PathName] = uiputfile('.mat');
surface_absoustr = handles.surface_absoustr;
save(strcat(PathName,FileName),'surface_absoustr');
guidata(hObject, handles);

% --- Executes on button press in push_mesure_saveimages.
% --- SAUVEGARDE LES IMAGES DANS UN FICHIER .MAT
function push_mesure_saveimages_Callback(hObject, eventdata, handles)

Imgs = cat(3,handles.img1,handles.img2,handles.img3,handles.img4,handles.img5);
[FileName,PathName] = uiputfile('.mat');
save(strcat(PathName,FileName),'Imgs'); %%%%%sauve les 5 images en .mat
fichier_jpg=[strcat(PathName,FileName) '.jpg'];
imwrite(uint8(handles.img1),fichier_jpg,'jpg');%%%%%%%%%sauve le premier interfero en jpg

%%
%--------------------------------------------------------------------------
%SOUSTRACTION ABERRATIONS
%--------------------------------------------------------------------------

%TILT
% --- Executes on button press in check_absoustr_tilt.
function check_absoustr_tilt_Callback(hObject, eventdata, handles)
% Hint: get(hObject,'Value') returns toggle state of check_absoustr_tilt

absoustr = handles.absoustr ;
phi=handles.surface;

if ~(isequal(phi,[]))
    coeff_zernike=handles.coeff_zernike;
    absoustr(2) = get(handles.check_absoustr_tilt,'Value') ;
    absoustr(3) = get(handles.check_absoustr_tilt,'Value') ;
    handles.absoustr=absoustr ;
    phi= affichage_surface_2(phi,absoustr);
    handles.surface_absoustr=phi;
    axes(handles.image_surface);
    guidata(hObject, handles);
    updategraph(hObject,handles,phi);
    [PV,RMS]=statistique_surface(phi*handles.unit) ;
    set(handles.valeur_pv,'string',num2str(PV,'%0.3g')) ;
    set(handles.valeur_rms,'string',num2str(RMS,'%0.3g')) ;
    guidata(hObject, handles);
end

%DEFOCUS
% --- Executes on button press in check_absoustr_defocus.
function check_absoustr_defocus_Callback(hObject, eventdata, handles)
absoustr = handles.absoustr ;
phi=handles.surface;

if ~(isequal(phi,[]))
    coeff_zernike=handles.coeff_zernike;
    absoustr(4) = get(handles.check_absoustr_defocus,'Value') ;
    handles.absoustr=absoustr ;
    phi= affichage_surface_2(phi,absoustr);
    handles.surface_absoustr=phi;
    axes(handles.image_surface);
    guidata(hObject, handles);
    updategraph(hObject,handles,phi);
    [PV,RMS]=statistique_surface(phi*handles.unit) ;
    set(handles.valeur_pv,'string',num2str(PV,'%0.3g')) ;
    set(handles.valeur_rms,'string',num2str(RMS,'%0.3g')) ;
   % zernike=zern(phi);
    guidata(hObject, handles);
end

%ABERRATION SPHERIQUE
% --- Executes on button press in check_absoustr_abspher.
function check_absoustr_abspher_Callback(hObject, eventdata, handles)
% Hint: get(hObject,'Value') returns toggle state of check_absoustr_abspher
absoustr = handles.absoustr ;
phi=handles.surface;
if ~(isequal(phi,[]))
    coeff_zernike=handles.coeff_zernike;
    absoustr(9) = get(handles.check_absoustr_abspher,'Value') ;
    handles.absoustr=absoustr ;
    phi= affichage_surface_2(phi,absoustr);
    handles.surface_absoustr=phi;
    axes(handles.image_surface);
    guidata(hObject, handles);
    updategraph(hObject,handles,phi);
    [PV,RMS]=statistique_surface(phi*handles.unit) ;
    set(handles.valeur_pv,'string',num2str(PV,'%0.3g')) ;
    set(handles.valeur_rms,'string',num2str(RMS,'%0.3g')) ;
    guidata(hObject, handles);
end

%ASTIGMATISME
% --- Executes on button press in check_absoustr_astig.
function check_absoustr_astig_Callback(hObject, eventdata, handles)
absoustr = handles.absoustr ;
phi=handles.surface;

if ~(isequal(phi,[]))
    coeff_zernike=handles.coeff_zernike;
    absoustr(5) = get(handles.check_absoustr_astig,'Value') ;
    absoustr(6) = get(handles.check_absoustr_astig,'Value') ;
    handles.absoustr=absoustr ;
    phi= affichage_surface_2(phi,absoustr);
    handles.surface_absoustr=phi;
    axes(handles.image_surface);
    guidata(hObject, handles);
    updategraph(hObject,handles,phi);
    [PV,RMS]=statistique_surface(phi*handles.unit) ;
    set(handles.valeur_pv,'string',num2str(PV,'%0.3g')) ;
    set(handles.valeur_rms,'string',num2str(RMS,'%0.3g')) ;
    guidata(hObject, handles);
end

%COMA
% --- Executes on button press in check_absoustr_coma.
function check_absoustr_coma_Callback(hObject, eventdata, handles)
absoustr = handles.absoustr ;
phi=handles.surface;
coeff_zernike=handles.coeff_zernike;
absoustr(7) = get(handles.check_absoustr_coma,'Value') ;
absoustr(8) = get(handles.check_absoustr_coma,'Value') ;
handles.absoustr=absoustr ;
phi= affichage_surface_2(phi,absoustr);
handles.surface_absoustr=phi;
axes(handles.image_surface);
guidata(hObject, handles);
updategraph(hObject,handles,phi);
[PV,RMS]=statistique_surface(phi*handles.unit) ;
set(handles.valeur_pv,'string',num2str(PV,'%0.3g')) ;
set(handles.valeur_rms,'string',num2str(RMS,'%0.3g')) ;
guidata(hObject, handles);
%%
%--------------------------------------------------------------------------
% GRAPHIQUES
%--------------------------------------------------------------------------

% --- Click sur la figure ouvre une nouvelle fenetre pour grande figure
% imprimable
function image_surface_ButtonDownFcn(src,eventdata, handles)
figure('color',[0.2 0.357 0.6],'name','Surface');
phi=handles.surface_absoustr*handles.unit;
PV_str=get(handles.valeur_pv,'string');
RMS_str=get(handles.valeur_rms,'string');
Titre_text=['Défaut du front d''onde :  PV : ' PV_str ' et     RMS : ' RMS_str];

%%%%%Echelle en x et en y
x_image=linspace(0,size(phi,2)*handles.conversionechelle,size(phi,2));
y_image=linspace(0,size(phi,1)*handles.conversionechelle,size(phi,1));

switch handles.typeplot
    case {1}
        surfl(x_image,y_image,flipud(phi),[-45 70]);shading interp;colormap copper, view(-45,60)
        title(Titre_text)
    case {2}
        contour(x_image,y_image,flipud(phi),handles.nbcont);,axis ij,axis equal, colorbar;
        title(Titre_text)
    case {3}
        p=improfile(phi,handles.profile_xi,handles.profile_yi)
        grph=plot(linspace(0,size(p,1)*handles.conversionechelle,size(p,1)),p);grid
        title(Titre_text)
    
end

% --- Executes during object creation, after setting all properties.
function image_surface_CreateFcn(hObject, eventdata, handles)

% --- 4 types d'affichage du front d'onde------------
function typeplot_Callback(hObject, eventdata, handles)
val = get(hObject,'Value');
phi=handles.surface_absoustr;
set(gca,'XLimMode','auto','YLimMode','auto');
axes(handles.image_surface);

%%%%%Echelle en x et en y
x_image=linspace(0,size(phi,2)*handles.conversionechelle,size(phi,2));
y_image=linspace(0,size(phi,1)*handles.conversionechelle,size(phi,1));

switch val
    case 1
        set(handles.nbcontour,'Visible','off');
        handles.typeplot=1;
        if ~(isequal(phi,[]))
            grph=mesh(x_image,y_image,flipud(phi)*handles.unit);view(-45,60)
            set(grph,'ButtonDownFcn',{@image_surface_ButtonDownFcn,handles});
        end
        set(handles.image_surface,'Color','black','XColor','white', 'YColor','white', 'ZColor','white');
    case 2
        handles.typeplot=2;
        set(handles.nbcontour,'Visible','on');
        [C,h]=contour(x_image,y_image,flipud(phi),20);,axis equal,colorbar;set(h,'HitTestArea','on');set(h,'ButtonDownFcn',{@image_surface_ButtonDownFcn, handles});
        val=get(handles.nbcontour,'Value')
        if(val~=1)
            [C,h]=contour(flipud(phi),handles.nbcont);,axis ij,colorbar;set(h,'HitTestArea','on');set(h,'ButtonDownFcn',{@image_surface_ButtonDownFcn, handles});
        end
        set(handles.image_surface,'Color','black','XColor','white', 'YColor','white', 'ZColor','white');
    case 3
        handles.typeplot=3;
        set(handles.nbcontour,'Visible','off');
        if ~(isequal(phi,[]))
            view(2);
            imagesc(x_image,y_image,phi*handles.unit),axis equal;
            [px,py,p,xi,yi] = improfile;
            handles.profile_xi=xi;
            handles.profile_yi=yi;
             grph=plot(linspace(0,size(p,1)*handles.conversionechelle,size(p,1)),p)
            set(grph,'ButtonDownFcn',{@image_surface_ButtonDownFcn,handles});
            set(handles.image_surface,'Color','black','XColor','white', 'YColor','white', 'ZColor','white');
            grid
        end
    case 4
        set(handles.nbcontour,'Visible','off');
        grph=imagesc(x_image,y_image,phi*handles.unit);axis(handles.image_surface,'equal');
         set(handles.image_surface,'Color','black','XColor','white', 'YColor','white', 'ZColor','white');
end
guidata(hObject, handles);

% --- Executes on selection change in nbcontour.
function nbcontour_Callback(hObject, eventdata, handles)
phi=handles.surface_absoustr;
%%%%%Echelle en x et en y
x_image=linspace(0,size(phi,2)*handles.conversionechelle,size(phi,2));
y_image=linspace(0,size(phi,1)*handles.conversionechelle,size(phi,1));
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
if ~(isequal(handles.surface_absoustr,[]))
    val=get(hObject,'Value');
    switch val
        case 2
            handles.nbcont=5;
        case 3
            handles.nbcont=10;
        case 4
            handles.nbcont=15;
        case 5
            handles.nbcont=20;
    end
    if(handles.typeplot==2)
        [C,h]=contour(x_image,y_image,handles.surface_absoustr*handles.unit,handles.nbcont);
        set(h,'HitTestArea','on'), axis ij,axis equal, colorbar;set(h,'ButtonDownFcn',{@image_surface_ButtonDownFcn, handles});
        set(handles.image_surface,'Color','black','XColor','white', 'YColor','white', 'ZColor','white');
    end
end
guidata(hObject, handles);

% --- Executes during object creation, after setting all properties.
function nbcontour_CreateFcn(hObject, eventdata, handles)
if ispc && isequal(get(hObject,'BackgroundColor'), get(0,'defaultUicontrolBackgroundColor'))
    set(hObject,'BackgroundColor','white');
end

%%%%%%%mise a jour des fronts d onde
function updategraph(hObject,handles,phi)

%%%%%Echelle en x et en y
x_image=linspace(0,size(phi,2)*handles.conversionechelle,size(phi,2));
y_image=linspace(0,size(phi,1)*handles.conversionechelle,size(phi,1));

switch handles.typeplot
    case 1
        grph=mesh(x_image,y_image,flipud(phi)*handles.unit);set(grph,'ButtonDownFcn',{@image_surface_ButtonDownFcn, handles});view(-45,60)
        set(handles.image_surface,'Color','black','XColor','white', 'YColor','white', 'ZColor','white');
    case 2

        [C,h]=contour(x_image,y_image,flipud(phi)*handles.unit,handles.nbcont);,axis equal,colorbar;
        set(h,'HitTestArea','on');set(h,'ButtonDownFcn',{@image_surface_ButtonDownFcn, handles});
        set(handles.image_surface,'Color','black','XColor','white', 'YColor','white', 'ZColor','white');
    case 3

        set(handles.nbcontour,'Visible','off');
        p=improfile(phi*handles.unit,handles.profile_xi,handles.profile_yi);
        grph=plot(linspace(0,size(p,1)*handles.conversionechelle,size(p,1)),p);set(grph,'ButtonDownFcn',{@image_surface_ButtonDownFcn,handles});
        set(handles.image_surface,'Color','black','XColor','white', 'YColor','white', 'ZColor','white');
        grid
    case 4
        set(handles.image_surface,'Color','black','XColor','white', 'YColor','white', 'ZColor','white');
        grph=imagesc(x_image,y_image,phi*handles.unit),axis equal;
end
guidata(hObject, handles);

% --- Executes during object creation, after setting all properties.
function typeplot_CreateFcn(hObject, eventdata, handles)
if ispc && isequal(get(hObject,'BackgroundColor'), get(0,'defaultUicontrolBackgroundColor'))
    set(hObject,'BackgroundColor','white');
end
%%
%--------------------------------------------------------------------------
% ANALYSE
%--------------------------------------------------------------------------
% --- Executes on button press in button_menu_analyse.
function button_menu_analyse_Callback(hObject, eventdata, handles)
affichagemenu(handles.tousmenus,handles.menuanalyse);
set(handles.panel_config_calibrations,'visible','off');
%masquage autres menus et affichage du menu de config
% --- Executes on button press in button_menu_seidel.
function button_menu_seidel_Callback(hObject, eventdata, handles)
zernike=handles.coeff_zernike;
affichage_seidel(handles, zernike);
set(handles.panel_aff_seidel,'visible','on');
guidata(hObject, handles);

% --- Executes on button press in button_menu_zernike.
function button_menu_zernike_Callback(hObject, eventdata, handles)
zernike=handles.coeff_zernike;
affichage_zernike(handles,zernike);
set(handles.panel_aff_zernike,'visible','on');
guidata(hObject, handles);

%%%%%%%%%%%%%%%%%%%%%%Je sais pas a quoi ca sert!%
function edit5_Callback(hObject, eventdata, handles)
% --- Executes during object creation, after setting all properties.
function edit5_CreateFcn(hObject, eventdata, handles)
if ispc && isequal(get(hObject,'BackgroundColor'), get(0,'defaultUicontrolBackgroundColor'))
    set(hObject,'BackgroundColor','white');
end
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

% --- Executes on button press in button_close_seidel.
function button_close_seidel_Callback(hObject, eventdata, handles)
set(handles.panel_aff_seidel,'visible','off');
guidata(hObject, handles);

% --- Executes on button press in button_close_zernike.
function button_close_zernike_Callback(hObject, eventdata, handles)
set(handles.panel_aff_zernike,'visible','off');
guidata(hObject, handles);

% --- Executes on button press in check_absoustr_defocus.
function check_absoustr_defoc_Callback(hObject, eventdata, handles)

% --- Executes during object creation, after setting all properties.
function valeur_seidel_ampltilt_CreateFcn(hObject, eventdata, handles)

% --- Executes on button press in button_menu_spotdiagram.
function button_menu_spotdiagram_Callback(hObject, eventdata, handles)
spot_diagram3(handles.surface_absoustr,handles.N,handles.F,50) ;


% --- Executes on button press in button_menu_PSF.
function button_menu_PSF_Callback(hObject, eventdata, handles)
PSF_Zygo(handles.surface_absoustr,handles.N);

% --- Executes on button press in pushbuttonFTM.
function pushbuttonFTM_Callback(hObject, eventdata, handles)
FTM_Zygo(handles.surface_absoustr,handles.N);




% --- Executes on button press in radio_config_lambda.
function radio_config_lambda_Callback(hObject, eventdata, handles)
handles.unit = 1;
save_config('unite',handles.unit);
guidata(hObject, handles);

% --- Executes on button press in radio_config_nano.
function radio_config_nano_Callback(hObject, eventdata, handles)
% Hint: get(hObject,'Value') returns toggle state of radio_config_nano
handles.unit = 632,8;
save_config('unite',handles.unit);
guidata(hObject, handles);

% --- Executes on button press in radio_config_acquisition.
function radio_config_acquisition_Callback(hObject, eventdata, handles)

handles.typeacq = 0;
save_config('typeacq',handles.typeacq);
guidata(hObject, handles);

% --- Executes on button press in radio_config_images.
function radio_config_images_Callback(hObject, eventdata, handles)
handles.typeacq = 1;
save_config('typeacq',handles.typeacq);
text_imgpath=findobj('Tag','text_config_imgpath');
if(exist(handles.acqpath)~=0)
    set(text_imgpath,'String',handles.acqpath);
    load(handles.acqpath);
    handles.img1=Imgs(:,:,1);
    handles.img2=Imgs(:,:,2);
    handles.img3=Imgs(:,:,3);
    handles.img4=Imgs(:,:,4);
    handles.img5=Imgs(:,:,5);
else
    set(text_imgpath,'String','aucun fichier sélectionné');
    handles.img1=[];
    handles.img2=[];
    handles.img3=[];
    handles.img4=[];
    handles.img5=[];
end
guidata(hObject, handles);

% --- Executes during object deletion, before destroying properties.
function main_DeleteFcn(hObject, eventdata, handles)
%guide : ne pas effacer
clear handles;


% --- Executes on button press in bouton_print.
function bouton_print_Callback(hObject, eventdata, handles)

set(handles.panel_config_calibrations,'visible','off');
img_interf_NB=handles.img_interf_NB;
phi=handles.surface_absoustr;
[PV,RMS]=statistique_surface(phi*handles.unit) ;

impression_resultats(img_interf_NB,phi,PV,RMS,handles.conversionechelle,handles.unit,handles.coeff_zernike,handles.etude,handles.wedge,handles.absoustr);


% --- Executes on mouse press over axes background.
function image_video_ButtonDownFcn(hObject, eventdata, handles)
figure('color',[0.2 0.357 0.6],'name','Interferogramme');
image(handles.img_interf_NB);

% ---Quitter
function push_QUIT_Callback(hObject, eventdata, handles)
% hObject    handle to push_QUIT (see GCBO)
clear all ;
close all


% --- Executes during object creation, after setting all properties.
function buttongroup_mask_CreateFcn(hObject, eventdata, handles)
%ne pas effacer


% --- Executes during object creation, after setting all properties.
function text114_CreateFcn(hObject, eventdata, handles)
%texte : cliquer sur la figure pour agrandir






% --- Executes on selection change in popupmenu4.
function popupmenu4_Callback(hObject, eventdata, handles)
% hObject    handle to popupmenu4 (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

% Hints: contents = get(hObject,'String') returns popupmenu4 contents as cell array
%        contents{get(hObject,'Value')} returns selected item from popupmenu4


% --- Executes during object creation, after setting all properties.
function popupmenu4_CreateFcn(hObject, eventdata, handles)
% hObject    handle to popupmenu4 (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    empty - handles not created until after all CreateFcns called

% Hint: popupmenu controls usually have a white background on Windows.
%       See ISPC and COMPUTER.
if ispc && isequal(get(hObject,'BackgroundColor'), get(0,'defaultUicontrolBackgroundColor'))
    set(hObject,'BackgroundColor','white');
end


