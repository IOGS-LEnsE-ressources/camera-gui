function affichagemenu(tousmenus, menu)

m=size(tousmenus,1);
for i=1:m
    tous=char(tousmenus(i));
    h=findobj('Tag',tous);
    set(h,'visible','off');
end
m=size(menu,1);
for i=1:m
    tous=char(menu(i));
    tous=findobj('Tag',tous);
    set(tous,'visible','on');
end
