/*!
 * \file    device.cpp
 * \author  IDS Imaging Development Systems GmbH
 * \date    2023-05-15
 *
 * \version 1.3.0
 *
 * Copyright (C) 2021 - 2024, IDS Imaging Development Systems GmbH.
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

#include "device.h"

namespace
{
bool IsAccessable(const std::shared_ptr<peak::core::nodes::Node>& node)
{
    try
    {
        if ((peak::core::nodes::NodeAccessStatus::NotAvailable == node->AccessStatus())
            || (peak::core::nodes::NodeAccessStatus::NotImplemented == node->AccessStatus()))
        {
            return false;
        }
        else
        {
            return true;
        }
    }
    catch (const std::exception&)
    {}

    return false;
}

bool IsWriteAble(const std::shared_ptr<peak::core::nodes::Node>& node)
{
    try
    {
        if (peak::core::nodes::NodeAccessStatus::ReadWrite == node->AccessStatus()
            || peak::core::nodes::NodeAccessStatus::WriteOnly == node->AccessStatus())
        {
            return true;
        }
        else
        {
            return false;
        }
    }
    catch (const std::exception&)
    {}

    return false;
}
} // namespace

Device::Device()
{
    FindAndOpen();
    LoadDefaults();
    OpenDataStream();
    DisableAutoFeatures();
}

void Device::FindAndOpen()
{
    auto& deviceManager = peak::DeviceManager::Instance();

    // Update the device manager
    deviceManager.Update();

    // Return if no device was found
    if (deviceManager.Devices().empty())
    {
        throw std::runtime_error("No device found");
    }

    // open the first openable device in the device manager's device list
    size_t deviceCount = deviceManager.Devices().size();
    for (size_t i = 0; i < deviceCount; ++i)
    {
        if (deviceManager.Devices().at(i)->IsOpenable())
        {
            m_device = deviceManager.Devices().at(i)->OpenDevice(peak::core::DeviceAccessType::Control);

            // stop after the first opened device
            break;
        }
        else if (i == (deviceCount - 1))
        {
            throw std::runtime_error("Device could not be opened");
        }
    }

    m_nodemapRemoteDevice = m_device->RemoteDevice()->NodeMaps().at(0);
    CheckGain();
}

void Device::OpenDataStream()
{
    if (m_device)
    {
        // Open standard data stream
        auto dataStreams = m_device->DataStreams();
        if (dataStreams.empty())
        {
            throw std::runtime_error("Device has no DataStream");
        }

        // Open standard data stream
        m_dataStream = dataStreams.at(0)->OpenDataStream();

        // Get the payload size for correct buffer allocation
        auto payloadSize = m_nodemapRemoteDevice->FindNode<peak::core::nodes::IntegerNode>("PayloadSize")
                               ->Value();

        // Get the minimum number of buffers that must be announced
        auto bufferCountMax = m_dataStream->NumBuffersAnnouncedMinRequired();

        // Allocate and announce image buffers and queue them
        for (size_t bufferCount = 0; bufferCount < bufferCountMax; ++bufferCount)
        {
            auto buffer = m_dataStream->AllocAndAnnounceBuffer(static_cast<size_t>(payloadSize), nullptr);
            m_dataStream->QueueBuffer(buffer);
        }
    }
}

void Device::LoadDefaults()
{
    // To prepare for untriggered continuous image acquisition, load the default user set if available
    // and wait until execution is finished
    try
    {
        m_nodemapRemoteDevice->FindNode<peak::core::nodes::EnumerationNode>("UserSetSelector")
            ->SetCurrentEntry("Default");

        m_nodemapRemoteDevice->FindNode<peak::core::nodes::CommandNode>("UserSetLoad")->Execute();
        m_nodemapRemoteDevice->FindNode<peak::core::nodes::CommandNode>("UserSetLoad")->WaitUntilDone();

        // Set exposure to minimum
        double exposure = m_nodemapRemoteDevice->FindNode<peak::core::nodes::FloatNode>("ExposureTime")
                              ->Minimum();
        m_nodemapRemoteDevice->FindNode<peak::core::nodes::FloatNode>("ExposureTime")->SetValue(exposure);

        // Set frame rate
        const auto frameRate = (std::min)(
            m_nodemapRemoteDevice->FindNode<peak::core::nodes::FloatNode>("AcquisitionFrameRate")->Maximum(),
            25.0);
        m_nodemapRemoteDevice->FindNode<peak::core::nodes::FloatNode>("AcquisitionFrameRate")
            ->SetValue(frameRate);

        m_frameRate = m_nodemapRemoteDevice->FindNode<peak::core::nodes::FloatNode>("AcquisitionFrameRate")
                          ->Value();
    }
    catch (const peak::core::NotFoundException&)
    {
        // UserSet is not available
    }
}

void Device::DisableAutoFeatures()
{
    // Make sure that no auto feature is enabled by default
    try
    {
        m_nodemapRemoteDevice->FindNode<peak::core::nodes::EnumerationNode>("ExposureAuto")
            ->SetCurrentEntry("Off");
    }
    catch (const std::exception&)
    {
        // Ignore
    }
    try
    {
        m_nodemapRemoteDevice->FindNode<peak::core::nodes::EnumerationNode>("GainAuto")
            ->SetCurrentEntry("Off");
    }
    catch (const std::exception&)
    {
        // Ignore
    }
    try
    {
        m_nodemapRemoteDevice->FindNode<peak::core::nodes::EnumerationNode>("BalanceWhiteAuto")
            ->SetCurrentEntry("Off");
    }
    catch (const std::exception&)
    {
        // Ignore
    }
}

void Device::StopAcquisition()
{
    if (m_device)
    {
        auto remoteNodeMap = m_device->RemoteDevice()->NodeMaps().at(0);
        remoteNodeMap->FindNode<peak::core::nodes::CommandNode>("AcquisitionStop")->Execute();
    }

    // if data stream was opened, try to stop it and revoke its image buffers
    if (m_dataStream)
    {
        m_dataStream->KillWait();
        m_dataStream->StopAcquisition(peak::core::AcquisitionStopMode::Default);
        m_dataStream->Flush(peak::core::DataStreamFlushMode::DiscardAll);

        for (const auto& buffer : m_dataStream->AnnouncedBuffers())
        {
            m_dataStream->RevokeBuffer(buffer);
        }
    }
}


bool Device::IsMono() const
{
    auto pixelFormat = m_nodemapRemoteDevice->FindNode<peak::core::nodes::EnumerationNode>("PixelFormat")
                           ->CurrentEntry()
                           ->SymbolicValue();
    return ("Mono" == pixelFormat.substr(0, 4));
}

bool Device::HasGain() const
{
    return m_hasGain;
}

void Device::CheckGain()
{
    m_hasGain = false;
    m_gainType.clear();

    try
    {
        if (!m_nodemapRemoteDevice->HasNode("GainSelector"))
        {
            return;
        }

        const auto node = m_nodemapRemoteDevice->FindNode<peak::core::nodes::EnumerationNode>(
            "GainSelector");
        if (!IsAccessable(node) || !IsWriteAble(node))
        {
            return;
        }

        const auto entries = node->Entries();
        for (const auto& gainType : { "AnalogAll", "DigitalAll", "All"})
        {
            auto found = std::any_of(entries.cbegin(), entries.cend(), [gainType](const auto& entry) {
                return gainType == entry->StringValue() && IsAccessable(entry) ;
            });

            if (found)
            {
                m_hasGain = true;
                m_gainType = gainType;
                return;
            }
        }
    }
    catch (std::exception&)
    {

    }
}

double Device::Gain() const
{
    try
    {
        auto lock = m_nodemapRemoteDevice->Lock();
        m_nodemapRemoteDevice->FindNode<peak::core::nodes::EnumerationNode>("GainSelector")
            ->SetCurrentEntry(m_gainType);
        return m_nodemapRemoteDevice->FindNode<peak::core::nodes::FloatNode>("Gain")->Value();
    }
    catch (const std::exception&)
    {
        return {};
    }
}

double Device::Exposure() const
{
    try
    {
        return m_nodemapRemoteDevice->FindNode<peak::core::nodes::FloatNode>("ExposureTime")->Value();
    }
    catch (const std::exception&)
    {
        return {};
    }
}

void Device::SetGain(double value)
{
    try
    {
        auto lock = m_nodemapRemoteDevice->Lock();
        m_nodemapRemoteDevice->FindNode<peak::core::nodes::EnumerationNode>("GainSelector")
            ->SetCurrentEntry(m_gainType);
        m_nodemapRemoteDevice->FindNode<peak::core::nodes::FloatNode>("Gain")->SetValue(value);
    }
    catch (const std::exception&)
    {

    }
}

void Device::SetExposure(double value)
{
    try
    {
        return m_nodemapRemoteDevice->FindNode<peak::core::nodes::FloatNode>("ExposureTime")->SetValue(value);
    }
    catch (const std::exception&)
    {

    }
}

std::pair<double, double> Device::GainRange() const
{
    try
    {
        auto lock = m_nodemapRemoteDevice->Lock();
        m_nodemapRemoteDevice->FindNode<peak::core::nodes::EnumerationNode>("GainSelector")
            ->SetCurrentEntry(m_gainType);
        const auto& node = m_nodemapRemoteDevice->FindNode<peak::core::nodes::FloatNode>("Gain");
        return { node->Minimum(), node->Maximum()};
    }
    catch (const std::exception&)
    {
        return {};
    }
}

std::pair<double, double> Device::ExposureRange() const
{
    try
    {
        const auto& node = m_nodemapRemoteDevice->FindNode<peak::core::nodes::FloatNode>("ExposureTime");
        return { node->Minimum(), node->Maximum()};
    }
    catch (const std::exception&)
    {
        return {};
    }
}

void Device::SetFrameRate(double value)
{
    try
    {
        return m_nodemapRemoteDevice->FindNode<peak::core::nodes::FloatNode>("AcquisitionFrameRate")->SetValue(value);
    }
    catch (const std::exception&)
    {

    }
}

std::pair<double, double> Device::FramerateRange() const
{
    try
    {
        const auto& node = m_nodemapRemoteDevice->FindNode<peak::core::nodes::FloatNode>("AcquisitionFrameRate");
        return { node->Minimum(), node->Maximum()};
    }
    catch (const std::exception&)
    {
        return {};
    }
}

void Device::UpdateFramerate()
{
    try
    {
        m_frameRate = m_nodemapRemoteDevice->FindNode<peak::core::nodes::FloatNode>("AcquisitionFrameRate")
                          ->Value();
    }
    catch (const std::exception&)
    {
    }
}
