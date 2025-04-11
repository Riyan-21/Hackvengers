@echo off
echo Stopping ZenZone System...

REM Find and stop server.py
for /f "tokens=2" %%a in ('tasklist /FI "IMAGENAME eq python.exe" /FO LIST ^| find "PID"') do (
    for /f "tokens=1" %%b in ('wmic process where "ProcessId=%%a" get CommandLine ^| find "server.py"') do (
        taskkill /F /PID %%a
        echo Stopped server.py (PID: %%a)
    )
)

REM Find and stop chat.py
for /f "tokens=2" %%a in ('tasklist /FI "IMAGENAME eq python.exe" /FO LIST ^| find "PID"') do (
    for /f "tokens=1" %%b in ('wmic process where "ProcessId=%%a" get CommandLine ^| find "chat.py"') do (
        taskkill /F /PID %%a
        echo Stopped chat.py (PID: %%a)
    )
)

REM Find and stop voice.py
for /f "tokens=2" %%a in ('tasklist /FI "IMAGENAME eq python.exe" /FO LIST ^| find "PID"') do (
    for /f "tokens=1" %%b in ('wmic process where "ProcessId=%%a" get CommandLine ^| find "voice.py"') do (
        taskkill /F /PID %%a
        echo Stopped voice.py (PID: %%a)
    )
)

REM Wait for processes to terminate
timeout /t 2 /nobreak > nul

REM Clear any remaining temporary files
if exist "*.pyc" del /Q "*.pyc"
if exist "__pycache__" rmdir /S /Q "__pycache__"

echo.
echo System stopped successfully.
echo Press any key to exit...
pause > nul 