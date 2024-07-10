function VisuPh(AC,type_lut)
% VisuPh: visualise la phase d'une image en amplitude complexe.
% USAGE: VisuPh(ImAC)  ou   VisuPh(ImAC,type_LUT)
% ImAC:      matrice complexe contenant l'image en amplitude complexe
% type_LUT: [OPTIONNEL]. chaîne de caractère 'G','C', ou 'P' pour
%           Gris, Couleur ou Périodique caractérisant la LUT utilisée.
%           (Par défaut la LUT est périodique).
% 
% © Hervé SAUER - SupOptique - 05 novembre 1997.
%


Ph=angle(AC);

if nargin < 2
   type_lut='P';
end

TL=upper(type_lut(1,1));
if TL=='G'
   map=gray(256);
elseif TL=='C'
   map=jeths(256);
elseif TL=='P'
   map=hsv(256);
else
   error('L''argument  type_LUT  doit être ''G'', ''C'' ou ''P''.')
end
   
figure(gcf),colormap(map),imagesc(Ph,[-pi pi]),axis image,colorbar




