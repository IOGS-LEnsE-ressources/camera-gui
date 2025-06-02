import os
import time
import sys
import clr
from win32cryptcon import SCHANNEL_ENC_KEY

clr.AddReference("C:\\Program Files\\Thorlabs\\Kinesis\\Thorlabs.MotionControl.DeviceManagerCLI.dll")
clr.AddReference("C:\\Program Files\\Thorlabs\\Kinesis\\Thorlabs.MotionControl.GenericMotorCLI.dll")
clr.AddReference("C:\\Program Files\\Thorlabs\\Kinesis\\ThorLabs.MotionControl.Benchtop.StepperMotorCLI.dll")
clr.AddReference("C:\\Program Files\\Thorlabs\\Kinesis\\Thorlabs.MotionControl.DeviceManagerCLI.dll")
clr.AddReference("C:\\Program Files\\Thorlabs\\Kinesis\\Thorlabs.MotionControl.GenericMotorCLI.dll")
clr.AddReference("C:\\Program Files\\Thorlabs\\Kinesis\\ThorLabs.MotionControl.KCube.PiezoCLI.dll")
from Thorlabs.MotionControl.DeviceManagerCLI import *
from Thorlabs.MotionControl.GenericMotorCLI import *
from Thorlabs.MotionControl.Benchtop.StepperMotorCLI import *
from Thorlabs.MotionControl.KCube.PiezoCLI import *
from System import Decimal  # necessary for real world units

class Motor:
    def __init__(self):
        try:
            device_list = DeviceManagerCLI.BuildDeviceList()

            # create new device
            serial_no = "40897338"  # Replace this line with your device's serial number

            # Connect, begin polling, and enable
            device = BenchtopStepperMotor.CreateBenchtopStepperMotor(serial_no)
            device.Connect(serial_no)
            time.sleep(0.25)  # wait statements are important to allow settings to be sent to the device

            # For benchtop devices, get the channel
            channel = device.GetChannel(1)

            # Ensure that the device settings have been initialized
            if not channel.IsSettingsInitialized():
                channel.WaitForSettingsInitialized(10000)  # 10 second timeout
                assert channel.IsSettingsInitialized() is True

            # Start polling and enable
            channel.StartPolling(250)  # 250ms polling rate
            time.sleep(0.25)
            channel.EnableDevice()
            time.sleep(0.25)  # Wait for device to enable

            # Get Device Information and display description
            device_info = channel.GetDeviceInfo()
            #print(device_info.Description)
            #print(f'Device ID : {channel.DeviceID}')

            ## Load any configuration settings needed by the controller/stage
            channel_config = channel.LoadMotorConfiguration(channel.DeviceID)
            chan_settings = channel.MotorDeviceSettings

            channel.GetSettings(chan_settings)

            channel_config.DeviceSettingsName = 'DRV208'

            channel_config.UpdateCurrentConfiguration()

            channel.SetSettings(chan_settings, True, False)

            #print(f'Position = {channel.DevicePosition}')

            ## Get parameters related to homing/zeroing/other
            # Home or Zero the device (if a motor/piezo)
            print("Retour à zéro du moteur")
            channel.Home(50000)
            print("Retour à zéro effectué")

            self.device = device
            self.channel = channel
            self.pos = channel.DevicePosition

        except Exception as e:
            # this can be bad practice: It sometimes obscures the error source
            print(e)

    def move_motor(self, position:float, SleepTime = 1):
        '''
        déplace le moteur vers la position recherchée
        :param position: position recherchée
        :return: None
        '''
        if position <= 7 and position > 0:
            channel = self.channel
            time.sleep(SleepTime)
            print("Mise en position du moteur ...")
            channel.MoveTo(Decimal(position), 50000)  # Move to 1 mm
            self.pos = channel.DevicePosition
            print(f"Position = {self.pos}mm")
            time.sleep(SleepTime)

        else:
            print(f"la position choisie doit être comprise entre 0 et 7mm")

    def home_motor(self, SleepTime = 1):
        channel = self.channel
        time.sleep(SleepTime)
        print("Retour à zéro du moteur")
        channel.Home(50000)
        print("Retour à zéro effectué")
        time.sleep(SleepTime)

    def disconnect_motor(self):
        """
        Permet de désappairer le moteur
        """
        device = self.device
        channel = self.channel

        channel.StopPolling()
        device.Disconnect()



class Piezo:
    def __init__(self):
        SimulationManager.Instance.InitializeSimulations()

        try:
            print(f"Initialisation...")
            DeviceManagerCLI.BuildDeviceList()

            # create new device
            serial_no = "29501399"  # Replace this line with your device's serial number

            # Connect, begin polling, and enable
            device = KCubePiezo.CreateKCubePiezo(serial_no)

            device.Connect(serial_no)

            # Get Device Information and display description
            device_info = device.GetDeviceInfo()
            #print(device_info.Description)

            # Start polling and enable
            device.StartPolling(250)  # 250ms polling rate
            time.sleep(0.25)
            device.EnableDevice()
            time.sleep(0.25)  # Wait for device to enable

            if not device.IsSettingsInitialized():
                device.WaitForSettingsInitialized(10000)  # 10 second timeout
                assert device.IsSettingsInitialized() is True

            # Load the device configuration
            device_config = device.GetPiezoConfiguration(serial_no)

            # This shows how to obtain the device settings
            device_settings = device.PiezoDeviceSettings

            # Set the Zero point of the device
            #print("Setting Zero Point")
            device.SetZero()

            # Get the maximum voltage output of the KPZ
            max_voltage = device.GetMaxOutputVoltage()  # This is stored as a .NET decimal
            #print(f'Max voltage {max_voltage}')
            device.SetMaxOutputVoltage(max_voltage)

            self.device = device
            self.max_voltage = max_voltage
            print(f"Piezo initialisé")

        except Exception as e:
            # this can be bad practice: It sometimes obscures the error source
            print(e)

    def set_voltage_piezo(self, voltage: float):

        device = self.device
        max_voltage = self.max_voltage
        dev_voltage = Decimal(voltage)

        if dev_voltage != Decimal(0) and dev_voltage <= max_voltage:
            timeout = time.time() + 30
            device.SetOutputVoltage(dev_voltage)
            time.sleep(0.5)
            '''while (device.IsSetOutputVoltageActive()):
                time.sleep(30)
                if time.time() < timeout:
                    raise Exception("Timeout Exceeded")'''
            print(f"Tension appliquée {device.GetOutputVoltage()}")
        else:
            print(f'La tension doit être inférieure à {max_voltage}')

    def set_zero_piezo(self):
        device = self.device
        device.SetZero()
        print(f"Piezo placé en zéro")

    def diconnect_piezo(self):
        device = self.device
        device.StopPolling()
        device.Disconnect()


if __name__ == "__main__":
    P = Piezo()
    M = Motor()
    time.sleep(1)
    P.set_voltage_piezo(2)
    time.sleep(1)
    P.set_voltage_piezo(4)
    time.sleep(1)
    P.set_voltage_piezo(8)
    time.sleep(1)
    P.set_voltage_piezo(10)
    time.sleep(1)
    P.set_voltage_piezo(12)
    time.sleep(1)
    P.set_voltage_piezo(14)

