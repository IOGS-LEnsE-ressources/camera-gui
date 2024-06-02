function h=surfz(x,y,z,c)

source = [-45 70];	    			%Position de la source d'éclairage
%K = [0.8,1,0.5,1];				%K=[ka,kd,ks,spread]

error(nargchk(1,4,nargin));

if nargin==1,  % Generate x,y matrices for surface z.
  if min(size(x)) == 1 | isstr(x)
      error('Invalid input argument.')
  end
  z = x;
  [m,n] = size(z);
  [x,y] = meshgrid(0:n-1,0:m-1);
  c = z;

elseif nargin==2,
  if isstr(x) | isstr(y)
    error('Invalid input argument.')
  end
  if min(size(x)) == 1 | min(size(y)) == 1
      error('Invalid input argument.')
  end
  z = x; c = y;
  [m,n] = size(z);
  [x,y] = meshgrid(0:n-1,0:m-1);
  if ~isequal(size(c),size(z))
      error('Invalid input argument.')
  end

elseif nargin>=3,
  if isstr(x) | isstr(y) | isstr(z)
      error('Invalid input argument.')
  end
  [m,n] = size(z);
  [mx,nx] = size(x);
  [my,ny] = size(y);
  if m == 1 | n == 1
      error('Invalid input argument.')
  end
  if ~isequal(size(x),size(z)) | ~isequal(size(y),size(z)),
    % Create x and y vectors that are the same size as z.
    xmin = min(min(x)); ymin = min(min(y));
    xmax = max(max(x)); ymax = max(max(y));
    [x,y] = meshgrid(xmin+(0:n-1)/(n-1)*(xmax-xmin), ...
                     ymin+(0:m-1)/(m-1)*(ymax-ymin));
  end
  if nargin == 3
    c = z;
  end
  if ~isequal(size(c),size(z))
      error('Invalid input argument.')
  end
  if ~isequal(size(z),size(x)) | ~isequal(size(z),size(y))
      error('Invalid input argument.')
  end
end
if isstr(c)
      error('Invalid input argument.')
end

% Define position of curtains
zref = min(min(z(isfinite(z))))-(max(max(z(isfinite(z))))-min(min(z(isfinite(z)))))/2;

% Define new x,y,z and then call mesh.
zrow = zref*ones(1,n); zcol = zref*ones(m,1);
d = [1 1]; mm = [m m]; nn = [n n];
newZ = [zref zref   zrow   zref   zref;
        zref zref   z(1,:) zref   zref;
        zcol z(:,1) z      z(:,n) zcol;
        zref zref   z(m,:) zref   zref;
        zref zref   zrow   zref   zref];
newX = [x(d,d),x(d,:),x(d,nn);x(:,d),x,x(:,nn);x(mm,d),x(mm,:),x(mm,nn)];
newY = [y(d,d),y(d,:),y(d,nn);y(:,d),y,y(:,nn);y(mm,d),y(mm,:),y(mm,nn)];

    cref = (max(max(c(isfinite(c))))+min(min(c(isfinite(c)))))/2;
    crow = cref*ones(2,n); ccol = cref*ones(m,2); cref = cref*ones(2,2);
    c = [cref,crow,cref;ccol,c,ccol;cref,crow,cref];
    
    %hm=surfl(newX,newY,newZ,source);
    %hm=surfl(newX,newY,newZ);
    %SURFL(newX,newY,newZ,source,K)
    SURFL(newX,newY,newZ,source)
    %SURFL(newX,newY,newZ)

  
  if nargout > 0
    h = hm;
end

