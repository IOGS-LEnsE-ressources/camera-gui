function [PhD,Pb,info,both,pb]=unwrap2D(Ph)
% unwrap2D: déroulement 2D de la phase
% USAGE: PhD=unwrap2D(Ph);
%        [PhD,Pb]=unwrap2D(Ph);
%        [PhD,Pb,info,MaskCOM,MaskDIF]=unwrap2D(Ph);
%
% Ph : Matrice réelle contenant les phases enroulées en détermination principale,
%      i.e. dans ]-pi,+pi] (/!\ et pas dans ]-pi/2,pi/2] !!!).
%      Des points peuvent être marqués à NaN si nécessaire (information significative 
%      de phase non disponible par exemple).
%
% PhD: Matrice réelle, de même taille que Ph, contenant les phases déroulées.
% 
% Pb:  [Optionnel] scalaire logique. VRAI (logicical(1)) si l'algorithme a détecté un
%      problème, FAUX (logical(0)) sinon. (Voir la partie "information complémentaires 
%      sur le principe de l'algorithme" pour plus de détails).
% Les autres arguments optionnels de retour sont décrits dans la partie  "Informations 
% complémentaires sur le principe de l'algorithme", en fin de l'en-tête de cette fonction.
%
% L'algorithme de déroulement utilisé est simple et peut être mis en défaut. Il est
% toutefois un peu plus robuste que celui de la fonction "unwrap2".
% La surface à reconstruire doit être simple et 'douce', si possible sans discontinuité
% effective. Par ailleurs, le support des points utiles (non NaN) doit être d'un seul
% tenant (i.e. connexe), sans trou ni déchirure notable. La forme optimale du support 
% est un disque ou un rectangle (une ellipsoïde) aux bords (axes) parallèles à ceux de
% la matrice Ph. (Le cas du rectangle allongé incliné est plutôt mal traité; par contre
% un carré sur la pointe sera convenablement traité... En fait, la surface pouvant être
% déroulée est grosso-modo réduite à l'union des rectangles engendrés respectivement par
% le déplacement vertical du plus long segment horizontal contenu dans le support et le
% déplacement horizontal du plus long segment vertical contenu dans le support.)
%
% Quelques piqûres ou rayures (points à NaN) sur la surface utile peuvent éventuellement 
% être présents sans trop nuire au résultat si leur densité global et surtout l'aire de
% chaque défaut est faible (un pixel sur l'image). Les défauts concernant plusieurs
% pixels adjacents peuvent éventuellement induire des erreurs ou des points supplémen-
% taires à NaN.
%
% La transposée du déroulement de la transposée (i.e. "unwrap2D(Ph')'") donne un résultat
% normalement identique à un offset global près lorsque l'algorithme n'a pas rencontré de
% problème (i.e. l'argument de retour Pb est FAUX).
%
% 
% Informations complémentaires sur le principe de l'algorithme:
% ============================================================
% L'idée de base de cet algorithme est de fusionner les informations obtenues par
% déroulement par colonnes avec recalage sur une ligne et le déroulement par lignes 
% avec recalage sur une colonne  (soit, grosso-modo, la fusion de PhDC=unwrap2(Ph) et
% PhDL=unwrap2(Ph')', avec un unwrap2 légèrement plus robuste que la version 'publique')
% On détermine alors l'offset global moyen entre les deux déroulements offset=PhDC-PhDL
% (normalement un nombre entier de fois 2*pi).
% On détecte ensuite les points où PhDC-PhDL s'éloigne significativement de l'offset
% moyen arrondi au 2*k*pi le plus proche.
% Si ceux-ci son trop nombreux, cela indique un problème sérieux et la fusion n'est pas 
% envisageable. Pb est mis à VRAI, et le résultat PhD est le déroulement PhDC limité aux
% points communs à PhDC et PhDL (i.e. simultanément non-NaN) tels que PhDC-PhDL soit
% peu différent de l'offset moyen.
% S'il y a un taux raisonnablement faible de points aberrants, le résultat est donné par
% la fusion de PhDC et de PhDL+offset. Pb est mis à FAUX et les points aberrants résiduels
% sont par ailleurs examinés un à un pour tenter de corriger le problème par analyse des
% discontinuités locales.
% Diverses informations peuvent être obtenues par des arguments optionnels de retour:
% info:    [Optionnel] vecteur ligne de trois nombres [écarttype écartoff tauxPtsAb].
%          "écarttype" est l'écart-type résiduel de PhDC-PhDL sur les points communs
%          NON aberrants. Cela doit normalement être un nombre très petit (<1E-10)
%          lorsque Pb est FAUX.
%          "écartoff" est l'écart entre l'offset moyen sur tous les points communs et
%          le nombre 2*k*pi le plus proche. Cela doit normalement être un nombre petit.          
%          "tauxPtsAb" est le taux du nombre de points communs à PhDC et PhDL ABERRANTS,
%          c'est à dire tels que PhDC diffère significativement de PhDL+offset_moyen.
% MaskCOM: [Optionnel] matrice logique de même taille que Ph indiquant où se trouve les
%          points COMMUNS (i.e. simultanément non-NaN dans PhDC et PhDL). Seuls ces
%          points ont subit un contrôle par cohérence lors de la fusion des données, et
%          présentent donc une fiabilité accrue. {"PhD(~MaskCOM)=NaN;" force à NaN les
%          points n'ayant pas subi le contrôle de cohérence)
% MaskDIF: [Optionnel] matrice logique de même taille que Ph indiquant où se trouve les
%          points communs dont la différence s'éloigne significativement de l'offset moyen
%          entre les deux calculs PhDC et PhDL. Si Pb est vrai, ces points ont été forcés
%          à NaN. Si Pb est faux, une tentative de suppression de l'incohérence a été 
%          effectuée. {Ces points peuvent être éliminés par "PhD(MaskDIF)=NaN;"}
%
%
% © Hervé SAUER - SupOptique - 07 novembre 1999
%
% Voir également/See also: UNWRAP2, UNWRAP1, UNWRAP (et TSTUNWRAP2T).

%----------------------------------------------------------------------------
% CALCULS PRÉLIMINAIRES AVEC ALGORITHME SIMPLE, PAR COLONNES PUIS PAR LIGNES:
%
PhDc=unwrap2Dc(Ph);    % déroulement 2D en commençant par les colonnes
PhDl=unwrap2Dc(Ph.').';% déroulement 2D en commençant par les lignes.
% "unwrap2Dc" est une fonction locale (voir ci-dessous).
%%figure %DEBUG
%%subplot(2,3,1),imagesc(PhDc),axis image,colorbar,title('C') %DEBUG
%%subplot(2,3,2),imagesc(PhDl),axis image,colorbar,title('L') %DEBUG



%----------------------------------------------------------------------------
% FUSION DES DEUX INFORMATIONS:
%
isnc=isnan(PhDc);
isnl=isnan(PhDl);

both=(~isnc)&(~isnl); % non-NAN c & non-NaN l
%%subplot(2,3,4),imagesc(both),axis image,title('~isNaN_C & ~isNaN_L') %DEBUG

Voffset=PhDc(both(:))-PhDl(both(:));
offsetBrut=mean(Voffset);
offset=2*pi*round(offsetBrut/(2*pi));
ecarto=abs(offset-offsetBrut);
%%ecarttype=std(Voffset); %DEBUG
%%fprintf(1,'offset/(2*pi)=%14.10f;  écart_type=%e;  ecart_off=%e\n',...
%%  offsetBrut/(2*pi),ecarttype,ecarto) %DEBUG

% Points problématiques détectés:
pb=abs(PhDc-PhDl-offset)>pi/10000; %Rq: NaN n'est jamais > à quoi que ce soit!
%%subplot(2,3,5),imagesc(pb),axis image,title('PhDC \neq PhdL') %DEBUG


% recalcul de l'offset sans les points aberrants ('divergents'):
Voffset=PhDc(both(:)&(~pb(:)))-PhDl(both(:)&(~pb(:)));
if length(Voffset)>=2
  offsetBrut=mean(Voffset);
  offset=2*pi*round(offsetBrut/(2*pi));
  ecarttype=std(Voffset);
  %%fprintf(1,'Sans les pts aber: new_offset/(2*pi)=%14.10f;  new_écart_type=%e\n',...
  %%  offsetBrut/(2*pi),ecarttype) %DEBUG
else
  ecarttype=inf;
  %%fprintf(1,'Il y a moins de 2 points NON aberrants!!!\n') %DEBUG
end  

NbPPb=sum(pb(:));
NbBoth=sum(both(:));
rapp=NbPPb/NbBoth;
fprintf(1,'Il y a %d points problématiques détectés sur %d points communs (rapp=%f)\n', NbPPb,NbBoth,rapp) %DEBUG

info=[ecarttype ecarto rapp];

tauxMaxPtsDiff=0.05;

if  rapp>tauxMaxPtsDiff | ecarttype>pi/10000 % IL Y A UN PROBLÈME SÉRIEUX!!!
  Pb=logical(1);
  % Décision drastique: on ne conserve que les points communs non 'divergents'
  PhD=PhDc;
  PhD(~both)=NaN; % on supprime les points non communs aux calculs par C et par L
  PhD(pb)=NaN;    % on supprime les points divergents
  
else
  Pb=logical(0);

  % fusion des données: 
  PhD=PhDc;
  PhD(isnc&(~isnl))=PhDl(isnc&(~isnl))+offset; % FUSION
  %%subplot(2,3,6),imagesc(isnc&(~isnl)),axis image,title('isNaN_C & ~isNaN_L') %DEBUG
  
  
  
  % traitement des points communs divergents:
  
  [iPb,jPb]=find(pb);
  %NbPPb=length(iPb);
  [Ni,Nj]=size(Ph);
  
  for m=1:NbPPb
    %%fprintf(1,'\nm=%f; (iPB,jPB)=(%3d,%3d): ',m,iPb(m),jPb(m)) %DEBUG
    if ismember(iPb(m),[1 Ni]) | ismember(jPb(m),[1 Nj])
      % bord de l'image
      PhD(iPb(m),jPb(m))=NaN;
      % on ne traite pas ==> point marqué comme invalide!
      %%fprintf(1,'PbC&PbL ==>NaN') %DEBUG
    else
      % les erreurs potentielles sont des 'filaments' verticaux dans PhDc et
      % des filaments horizontaux dans PhDl, donc...
      errc=diff(PhDc(iPb(m),jPb(m)+(-1:1))); % dérivée horizontale
      errc=errc(~isnan(errc)); % on supprime les NaNs éventuels
      errl=diff(PhDl(iPb(m)+(-1:1),jPb(m))); % dérivée verticale
      errl=errl(~isnan(errl)); % on supprime les NaNs éventuels
      
      Pbc=any(abs(errc)>pi)|isempty(errc);
      % la dérivée horzontale est grande ==> il y a un filament vertical
      Pbl=any(abs(errl)>pi)|isempty(errl);
      % la dérivée verticale est grande ==> il y a un filament horizontal
      % NOTA: S'il y a des NaNs des deux côtés, isempty est vrai et on
      % considère qu'il y a un problème.
      
      if Pbc & Pbl
        % il y a un problème suivant les deux directions!!
        PhD(iPb(m),jPb(m))=NaN; % on marque le point à NaN!
        %%fprintf(1,'PbC&PbL ==>NaN') %DEBUG
      elseif Pbc
        %PhDc semble avoir un problème de filament
        PhD(iPb(m),jPb(m))=PhDl(iPb(m),jPb(m))+offset;
        % on utilise PhDl!
        %%fprintf(1,'PbC ==> PhDL') %DEBUG
      elseif Pbl
        %PhDl semble avoir un problème de filament
        % La valeur issue de PhDc utilisée est optimale
        %%fprintf(1,'PbL (==> PhDC)') %DEBUG
      else
        % il y a divergence sans problème de ligne ou de colonne ???
        PhD(iPb(m),jPb(m))=NaN; % on marque le point à NaN!
        %%fprintf(1,'??? ==>NaN') %DEBUG
      end
    end
  end
  
end

%%subplot(2,3,3),imagesc(PhD),axis image,colorbar,title('fusion finale') %DEBUG
%%fprintf(1,'\n\n') %DEBUG


%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% FONCTIONS LOCALES:
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%
%########################################################################################
function PhD=unwrap2Dc(Ph)
% unwrap2Dc: déroulement 2D de la phase (déroulement des colonnes d'abord)
% USAGE: PhD=unwrap2Dc(Ph)
% Ph : Matrice réelle contenant les phases enroulées en détermination principale,
% PhD: Matrice réelle de même taille que Ph contenant les phases déroulées.
%
% fonction de service de unwrap2D
%
% © Hervé SAUER - SupOptique - 14 octobre 1999
%


PhD=unwrap1(Ph); % déroulement indépendant de chaque colonne.
% /!\ unwrap1, à la différence de la fonction native unwrap, traite correctement les NaNs!

N=size(Ph,1);
isnPh=isnan(Ph);
nbNaNparLigne=sum(isnPh,2);

[m,l1]=min(nbNaNparLigne); % l1 est l'indice de la ligne contenant le moins de NaNs
L1=PhD(l1,:); % la ligne principale choisie

coef=0.025; % (2.5%)
delta=ceil(N*coef); % coef fois la taille de la matrice
i_rej=max(1,l1-delta):min(N,l1+delta);
k_rej=~ismember((1:N)',i_rej);
[m,l2]=min(nbNaNparLigne(k_rej));
if l2>min(i_rej)
  l2=l2+length(i_rej);
end
% l2 est l'indice de la ligne contenant le moins de NaNs en ayant exclu les lignes situées
% à +ou-coef fois la taille de la matrice de la ligne principale précédente.
L2=PhD(l2,:); % la ligne secondaire choisie


LD1=unwrap1(L1);
sautL1=LD1-L1; % vecteur ligne décrivant les sauts de 2*pi provoquant le déroulement de
% la ligne principale.
LD2=unwrap1(L2);
sautL2=LD2-L2; % vecteur ligne décrivant les sauts de 2*pi provoquant le déroulement de
% la ligne secondaire.

% # Si L1 contient des NaNs, sautL1 en contient aussi, ce qui conduirait à des colonnes
% # de NaNs dans le résultat final. Ce n'est pas souhaitable: on va les supprimer
sautLsN=supprimeNaN(sautL1,sautL2); % Appel d'une fonction locale 
%figure,plot([sautL1(:) sautL2(:)+0.05*2*pi sautLsN(:)+0.1*2*pi]/(2*pi))

sautM=ones(N,1)*sautLsN; % Matrice de N lignes identiques à sautLsN

PhD=PhD+sautM; % !!l'astuce:
% raccord entre les colonnes (déroulées indépendamment les unes des autres) par
% le déroulement de la seule ligne L choisie!



%########################################################################################
function y=supprimeNaN(x1,x2)
% supprimeNaN: supprime les NaN de deux "réalisations" d'un vecteur de sauts de 2*k*pi.
% x1 et x2 sont des vecteurs d'échantillonnage d'une fonction constante par morceau à
% 2*k*pi,avec k entier. Normalement x1 et x2 ne diffèrent, hors NaNs, que par un offset 
% global constant de 2*m*pi. La 'fusion' des deux vecteurs autorise la suppression
% d'un certain nombre de NaN, une grande partie si les positions des NaNs ne sont pas
% correlées entre les deux vecteurs x (ceci est en partie contrôlé par le coefficient coef
% déterminant dans le programme appelant la distance minimale séparant les deux lignes).
% De surcroît, si les deux points de par et d'autre d'un NaN ou d'un groupe consécutif de
% NaNs sont à la même valeur, on remplace les NaNs par cette valeur. Sinon, on laisse
% le(s) NaN(s) puisque l'on ne sait pas quelle valeur prendre (ce qui conduit à une
% colonne noire)


%-- ÉTAPE 1: 'fusion' de x1 et x2:
in1=isnan(x1);
in2=isnan(x2);
both=(~in1)&(~in2); % non-NaN dans x1 ET non-NaN dans x2
y=x1;
if isempty(both) % cela se passe mal!
  % On ne prend en compte que x1  
else
  % sinon, on prend les informations des deux vecteurs:
  offset=mean(x2(both)-x1(both));
  y(in1&(~in2))=x2(in1&(~in2))-offset;
  % où x1 vaut NaN et x2 n'est pas NaN, on prend x2-offset.
end
% La 'correlation' des vecteurs x1 et x2 est dans y!



%-- ÉTAPE 2: Suppression des NaNs 
Lx=length(x1);

k=find(isnan(y)); % donne les indices des points à NaN
Lk=length(k);

if Lk~=0 % il existe un ou des NaNs dans x
  
  dk=[diff(k) 0];   % les valeurs à 1 indique des NaNs consécutifs.
  % dk a même longueur que k, grace à la concaténation du 0.
  
  % Construction d'une matrice des indices des groupes de NaNs consécutifs
  % iDF=[iDébut1 iFin1;iDébut2 iFin2; ...]. Les NaNs isolés donnent iDébutx==iFinx.
  iDF=zeros(0,2);
  j=1;
  while j<=Lk
    iDF=[iDF;k(j) k(j)];
    while j<=Lk & dk(j)==1
      j=j+1;
      iDF(end,2)=k(j); % comme dk(L)==0, k(j) ne peut provoquer une erreur d'indexation ici.
    end
    j=j+1;
  end  
  
  % pré-traitement des cas groupe de NaNs en début ou fin:
  if iDF(1,1)==1
    iDF=iDF(2:end,:); %on supprime de la liste le groupe de NaNs de tête
  end
  if ~isempty(iDF) & iDF(end,2)==Lx
    iDF=iDF(1:end-1,:); % on supprime de la liste le groupe de NaNs de queue
  end
  
  % suppression des groupes de NaNs entre-coupant un plateau de valeur:
  % (Rq: les indexations sont obligatoirement correctes grâce au pré-traitement précédent)
  for j=1:size(iDF,1)
    if abs(y(iDF(j,1)-1)-y(iDF(j,2)+1))<eps*2000
      y(iDF(j,1):iDF(j,2))=y(iDF(j,1)-1);
    else
      % on laisse à NaN, puisque l'on ne sait pas laquelle des valeurs de gauche ou
      % de droite prendre!
    end
  end
  
end




