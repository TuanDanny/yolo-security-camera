# Hướng 2 – Camera an ninh RTSP

Dùng **camera an ninh IP** (ví dụ EZVIZ) làm nguồn video, truyền qua giao thức **RTSP**.
Máy tính chạy YOLO đọc luồng RTSP để nhận diện người và (tùy chọn) gửi lệnh bật/tắt
đèn LED tới một ESP32-CAM qua HTTP.

## Thành phần

| File | Mô tả |
|------|-------|
| `detect_rtsp.py` | Kết nối camera EZVIZ qua **RTSP** (`rtsp://user:pass@ip:554/`), nhận diện người, điều khiển đèn ESP32 |
| `detect_ip_webcam.py` | Biến thể: đọc luồng **HTTP MJPEG** từ app *IP Webcam* trên điện thoại (nhận diện người, ly, ghế, bàn) |
| `run_rtsp.bat` / `run_ip_webcam.bat` | Kích hoạt `yolo_env` và chạy script tương ứng |

> `detect_ip_webcam.py` dùng luồng HTTP chứ không phải RTSP, nhưng cách đọc luồng
> camera mạng qua `cv2.VideoCapture(URL)` giống nhau nên được gom chung ở đây.

## Chuẩn bị (`detect_rtsp.py`)

Sửa các thông số kết nối camera cho đúng thiết bị của bạn:

- `USERNAME`, `PASSWORD` – tài khoản camera
- `PUBLIC_IP`, `EXTERNAL_PORT` – IP công cộng và cổng RTSP (thường `554`) đã mở Port Forwarding
- `ESP32_IP` – IP của ESP32-CAM điều khiển đèn (nếu dùng)

Với `detect_ip_webcam.py`: cài app **IP Webcam** trên điện thoại, sửa `STREAM_URL`
thành `http://<IP-dien-thoai>:8080/video`.

## Chạy

```bat
run_rtsp.bat            REM camera EZVIZ qua RTSP
run_ip_webcam.bat       REM app IP Webcam dien thoai
```

## ⚠️ Bảo mật
`detect_rtsp.py` đang hardcode `USERNAME`/`PASSWORD`/`PUBLIC_IP` của camera. Nên đưa
các giá trị này ra biến môi trường hoặc file config riêng trước khi chia sẻ mã nguồn.
