@echo off
setlocal
REM Di chuyen ve thu muc goc repo
cd /d "%~dp0.."

echo ===================================================
echo     ESP32-CAM - Truy cap tu xa qua DDNS (Internet)
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

echo Bat dau chay esp32-cam\detect_esp32_ddns.py...
"%VENV_PY%" esp32-cam\detect_esp32_ddns.py

echo.
echo Chuong trinh da ket thuc.
pause
