%realise le lissage d'une courbe en effectuant une moyenne glissante
%le parametre p peut etre choisi librement

function profile_lisse=lissage(profile,p)

m=size(profile) ;
for i=p+1:m-p
    profile_lisse(i-p) = sum(profile(i-p:i+p))/(2*p+1) ;
end
end