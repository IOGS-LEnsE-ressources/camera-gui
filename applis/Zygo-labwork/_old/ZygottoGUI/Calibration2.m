function varargout = calibration2(varargin)
% calibration2 MATLAB code for calibration2.fig
%      calibration2, by itself, creates a new calibration2 or raises the existing
%      singleton*.
%
%      H = calibration2 returns the handle to a new calibration2 or the handle to
%      the existing singleton*.
%
%      calibration2('CALLBACK',hObject,eventData,handles,...) calls the local
%      function named CALLBACK in calibration2.M with the given input arguments.
%
%      calibration2('Property','Value',...) creates a new calibration2 or raises the
%      existing singleton*.  Starting from the left, property value pairs are
%      applied to the GUI before calibration2_OpeningFcn gets called.  An
%      unrecognized property name or invalid value makes property application
%      stop.  All inputs are passed to calibration2_OpeningFcn via varargin.
%
%      *See GUI Options on GUIDE's Tools menu.  Choose "GUI allows only one
%      instance to run (singleton)".
%
% See also: GUIDE, GUIDATA, GUIHANDLES

% Edit the above text to modify the response to help calibration2

% Last Modified by GUIDE v2.5 28-May-2015 16:21:39

% Begin initialization code - DO NOT EDIT
gui_Singleton = 1;
gui_State = struct('gui_Name',       mfilename, ...
                   'gui_Singleton',  gui_Singleton, ...
                   'gui_OpeningFcn', @calibration2_OpeningFcn, ...
                   'gui_OutputFcn',  @calibration2_OutputFcn, ...
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


% --- Executes just before calibration2 is made visible.
function calibration2_OpeningFcn(hObject, eventdata, handles, varargin)
% This function has no output args, see OutputFcn.
% hObject    handle to figure
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)
% varargin   command line arguments to calibration2 (see VARARGIN)
global o;
o=0;
global u;
u=0;
global k;
k=0;


% Choose default command line output for calibration2
handles.output = hObject;

% Update handles structure
guidata(hObject, handles);

% UIWAIT makes calibration2 wait for user response (see UIRESUME)
 %uiwait(handles.figure1);


% --- Outputs from this function are returned to the command line.
function varargout = calibration2_OutputFcn(hObject, eventdata, handles) 
% varargout  cell array for returning output args (see VARARGOUT);
% hObject    handle to figure
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

% Get default command line output from handles structure
varargout{1} = handles.output;


% --- Executes on button press in Bouton_Initialisation.
function Bouton_Initialisation_Callback(hObject, eventdata, handles)
% hObject    handle to Bouton_Initialisation (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)
global o;
switch (o)
    case (0)
handles.h=actxcontrol('UEYECAM.uEyeCamCtrl.1','position',[30 30 300 300]); % on crée l'objet pour la caméra
handles.h.InitCamera(0);
set(handles.Bouton_Initialisation,'String','Paramètres Caméra');

o=1;
guidata(hObject, handles);


    case(1)
       handles.h.PropertyDialog();
end


% --- Executes on button press in Image.
function Image_Callback(hObject, eventdata, handles)
% hObject    handle to Image (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

handles.h.SaveImage('Caméra.png'); % on enregistre l'image sur le disque dur
a=double(imread('Caméra.png'));
axes(handles.axes1);
imagesc(a),colorbar;





        


% --- Executes when uipanel1 is resized.
function uipanel1_ResizeFcn(hObject, eventdata, handles)
% hObject    handle to uipanel1 (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)


% --- Executes on button press in pushbutton7.
function pushbutton7_Callback(hObject, eventdata, handles)
% hObject    handle to pushbutton7 (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)
Vmin = 0 ;
Vmax = 5 ;
pas = 0.1 ;
nbechantillons = round((Vmax - Vmin)/pas)+1 ;
nbmesures = 1 ;

valeurs = zeros(nbmesures,nbechantillons) ;

wbar = waitbar(0,'calibration2 en cours...','color',[0.2 0.357 0.6],'name','Progression') ;
set(wbar,'CloseRequestFcn','return')
pause(0.5) ;



for k=1:nbmesures
    
    disp(['Mesure ',int2str(k),'/',int2str(nbmesures)]) ;
 
    handles.h.SaveImage('Test.png'); % on enregistre l'image sur le disque dur
    img=double(imread('Test.png'));
   
    i=1 ;
    
    clear Imgs ;
    
handles.h.SaveImage('Test.png'); % on enregistre l'image sur le disque dur
sizeimg=double(imread('Test.png'));
vert=size(sizeimg,1);
hor=size(sizeimg,2);

Imgs = zeros(vert,hor,nbechantillons+1) ;
    
    
    for V=Vmin:pas:Vmax
        Piezo(V);
        handles.h.SaveImage('Test.png'); % on enregistre l'image sur le disque dur
        Imgs(:,:,i)=double(imread('Test.png'));
        %figure
        %imagesc(double(imread('Test.png')));
        
        i=i+1 ;
        waitbar((k-1)/nbmesures+(V-Vmin)/(2*nbmesures * (Vmax-Vmin)),wbar) ;
    end
    
    Piezo(0) ;
   % for i=0:10
   %     Imgs = Imgs(200+i*10:300+i*10,200+i*10:300+i*10,:);
    %Img = Img(200:300,200:300) ;
  Imgs = Imgs(200:300,200:300,:) ;% VRAI TRUC PAS PIMS
%    %ASUPR PIMS
%     figure
%     imagesc(Imgs(:,:,11))
%     title('image11')
%     figure
%     imagesc(Imgs(:,:,22))
%     title('image22')
%     figure
%     imagesc(difference_images(Imgs(:,:,12),Imgs(:,:,11)));
%     title('différence')
% %FIN SUPR PIMS

    for j=11:nbechantillons %11:nbechantillons
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
%PIMS 
% for i=1:5
% temp=tensions_commande(1,i);
% plot(temp)
% hold on
% end

    %end
%end
save_config('calibpiezo_tensions',tensions_appliquees)
save_config('calibpiezo_valeurs',valeurs_moy)
save_config('Tensions',tensions_commande)

%hold on ; plot(tensions_commande,dephasages_commande,'m+') ; hold off
