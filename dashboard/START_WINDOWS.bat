@echo off
setlocal
cd /d "%~dp0"
echo MouldShield - starting local dashboard...
py -3 -c "import sys; sys.exit(0 if sys.version_info >= (3, 8) else 1)" >nul 2>&1
if not errorlevel 1 goto use_py
python -c "import sys; sys.exit(0 if sys.version_info >= (3, 8) else 1)" >nul 2>&1
if not errorlevel 1 goto use_python
python3 -c "import sys; sys.exit(0 if sys.version_info >= (3, 8) else 1)" >nul 2>&1
if not errorlevel 1 goto use_python3
echo.
echo Python 3.8 or newer was not found. Opening the self-contained demo instead.
echo Live API connections require Python and the project backend.
start "" "%~dp0START_HERE.html"
echo.
pause
exit /b 0
:use_py
py -3 "%~dp0run.py" %*
goto finished
:use_python
python "%~dp0run.py" %*
goto finished
:use_python3
python3 "%~dp0run.py" %*
:finished
if errorlevel 1 goto failed
exit /b 0
:failed
echo.
echo The server could not start. Read the error above.
echo You can still view the sample dashboard by opening START_HERE.html.
pause
exit /b 1
