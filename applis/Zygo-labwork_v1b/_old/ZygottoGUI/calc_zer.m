%Calcul des polynômes du N ieme polynome de zernicke  
function Z=calc_zer(Pts_polaire,N)


R=Pts_polaire(:,1);
A=Pts_polaire(:,2);

Z=ones(length(R),1);

switch N

    case 1
        %piston
        %Z=zeros(size(R,1),1);
        Z=ones(size(R,1),1);

    case 2
        %tilt
        Z=R.*cos(A);

    case 3
        Z=R.*sin(A);

    case 4
        %defoc
        Z=2*(R.^2)-1;

    case 5
        Z=R.^2.*cos(2*A);

    case 6
        %astig
        Z=R.^2.*sin(2*A);

    case 7
        Z=(3*R.^3-2.*R).*cos(A);

    case 8
        Z=(3*R.^3-2.*R).*sin(A);

    case 9
        Z=6*R.^4-6*R.^2+1;

    case 10
        Z=R.^3.*cos(3*A);

    case 11
        Z=R.^3.*sin(3*A);

    case 12
        Z=(4*R.^4-3.*R.^2).*cos(2*A);

    case 13
        Z=(4*R.^4-3.*R.^2).*sin(2*A);

    case 14
        Z=(10*R.^5-12.*R.^3+3*R).*cos(A);

    case 15
        Z=(10*R.^5-12.*R.^3+3*R).*sin(A);

    case 16
        Z=20*R.^6-30*R.^4+12*R.^2-1;

    case 17
        Z=R.^4.*cos(4*A);

    case 18
        Z=R.^4.*sin(4*A);

    case 19
        Z=(5*R.^5-4.*R.^3).*cos(3*A);

    case 20
        Z=(5*R.^5-4.*R.^3).*sin(3*A);

    case 21
        Z=(15.*R.^6-20.*R.^4+6.*R.^2).*cos(2*A);

    case 22
        Z=(15.*R.^6-20.*R.^4+6.*R.^2).*sin(2*A);

    case 23
        Z=(35.*R.^7-60.*R.^5+30.*R.^3-4.*R).*cos(A);

    case 24
        Z=(35.*R.^7-60.*R.^5+30.*R.^3-4.*R).*sin(A);

    case 25
        Z=70.*R.^8-140*R.^6+90*R.^4-20.*R.^2+1;

    case 26
        Z=R.^5.*cos(5*A) ;

    case 27
        Z=R.^5.*sin(5*A) ;

    case 28
        Z=(6*R.^2-5).*R.^4.*cos(4*A) ;

    case 29
        Z=(6*R.^2-5).*R.^4.*sin(4*A) ;

    case 30
        Z=(21*R.^4-30*R.^2+10).*R.^3.*cos(3*A) ;

    case 31
        Z=(21*R.^4-30*R.^2+10).*R.^3.*sin(3*A) ;

    case 32
        Z=(56*R.^6-105*R.^4+60*R.^2-10).*R.^2.*cos(2*A) ;

    case 33
        Z=(56*R.^6-105*R.^4+60*R.^2-10).*R.^2.*sin(2*A) ;

    case 34
        Z=(126*R.^8-280*R.^6+210*R.^4-60*R.^2+5).*R.*cos(A) ;

    case 35
        Z=(126*R.^8-280*R.^6+210*R.^4-60*R.^2+5).*R.*sin(A) ;

    case 36
        Z=252*R.^10-630*R.^8+560*R.^6-210*R.^4+30*R.^2-1 ;

    case 37
        Z=924*R.^12-2772*R.^10+3150*R.^8-1680*R.^6+420*R.^4-42*R.^2+1 ;

end

ihors_pupille=find(R>1);
%Z(ihors_pupille)=zeros(size(ihors_pupille));
