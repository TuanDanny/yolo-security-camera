<div align="center">

# 🎥 yolo-security-camera

**AI security camera with YOLOv8 — person/object detection & smart-lamp control, supporting ESP32-CAM and RTSP IP cameras.**

![Python](https://img.shields.io/badge/Python-3.13-3776AB?logo=python&logoColor=white)
![YOLOv8](https://img.shields.io/badge/YOLOv8-Ultralytics-0B23A9)
![OpenCV](https://img.shields.io/badge/OpenCV-5C3EE8?logo=opencv&logoColor=white)
![ESP32-CAM](https://img.shields.io/badge/ESP32--CAM-E7352C?logo=espressif&logoColor=white)
![Platform](https://img.shields.io/badge/Platform-Windows-0078D6?logo=windows&logoColor=white)

</div>

---

## 📖 Giới thiệu

Hệ thống dùng **YOLOv8 (Ultralytics)** nhận diện người / vật thể **realtime** từ luồng camera,
rồi **tự động bật/tắt đèn LED** khi phát hiện mục tiêu. Dự án hỗ trợ **2 hướng phần cứng camera**,
được tách riêng thành 2 thư mục độc lập.

## ✨ Tính năng

- 🧠 Nhận diện người/vật thể realtime bằng **YOLOv8** (n / m / l)
- 💡 Tự động **điều khiển đèn LED** khi phát hiện người/vật thể
- 🌐 Truy cập camera **từ xa qua Internet (DDNS)** hoặc trong **mạng LAN**
- 🎛️ Bảng điều khiển console: `on` / `off` / `auto`
- ⚡ Tối ưu **GPU NVIDIA** (FP16 `half=True`) để tăng FPS

## 🧭 Hai hướng phần cứng

| Thư mục | Hướng | Nguồn video | Script chính |
|---|---|---|---|
| [`esp32-cam/`](esp32-cam/) | **① Module ESP32-CAM** | Stream MJPEG từ ESP32-CAM (LAN / DDNS) | `detect_esp32_ddns.py`, `detect_esp32_local.py` |
| [`rtsp-camera/`](rtsp-camera/) | **② Camera an ninh RTSP** | Luồng RTSP camera IP (EZVIZ) / IP Webcam | `detect_rtsp.py`, `detect_ip_webcam.py` |

## 🗂️ Cấu trúc

```
yolo-security-camera/
├─ esp32-cam/                 # ① ESP32-CAM
│  ├─ firmware/               #   code Arduino nạp cho ESP32-CAM
│  ├─ detect_esp32_ddns.py    #   truy cập từ xa qua DDNS + điều khiển đèn
│  ├─ detect_esp32_local.py   #   stream trong mạng LAN
│  └─ run_esp32_*.bat
├─ rtsp-camera/               # ② Camera an ninh RTSP
│  ├─ detect_rtsp.py          #   camera EZVIZ qua RTSP + điều khiển đèn
│  ├─ detect_ip_webcam.py     #   IP Webcam điện thoại (HTTP MJPEG)
│  └─ run_*.bat
├─ models/                    # yolov8n/m/l.pt (không commit — tải từ Ultralytics)
├─ test_laptop_cam.bat        # tiện ích test nhanh webcam laptop
├─ requirements.txt
└─ README.md
```

## 🛠️ Công nghệ

`Python 3.13` · `Ultralytics YOLOv8` · `OpenCV` · `PyTorch (CUDA)` · `ESP32-CAM (Arduino/C++)` · `RTSP / MJPEG`

## 📦 Cài đặt

```bat
python -m venv yolo_env
yolo_env\Scripts\activate
pip install -r requirements.txt
```

> 💡 Máy có **GPU NVIDIA** nên cài `torch` bản CUDA (https://pytorch.org) vì script dùng
> `device='0'`, `half=True`. Chạy CPU thì đổi `device='cpu'` và bỏ `half=True`.
> Weight `.pt` sẽ tự tải về `models/` trong lần chạy đầu nếu chưa có.

## ▶️ Cách chạy

| Kịch bản | Lệnh |
|---|---|
| ESP32-CAM qua Internet (DDNS) | `esp32-cam\run_esp32_ddns.bat` |
| ESP32-CAM trong mạng LAN | `esp32-cam\run_esp32_local.bat` |
| Camera an ninh RTSP (EZVIZ) | `rtsp-camera\run_rtsp.bat` |
| IP Webcam điện thoại | `rtsp-camera\run_ip_webcam.bat` |
| Test webcam laptop | `test_laptop_cam.bat` |

Nhấn `q` trong cửa sổ hiển thị để thoát.

## ⚙️ Cấu hình

Các thông số kết nối trong code đang để **placeholder** (`YOUR_WIFI_SSID`, `YOUR_CAMERA_PASSWORD`,
`YOUR_PUBLIC_IP`, DDNS, IP stream...). Hãy điền giá trị thật của bạn trước khi chạy — chi tiết trong
README từng thư mục: [`esp32-cam/`](esp32-cam/README.md) · [`rtsp-camera/`](rtsp-camera/README.md).

## 🔒 Bảo mật

- **Không commit thông tin thật** (mật khẩu WiFi / camera). `.gitignore` đã bỏ qua `.env` và
  `config.local.py` để bạn lưu giá trị nhạy cảm ngoài Git.
- Mở Port Forwarding RTSP ra Internet có rủi ro — nên đặt **mật khẩu mạnh** và giới hạn IP truy cập.

---

<div align="center">
Made with ❤️ &nbsp;·&nbsp; YOLOv8 + ESP32-CAM + RTSP
</div>
