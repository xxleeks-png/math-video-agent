@echo off
setlocal
cd /d "%~dp0.."

set "LOG=%cd%\sample_error.txt"
echo Math Video Agent sample launcher > "%LOG%"
echo Project: %cd% >> "%LOG%"
echo. >> "%LOG%"

echo ==========================================
echo Math Video Agent - Sample Launcher
echo ==========================================
echo Project: %cd%
echo.
echo Checking Python...
where python >> "%LOG%" 2>&1
python --version >> "%LOG%" 2>&1
type "%LOG%"

if errorlevel 1 goto PYTHON_ERROR

echo.
echo Starting sample generation...
echo Output will be saved under output\sample_01
echo Please wait...
echo.

python scripts\run_sample.py >> "%LOG%" 2>&1
set "ERR=%ERRORLEVEL%"

echo.
type "%LOG%"
echo.

if not "%ERR%"=="0" goto GENERATION_ERROR

if exist "%cd%\output\sample_01\math_video.mp4" goto SUCCESS

echo WARNING: generation finished but MP4 was not found.
echo See sample_error.txt for details.
pause
exit /b 1

:PYTHON_ERROR
echo.
echo ERROR: Python was not found or could not start.
echo Full details are in:
echo %LOG%
echo.
pause
exit /b 1

:GENERATION_ERROR
echo ==========================================
echo SAMPLE GENERATION FAILED
echo ==========================================
echo Full error log:
echo %LOG%
echo.
pause
exit /b 1

:SUCCESS
echo ==========================================
echo SAMPLE GENERATION SUCCESS
echo ==========================================
echo.
echo Video:
echo %cd%\output\sample_01\math_video.mp4
echo.
start "" "%cd%\output\sample_01\math_video.mp4"
pause
