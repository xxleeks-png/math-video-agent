@echo off
setlocal
cd /d "%~dp0.."
echo [Math Video Agent] 正在生成第一条样片...
python scripts\generate_video.py "一个空水池，单独开进水管，6小时可以注满；单独开出水管，8小时可以放完一池水。现在雨天雨水匀速注入池中，同时打开进水管和出水管，12小时刚好注满水池。如果雨天只开出水管，多少小时可以把满池水放完？" --output-dir output\sample_01
if errorlevel 1 (
  echo.
  echo 样片生成失败，请把上面的完整报错发给我。
  pause
  exit /b 1
)
echo.
echo 样片已生成：
echo %cd%\output\sample_01\math_video.mp4
start "" "%cd%\output\sample_01\math_video.mp4"
pause
