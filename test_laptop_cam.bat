@echo off
setlocal
REM File tien ich test nhanh bang webcam cua laptop (khong thuoc huong ESP32/RTSP)
cd /d "%~dp0"

echo ===================================================
echo     TEST NHANH YOLO VOI CAMERA LAPTOP
echo ===================================================
echo.

REM Cau hinh nhanh
set MODEL=models\yolov8n.pt
set CAMERA_INDEX=0
set CONFIDENCE=0.50
set DEVICE=0
set SAVE_OUTPUT=True

REM Neu may khong co GPU NVIDIA/CUDA, doi dong tren thanh:
REM set DEVICE=cpu
REM Neu muon chinh xac hon nhung cham hon, doi MODEL thanh models\yolov8m.pt hoac models\yolov8l.pt

echo Kich hoat moi truong ao 'yolo_env'...
call yolo_env\Scripts\activate.bat
if %errorlevel% neq 0 (
    echo LOI: Khong the kich hoat moi truong ao.
    pause
    exit /b
)

echo Moi truong ao da san sang.
echo Camera index: %CAMERA_INDEX%  Model: %MODEL%  Device: %DEVICE%
echo Ket qua neu luu se nam trong thu muc runs\detect\laptop_cam_yolo
echo.

yolo predict model=%MODEL% source=%CAMERA_INDEX% show=True conf=%CONFIDENCE% device=%DEVICE% save=%SAVE_OUTPUT% project=runs\detect name=laptop_cam_yolo exist_ok=True

echo.
echo Chuong trinh da ket thuc.
pause
