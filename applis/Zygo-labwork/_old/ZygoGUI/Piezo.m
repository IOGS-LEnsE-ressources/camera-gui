function  Piezo( volt )
%UNTITLED Summary of this function goes here
%   Detailed explanation goes here
  s = daq.createSession ('adi');
  s.addAnalogOutputChannel('Dev1','ao1', 'Voltage');
  s.IsContinuous= true
  outputSingleScan(s,volt);
  %delete(s);
end
