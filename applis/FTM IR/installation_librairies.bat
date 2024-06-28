@ECHO OFF
cd %~dp0
copy "GLECB.ttf" "%WINDIR%\Fonts"
reg add "HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Fonts" /v "GloucesterMTExtraCondensed (TrueType)" /t REG_SZ /d GLECB.ttf /f
pip install PySide6 pyqtgraph matplotlib pyserial scipy numpy pandas
PAUSE