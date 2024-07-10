function Imgs = acquisition_images_projet_matlab;

methode = 1;
N = 6 ; 
theta = 90 ;

pas = 0.1 ;

tensions_commande = calcul_tensions(N, theta) 
tensions_commande  
%Modif Lionel 17 nov 2010
%tensions_commande = [1 1.6 3.4 4.8 5.7 6.5]
sizeimg=videosnap;
vert=size(sizeimg,1);
hor=size(sizeimg,2);

Imgs = zeros(vert,hor,N) ;

if (methode == 1)

    daqoutfloat(0) ;

   % pause(1) ;
       % visu_images=figure;
    for i=1:N
        daqoutfloat(tensions_commande(i)) ;
        %pause(1)
        
        [Img,status,ErrLoc]=VideoSNAP ;
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


    