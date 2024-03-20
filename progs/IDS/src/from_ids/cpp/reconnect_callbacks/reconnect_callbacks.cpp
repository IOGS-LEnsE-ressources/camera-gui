/*!
 * \file    reconnect_callbacks.cpp
 * \author  IDS Imaging Development Systems GmbH
 * \date    2023-11-09
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

#include <cstddef>
#include <iostream>

#include <peak/peak.hpp>


void EnsureCompatibleBuffersAndRestartAcquisition(
    const std::shared_ptr<peak::core::DeviceDescriptor>& reconnectedDevice,
    peak::core::DeviceReconnectInformation reconnectInformation);

bool EnableReconnect(const std::shared_ptr<peak::core::NodeMap>& nodeMapSystem);

int main()
{
    try
    {
        using namespace peak::core::nodes;
        using namespace peak::core;

        bool acquisitionRunning = false;

        peak::Library::Initialize();

        auto&& deviceManager = peak::DeviceManager::Instance();

        // ids_peak provides several events that you can subscribe to in order
        // to be notified when the connection status of a device changes.
        //
        // The 'found' event is triggered if a new device is found upon calling
        // `DeviceManager.Update()`
        deviceManager.RegisterDeviceFoundCallback(
            [](auto& foundDevice) { std::cout << "Found-Device-Callback: Key=" << foundDevice->Key() << "\n"; });

        // The 'lost' event is only called for this application's opened devices if
        // a device is closed explicitly or if connection is lost while the reconnect is disabled,
        // otherwise the 'disconnected' event is triggered.
        // Other devices that were not opened or were opened by someone else still trigger
        // a 'lost' event.
        deviceManager.RegisterDeviceLostCallback(
            [](const auto& deviceKey) { std::cout << "Lost-Device-Callback: Key=" << deviceKey << "\n"; });

        // Only called if the reconnect is enabled and if the device was previously opened by this
        // application instance.
        deviceManager.RegisterDeviceDisconnectedCallback([](auto& disconnectedDevice) {
            std::cout << "Disconnected-Device-Callback: Key=" << disconnectedDevice->Key() << "\n";
        });

        // When a device that was opened by the same application instance regains connection
        // after a previous disconnect the 'Reconnected' event is triggered.
        deviceManager.RegisterDeviceReconnectedCallback([](
                    const auto& reconnectedDevice, auto reconnectInformation) {
            std::cout << std::boolalpha
                    << "Reconnected-Device-Callback:\n"
                    << "\tKey=" << reconnectedDevice->Key() << "\n"
                    << "\tReconnectSuccessful: " << reconnectInformation.IsSuccessful() << "\n"
                    << "\tRemoteDeviceAcquisitionRunning: "
                    << reconnectInformation.IsRemoteDeviceAcquisitionRunning() << " \n"
                    << "\tRemoteDeviceConfigurationRestored: "
                    << reconnectInformation.IsRemoteDeviceConfigurationRestored()
                    << "\n";

            // Using the `reconnectInformation` the user can tell whether they need to take actions
            // in order to resume the image acquisition.
            if (reconnectInformation.IsSuccessful())
            {
                // Device was reconnected successfully, nothing to do.
                return;
            }

            EnsureCompatibleBuffersAndRestartAcquisition(reconnectedDevice, reconnectInformation);
        });

        deviceManager.RegisterDeviceListChangedCallback([]() { std::cout << "Device-List-Changed-Callback\n"; });

        deviceManager.Update(peak::DeviceManager::UpdatePolicy::ScanEnvironmentForProducerLibraries);

        // search for the first openable camera
        const auto& devices = deviceManager.Devices();
        const auto deviceIt = std::find_if(devices.cbegin(), devices.cend(), [](auto& device) {
            return device->IsOpenable(DeviceAccessType::Control);
        });

        if (deviceIt == devices.cend())
        {
            std::cout << "No (openable) device found. Exiting program!\n";
            peak::Library::Close();
            return -1;
        }

        const auto device = (*deviceIt)->OpenDevice(DeviceAccessType::Control);
        std::cout << "Using device " << device->DisplayName() << "\n";

        const auto systemNodeMap = device->ParentInterface()->ParentSystem()->NodeMaps().at(0);
        if (!EnableReconnect(systemNodeMap))
        {
            peak::Library::Close();
            return -1;
        }

        const auto remoteDeviceNodeMap = device->RemoteDevice()->NodeMaps()[0];

        // NOTE: Uncommenting these lines will modify the PayloadSize without saving the
        // changes in the UserSet. If the device reboots (e.g. by losing and then regaining
        // power) the PayloadSize will have changed, which means the acquisition on
        // the remote device will not be restarted.
        // In order to restart the acquisition additional steps are required:
        // see "The payload size might have changed." above
        // remoteDeviceNodeMap->FindNode<IntegerNode>("Height")->SetValue(512);
        // remoteDeviceNodeMap->FindNode<IntegerNode>("Width")->SetValue(512);

        const auto dataStream = device->DataStreams()[0]->OpenDataStream();

        const auto payloadSize = remoteDeviceNodeMap->FindNode<IntegerNode>("PayloadSize")->Value();
        const auto minBuffers = dataStream->NumBuffersAnnouncedMinRequired();
        for (int i = 0; i < minBuffers; i++)
        {
            auto buffer = dataStream->AllocAndAnnounceBuffer(payloadSize, nullptr);
            dataStream->QueueBuffer(buffer);
        }

        dataStream->StartAcquisition();
        remoteDeviceNodeMap->FindNode<CommandNode>("AcquisitionStart")->Execute();
        acquisitionRunning = true;

        std::cout << "Now you can disconnect or reboot the device to trigger a reconnect!\n";
        while (acquisitionRunning)
        {
            try
            {
                auto buffer = dataStream->WaitForFinishedBuffer(peak::core::Timeout::INFINITE_TIMEOUT);
                std::cout << "Received Frame ID: " << buffer->FrameID() << "\n";
                dataStream->QueueBuffer(buffer);
            }
            catch (const std::exception& e)
            {
                std::cout << "Error getting frame: " << e.what() << "\n";
            }
        }

        peak::Library::Close();

        return 0;
    }
    catch(const std::exception& e)
    {
        std::cout << "Exception: " << e.what() << "\n";

        return -1;
    }
}

void EnsureCompatibleBuffersAndRestartAcquisition(
    const std::shared_ptr<peak::core::DeviceDescriptor>& reconnectedDevice,
    peak::core::DeviceReconnectInformation reconnectInformation)
{
    const auto device = reconnectedDevice->OpenedDevice();
    const auto remoteDeviceNodeMap = device->RemoteDevice()->NodeMaps()[0];
    const auto dataStream = device->DataStreams()[0]->OpenedDataStream();
    const auto payloadSize = remoteDeviceNodeMap->FindNode<peak::core::nodes::IntegerNode>("PayloadSize")
                                 ->Value();

    const bool hasPayloadSizeMismatch = payloadSize != dataStream->AnnouncedBuffers()[0]->Size();

    // The payload size might have changed. In this case it's required to reallocate the buffers.
    if (hasPayloadSizeMismatch)
    {
        std::cout << "PayloadSize has changed. Reallocating buffers...\n";
        const bool isDataStreamRunning = dataStream->IsGrabbing();

        if (isDataStreamRunning)
        {
            dataStream->StopAcquisition();
        }

        // Discard all buffers from the acquisition engine.
        // They remain in the announced buffer pool.
        dataStream->Flush(peak::core::DataStreamFlushMode::DiscardAll);
        const auto numBuffersBefore = dataStream->AnnouncedBuffers().size();

        // Remove them from the announced pool.
        for (auto& buffer : dataStream->AnnouncedBuffers())
        {
            dataStream->RevokeBuffer(buffer);
        }

        // Allocate and queue the buffers using the new "PayloadSize".
        const auto minBuffers = dataStream->NumBuffersAnnouncedMinRequired();
        const auto numBuffers = std::max(minBuffers, numBuffersBefore);
        for (int i = 0; i < numBuffers; i++)
        {
            auto buffer = dataStream->AllocAndAnnounceBuffer(payloadSize, nullptr);
            dataStream->QueueBuffer(buffer);
        }

        if (isDataStreamRunning)
        {
            dataStream->StartAcquisition();
        }
    }

    if (!reconnectInformation.IsRemoteDeviceAcquisitionRunning())
    {
        remoteDeviceNodeMap->FindNode<peak::core::nodes::CommandNode>("AcquisitionStart")->Execute();
    }
}

bool EnableReconnect(const std::shared_ptr<peak::core::NodeMap>& nodeMapSystem)
{
    if (!nodeMapSystem->HasNode("ReconnectEnable"))
    {
        std::cout << "ReconnectEnable not found!\n";
        return false;
    }

    const auto& reconnectEnableNode = nodeMapSystem->FindNode<peak::core::nodes::BooleanNode>("ReconnectEnable");
    const auto reconnectEnableAccessStatus = reconnectEnableNode->AccessStatus();
    if (reconnectEnableAccessStatus == peak::core::nodes::NodeAccessStatus::ReadWrite)
    {
        reconnectEnableNode->SetValue(true);
        return true;
    }

    if (reconnectEnableAccessStatus == peak::core::nodes::NodeAccessStatus::ReadOnly)
    {
        const auto value = reconnectEnableNode->Value();
        if (value)
        {
            return true;
        }
    }

    std::cout << "Error: ReconnectEnable cannot be set to true.\n";
    return false;
}
