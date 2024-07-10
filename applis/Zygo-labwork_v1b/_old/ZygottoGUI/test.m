function varargout = test(varargin)
% TEST M-file for test.fig
%      TEST, by itself, creates a new TEST or raises the existing
%      singleton*.
%
%      H = TEST returns the handle to a new TEST or the handle to
%      the existing singleton*.
%
%      TEST('CALLBACK',hObject,eventData,handles,...) calls the local
%      function named CALLBACK in TEST.M with the given input arguments.
%
%      TEST('Property','Value',...) creates a new TEST or raises the
%      existing singleton*.  Starting from the left, property value pairs are
%      applied to the GUI before test_OpeningFunction gets called.  An
%      unrecognized property name or invalid value makes property application
%      stop.  All inputs are passed to test_OpeningFcn via varargin.
%
%      *See GUI Options on GUIDE's Tools menu.  Choose "GUI allows only one
%      instance to run (singleton)".
%
% See also: GUIDE, GUIDATA, GUIHANDLES

% Edit the above text to modify the response to help test

% Last Modified by GUIDE v2.5 04-Apr-2007 13:51:32

%%
%--------------------------------------------------------------------------
% INITIALISATION
%--------------------------------------------------------------------------
% Begin initialization code - DO NOT EDIT
gui_Singleton = 1;
gui_State = struct('gui_Name',       mfilename, ...
    'gui_Singleton',  gui_Singleton, ...
    'gui_OpeningFcn', @test_OpeningFcn, ...
    'gui_OutputFcn',  @test_OutputFcn, ...
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
function test_OpeningFcn(hObject, eventdata, handles, varargin)
% Choose default command line output for test
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
        img = VideoSNAP;
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
handles.nbcont = 5;
%initialisation de la surface
handles.surface=[];
%initialisation du masque
handles.mask=[];
set(handles.txt_mask_value,'String','Automatique');
%initialisation des aberrations soustraites
handles.surface_absoustr=[];
handles.absoustr=[1 0 0 0 0 0 0 0 0];
%initialisation des coefficients de zernike
handles.coeff_zernike=zeros(1,37) ;

%affichage_imgvideo(handles);

%mise du fond des graphes en noir 
% set(handles.image_surface,'Color','black');

% Update handles structure
guidata(hObject, handles);



% --- Executes just before test is made visible.
function test_CreateFcn(hObject, eventdata, handles, varargin)
% This function has no output args, see OutputFcn.
% hObject    handle to figure
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)
% varargin   command line arguments to test (see VARARGIN)

function main_CreateFcn(hObject, eventdata, handles, varargin)

% --- Executes when main is resized.
function main_ResizeFcn(hObject, eventdata, handles)
% hObject    handle to main (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

% --- Outputs from this function are returned to the command line.
function varargout = test_OutputFcn(hObject, eventdata, handles)
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
function button_menu_calibpiezo_Callback(hObject, eventdata, handles)
valeurs=recherche_dephasage;


% --- Executes on button press in button_menu_calibgamma.
% -- Lance evaluation du gamma
function button_menu_calibgamma_Callback(hObject, eventdata, handles)
handles.gamma = evaluation_gamma;
guidata(hObject, handles);


% --- Executes on button press in push_config_valider.
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

% unite
a = 1 - get(handles.radio_config_lambda,'Value');
switch a
    case 0
        handles.unit = 1;
    case 1
        handles.unit = 632.8;
end
save_config('unite',handles.unit);

% N,F
handles.N = str2double(get(handles.edit_config_N,'string'));
handles.F = str2double(get(handles.edit_config_f,'string'));
save_config('N',handles.N);
save_config('F',handles.F);

% wedge factor
handles.wedge = str2double(get(handles.edit_config_wedgevalue,'string'));
save_config('wedge',handles.wedge);

guidata(hObject, handles);


% --- Executes on button press in push_config_parcourir.
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

function edit_config_wedgevalue_Callback(hObject, eventdata, handles)
% hObject    handle to edit_config_wedgevalue (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

% Hints: get(hObject,'String') returns contents of edit_config_wedgevalue as text
%        str2double(get(hObject,'String')) returns contents of edit_config_wedgevalue as a double
handles.wedge = str2double(get(handles.edit_config_wedgevalue,'string'));
save_config('wedge',handles.wedge);
set(handles.text_wedge_value,'String',num2str(handles.wedge));
guidata(hObject, handles);

% --- Executes during object creation, after setting all properties.
% --- champ de valeur du wedge value
function edit_config_wedgevalue_CreateFcn(hObject, eventdata, handles)
if ispc && isequal(get(hObject,'BackgroundColor'), get(0,'defaultUicontrolBackgroundColor'))
    set(hObject,'BackgroundColor','white');
end


% --- Executes on button press in push_config_gamma.
% --- bouton de calibration du gamma
function push_config_gamma_Callback(hObject, eventdata, handles)



% --- Executes on button press in push_config_piezo.
% --- bouton de calibration de la cale piezo
function push_config_piezo_Callback(hObject, eventdata, handles)


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

% --- Executes on button press in button_menu_masques.
% --- AFFICHAGE DU MENU MASQUES
function button_menu_masques_Callback(hObject, eventdata, handles)

% affichage du menu Masques
affichagemenu(handles.tousmenus,handles.menumasque);
% affichage d'une image video permettant la selection du masque
%affichage_imgvideo(handles);
% save
guidata(hObject, handles);


% --- Executes on button press in button_menu_maskcirc.
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

% --- Executes on button press in button_menu_maskpoly.
% --- SELECTION D'UN MASQUE POLYGONAL
function button_menu_maskpoly_Callback(hObject, eventdata, handles)
img = affichage_imgvideo(handles);

[img,mask]=mask_polygon(img);
% imagesc(img);
img_interf_NB=repmat(img/max(max(img)),[1,1,3]);
handles.img_interf_NB = img_interf_NB;
image(img_interf_NB);
handles.mask=mask;
set(handles.txt_mask_value,'String','Polygonal');
guidata(hObject,handles);

% --- Executes on button press in button_menu_automask.
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

% --- Executes on button press in button_menu_mesure.
% --- AFFICHAGE DU MENU DE MESURE et MISE A JOUR DE L'AFFICHAGE
function button_menu_mesure_Callback(hObject, eventdata, handles)
%affichage du menu de mesure
affichagemenu(handles.tousmenus,handles.menumesure);

%si une mesure a déjà été faite, les valeurs sont mises à jour (changement
%d'unité dans la configuration, p.ex)
phi=handles.surface_absoustr;
if(~isempty(phi))
    
    %mise à jour du graphe
    %axes(handles.image_surface);
    %updategraph(hObject,handles,phi);
    
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

%affichage du graphe
switch handles.typeplot
    case 1
        axis(handles.image_surface,'auto');
        grph=mesh(phi*handles.unit);set(grph,'ButtonDownFcn',{@image_surface_ButtonDownFcn, handles});view(-45,60)
        set(handles.image_surface,'Color','black','XColor','white', 'YColor','white', 'ZColor','white');
    case 2
        axis(handles.image_surface,'auto');
        [C,h]=contour(phi*handles.unit),axis ij,axis equal, colorbar;set(h,'HitTestArea','on');set(h,'ButtonDownFcn',{@image_surface_ButtonDownFcn, handles});
        set(handles.image_surface,'Color','black','XColor','white', 'YColor','white', 'ZColor','white');
    case 3
        grph=imagesc(phi*handles.unit);axis(handles.image_surface,'equal');
        handles.img_phi=grph;
        [px,py,p,xi,yi] = improfile;
        handles.profile_xi=xi;
        handles.profile_yi=yi;
        grph=plot(p);set(grph,'ButtonDownFcn',{@image_surface_ButtonDownFcn,handles});
        set(handles.image_surface,'Color','black','XColor','white', 'YColor','white', 'ZColor','white');
    case 4
        grph=imagesc(phi*handles.unit);axis(handles.image_surface,'equal');
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
figure('color',[0.2 0.357 0.6],'Name','Interférogrammes');
subplot(2,3,1,'Position',[0.05 0.5 0.3 0.5]);imshow(uint8(img1));
subplot(2,3,2,'Position',[0.36 0.5 0.3 0.5]);imshow(uint8(img2));
subplot(2,3,3,'Position',[0.67 0.5 0.3 0.5]);imshow(uint8(img3));
subplot(2,3,4,'Position',[0.05 0.1 0.3 0.5]);imshow(uint8(img4));
subplot(2,3,5,'Position',[0.36 0.1 0.3 0.5]);imshow(uint8(img5));


% --- Executes on button press in push_mesure_savephasemap.
% --- SAUVEGARDE LE PHASE MAP DANS UN FICHIER .MAT
function push_mesure_savephasemap_Callback(hObject, eventdata, handles)
% hObject    handle to push_mesure_savephasemap (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)
[FileName,PathName] = uiputfile('.mat');
surface_absoustr = handles.surface_absoustr;
save(strcat(PathName,FileName),'surface_absoustr');
guidata(hObject, handles);

% --- Executes on button press in push_mesure_saveimages.
% --- SAUVEGARDE LES IMAGES DANS UN FICHIER .MAT
function push_mesure_saveimages_Callback(hObject, eventdata, handles)
% hObject    handle to push_mesure_saveimages (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)
Imgs = cat(3,handles.img1,handles.img2,handles.img3,handles.img4,handles.img5);
[FileName,PathName] = uiputfile('.mat');
save(strcat(PathName,FileName),'Imgs');



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

    %%%%%%%%%%%%%%%?   zernike=zern(phi);

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

    zernike=zern(phi);

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

% --- Executes on mouse press over axes background.
function image_surface_ButtonDownFcn(src,eventdata, handles)
figure('color',[0.2 0.357 0.6],'name','Surface');
phi=handles.surface_absoustr*handles.unit;

PV_str=get(handles.valeur_pv,'string');
RMS_str=get(handles.valeur_rms,'string');

text=['Défaut du front d''onde :  PV : ' PV_str ' et     RMS : ' RMS_str]; 
switch handles.typeplot
    case {1}
        surfl(phi,[-45 70]);shading interp;colormap copper, view(-45,60)
       title(text)
            case {2}
        contour(phi,handles.nbcont),axis ij,axis equal, colorbar;
          title(text)
    case {3}
        p=improfile(phi,handles.profile_xi,handles.profile_yi)
        grph=plot(p);
          title(text)
end

% --- Executes during object creation, after setting all properties.
function image_surface_CreateFcn(hObject, eventdata, handles)




% --- Executes on selection change in typeplot.
function typeplot_Callback(hObject, eventdata, handles)
val = get(hObject,'Value');
phi=handles.surface_absoustr;
set(gca,'XLimMode','auto','YLimMode','auto');
axes(handles.image_surface);

switch val
    case 1

        set(handles.nbcontour,'Visible','off');
        handles.typeplot=1;
        if ~(isequal(phi,[]))
           grph=mesh(phi*handles.unit);
            set(grph,'ButtonDownFcn',{@image_surface_ButtonDownFcn,handles});
        end
        set(handles.image_surface,'Color','black','XColor','white', 'YColor','white', 'ZColor','white');
    case 2

        handles.typeplot=2;
        set(handles.nbcontour,'Visible','on');
        [C,h]=contour(phi,5),axis equal,colorbar;set(h,'HitTestArea','on');set(h,'ButtonDownFcn',{@image_surface_ButtonDownFcn, handles});
        val=get(handles.nbcontour,'Value')
        if(val~=1)
            [C,h]=contour(phi,handles.nbcont),axis ij,colorbar;set(h,'HitTestArea','on');set(h,'ButtonDownFcn',{@image_surface_ButtonDownFcn, handles});
        end
        set(handles.image_surface,'Color','black','XColor','white', 'YColor','white', 'ZColor','white');

    case 3

        handles.typeplot=3;
        set(handles.nbcontour,'Visible','off');
        if ~(isequal(phi,[]))
            view(2);
            imagesc(phi*handles.unit),axis equal;
            [px,py,p,xi,yi] = improfile;
            handles.profile_xi=xi;
            handles.profile_yi=yi;
            grph=plot(p);

            set(grph,'ButtonDownFcn',{@image_surface_ButtonDownFcn,handles});
            set(handles.image_surface,'Color','black','XColor','white', 'YColor','white', 'ZColor','white');
        end
    case 4
        set(handles.nbcontour,'Visible','off');
        grph=imagesc(phi*handles.unit);axis(handles.image_surface,'equal');
end

guidata(hObject, handles);



% --- Executes on selection change in nbcontour.
function nbcontour_Callback(hObject, eventdata, handles)
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
        [C,h]=contour(handles.surface_absoustr*handles.unit,handles.nbcont);
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


function updategraph(hObject,handles,phi)

switch handles.typeplot
    case 1
        grph=mesh(phi*handles.unit);set(grph,'ButtonDownFcn',{@image_surface_ButtonDownFcn, handles});
        set(handles.image_surface,'Color','black','XColor','white', 'YColor','white', 'ZColor','white');
    case 2

        [C,h]=contour(phi*handles.unit,handles.nbcont),axis equal,colorbar;
        set(h,'HitTestArea','on');set(h,'ButtonDownFcn',{@image_surface_ButtonDownFcn, handles});
        set(handles.image_surface,'Color','black','XColor','white', 'YColor','white', 'ZColor','white');
    case 3

        set(handles.nbcontour,'Visible','off');
        p=improfile(phi*handles.unit,handles.profile_xi,handles.profile_yi);
        grph=plot(p);set(grph,'ButtonDownFcn',{@image_surface_ButtonDownFcn,handles});
        set(handles.image_surface,'Color','black','XColor','white', 'YColor','white', 'ZColor','white');
    case 4
        set(handles.image_surface,'Color','black','XColor','white', 'YColor','white', 'ZColor','white');grph=imagesc(phi*handles.unit),axis equal;
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


function edit5_Callback(hObject, eventdata, handles)



% --- Executes during object creation, after setting all properties.
function edit5_CreateFcn(hObject, eventdata, handles)

if ispc && isequal(get(hObject,'BackgroundColor'), get(0,'defaultUicontrolBackgroundColor'))
    set(hObject,'BackgroundColor','white');
end

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


% --- Executes on button press in button_menu_PSF.
function button_menu_PSF_Callback(hObject, eventdata, handles)
PSF_Zygo(handles.surface_absoustr,handles.N);

% --- Executes on button press in button_menu_spotdiagram.
function button_menu_spotdiagram_Callback(hObject, eventdata, handles)

spot_diagram2(handles.surface_absoustr,handles.N,handles.F,3) ;


% --- Executes on button press in push_change_scale.
% Faut voir si on poursuit
function push_change_scale_Callback(hObject, eventdata, handles)
% hObject    handle to push_change_scale (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)
if(~isempty(handles.img_interf_NB))
    h = figure;
    image(handles.img_interf_NB);
    C = improfile;
    L = length(C);
    answer = inputdlg('Entrer la dimension correspondante (en mm) :')
    close(h);
    dimension = str2double(answer);
    handles.conversionechelle = dimension/L;
else
    errordlg('Aucune image à exploiter','Erreur de chargement de l''image');
end


% --- Executes on button press in radio_config_lambda.
function radio_config_lambda_Callback(hObject, eventdata, handles)
% hObject    handle to radio_config_lambda (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
 % handles    structure with handles and user data (see GUIDATA)

% Hint: get(hObject,'Value') returns toggle state of radio_config_lambda
handles.unit = 1;
save_config('unite',handles.unit);
guidata(hObject, handles);


% --- Executes on button press in radio_config_nano.
function radio_config_nano_Callback(hObject, eventdata, handles)
% hObject    handle to radio_config_nano (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

% Hint: get(hObject,'Value') returns toggle state of radio_config_nano
handles.unit = 632,8;
save_config('unite',handles.unit);
guidata(hObject, handles);



% --- Executes on button press in radio_config_acquisition.
function radio_config_acquisition_Callback(hObject, eventdata, handles)
% hObject    handle to radio_config_acquisition (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

% Hint: get(hObject,'Value') returns toggle state of radio_config_acquisition
handles.typeacq = 0;
save_config('typeacq',handles.typeacq);
guidata(hObject, handles);



% --- Executes on button press in radio_config_images.
function radio_config_images_Callback(hObject, eventdata, handles)
% hObject    handle to radio_config_images (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

% Hint: get(hObject,'Value') returns toggle state of radio_config_images
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
% hObject    handle to main (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)
clear handles;





% --- Executes on button press in button_print_zernike.
function button_print_zernike_Callback(hObject, eventdata, handles)
% hObject    handle to button_print_zernike (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)
figure('Resize','off','Color','white','Position',[20,200,700,450],'Name','Coefficients de Zernike');
coeff = zernike_imprimables(handles.coeff_zernike);
coeff=char(coeff);
uicontrol('style','text','BackgroundColor','white','HorizontalAlignment','left','Position',[0,0,700,450],'FontName','Monospaced','String',coeff);


% --- Executes on button press in bouton_print_seidel.
function bouton_print_seidel_Callback(hObject, eventdata, handles)
% hObject    handle to bouton_print_seidel (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)
figure('Resize','off','Color','white','Position',[20,200,700,450],'Name','Coefficients de Seidel');
coeff = seidel_imprimables(handles.coeff_zernike);
coeff=char(coeff);
uicontrol('style','text','BackgroundColor','white','HorizontalAlignment','left','Position',[0,0,700,450],'FontName','Monospaced','String',coeff);


% --- Executes on mouse press over axes background.
function image_video_ButtonDownFcn(hObject, eventdata, handles)
% hObject    handle to image_video (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)
figure('color',[0.2 0.357 0.6],'name','Interférogramme');
image(handles.img_interf_NB);


% --- Executes on button press in push_QUIT.
function push_QUIT_Callback(hObject, eventdata, handles)
% hObject    handle to push_QUIT (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)
clear handles ;
quit ;

