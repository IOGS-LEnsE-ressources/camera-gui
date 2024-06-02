function value = read_config(item,default)

try
    
    S = load('-mat','config.dat') ;

    if (isfield(S,item))
        value = getfield(S,item) ;
    else
        save_config(item,default);
        value = default ;
    end
    
catch
    
    save_config(item,default);
    value = default;
end