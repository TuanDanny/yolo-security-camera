@echo off
setlocal
REM Di chuyen ve thu muc goc repo (thu muc cha cua file .bat nay)
cd /d "%~dp0.."

echo ===================================================
echo     CAMERA MANG - App IP Webcam dien thoai (HTTP)
echo ===================================================
echo.

echo Kich hoat moi truong ao 'yolo_env'...
call yolo_env\Scripts\activate.bat
if %errorlevel% neq 0 (
    echo LOI: Khong the kich hoat moi truong ao.
    pause
    exit /b
)

echo Bat dau chay rtsp-camera\detect_ip_webcam.py...
python rtsp-camera\detect_ip_webcam.py

echo.
echo Chuong trinh da ket thuc.
pause
