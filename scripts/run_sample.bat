@echo off
setlocal
cd /d "%~dp0.."

echo ==========================================
echo Math Video Agent - 第一条样片
echo ==========================================
echo.
echo 项目目录：
echo %cd%
echo.
echo 正在检查 Python...
python --version

if errorlevel 1 (
  echo.
  echo [错误] 找不到 Python。
  echo.
  pause
  exit /b 1
)

echo.
echo 开始生成样片，请不要关闭窗口...
echo.

python scripts\generate_video.py "一个空水池，单独开进水管，6小时可以注满；单独开出水管，8小时可以放完一池水。现在雨天雨水匀速注入池中，同时打开进水管和出水管，12小时刚好注满水池。如果雨天只开出水管，多少小时可以把满池水放完？" --output-dir output\sample_01

if errorlevel 1 (
  echo.
  echo ==========================================
  echo 样片生成失败！
  echo ==========================================
  echo 请把这个窗口的完整报错截图发给我。
  echo.
  pause
  exit /b 1
)

echo.
echo ==========================================
echo 样片生成成功！
echo ==========================================
echo.
echo 视频位置：
echo %cd%\output\sample_01\math_video.mp4
echo.

if exist "%cd%\output\sample_01\math_video.mp4" (
  echo 正在打开视频...
  start "" "%cd%\output\sample_01\math_video.mp4"
) else (
  echo [警告] 程序运行结束，但没有找到 MP4 文件。
  echo 请把这个窗口截图发给我。
)

echo.
pause
