function yd=unwrap1(xe,sautLimite,dim)
%unwrap1: d�roule un vecteur de phase (Les NaNs sont correctement ignor�s)
% USAGE: yd=unwrap1(xe)
%        yd=unwrap1(xe,sautLimite,dim)
% xe        : tableau num�rique dont on veut d�rouler les vecteurs colonnes ou
%             de la dimension dim, si dim est pr�sent.
% sautLimite: [OPTIONNEL] scalaire num�rique indiquant la valeur du saut
%             maximale tol�r�e. [pi par d�faut].
% dim       : [OPTIONNEL] scalaire entier strictement positif indiquant la
%             dimension suivant laquelle le d�roulement doit �tre effectu�.
%             [Par d�faut, le traitement est fait suivant la premi�re dimension
%              non r�duite � 1, i.e. par colonne pour les matrices, suivant la
%              direction du vecteur pour les vecteurs lignes ou colonnes.]
% yd         : tableau de m�me dimension que xe contenant le r�sultat.
%
% unwrap1 est similaire � la fonction native unwrap aux importantes diff�rences
% que, les NaNs pr�sents sont correctement ignor�s, que l'argument  dim  fonctionne
% correctement et que si SautLimite est pr�sent, le d�roulement est effectu� sur la
% base d'un enroulement de 2*sautLimite et pas de 2*pi (une valeur de 180 permet
% donc de d�rouler un tableau de phase en degr� o� le modulo est de 360�...).
%
% � Herv� SAUER - SupOptique - 15 octobre 1999
%
% Voir �galement/see also: UNWRAP, UNWRAP2, UNWRAP2D.


if ~exist('sautLimite','var') | isempty(sautLimite)
  sautLimite=pi;
end
P=2*sautLimite;

sxe=size(xe);
if ~exist('dim','var') | isempty(dim)
  dim=1;
  [yd,nbs]=shiftdim(xe); % on supprime les premi�res dimensions r�duites � 1
  % (en particulier, vecteur ligne  --> vecteur colonne).
else
  if dim<1 | dim>ndims(xe) | dim-floor(dim)~=0
    error('L''argument dim est incorrect')
  end
  yd=permute(xe,[dim:ndims(xe) 1:dim-1]); % On met la dimension de travail en premi�re position
end


[n,m]=size(yd); % m = produit de toutes les dimensions autres que la premi�re

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



