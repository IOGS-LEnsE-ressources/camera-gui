function varargout = spot_diagram_slider(varargin)
% spot_diagram_slider M-file for spot_diagram_slider.fig
%      SPOT_DIAGRAM_SLIDER, by itself, creates a new SPOT_DIAGRAM_SLIDER or raises the existing
%      singleton*.
%
%      H = SPOT_DIAGRAM_SLIDER returns the handle to a new spot_diagram_slider or the handle to
%      the existing singleton*.
%
%      SPOT_DIAGRAM_SLIDER('CALLBACK',hObject,eventData,handles,...) calls the local
%      function named CALLBACK in SPOT_DIAGRAM_SLIDER.M with the given input arguments.
%
%      SPOT_DIAGRAM_SLIDER('Property','Value',...) creates a new SPOT_DIAGRAM_SLIDER or raises the
%      existing singleton*.  Starting from the left, property value pairs are
%      applied to the GUI before spot_diagram_slider_OpeningFunction gets called.  An
%      unrecognized property name or invalid value makes property application
%      stop.  All inputs are passed to spot_diagram_slider_OpeningFcn via varargin.
%
%      *See GUI Options on GUIDE's Tools menu.  Choose "GUI allows only one
%      instance to run (singleton)".
%
% See also: GUIDE, GUIDATA, GUIHANDLES

% Copyright 2002-2003 The MathWorks, Inc.

% Edit the above text to modify the response to help spot_diagram_slider

% Last Modified by GUIDE v2.5 24-Apr-2007 00:25:15

% Begin initialization code - DO NOT EDIT
gui_Singleton = 1;
gui_State = struct('gui_Name',       mfilename, ...
                   'gui_Singleton',  gui_Singleton, ...
                   'gui_OpeningFcn', @spot_diagram_slider_OpeningFcn, ...
                   'gui_OutputFcn',  @spot_diagram_slider_OutputFcn, ...
                   'gui_LayoutFcn',  [] , ...
                   'gui_Callback',   []);
if nargin && ischar(varargin{1})
    gui_State.gui_Callback = str2func(varargin{1});
end

if nargout
    [varargout{1:nargout}] = gui_mainfcn(gui_State, varargin{:});
else
    gui_mainfcn(gui_State, varargin{:});
end
% End initialization code - DO NOT EDIT



% --- Executes just before spot_diagram_slider is made visible.
function spot_diagram_slider_OpeningFcn(hObject, eventdata, handles, varargin)
% This function has no output args, see OutputFcn.
% hObject    handle to figure
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)
% varargin   command line arguments to spot_diagram_slider (see VARARGIN)

handles.origines = varargin{2} ;
handles.angles = varargin{4} ;
handles.N = varargin{6} ;
handles.f = varargin{8} ;
handles.r = varargin{10} ;
handles.deltaf = 0 ;

set(handles.nbdefoc,'String','0') ;
set(handles.slddefoc,'Value',0) ;

% Choose default command line output for spot_diagram_slider
handles.output = hObject;

% Update handles structure
guidata(hObject, handles);

trace_spot_diagram(handles) ;

% UIWAIT makes spot_diagram_slider wait for user response (see UIRESUME)
% uiwait(handles.figure1);


% --- Outputs from this function are returned to the command line.
function varargout = spot_diagram_slider_OutputFcn(hObject, eventdata, handles) 
% varargout  cell array for returning output args (see VARARGOUT);
% hObject    handle to figure
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

% Get default command line output from handles structure
varargout{1} = handles.output;


% --- Executes on slider movement.
function slddefoc_Callback(hObject, eventdata, handles)
% hObject    handle to slddefoc (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

% Hints: get(hObject,'Value') returns position of slider
%        get(hObject,'Min') and get(hObject,'Max') to determine range of slider
deltaf = get(handles.slddefoc,'Value') ;
set(handles.nbdefoc,'String',num2str(deltaf,3)) ;
handles.deltaf = deltaf ;

guidata(hObject, handles);

trace_spot_diagram(handles) ;


% --- Executes during object creation, after setting all properties.
function slddefoc_CreateFcn(hObject, eventdata, handles)
% hObject    handle to slddefoc (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    empty - handles not created until after all CreateFcns called

% Hint: slider controls usually have a light gray background.
if isequal(get(hObject,'BackgroundColor'), get(0,'defaultUicontrolBackgroundColor'))
    set(hObject,'BackgroundColor',[.9 .9 .9]);
end


function nbdefoc_Callback(hObject, eventdata, handles)
% hObject    handle to nbdefoc (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

% Hints: get(hObject,'String') returns contents of nbdefoc as text
%        str2double(get(hObject,'String')) returns contents of nbdefoc as a double

deltaf = str2double(get(handles.nbdefoc,'String')) ;
if ( deltaf < get(handles.slddefoc,'Min') )
    deltaf = get(handles.slddefoc,'Min') ;
    set(handles.nbdefoc,'String',num2str(deltaf,3)) ;
elseif ( deltaf > get(handles.slddefoc,'Max') )
    deltaf = get(handles.slddefoc,'Max') ;
    set(handles.nbdefoc,'String',num2str(deltaf,3)) ;
end
set(handles.slddefoc,'Value',deltaf) ;

handles.deltaf = deltaf ;

guidata(hObject, handles);

trace_spot_diagram(handles) ;


% --- Executes during object creation, after setting all properties.
function nbdefoc_CreateFcn(hObject, eventdata, handles)
% hObject    handle to nbdefoc (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    empty - handles not created until after all CreateFcns called

% Hint: edit controls usually have a white background on Windows.
%       See ISPC and COMPUTER.
if ispc && isequal(get(hObject,'BackgroundColor'), get(0,'defaultUicontrolBackgroundColor'))
    set(hObject,'BackgroundColor','white');
end


