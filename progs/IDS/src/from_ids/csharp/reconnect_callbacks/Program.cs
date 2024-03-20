/*!
 * \file    Program.cs
 * \author  IDS Imaging Development Systems GmbH
 * \date    2023-11-03
 *
 * \brief   This application demonstrates how to register device connection change callbacks and handle a reconnected device
 *
 * \version 1.0.0
 *
 * Copyright (C) 2023 - 2024, IDS Imaging Development Systems GmbH.
 *
 * The information in this document is subject to change without notice
 * and should not be construed as a commitment by IDS Imaging Development Systems GmbH.
 * IDS Imaging Development Systems GmbH does not assume any responsibility for any errors
 * that may appear in this document.
 *
 * This document, or source code, is provided solely as an example of how to utilize
 * IDS Imaging Development Systems GmbH software libraries in a sample application.
 * IDS Imaging Development Systems GmbH does not assume any responsibility
 * for the use or reliability of any portion of this document.
 *
 * General permission to copy or modify is hereby granted.
 */

using System;
using peak.core;
using peak.core.nodes;

namespace ReconnectCallbacks
{
    internal class Program
    {
        static void Main(string[] args)
        {
            peak.Library.Initialize();

            var deviceManager = peak.DeviceManager.Instance();
            bool acquisitionRunning = false;

            // ids_peak provides several events that you can subscribe to in order
            // to be notified when the connection status of a device changes.
            //
            // The 'found' event is triggered if a new device is found upon calling
            // `DeviceManager.Update()`
            deviceManager.DeviceFoundEvent += (object sender, DeviceDescriptor foundDevice) =>
            {
                Console.WriteLine($"Found-Device-Callback: Key={foundDevice.Key()}");
            };
            // The 'lost' event is only called for this application's opened devices if
            // a device is closed explicitly or if connection is lost while the reconnect is disabled,
            // otherwise the 'disconnected' event is triggered.
            // Other devices that were not opened or were opened by someone else still trigger
            // a 'lost' event.
            deviceManager.DeviceLostEvent += (object sender, string deviceKey) =>
            {
                Console.WriteLine($"Lost-Device-Callback: Key={deviceKey}");
            };
            // Only called if the reconnect is enabled and if the device was previously opened by this
            // application instance.
            deviceManager.DeviceDisconnectedEvent += (object sender, DeviceDescriptor disconnectedDevice) =>
            {
                Console.WriteLine($"Disconnected-Device-Callback: Key={disconnectedDevice.Key()}");
            };

            // When a device that was opened by the same application instance regains connection
            // after a previous disconnect the 'Reconnected' event is triggered.
            deviceManager.DeviceReconnectedEvent += (
                    object sender,
                    DeviceDescriptor reconnectedDevice,
                    DeviceReconnectInformation reconnectInformation) =>
            {
                Console.WriteLine($"Reconnected-Device-Callback:\n" +
                    $"\tKey={reconnectedDevice.Key()}\n" +
                    $"\tReconnectSuccessful: {reconnectInformation.IsSuccessful()}\n" +
                    $"\tRemoteDeviceAcquisitionRunning: {reconnectInformation.IsRemoteDeviceAcquisitionRunning()}\n" +
                    $"\tRemoteDeviceConfigurationRestored: {reconnectInformation.IsRemoteDeviceConfigurationRestored()}\n");

                // Using the `reconnectInformation` the user can tell whether they need to take actions
                // in order to resume the image acquisition.
                if (reconnectInformation.IsSuccessful())
                {
                    // Device was reconnected successfully, nothing to do.
                    return;
                }

                EnsureCompatibleBuffersAndRestartAcquisition(reconnectedDevice, reconnectInformation);
            };
            deviceManager.DeviceListChangedEvent += (object sender) =>
            {
                Console.WriteLine($"Device-List-Changed-Callback");
            };

            deviceManager.Update(peak.DeviceManager.UpdatePolicy.ScanEnvironmentForProducerLibraries);

            peak.core.Device device = null;
            foreach(var dev in deviceManager.Devices())
            {
                if(dev.IsOpenable(DeviceAccessType.Control))
                {
                    device = dev.OpenDevice(DeviceAccessType.Control);
                    break;
                }
            }
            if (device == null)
            {
                Console.WriteLine("No device found. Exiting program!");
                peak.Library.Close();
                return;
            }

            Console.WriteLine($"Using Device {device.DisplayName()}");

            var systemNodeMap = device.ParentInterface().ParentSystem().NodeMaps()[0];
            if (!EnableReconnect(systemNodeMap))
            {
                peak.Library.Close();
                return;
            }

            var remoteDeviceNodeMap = device.RemoteDevice().NodeMaps()[0];

            // NOTE: Uncommenting these lines will modify the PayloadSize without saving the
            // changes in the UserSet. If the device reboots (e.g. by losing and then regaining
            // power) the PayloadSize will have changed, which means the acquisition on
            // the remote device will not be restarted.
            // In order to restart the acquisition additional steps are required:
            // see "The payload size might have changed." above
            // remoteDeviceNodeMap.FindNode<IntegerNode>("Height").SetValue(512);
            // remoteDeviceNodeMap.FindNode<IntegerNode>("Width").SetValue(512);

            var dataStream = device.DataStreams()[0].OpenDataStream();

            var payloadSize = (uint)remoteDeviceNodeMap.FindNode<IntegerNode>("PayloadSize").Value();
            var minBuffers = dataStream.NumBuffersAnnouncedMinRequired();
            for (int i = 0; i < minBuffers; i++)
            {
                var buffer = dataStream.AllocAndAnnounceBuffer(payloadSize, IntPtr.Zero);
                dataStream.QueueBuffer(buffer);
            }

            dataStream.StartAcquisition();
            remoteDeviceNodeMap.FindNode<CommandNode>("AcquisitionStart").Execute();
            acquisitionRunning = true;

            Console.CancelKeyPress += (sender, eventArgs) =>
            {
                Console.WriteLine("KeyboardInterrupt: Exiting program...");
                acquisitionRunning = false;
                dataStream.KillWait();
                // The process should not be terminated immediately.
                eventArgs.Cancel = true;
            };

            Console.WriteLine("Now you can disconnect or reboot the device to trigger a reconnect!");
            while (acquisitionRunning)
            {
                try
                {
                    var buffer = dataStream.WaitForFinishedBuffer(peak.core.Timeout.INFINITE_TIMEOUT);
                    Console.WriteLine($"Received Frame ID: {buffer.FrameID()}");
                    dataStream.QueueBuffer(buffer);
                }
                catch (Exception e)
                {
                    Console.WriteLine($"Error getting frame: {e.Message}");
                }
            }

            peak.Library.Close();
        }

        static void EnsureCompatibleBuffersAndRestartAcquisition(DeviceDescriptor reconnectedDevice, DeviceReconnectInformation reconnectInformation)
        {
            var device = reconnectedDevice.OpenedDevice();
            var remoteDeviceNodeMap = device.RemoteDevice().NodeMaps()[0];
            var dataStream = device.DataStreams()[0].OpenedDataStream();
            var payloadSize = (uint)remoteDeviceNodeMap.FindNode<IntegerNode>("PayloadSize").Value();

            bool hasPayloadSizeMismatch = payloadSize != dataStream.AnnouncedBuffers()[0].Size();

            // The payload size might have changed. In this case it's required to reallocate the buffers.
            if (hasPayloadSizeMismatch)
            {
                Console.WriteLine("PayloadSize has changed. Reallocating buffers...");

                bool isDataSteamGrabbing = dataStream.IsGrabbing();
                if (isDataSteamGrabbing)
                {
                    dataStream.StopAcquisition();
                }

                // Discard all buffers from the acquisition engine.
                // They remain in the announced buffer pool.
                dataStream.Flush(DataStreamFlushMode.DiscardAll);
                var numBuffersBefore = dataStream.AnnouncedBuffers().Count;

                // Remove them from the announced pool.
                foreach (var buffer in dataStream.AnnouncedBuffers())
                {
                    dataStream.RevokeBuffer(buffer);
                }

                // Allocate and queue the buffers using the new "PayloadSize".
                var minBuffers = dataStream.NumBuffersAnnouncedMinRequired();
                var numBuffers = Math.Max(minBuffers, numBuffersBefore);
                for (int i = 0; i < numBuffers; i++)
                {
                    var buffer = dataStream.AllocAndAnnounceBuffer(payloadSize, IntPtr.Zero);
                    dataStream.QueueBuffer(buffer);
                }

                if (isDataSteamGrabbing)
                {
                    dataStream.StartAcquisition();
                }
            }

            if (!reconnectInformation.IsRemoteDeviceAcquisitionRunning())
            {
                remoteDeviceNodeMap.FindNode<CommandNode>("AcquisitionStart").Execute();
            }
        }

        static bool EnableReconnect(peak.core.NodeMap systemNodeMap)
        {
            if(!systemNodeMap.HasNode("ReconnectEnable"))
            {
                Console.WriteLine("ReconnectEnable not found!");
                return false;
            }

            var reconnectEnableNode = systemNodeMap.FindNode<BooleanNode>("ReconnectEnable");
            var reconnectEnableAccessStatus = reconnectEnableNode.AccessStatus();

            if (reconnectEnableAccessStatus == peak.core.nodes.NodeAccessStatus.ReadWrite)
            {
                reconnectEnableNode.SetValue(true);
                return true;
            }

            if (reconnectEnableAccessStatus == peak.core.nodes.NodeAccessStatus.ReadOnly)
            {
                if (reconnectEnableNode.Value())
                {
                    return true;
                }
            }

            Console.WriteLine("Error: ReconnectEnable cannot be set to true.");
            return false;
        }
    }
}
