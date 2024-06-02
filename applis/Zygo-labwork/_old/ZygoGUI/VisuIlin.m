function VisuIlin(AC,mn,mx)
% VisuIlin: visualise lin�airement "l'intensit�" d'une image en amplitude complexe.
% USAGE: VisuIlin(ImAC)  ou  VisuIlin(ImAC,min)  ou  VisuIlin(ImAC,min,max)
% ImAC:  matrice complexe contenant l'image en amplitude complexe
% min:  [OPTIONNEL] scalaire r�elle positif indiquant la valeur minimale repr�sent�e par la LUT
%       (par d�faut, c'est la valeur minimale de |ImAC|�.)
% max:  [OPTIONNEL] scalaire r�elle positif indiquant la valeur maximale repr�sent�e par la LUT
%       (par d�faut, c'est la valeur maximale de |ImAC|�.)
% Pour pr�ciser la valeur  max  en utilisant la valeur  min  par d�faut, introduire [] pour min.
% 
% � Herv� SAUER - SupOptique - 14 novembre 1997.
%


U=AC.*conj(AC);

if nargin < 2
   mn=min(min(U));
elseif isempty(mn)
   mn=min(min(U));
end

if nargin < 3
   mx=max(max(U));
elseif isempty(mx)
   mx=max(max(U));
end

figure(gcf),colormap(gray(256)),imagesc(U,[mn mx]),axis image,axis off
%colorbar




