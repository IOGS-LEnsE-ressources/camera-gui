function  Piezo( volt )
%UNTITLED Summary of this function goes here
%   Detailed explanation goes here
  s = daq.createSession ('ni');
  s.addAnalogOutputChannel('Dev1','ao1', 'Voltage');
  outputSingleScan(s,volt);
  delete(s);
end
