function save_config(item,value)

try

    S = load('-mat','config.dat') ;
    S = setfield(S,item,value) ;
    
catch

    S = struct(item,value) ;
    
end

save('config.dat', '-struct', 'S') ;