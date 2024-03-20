/*!
 * \file    mainwindow.cpp
 * \author  IDS Imaging Development Systems GmbH
 * \date    2022-08-19
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

#include "mainwindow.h"
#include "floatcontrol.h"

#include "acquisitionworker.h"
#include "display.h"

#include <QDebug>
#include <QFrame>
#include <QMessageBox>
#include <QTimer>


#define VERSION "1.3.0"

namespace
{
constexpr int skip_frames_default = 2;
constexpr int skip_frames_min = 1;
constexpr int skip_frames_max = 10;
} // namespace


MainWindow::MainWindow(QWidget* parent)
    : QMainWindow(parent)
{
    // Create a display for the camera image
    m_display = new Display(this);
    m_display->setMinimumSize(640, 480);

    CreateControls();

    // initialize IDS peak genericAPI library
    peak::Library::Initialize();
    peak::afl::library::Init();

    try
    {
        OpenDevice();
        CreateAutoFeatures();

        // Create worker thread that waits for new images from the camera
        m_acquisitionWorker = new AcquisitionWorker();
        m_acquisitionWorker->SetDataStream(m_device->DataSteam());
        m_acquisitionWorker->moveToThread(&m_acquisitionThread);

        // worker must be started, when the acquisition starts, and deleted, when the worker thread finishes
        connect(&m_acquisitionThread, &QThread::started, m_acquisitionWorker, &AcquisitionWorker::Start);
        connect(&m_acquisitionThread, &QThread::destroyed, m_acquisitionWorker, &QObject::deleteLater);

        // Connect the 'image received' signal of the acquisition worker with the update slot of the display
        connect(m_acquisitionWorker, QOverload<QImage>::of(&AcquisitionWorker::imageReceived), m_display,
            &Display::onImageReceived);
        connect(m_acquisitionWorker, QOverload<const peak::ipl::Image*>::of(&AcquisitionWorker::imageReceived),
            this, &MainWindow::OnImageReceived, Qt::DirectConnection);

        // Connect the 'counter changed' signal of the acquisition worker with the update slot of the mainwindow
        connect(m_acquisitionWorker, &AcquisitionWorker::counterChanged, this, &MainWindow::OnCounterChanged);

        // Start thread execution
        m_acquisitionThread.start();

        m_updateTimer = new QTimer(this);
        connect(m_updateTimer, &QTimer::timeout, this, &MainWindow::UpdateValues);

        UpdateControls();
        m_updateTimer->start(500);
    }
    catch (const std::exception& e)
    {
        QMessageBox::information(this, "Exception", e.what(), QMessageBox::Ok);
        QTimer::singleShot(0, this, SLOT(close()));
    }
}

void MainWindow::UpdateControls()
{
    const auto disableButtonGroup = [](const QButtonGroup* buttonGroup) {
        buttonGroup->button(0)->setChecked(false);
        for (const auto button : buttonGroup->buttons())
        {
            button->setDisabled(true);
        }
    };

    if (!m_device->HasGain())
    {
        disableButtonGroup(m_groupGainAuto);
    }

    if (m_device->IsMono())
    {
        disableButtonGroup(m_groupBalanceWhiteAuto);
    }

    UpdateValues();
}

void MainWindow::OnImageReceived(const peak::ipl::Image* image)
{
    m_autoFeatures->ProcessImage(image);
}

MainWindow::~MainWindow()
{
    if (m_acquisitionWorker)
    {
        m_acquisitionWorker->Stop();
        m_acquisitionThread.quit();
        m_acquisitionThread.wait();
    }

    m_autoFeatures = nullptr;

    CloseDevice();

    // close IDS peak genericAPI library
    peak::Library::Close();
    peak::afl::library::Exit();
}

void MainWindow::OpenDevice()
{
    m_device = std::make_unique<Device>();
}

void MainWindow::CloseDevice()
{
    try
    {
        if (m_device)
        {
            // if device was opened, try to stop acquisition
            m_device->StopAcquisition();
            m_device = nullptr;
        }
    }
    catch (const std::exception& e)
    {
        QMessageBox::information(this, "Exception", e.what(), QMessageBox::Ok);
    }
}

void MainWindow::CreateAutoFeatures()
{
    m_autoFeatures = std::make_unique<AutoFeatures>(m_device->RemoteNodeMap());
    m_autoFeatures->RegisterGainCallback([&] { emit AutoGainFinished();});
    m_autoFeatures->RegisterExposureCallback([&] { emit AutoExposureFinished();});
    m_autoFeatures->RegisterWhiteBalanceCallback([&] { emit AutoBalanceWhiteFinished();});

    connect(this, &MainWindow::AutoGainFinished, this, [this](){
        m_groupGainAuto->button(0)->setChecked(true);
        m_controlGain->setEnabled(true);
    });
    connect(this, &MainWindow::AutoExposureFinished, this, [this](){
        m_groupExposureAuto->button(0)->setChecked(true);
        m_controlExposure->setEnabled(true);
    });
    connect(this, &MainWindow::AutoBalanceWhiteFinished, this, [this](){
        m_groupBalanceWhiteAuto->button(0)->setChecked(true);
    });
}

void MainWindow::CreateControls()
{
    auto mainLayout = new QVBoxLayout;
    mainLayout->addWidget(m_display);

    const auto cameraControls = CreateCameraControls();
    mainLayout->addLayout(cameraControls);

    mainLayout->addWidget(CreateHLine());

    const auto autoControlsLayout = CreateAutoControls();
    mainLayout->addLayout(autoControlsLayout);

    auto mainWidget = new QWidget(this);
    mainWidget->setLayout(mainLayout);

    const auto statusLayout = CreateStatusControls();
    mainLayout->addLayout(statusLayout);

    setCentralWidget(mainWidget);
}

QFrame* MainWindow::CreateHLine()
{
    auto hLine = new QFrame();
    hLine->setFrameShape(QFrame::Shape::HLine);
    hLine->setFrameShadow(QFrame::Shadow::Plain);
    hLine->setStyleSheet("QFrame{color: gray}");

    return hLine;
}

QLayout* MainWindow::CreateStatusControls()
{
    m_labelInfo = new QLabel();
    m_labelInfo->setAlignment(Qt::AlignLeft);

    auto labelVersion = new QLabel();
    labelVersion->setText(("host_auto_features_live_qtwidgets v" VERSION));
    labelVersion->setAlignment(Qt::AlignRight);

    auto labelAbout = new QLabel();
    labelAbout->setObjectName("aboutQt");
    labelAbout->setText(R"(<a href="#aboutQt">About Qt</a>)");
    labelAbout->setAlignment(Qt::AlignRight);
    connect(labelAbout, &QLabel::linkActivated, this, &MainWindow::OnAboutQtLinkActivated);

    auto statusLayout = new QHBoxLayout;
    statusLayout->setContentsMargins(0, 0, 0, 0);
    statusLayout->addWidget(m_labelInfo);
    statusLayout->addStretch();
    statusLayout->addWidget(labelVersion);
    statusLayout->addWidget(labelAbout);

    return statusLayout;
}

QLayout* MainWindow::CreateAutoControls()
{
    const auto createAutoControlButtons = [&](const QString& autoFeature, QButtonGroup* buttonGroup) -> QLayout* {
        auto label = new QLabel(this);
        label->setText(autoFeature);

        auto off = new QRadioButton("Off", this);
        off->setChecked(true);
        buttonGroup->addButton(off, static_cast<int>(PEAK_AFL_CONTROLLER_AUTOMODE_OFF));

        auto once = new QRadioButton("Once", this);
        buttonGroup->addButton(once, static_cast<int>(PEAK_AFL_CONTROLLER_AUTOMODE_ONCE));

        auto continuous = new QRadioButton("Continuous", this);
        buttonGroup->addButton(continuous, static_cast<int>(PEAK_AFL_CONTROLLER_AUTOMODE_CONTINUOUS));

        auto layout = new QHBoxLayout;
        layout->addWidget(label);
        for (const auto button : buttonGroup->buttons())
        {
            layout->addWidget(button);
        }

        return layout;
    };

    m_groupExposureAuto = new QButtonGroup(this);
    const auto exposureLayout = createAutoControlButtons("Exposure Auto", m_groupExposureAuto);
    connect(
        m_groupExposureAuto, QOverload<int>::of(&QButtonGroup::buttonClicked), this, &MainWindow::OnRadioExposureAuto);

    m_groupGainAuto = new QButtonGroup(this);
    const auto gainLayout = createAutoControlButtons("Gain Auto", m_groupGainAuto);
    connect(m_groupGainAuto, QOverload<int>::of(&QButtonGroup::buttonClicked), this, &MainWindow::OnRadioGainAuto);

    m_groupBalanceWhiteAuto = new QButtonGroup(this);
    const auto whiteBalanceLayout = createAutoControlButtons("Balance White Auto", m_groupBalanceWhiteAuto);

    connect(m_groupBalanceWhiteAuto, QOverload<int>::of(&QButtonGroup::buttonClicked), this,
        &MainWindow::OnRadioBalanceWhiteAuto);

    auto resetButton = new QPushButton("Reset all", this);
    connect(resetButton, &QPushButton::clicked, this, &MainWindow::OnButtonReset);

    auto optionsLayout = new QGridLayout;

    auto labelSkipFrames = new QLabel("Damping (skip frames)", this);
    optionsLayout->addWidget(labelSkipFrames, 0, 0);

    m_spinBoxSkipFrames = new QSpinBox(this);
    m_spinBoxSkipFrames->setToolTip(
        "Damping value from 1 to 10. Set higher values to avoid oscillation.\n\n"
        "1: skip one frame, calculate and set new image parameters for every second frame.\n"
        "2: skip two frames, calculate and set new image parameters for every third frame.\n"
        "...");
    m_spinBoxSkipFrames->setRange(skip_frames_min, skip_frames_max);
    m_spinBoxSkipFrames->setValue(skip_frames_default);
    connect(m_spinBoxSkipFrames, QOverload<int>::of(&QSpinBox::valueChanged), this, &MainWindow::OnSpinBoxSkipFrames);
    optionsLayout->addWidget(m_spinBoxSkipFrames, 0, 1);

    m_controlGainMin = new FloatControl(this);
    connect(m_controlGainMin, &FloatControl::ValueChanged, this, [this](double value){
        m_autoFeatures->SetGainLimit({ value, m_controlGainMax->Value() });
    });

    m_controlGainMax = new FloatControl(this);
    connect(m_controlGainMax, &FloatControl::ValueChanged, this, [this](double value){
        m_autoFeatures->SetGainLimit({ m_controlGainMin->Value(), value });
    });

    optionsLayout->addWidget(new QLabel("Gain limit min"), 1, 0);
    optionsLayout->addWidget(m_controlGainMin, 1, 1);
    optionsLayout->addWidget(new QLabel("Gain limit max"), 2, 0);
    optionsLayout->addWidget(m_controlGainMax, 2, 1);

    auto layout = new QVBoxLayout;
    layout->addLayout(exposureLayout);
    layout->addLayout(gainLayout);
    layout->addLayout(whiteBalanceLayout);

    layout->addWidget(CreateHLine());

    layout->addLayout(optionsLayout);
    layout->addWidget(resetButton);

    return layout;
}

QLayout* MainWindow::CreateCameraControls()
{
    auto layout = new QGridLayout;

    layout->addWidget(new QLabel("FrameRate"), 0, 0);

    m_controlFrameRate = new FloatControl();
    connect(m_controlFrameRate, &FloatControl::ValueChanged, this, [this](double value){
        m_device->SetFrameRate(value);
        UpdateValues();
    });
    layout->addWidget(m_controlFrameRate, 0, 1);

    layout->addWidget(new QLabel("Exposure"), 1, 0);

    m_controlExposure = new FloatControl();
    connect(m_controlExposure, &FloatControl::ValueChanged, this, [this](double value){
        m_device->SetExposure(value);
        UpdateValues();
    });
    layout->addWidget(m_controlExposure, 1, 1);

    layout->addWidget(new QLabel("Gain"), 2, 0);

    m_controlGain = new FloatControl();
    connect(m_controlGain, &FloatControl::ValueChanged, this, [this](double value){
        m_device->SetGain(value);
        UpdateValues();
    });
    layout->addWidget(m_controlGain, 2, 1);

    return layout;
}

void MainWindow::OnCounterChanged(unsigned int frameCounter, unsigned int errorCounter)
{
    m_labelInfo->setText(QString("Framerate: %1, frames acquired: %2, errors: %3")
                             .arg(QString::number(m_device->Framerate(), 'f', 1), QString::number(frameCounter),
                                 QString::number(errorCounter)));
}

void MainWindow::OnAboutQtLinkActivated(const QString& link)
{
    if (link == "#aboutQt")
    {
        QMessageBox::aboutQt(this, "About Qt");
    }
}

void MainWindow::OnRadioExposureAuto(int mode)
{
    m_autoFeatures->SetExposureMode(static_cast<peak_afl_controller_automode>(mode));
    m_controlExposure->setEnabled(mode == PEAK_AFL_CONTROLLER_AUTOMODE_OFF);
}

void MainWindow::OnRadioGainAuto(int mode)
{
    m_autoFeatures->SetGainMode(static_cast<peak_afl_controller_automode>(mode));
    m_controlGain->setEnabled(mode == PEAK_AFL_CONTROLLER_AUTOMODE_OFF);
}

void MainWindow::OnRadioBalanceWhiteAuto(int mode)
{
    m_autoFeatures->SetWhiteBalanceMode(static_cast<peak_afl_controller_automode>(mode));
}

void MainWindow::OnButtonReset()
{
    m_spinBoxSkipFrames->setValue(skip_frames_default);

    m_autoFeatures->Reset();
    for (const auto buttonGroup : { m_groupExposureAuto, m_groupGainAuto, m_groupBalanceWhiteAuto })
    {
        buttonGroup->button(static_cast<int>(PEAK_AFL_CONTROLLER_AUTOMODE_OFF))->setChecked(true);
    }
}

void MainWindow::OnSpinBoxSkipFrames(int skipFrames)
{
    m_autoFeatures->SetSkipFrames(skipFrames);
}

void MainWindow::UpdateValues()
{
    m_device->UpdateFramerate();

    m_controlExposure->SetRange(m_device->ExposureRange());
    m_controlExposure->SetValue(m_device->Exposure());
    m_controlFrameRate->SetRange(m_device->FramerateRange());
    m_controlFrameRate->SetValue(m_device->Framerate());

    const auto gainRange = m_device->GainRange();
    m_controlGain->SetRange(gainRange);
    m_controlGain->SetValue(m_device->Gain());

    const auto limit = m_autoFeatures->GainLimit();
    m_controlGainMin->blockSignals(true);
    m_controlGainMax->blockSignals(true);

    m_controlGainMin->SetRange({ gainRange.first, limit.second });
    m_controlGainMin->SetValue(limit.first);
    m_controlGainMax->SetRange({ limit.first, gainRange.second });
    m_controlGainMax->SetValue(limit.second);

    m_controlGainMin->blockSignals(false);
    m_controlGainMax->blockSignals(false);
}
