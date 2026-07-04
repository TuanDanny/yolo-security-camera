@echo off
setlocal
REM Di chuyen ve thu muc goc repo
cd /d "%~dp0.."

echo ===================================================
echo     CAMERA MANG - App IP Webcam dien thoai (HTTP)
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

echo Bat dau chay rtsp-camera\detect_ip_webcam.py...
"%VENV_PY%" rtsp-camera\detect_ip_webcam.py

echo.
echo Chuong trinh da ket thuc.
pause
