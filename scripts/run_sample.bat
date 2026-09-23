@echo off
setlocal
cd /d "%~dp0.."

echo ==========================================
echo Math Video Agent - Sample Launcher
echo ==========================================
echo.
echo Project directory:
echo %cd%
echo.
echo Checking Python...
python --version
if errorlevel 1 (
  echo.
  echo ERROR: Python command was not found.
  echo Install Python or add it to PATH, then run this file again.
  echo.
  pause
  exit /b 1
)

echo.
echo Starting local sample generation...
echo Do not close this window.
echo.

python scripts\run_sample.py

if errorlevel 1 (
  echo.
  echo ==========================================
  echo SAMPLE GENERATION FAILED
  echo ==========================================
  echo Please send a screenshot of this window.
  echo.
  pause
  exit /b 1
)

echo.
echo ==========================================
echo SAMPLE GENERATION FINISHED
echo ==========================================
echo.
echo Expected video:
echo %cd%\output\sample_01\math_video.mp4
echo.

if exist "%cd%\output\sample_01\math_video.mp4" (
  echo Opening video...
  start "" "%cd%\output\sample_01\math_video.mp4"
) else (
  echo WARNING: MP4 file was not found.
  echo Please send a screenshot of this window.
)

echo.
pause
