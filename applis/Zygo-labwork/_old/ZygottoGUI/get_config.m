function get_config(item,value)

try

    S = load('-mat','config.dat') ;
    etude = getfield(S,'etude') ;
    type_acq = getfield(S,'typeacq');
    
    
catch

    S = struct(item,value) ;
    
end

save('config.dat', '-struct', 'S') ;