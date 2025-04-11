@echo off
echo Starting ZenZone System...

REM Start chat.py in a new window
start "Chat System" cmd /c "python chat.py"

REM Wait for 2 seconds to ensure chat system is initialized
timeout /t 2 /nobreak > nul

REM Start voice.py in a new window
start "Voice System" cmd /c "python voice.py"

REM Wait for 2 seconds to ensure voice system is initialized
timeout /t 2 /nobreak > nul

REM Start Flask server (API) in a new window
start "API Server" cmd /c "python server.py --port 5500"

REM Wait for 2 seconds to ensure API server is initialized
timeout /t 2 /nobreak > nul

REM Start static file server for the website
start "Web Server" cmd /c "python -m http.server 5501"

REM Wait for 2 seconds to ensure web server is initialized
timeout /t 2 /nobreak > nul

REM Open the website in the default browser
start http://localhost:5501

echo.
echo All components started successfully:
echo - Chat System
echo - Voice System
echo - API Server (running on port 5500)
echo - Web Server (running on port 5501)
echo.
echo Website should open automatically in your browser.
echo If it doesn't, please manually open: http://localhost:5501
echo.
echo Press any key to close this window...
pause > nul 