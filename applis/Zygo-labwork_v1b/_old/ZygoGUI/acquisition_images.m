function Imgs = acquisition_images;

methode = 1;
N = 5 ; 
theta = 90 ;

pas = 0.1 ;

%tensions_commande = calcul_tensions(N, theta) 

%Modif Lionel 17 nov 2010
%tensions_commande = [2.679128629717374   3.635387236993990   4.800000000000001   5.636407886199419   6.505772905378959];
%tensions_commande =     [0.8800085464131472	2.5642937425811096	3.962996790165622	4.891736357553595	5.856024629071319];
%tensions_commande =    [0 1.7 3.4 5.5 7.5];

%UNe bonne configuration : la calibration est délicate

% ***Ancienne calibration (donne de meilleurs résultats)
save_config('Tensions',  [0 1.5 2.5 4 6]);

% *** Nouvelle calibration 12/07/16
% save_config('Tensions',[2.679128629717374   3.635387236993990   4.800000000000001   5.636407886199419   6.505772905378959]);

%save_config('Tensions',[  0.800000000000000   1.951400036234278   4.000000000000000   5.825707374015948  7]);

tensions_commande=read_config('Tensions',1);

sizeimg=videosnap();
vert=size(sizeimg,1);
hor=size(sizeimg,2);

Imgs = zeros(vert,hor,N) ;

if (methode == 1)

    daqoutfloat(0) ;

    pause(1) ;
       % visu_images=figure;
    for i=1:N
        daqoutfloat(tensions_commande(i)) ;
        %pause(1)
        
        Img=videosnap;
        Imgs(:,:,i) = Img ;
        
       
   
        %imagesc(Img),colormap gray,axis image
         %    pause(0.2) 
    end
    %close(visu_images);
   
     daqoutfloat(0) ; 

elseif (methode == 2)
    
    i = 1 ;
    %Imgs = zeros(576,576,5) ;
    Vmax = (round(10*tensions_commande(5))/10)
    tensions_commande
    visu_images=figure;
    
    
    for V=0:0.1:Vmax
        
        daqoutfloat(V) ;
            
            
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

daqoutfloat(0) ;


    