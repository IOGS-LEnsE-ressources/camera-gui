/*!
* \file    floatcontrol.h
* \author  IDS Imaging Development Systems GmbH
* \date    2023-11-20
*
* \brief   The float control class combines a slider and a spin box to control float parameters
*
* \version 1.0.0
*
* Copyright (C) 2019 - 2024, IDS Imaging Development Systems GmbH.
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

#ifndef FLOATCONTROL_H
#define FLOATCONTROL_H

#include <QWidget>
#include <QHBoxLayout>
#include <QSlider>
#include <QDoubleSpinBox>

class FloatControl : public QWidget
{
    Q_OBJECT
public:
    explicit FloatControl(QWidget* parent = nullptr);

    void SetValue(double value);
    void SetRange(std::pair<double, double> range);

    double Value() const;

private:
    QHBoxLayout* m_layout{};
    QSlider* m_slider{};
    QDoubleSpinBox* m_spinBox{};

    constexpr static double m_sliderFInc = 1'000.0;

signals:
    void ValueChanged(double value);
};


#endif // FLOATCONTROL_H
