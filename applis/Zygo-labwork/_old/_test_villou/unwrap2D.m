function [PhD,Pb,info,both,pb]=unwrap2D(Ph)
% unwrap2D: d�roulement 2D de la phase
% USAGE: PhD=unwrap2D(Ph);
%        [PhD,Pb]=unwrap2D(Ph);
%        [PhD,Pb,info,MaskCOM,MaskDIF]=unwrap2D(Ph);
%
% Ph : Matrice r�elle contenant les phases enroul�es en d�termination principale,
%      i.e. dans ]-pi,+pi] (/!\ et pas dans ]-pi/2,pi/2] !!!).
%      Des points peuvent �tre marqu�s � NaN si n�cessaire (information significative 
%      de phase non disponible par exemple).
%
% PhD: Matrice r�elle, de m�me taille que Ph, contenant les phases d�roul�es.
% 
% Pb:  [Optionnel] scalaire logique. VRAI (logicical(1)) si l'algorithme a d�tect� un
%      probl�me, FAUX (logical(0)) sinon. (Voir la partie "information compl�mentaires 
%      sur le principe de l'algorithme" pour plus de d�tails).
% Les autres arguments optionnels de retour sont d�crits dans la partie  "Informations 
% compl�mentaires sur le principe de l'algorithme", en fin de l'en-t�te de cette fonction.
%
% L'algorithme de d�roulement utilis� est simple et peut �tre mis en d�faut. Il est
% toutefois un peu plus robuste que celui de la fonction "unwrap2".
% La surface � reconstruire doit �tre simple et 'douce', si possible sans discontinuit�
% effective. Par ailleurs, le support des points utiles (non NaN) doit �tre d'un seul
% tenant (i.e. connexe), sans trou ni d�chirure notable. La forme optimale du support 
% est un disque ou un rectangle (une ellipso�de) aux bords (axes) parall�les � ceux de
% la matrice Ph. (Le cas du rectangle allong� inclin� est plut�t mal trait�; par contre
% un carr� sur la pointe sera convenablement trait�... En fait, la surface pouvant �tre
% d�roul�e est grosso-modo r�duite � l'union des rectangles engendr�s respectivement par
% le d�placement vertical du plus long segment horizontal contenu dans le support et le
% d�placement horizontal du plus long segment vertical contenu dans le support.)
%
% Quelques piq�res ou rayures (points � NaN) sur la surface utile peuvent �ventuellement 
% �tre pr�sents sans trop nuire au r�sultat si leur densit� global et surtout l'aire de
% chaque d�faut est faible (un pixel sur l'image). Les d�fauts concernant plusieurs
% pixels adjacents peuvent �ventuellement induire des erreurs ou des points suppl�men-
% taires � NaN.
%
% La transpos�e du d�roulement de la transpos�e (i.e. "unwrap2D(Ph')'") donne un r�sultat
% normalement identique � un offset global pr�s lorsque l'algorithme n'a pas rencontr� de
% probl�me (i.e. l'argument de retour Pb est FAUX).
%
% 
% Informations compl�mentaires sur le principe de l'algorithme:
% ============================================================
% L'id�e de base de cet algorithme est de fusionner les informations obtenues par
% d�roulement par colonnes avec recalage sur une ligne et le d�roulement par lignes 
% avec recalage sur une colonne  (soit, grosso-modo, la fusion de PhDC=unwrap2(Ph) et
% PhDL=unwrap2(Ph')', avec un unwrap2 l�g�rement plus robuste que la version 'publique')
% On d�termine alors l'offset global moyen entre les deux d�roulements offset=PhDC-PhDL
% (normalement un nombre entier de fois 2*pi).
% On d�tecte ensuite les points o� PhDC-PhDL s'�loigne significativement de l'offset
% moyen arrondi au 2*k*pi le plus proche.
% Si ceux-ci son trop nombreux, cela indique un probl�me s�rieux et la fusion n'est pas 
% envisageable. Pb est mis � VRAI, et le r�sultat PhD est le d�roulement PhDC limit� aux
% points communs � PhDC et PhDL (i.e. simultan�ment non-NaN) tels que PhDC-PhDL soit
% peu diff�rent de l'offset moyen.
% S'il y a un taux raisonnablement faible de points aberrants, le r�sultat est donn� par
% la fusion de PhDC et de PhDL+offset. Pb est mis � FAUX et les points aberrants r�siduels
% sont par ailleurs examin�s un � un pour tenter de corriger le probl�me par analyse des
% discontinuit�s locales.
% Diverses informations peuvent �tre obtenues par des arguments optionnels de retour:
% info:    [Optionnel] vecteur ligne de trois nombres [�carttype �cartoff tauxPtsAb].
%          "�carttype" est l'�cart-type r�siduel de PhDC-PhDL sur les points communs
%          NON aberrants. Cela doit normalement �tre un nombre tr�s petit (<1E-10)
%          lorsque Pb est FAUX.
%          "�cartoff" est l'�cart entre l'offset moyen sur tous les points communs et
%          le nombre 2*k*pi le plus proche. Cela doit normalement �tre un nombre petit.          
%          "tauxPtsAb" est le taux du nombre de points communs � PhDC et PhDL ABERRANTS,
%          c'est � dire tels que PhDC diff�re significativement de PhDL+offset_moyen.
% MaskCOM: [Optionnel] matrice logique de m�me taille que Ph indiquant o� se trouve les
%          points COMMUNS (i.e. simultan�ment non-NaN dans PhDC et PhDL). Seuls ces
%          points ont subit un contr�le par coh�rence lors de la fusion des donn�es, et
%          pr�sentent donc une fiabilit� accrue. {"PhD(~MaskCOM)=NaN;" force � NaN les
%          points n'ayant pas subi le contr�le de coh�rence)
% MaskDIF: [Optionnel] matrice logique de m�me taille que Ph indiquant o� se trouve les
%          points communs dont la diff�rence s'�loigne significativement de l'offset moyen
%          entre les deux calculs PhDC et PhDL. Si Pb est vrai, ces points ont �t� forc�s
%          � NaN. Si Pb est faux, une tentative de suppression de l'incoh�rence a �t� 
%          effectu�e. {Ces points peuvent �tre �limin�s par "PhD(MaskDIF)=NaN;"}
%
%
% � Herv� SAUER - SupOptique - 07 novembre 1999
%
% Voir �galement/See also: UNWRAP2, UNWRAP1, UNWRAP (et TSTUNWRAP2T).

%----------------------------------------------------------------------------
% CALCULS PR�LIMINAIRES AVEC ALGORITHME SIMPLE, PAR COLONNES PUIS PAR LIGNES:
%
PhDc=unwrap2Dc(Ph);    % d�roulement 2D en commen�ant par les colonnes
PhDl=unwrap2Dc(Ph.').';% d�roulement 2D en commen�ant par les lignes.
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
%%fprintf(1,'offset/(2*pi)=%14.10f;  �cart_type=%e;  ecart_off=%e\n',...
%%  offsetBrut/(2*pi),ecarttype,ecarto) %DEBUG

% Points probl�matiques d�tect�s:
pb=abs(PhDc-PhDl-offset)>pi/10000; %Rq: NaN n'est jamais > � quoi que ce soit!
%%subplot(2,3,5),imagesc(pb),axis image,title('PhDC \neq PhdL') %DEBUG


% recalcul de l'offset sans les points aberrants ('divergents'):
Voffset=PhDc(both(:)&(~pb(:)))-PhDl(both(:)&(~pb(:)));
if length(Voffset)>=2
  offsetBrut=mean(Voffset);
  offset=2*pi*round(offsetBrut/(2*pi));
  ecarttype=std(Voffset);
  %%fprintf(1,'Sans les pts aber: new_offset/(2*pi)=%14.10f;  new_�cart_type=%e\n',...
  %%  offsetBrut/(2*pi),ecarttype) %DEBUG
else
  ecarttype=inf;
  %%fprintf(1,'Il y a moins de 2 points NON aberrants!!!\n') %DEBUG
end  

NbPPb=sum(pb(:));
NbBoth=sum(both(:));
rapp=NbPPb/NbBoth;
fprintf(1,'Il y a %d points probl�matiques d�tect�s sur %d points communs (rapp=%f)\n', NbPPb,NbBoth,rapp) %DEBUG

info=[ecarttype ecarto rapp];

tauxMaxPtsDiff=0.05;

if  rapp>tauxMaxPtsDiff | ecarttype>pi/10000 % IL Y A UN PROBL�ME S�RIEUX!!!
  Pb=logical(1);
  % D�cision drastique: on ne conserve que les points communs non 'divergents'
  PhD=PhDc;
  PhD(~both)=NaN; % on supprime les points non communs aux calculs par C et par L
  PhD(pb)=NaN;    % on supprime les points divergents
  
else
  Pb=logical(0);

  % fusion des donn�es: 
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
      % on ne traite pas ==> point marqu� comme invalide!
      %%fprintf(1,'PbC&PbL ==>NaN') %DEBUG
    else
      % les erreurs potentielles sont des 'filaments' verticaux dans PhDc et
      % des filaments horizontaux dans PhDl, donc...
      errc=diff(PhDc(iPb(m),jPb(m)+(-1:1))); % d�riv�e horizontale
      errc=errc(~isnan(errc)); % on supprime les NaNs �ventuels
      errl=diff(PhDl(iPb(m)+(-1:1),jPb(m))); % d�riv�e verticale
      errl=errl(~isnan(errl)); % on supprime les NaNs �ventuels
      
      Pbc=any(abs(errc)>pi)|isempty(errc);
      % la d�riv�e horzontale est grande ==> il y a un filament vertical
      Pbl=any(abs(errl)>pi)|isempty(errl);
      % la d�riv�e verticale est grande ==> il y a un filament horizontal
      % NOTA: S'il y a des NaNs des deux c�t�s, isempty est vrai et on
      % consid�re qu'il y a un probl�me.
      
      if Pbc & Pbl
        % il y a un probl�me suivant les deux directions!!
        PhD(iPb(m),jPb(m))=NaN; % on marque le point � NaN!
        %%fprintf(1,'PbC&PbL ==>NaN') %DEBUG
      elseif Pbc
        %PhDc semble avoir un probl�me de filament
        PhD(iPb(m),jPb(m))=PhDl(iPb(m),jPb(m))+offset;
        % on utilise PhDl!
        %%fprintf(1,'PbC ==> PhDL') %DEBUG
      elseif Pbl
        %PhDl semble avoir un probl�me de filament
        % La valeur issue de PhDc utilis�e est optimale
        %%fprintf(1,'PbL (==> PhDC)') %DEBUG
      else
        % il y a divergence sans probl�me de ligne ou de colonne ???
        PhD(iPb(m),jPb(m))=NaN; % on marque le point � NaN!
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
% unwrap2Dc: d�roulement 2D de la phase (d�roulement des colonnes d'abord)
% USAGE: PhD=unwrap2Dc(Ph)
% Ph : Matrice r�elle contenant les phases enroul�es en d�termination principale,
% PhD: Matrice r�elle de m�me taille que Ph contenant les phases d�roul�es.
%
% fonction de service de unwrap2D
%
% � Herv� SAUER - SupOptique - 14 octobre 1999
%


PhD=unwrap1(Ph); % d�roulement ind�pendant de chaque colonne.
% /!\ unwrap1, � la diff�rence de la fonction native unwrap, traite correctement les NaNs!

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
% l2 est l'indice de la ligne contenant le moins de NaNs en ayant exclu les lignes situ�es
% � +ou-coef fois la taille de la matrice de la ligne principale pr�c�dente.
L2=PhD(l2,:); % la ligne secondaire choisie


LD1=unwrap1(L1);
sautL1=LD1-L1; % vecteur ligne d�crivant les sauts de 2*pi provoquant le d�roulement de
% la ligne principale.
LD2=unwrap1(L2);
sautL2=LD2-L2; % vecteur ligne d�crivant les sauts de 2*pi provoquant le d�roulement de
% la ligne secondaire.

% # Si L1 contient des NaNs, sautL1 en contient aussi, ce qui conduirait � des colonnes
% # de NaNs dans le r�sultat final. Ce n'est pas souhaitable: on va les supprimer
sautLsN=supprimeNaN(sautL1,sautL2); % Appel d'une fonction locale 
%figure,plot([sautL1(:) sautL2(:)+0.05*2*pi sautLsN(:)+0.1*2*pi]/(2*pi))

sautM=ones(N,1)*sautLsN; % Matrice de N lignes identiques � sautLsN

PhD=PhD+sautM; % !!l'astuce:
% raccord entre les colonnes (d�roul�es ind�pendamment les unes des autres) par
% le d�roulement de la seule ligne L choisie!



%########################################################################################
function y=supprimeNaN(x1,x2)
% supprimeNaN: supprime les NaN de deux "r�alisations" d'un vecteur de sauts de 2*k*pi.
% x1 et x2 sont des vecteurs d'�chantillonnage d'une fonction constante par morceau �
% 2*k*pi,avec k entier. Normalement x1 et x2 ne diff�rent, hors NaNs, que par un offset 
% global constant de 2*m*pi. La 'fusion' des deux vecteurs autorise la suppression
% d'un certain nombre de NaN, une grande partie si les positions des NaNs ne sont pas
% correl�es entre les deux vecteurs x (ceci est en partie contr�l� par le coefficient coef
% d�terminant dans le programme appelant la distance minimale s�parant les deux lignes).
% De surcro�t, si les deux points de par et d'autre d'un NaN ou d'un groupe cons�cutif de
% NaNs sont � la m�me valeur, on remplace les NaNs par cette valeur. Sinon, on laisse
% le(s) NaN(s) puisque l'on ne sait pas quelle valeur prendre (ce qui conduit � une
% colonne noire)


%-- �TAPE 1: 'fusion' de x1 et x2:
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
  % o� x1 vaut NaN et x2 n'est pas NaN, on prend x2-offset.
end
% La 'correlation' des vecteurs x1 et x2 est dans y!



%-- �TAPE 2: Suppression des NaNs 
Lx=length(x1);

k=find(isnan(y)); % donne les indices des points � NaN
Lk=length(k);

if Lk~=0 % il existe un ou des NaNs dans x
  
  dk=[diff(k) 0];   % les valeurs � 1 indique des NaNs cons�cutifs.
  % dk a m�me longueur que k, grace � la concat�nation du 0.
  
  % Construction d'une matrice des indices des groupes de NaNs cons�cutifs
  % iDF=[iD�but1 iFin1;iD�but2 iFin2; ...]. Les NaNs isol�s donnent iD�butx==iFinx.
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
  
  % pr�-traitement des cas groupe de NaNs en d�but ou fin:
  if iDF(1,1)==1
    iDF=iDF(2:end,:); %on supprime de la liste le groupe de NaNs de t�te
  end
  if ~isempty(iDF) & iDF(end,2)==Lx
    iDF=iDF(1:end-1,:); % on supprime de la liste le groupe de NaNs de queue
  end
  
  % suppression des groupes de NaNs entre-coupant un plateau de valeur:
  % (Rq: les indexations sont obligatoirement correctes gr�ce au pr�-traitement pr�c�dent)
  for j=1:size(iDF,1)
    if abs(y(iDF(j,1)-1)-y(iDF(j,2)+1))<eps*2000
      y(iDF(j,1):iDF(j,2))=y(iDF(j,1)-1);
    else
      % on laisse � NaN, puisque l'on ne sait pas laquelle des valeurs de gauche ou
      % de droite prendre!
    end
  end
  
end




