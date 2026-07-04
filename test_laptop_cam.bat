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

REM Neu may khong co GPU NVIDIA/CUDA, doi thanh: set DEVICE=cpu
REM Muon chinh xac hon: doi MODEL thanh models\yolov8m.pt hoac models\yolov8l.pt

REM Goi thang 'yolo' CLI cua venv (bo qua 'activate' vi venv da bi doi duong dan)
set "VENV_YOLO=%CD%\yolo_env\Scripts\yolo.exe"
if not exist "%VENV_YOLO%" (
    echo LOI: Khong tim thay "%VENV_YOLO%".
    echo Tao lai venv: python -m venv yolo_env ^&^& yolo_env\Scripts\activate ^&^& pip install -r requirements.txt
    pause
    exit /b
)

echo Camera index: %CAMERA_INDEX%  Model: %MODEL%  Device: %DEVICE%
echo Ket qua neu luu se nam trong thu muc runs\detect\laptop_cam_yolo
echo.

"%VENV_YOLO%" predict model=%MODEL% source=%CAMERA_INDEX% show=True conf=%CONFIDENCE% device=%DEVICE% save=%SAVE_OUTPUT% project=runs\detect name=laptop_cam_yolo exist_ok=True

echo.
echo Chuong trinh da ket thuc.
pause
