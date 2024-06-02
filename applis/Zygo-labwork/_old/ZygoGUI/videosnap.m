function img= videosnap ()
%UNTITLED4 Summary of this function goes here
%   Detailed explanation goes here

vid = videoinput('ni', 1, 'img0');
start(vid);
stoppreview(vid);
img = getdata(vid);
img=double(img(:,:,1,1)); %passage en reel)
%affimageNB(img)
%imagesc(img);
end

