/*!
* \file    floatcontrol.cpp
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

#include "floatcontrol.h"

FloatControl::FloatControl(QWidget* parent)
    : QWidget(parent)
    , m_layout{new QHBoxLayout()}
    , m_slider{new QSlider(Qt::Orientation::Horizontal, this)}
    , m_spinBox{new QDoubleSpinBox(this)}
{
    m_spinBox->setFixedWidth(120);

    setLayout(m_layout);
    m_layout->setContentsMargins(0, 0, 0, 0);
    m_layout->addWidget(m_slider);
    m_layout->addWidget(m_spinBox);

    connect(m_spinBox, QOverload<double>::of(&QDoubleSpinBox::valueChanged), [this](const auto& value){
        m_slider->blockSignals(true);
        m_slider->setValue(static_cast<int>(value * m_sliderFInc));
        m_slider->blockSignals(false);
        emit ValueChanged(value);
    });

    connect(m_slider, &QSlider::valueChanged, [this](const auto& value){
        const auto doubleValue = static_cast<double>(value) / m_sliderFInc;
        m_spinBox->blockSignals(true);
        m_spinBox->setValue(doubleValue);
        m_spinBox->blockSignals(false);
        emit ValueChanged(doubleValue);
    });
}

void FloatControl::SetValue(double value)
{
    m_spinBox->setValue(value);
}

void FloatControl::SetRange(std::pair<double, double> range)
{
    m_spinBox->blockSignals(true);
    m_spinBox->setRange(range.first, range.second);
    m_spinBox->blockSignals(false);

    m_slider->blockSignals(true);
    m_slider->setRange(static_cast<int>(range.first * m_sliderFInc), static_cast<int>(range.second * m_sliderFInc));
    m_slider->blockSignals(false);
}

double FloatControl::Value() const
{
    return m_spinBox->value();
}
