@echo off
setlocal
REM Di chuyen ve thu muc goc repo
cd /d "%~dp0.."

echo ===================================================
echo     SECURITY CAMERA DASHBOARD (RTSP - toi da 4 cam)
echo ===================================================
echo.

REM Goi thang python cua venv (bo qua 'activate' vi venv da bi doi duong dan)
set "VENV_PY=%CD%\yolo_env\Scripts\python.exe"
if not exist "%VENV_PY%" (
    echo LOI: Khong tim thay "%VENV_PY%".
    echo Tao lai venv: python -m venv yolo_env ^&^& yolo_env\Scripts\activate ^&^& pip install -r requirements.txt
    pause
    exit /b
)

echo Khoi dong dashboard... Mo trinh duyet tai http://127.0.0.1:5000
echo Nhan Ctrl+C de dung.
echo.
"%VENV_PY%" rtsp-camera\dashboard\app.py

echo.
echo Dashboard da dung.
pause
