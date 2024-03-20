/*!
 * \file    device.h
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

#ifndef DEVICE_H
#define DEVICE_H

#include <peak/peak.hpp>

#include <memory>

class Device
{
public:
    explicit Device();

    std::shared_ptr<peak::core::DataStream> DataSteam() const
    {
        return m_dataStream;
    };
    std::shared_ptr<peak::core::NodeMap> RemoteNodeMap() const
    {
        return m_nodemapRemoteDevice;
    }

    void FindAndOpen();
    void OpenDataStream();
    void StopAcquisition();
    void LoadDefaults();
    void DisableAutoFeatures();

    bool IsMono() const;
    bool HasGain() const;

    double Gain() const;
    double Exposure() const;
    double Framerate() const
    {
        return m_frameRate;
    }

    void SetGain(double value);
    void SetExposure(double value);
    void SetFrameRate(double value);

    std::pair<double, double> GainRange() const;
    std::pair<double, double> ExposureRange() const;
    std::pair<double, double> FramerateRange() const;

    void UpdateFramerate();

private:
    std::shared_ptr<peak::core::Device> m_device{};
    std::shared_ptr<peak::core::DataStream> m_dataStream{};
    std::shared_ptr<peak::core::NodeMap> m_nodemapRemoteDevice{};

    bool m_hasGain{};
    std::string m_gainType{};

    double m_frameRate;

    void CheckGain();
};

#endif // DEVICE_H
