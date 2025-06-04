import os
import time
import sys
import clr
#from win32cryptcon import SCHANNEL_ENC_KEY

clr.AddReference("C:\\Program Files\\Thorlabs\\Kinesis\\Thorlabs.MotionControl.DeviceManagerCLI.dll")
clr.AddReference("C:\\Program Files\\Thorlabs\\Kinesis\\Thorlabs.MotionControl.GenericMotorCLI.dll")
clr.AddReference("C:\\Program Files\\Thorlabs\\Kinesis\\ThorLabs.MotionControl.Benchtop.StepperMotorCLI.dll")
clr.AddReference("C:\\Program Files\\Thorlabs\\Kinesis\\ThorLabs.MotionControl.KCube.PiezoCLI.dll")
from Thorlabs.MotionControl.DeviceManagerCLI import *
from Thorlabs.MotionControl.GenericMotorCLI import *
from Thorlabs.MotionControl.Benchtop.StepperMotorCLI import *
from Thorlabs.MotionControl.KCube.PiezoCLI import *
from System import Decimal  # necessary for real world units

class Motor:
    """
    Class for controlling Thorlabs BSC20x step motor, through a DRV208 controller.
    """
    def __init__(self, serial_no = "40897338"):
        self.serial_no = serial_no
        try:
            # device_list = DeviceManagerCLI.BuildDeviceList()

            # Connect, begin polling, and enable
            self.device = BenchtopStepperMotor.CreateBenchtopStepperMotor(self.serial_no)
            self.device.Connect(self.serial_no)
            time.sleep(0.25)  # wait statements are important to allow settings to be sent to the device

            # For benchtop devices, get the channel
            self.channel = self.device.GetChannel(1)

            # Ensure that the device settings have been initialized
            if not self.channel.IsSettingsInitialized():
                self.channel.WaitForSettingsInitialized(10000)  # 10 second timeout
                assert self.channel.IsSettingsInitialized() is True

            # Start polling and enable
            self.channel.StartPolling(250)  # 250ms polling rate
            time.sleep(0.25)
            self.channel.EnableDevice()
            time.sleep(0.25)  # Wait for device to enable

            # Get Device Information and display description
            device_info = self.channel.GetDeviceInfo()
            #print(device_info.Description)
            #print(f'Device ID : {channel.DeviceID}')

            ## Load any configuration settings needed by the controller/stage
            channel_config = self.channel.LoadMotorConfiguration(channel.DeviceID)
            chan_settings = self.channel.MotorDeviceSettings

            self.channel.GetSettings(chan_settings)
            channel_config.DeviceSettingsName = 'DRV208'
            channel_config.UpdateCurrentConfiguration()
            self.channel.SetSettings(chan_settings, True, False)

            #print(f'Position = {channel.DevicePosition}')

            ## Get parameters related to homing/zeroing/other
            # Home or Zero the device (if a motor/piezo)
            print("Retour à zéro du moteur")
            self.channel.Home(50000)
            print("Retour à zéro effectué")

            self.pos = channel.DevicePosition

        except Exception as e:
            # this can be bad practice: It sometimes obscures the error source
            print(e)

    def move_motor(self, position:float, sleep_time = 1):
        """
        Move the motor to the position.
        :param position: desired position, in mm.
        :param sleep_time: Pause between movement of the motor, in s.
        """
        if 7 >= position > 0:
            time.sleep(sleep_time) # Useful ?
            print("Mise en position du moteur ...")
            self.channel.MoveTo(Decimal(position), 50000)  # Move to 1 mm
            self.pos = channel.DevicePosition
            print(f"Position = {self.pos}mm")
            time.sleep(sleep_time)

        else:
            print(f"la position choisie doit être comprise entre 0 et 7mm")

    def home_motor(self, sleep_time = 1):
        """
        Move the motor to its home position.
        :param sleep_time: Pause between movement of the motor, in s.
        """
        time.sleep(sleep_time)  # Useful ?
        print("Retour à zéro du moteur")
        self.channel.Home(50000)
        print("Retour à zéro effectué")
        time.sleep(sleep_time)

    def disconnect_motor(self):
        """
        Disconnect the motor.
        """
        self.channel.StopPolling()
        self.device.Disconnect()



class Piezo:
    """
    Class for controlling Thorlabs KPZ step motor, through a DRV208 controller.
    """
    def __init__(self, serial_no = "29501399"):
        SimulationManager.Instance.InitializeSimulations()
        self.serial_no = serial_no  # Replace this line with your device's serial number

        try:
            print(f"Initialisation...")
            DeviceManagerCLI.BuildDeviceList()

            # Connect, begin polling, and enable
            self.device = KCubePiezo.CreateKCubePiezo(self.serial_no)

            self.device.Connect(self.serial_no)

            # Get Device Information and display description
            device_info = self.device.GetDeviceInfo()
            #print(device_info.Description)

            # Start polling and enable
            self.device.StartPolling(250)  # 250ms polling rate
            time.sleep(0.25)
            self.device.EnableDevice()
            time.sleep(0.25)  # Wait for device to enable

            if not self.device.IsSettingsInitialized():
                self.device.WaitForSettingsInitialized(10000)  # 10 second timeout
                assert self.device.IsSettingsInitialized() is True

            # Load the device configuration
            device_config = self.device.GetPiezoConfiguration(self.serial_no)

            # This shows how to obtain the device settings
            device_settings = self.device.PiezoDeviceSettings

            # Set the Zero point of the device
            #print("Setting Zero Point")
            self.device.SetZero()

            # Get the maximum voltage output of the KPZ
            max_voltage = self.device.GetMaxOutputVoltage()  # This is stored as a .NET decimal
            #print(f'Max voltage {max_voltage}')
            self.device.SetMaxOutputVoltage(max_voltage)

            self.max_voltage = max_voltage
            print(f"Piezo initialisé")

        except Exception as e:
            # this can be bad practice: It sometimes obscures the error source
            print(e)

    def set_voltage_piezo(self, voltage: float):
        """
        Set a voltage to the piezo controller.
        :param voltage: voltage, in V.
        """
        max_voltage = self.max_voltage
        dev_voltage = Decimal(voltage)

        if dev_voltage != Decimal(0) and dev_voltage <= max_voltage:
            timeout = time.time() + 30
            self.device.SetOutputVoltage(dev_voltage)
            time.sleep(0.5)
            '''while (device.IsSetOutputVoltageActive()):
                time.sleep(30)
                if time.time() < timeout:
                    raise Exception("Timeout Exceeded")'''
            print(f"Tension appliquée {device.GetOutputVoltage()}")
        else:
            print(f'La tension doit être inférieure à {max_voltage}')

    def set_zero_piezo(self):
        self.device.SetZero()
        print(f"Piezo placé en zéro")

    def diconnect_piezo(self):
        self.device.StopPolling()
        self.device.Disconnect()


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

