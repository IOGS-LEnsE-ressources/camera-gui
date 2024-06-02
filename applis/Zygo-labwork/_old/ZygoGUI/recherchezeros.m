function profile_zeros=recherchezeros(profile)
%recherche les zeros d'un profil
%ressort un tableau contenant les positions des zeros

%on repere les zeros au changement de signe entre deux points successifs
j=1;
m=size(profile,2);
for i=1:m-1
    if ((profile(i)*profile(i+1))<0)
        profile_zeros(j) = i+(profile(i)/profile(i+1))/(profile(i)/profile(i+1)-1) ;
        j=j+1 ;
    end
end
end