function VisuIlin(AC,mn,mx)
% VisuIlin: visualise linéairement "l'intensité" d'une image en amplitude complexe.
% USAGE: VisuIlin(ImAC)  ou  VisuIlin(ImAC,min)  ou  VisuIlin(ImAC,min,max)
% ImAC:  matrice complexe contenant l'image en amplitude complexe
% min:  [OPTIONNEL] scalaire réelle positif indiquant la valeur minimale représentée par la LUT
%       (par défaut, c'est la valeur minimale de |ImAC|².)
% max:  [OPTIONNEL] scalaire réelle positif indiquant la valeur maximale représentée par la LUT
%       (par défaut, c'est la valeur maximale de |ImAC|².)
% Pour préciser la valeur  max  en utilisant la valeur  min  par défaut, introduire [] pour min.
% 
% © Hervé SAUER - SupOptique - 14 novembre 1997.
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




