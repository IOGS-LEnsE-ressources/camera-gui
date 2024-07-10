function  daqoutfloat( volt )
%UNTITLED Summary of this function goes here
%   Detailed explanation goes here
s = daq.createSession ('ni');
 s.addAnalogOutputChannel('Dev1','ao0', 'Voltage');
 s.queueOutputData(volt);
s.startForeground;
delete(s)

end

