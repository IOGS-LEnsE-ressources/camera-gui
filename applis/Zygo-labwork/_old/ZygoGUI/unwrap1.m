function yd=unwrap1(xe,sautLimite,dim)
%unwrap1: déroule un vecteur de phase (Les NaNs sont correctement ignorés)
% USAGE: yd=unwrap1(xe)
%        yd=unwrap1(xe,sautLimite,dim)
% xe        : tableau numérique dont on veut dérouler les vecteurs colonnes ou
%             de la dimension dim, si dim est présent.
% sautLimite: [OPTIONNEL] scalaire numérique indiquant la valeur du saut
%             maximale tolérée. [pi par défaut].
% dim       : [OPTIONNEL] scalaire entier strictement positif indiquant la
%             dimension suivant laquelle le déroulement doit être effectué.
%             [Par défaut, le traitement est fait suivant la première dimension
%              non réduite à 1, i.e. par colonne pour les matrices, suivant la
%              direction du vecteur pour les vecteurs lignes ou colonnes.]
% yd         : tableau de même dimension que xe contenant le résultat.
%
% unwrap1 est similaire à la fonction native unwrap aux importantes différences
% que, les NaNs présents sont correctement ignorés, que l'argument  dim  fonctionne
% correctement et que si SautLimite est présent, le déroulement est effectué sur la
% base d'un enroulement de 2*sautLimite et pas de 2*pi (une valeur de 180 permet
% donc de dérouler un tableau de phase en degré où le modulo est de 360°...).
%
% © Hervé SAUER - SupOptique - 15 octobre 1999
%
% Voir également/see also: UNWRAP, UNWRAP2, UNWRAP2D.


if ~exist('sautLimite','var') | isempty(sautLimite)
  sautLimite=pi;
end
P=2*sautLimite;

sxe=size(xe);
if ~exist('dim','var') | isempty(dim)
  dim=1;
  [yd,nbs]=shiftdim(xe); % on supprime les premières dimensions réduites à 1
  % (en particulier, vecteur ligne  --> vecteur colonne).
else
  if dim<1 | dim>ndims(xe) | dim-floor(dim)~=0
    error('L''argument dim est incorrect')
  end
  yd=permute(xe,[dim:ndims(xe) 1:dim-1]); % On met la dimension de travail en première position
end


[n,m]=size(yd); % m = produit de toutes les dimensions autres que la première

for j=1:m % pour toutes les colonnes
  y=yd(:,j);
  
  k=~isnan(y);
  ysn=y(k);
  
  dysn=[0;diff(ysn)];
  %ilYaSaut=abs(dysn)>sautLimite;
  %saut=zeros(size(ysn));
  %saut(ilYaSaut)=-round(dysn(ilYaSaut)/P)*P;
  saut=-round(dysn/P)*P;
  
  yd(k,j)=ysn+cumsum(saut);
end

yd=ipermute(yd,[dim:ndims(xe) 1:dim-1]);
yd=reshape(yd,sxe);



