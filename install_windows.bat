@echo off
net session >nul 2>&1
if errorlevel 1 (
    echo.
    echo GRESKA: Pokrenite kao Administrator
    echo Desni klik na install_windows.bat -^> Pokreni kao administrator
    echo.
    pause
    exit /b 1
)
chcp 65001 >nul
setlocal enabledelayedexpansion
set INSTALL_DIR=%LOCALAPPDATA%\PS5UART
set DESKTOP=%USERPROFILE%\Desktop
set STARTMENU=%APPDATA%\Microsoft\Windows\Start Menu\Programs
set PY_URL=https://www.python.org/ftp/python/3.11.9/python-3.11.9-amd64.exe
set PY_INSTALLER=%TEMP%\python_installer.exe
echo.
echo ============================================
echo   PS5 UART Dijagnostika v2.0
echo   Servis Port Sabac - Windows Instalacija
echo   [Administrator]
echo ============================================
echo.
echo [1/5] Provera Python...
python --version >nul 2>&1
if not errorlevel 1 goto :python_ok
echo Python nije pronadjen. Preuzimam Python 3.11.9...
curl -L -o "%PY_INSTALLER%" "%PY_URL%" --progress-bar 2>nul
if errorlevel 1 (
    echo Koristim PowerShell za preuzimanje...
    powershell -NoProfile -ExecutionPolicy Bypass -Command "[Net.ServicePointManager]::SecurityProtocol=[Net.SecurityProtocolType]::Tls12; Invoke-WebRequest -Uri '%PY_URL%' -OutFile '%PY_INSTALLER%' -UseBasicParsing"
)
if not exist "%PY_INSTALLER%" (
    echo GRESKA: Preuzimanje Python-a nije uspelo.
    echo Preuzmite rucno: https://www.python.org/downloads/
    pause & exit /b 1
)
echo Instaliram Python 3.11.9...
"%PY_INSTALLER%" /quiet PrependPath=1 Include_pip=1 Include_launcher=1 InstallAllUsers=1
del "%PY_INSTALLER%" >nul 2>&1
for /f "tokens=*" %%p in ('powershell -NoProfile -Command "[System.Environment]::GetEnvironmentVariable('PATH','Machine') + ';' + [System.Environment]::GetEnvironmentVariable('PATH','User')"') do set PATH=%%p
python --version >nul 2>&1
if errorlevel 1 (
    echo GRESKA: Python instalacija nije uspela. Restartujte i pokrenite ponovo.
    pause & exit /b 1
)
:python_ok
for /f "tokens=2" %%v in ('python --version 2^>^&1') do set PY_VER=%%v
echo OK - Python !PY_VER!
echo [2/5] Azuriranje pip-a...
python -m pip install --upgrade pip -q --disable-pip-version-check 2>nul
echo OK
echo [3/5] Instalacija pyserial...
python -m pip install pyserial -q --disable-pip-version-check
if errorlevel 1 ( echo GRESKA: pyserial & pause & exit /b 1 )
echo OK - pyserial
echo [4/5] Kopiranje aplikacije...
if not exist "%INSTALL_DIR%" mkdir "%INSTALL_DIR%"
copy /Y "%~dp0ps5_uart_windows.py" "%INSTALL_DIR%\ps5_uart.py" >nul
if errorlevel 1 ( echo GRESKA: kopiranje & pause & exit /b 1 )
echo OK
echo [5/5] Pravljenje precica...
powershell -NoProfile -ExecutionPolicy Bypass -Command "$ws=New-Object -ComObject WScript.Shell; $s=$ws.CreateShortcut([System.Environment]::GetFolderPath('Desktop')+'\PS5 UART.lnk'); $s.TargetPath='pythonw'; $s.Arguments=([System.Environment]::GetEnvironmentVariable('LOCALAPPDATA')+'\PS5UART\ps5_uart.py'); $s.WorkingDirectory=([System.Environment]::GetEnvironmentVariable('LOCALAPPDATA')+'\PS5UART'); $s.IconLocation='shell32.dll,22'; $s.Save()"
powershell -NoProfile -ExecutionPolicy Bypass -Command "$ws=New-Object -ComObject WScript.Shell; $p=[System.Environment]::GetFolderPath('ApplicationData')+'\Microsoft\Windows\Start Menu\Programs'; if(!(Test-Path $p)){New-Item -ItemType Directory -Path $p|Out-Null}; $s=$ws.CreateShortcut($p+'\PS5 UART Dijagnostika.lnk'); $s.TargetPath='pythonw'; $s.Arguments=([System.Environment]::GetEnvironmentVariable('LOCALAPPDATA')+'\PS5UART\ps5_uart.py'); $s.WorkingDirectory=([System.Environment]::GetEnvironmentVariable('LOCALAPPDATA')+'\PS5UART'); $s.IconLocation='shell32.dll,22'; $s.Save()"
echo OK - precice napravljene
echo.
echo ============================================
echo   Instalacija uspesno zavrsena!
echo ============================================
echo.
echo Aplikacija: %INSTALL_DIR%
echo Precica:    Desktop - PS5 UART
echo.
echo -- DRAJVERI ZA USB/RS232 ADAPTER --
echo CH340/CH341:  https://www.wch-ic.com/downloads/CH341SER_EXE.html
echo CP210x:       https://www.silabs.com/developers/usb-to-uart-bridge-vcp-drivers
echo FT232:        https://ftdichip.com/drivers/vcp-drivers/
echo.
pause
