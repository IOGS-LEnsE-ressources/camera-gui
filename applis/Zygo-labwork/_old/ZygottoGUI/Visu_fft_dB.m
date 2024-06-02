function Visu_fft_dB(U,seuil_dB,tronc_dB)
% VisuIdB: visualise "l'intensit�" en dB d'une image en amplitude complexe.
% USAGE: VisuIdB(ImAC,seuil_dB)  ou   VisuIdB(ImAC,seuil_dB,tronc_dB)
% ImAC:      matrice complexe contenant l'image en amplitude complexe
% seuil_dB:  scalaire r�elle indiquant le seuil bas en dB de l'image affich�e
%           (typiquement -30 ou -40).
% tronc_dB: [OPTIONNEL]. Si absent, le seuil pr�c�dent est RELATIF au maximum
%                        de l'image. Le max de l'image est normalis� � 0dB.
%                        Si pr�sent, le seuil est absolu et tronc_dB
%                        indique un niveau de troncature haute (Indiquer +Inf
%                        pour supprimer cette troncature).
% 
% � Herv� SAUER - SupOptique - 05 novembre 1997.
%



seuil_eff=10^(seuil_dB/10);

if nargin < 3
   figure(gcf),colormap(gray(256)),imagesc(10*log10(max(seuil_eff,U/max(max(U))))),...
   axis off,... 
   axis image
   %colorbar
   %log pris apr�s le seuillage pour �viter un �ventuel warning log of 0.
else
   figure(gcf),colormap(gray(256)),imagesc(min(tronc_dB,10*log10(max(seuil_eff,U)))),axis image,colorbar
   % log pris apr�s le seuillage pour �viter un �ventuel warning log of 0.
end




