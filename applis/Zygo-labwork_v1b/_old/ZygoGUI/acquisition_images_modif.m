function Imgs = acquisition_images(handles);

methode = 1;
N = 5 ; 
theta = 90 ;

pas = 0.1 ;

%tensions_commande = calcul_tensions(N, theta) 

%Modif Lionel 17 nov 2010

%tensions_commande =     [1.0856    2.6236    3.9753    4.0801    5.4728    6.8658];
%UNe bonne configuration : la calibration est délicate
%save_config('Tensions', [0.8800085464131472	2.5642937425811096	2.962996790165622	4.891736357553595	5.856024629071319]);
save_config('Tensions', [0.5 1.5 2.5 3.5 4.9]);
tensions_commande=read_config('Tensions',1);
%     handles.h=actxcontrol('UEYECAM.uEyeCamCtrl.1','position',[330 338 235 235]); % on crée l'objet pour la caméra
%     handles.h.InitCamera(0);
    handles.h.SaveImage('Caméra1.png'); % on enregistre l'image sur le disque dur
    sizeimg=double(imread('Caméra1.png'));

%sizeimg=videosnap();
vert=size(sizeimg,1);
hor=size(sizeimg,2);

Imgs = zeros(vert,hor,N) ;

if (methode == 1)

    Piezo(0) ;

   % pause(1) ;
       % visu_images=figure;
    for i=1:N
        Piezo(tensions_commande(i)) ;
        %pause(1)
        
    handles.h.SaveImage('Caméra2.png'); % on enregistre l'image sur le disque dur
    Img=double(imread('Caméra2.png'));
        %Img=videosnap;
        Imgs(:,:,i) = Img ;
        
        pause(1);
   
        %imagesc(Img),colormap gray,axis image
         %    pause(0.2) 
    end
    %close(visu_images);
   
     Piezo(0) ; 

elseif (methode == 2)
    
    i = 1 ;
    %Imgs = zeros(576,576,5) ;
    Vmax = (round(10*tensions_commande(5))/10)
    tensions_commande;
    visu_images=figure;
    
    
    for V=0:0.1:Vmax
        
        Piezo(V) ;
            
            
        if (V >= (round(10*tensions_commande(i))/10))
            V ;
            
            [Img,status,ErrLoc]=VideoSNAP ;
             imagesc(Img),colormap gray,axis image
             pause(0.25)
            Imgs(:,:,i) = Img ;
            i=i+1 ;
            
            
        else
            pause(0.1)
        end
             
    end
  close(visu_images)
    
    
   
elseif (methode == 3)
    
%         i = 1 ;
%         test = 0 ;
%         V = 0 ;
%         
%         Imgs = zeros(576,576,5) ;
%     
%     while (test == 0)
%         V = V + 0.1 ;
%         daqoutfloat(V) ;
%         if V > tensions_commande(i)
%             daqoutfloat(tensions_commande(i))
%             [Img,status,ErrLoc]=VideoSNAP ;
%             Imgs(:,:,i) = Img(:,97:672) ;
%             i=i+1 ;
%         else
%             pause(0.1)
%         end
%         
%         if (i==6)
%             test = 1 ;
%         end
%     end
    
    
end

Piezo(0) ;


    