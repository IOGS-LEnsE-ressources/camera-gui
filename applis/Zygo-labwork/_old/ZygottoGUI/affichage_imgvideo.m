function img = affichage_imgvideo(handles)
axes(handles.image_video);
axis(handles.image_video,'off');
switch handles.typeacq
    case 0
        img=videosnap;
    case 1
        img = handles.img1;
end
img_NB=repmat(img/max(max(img)),[1,1,3]);
image(img_NB);



