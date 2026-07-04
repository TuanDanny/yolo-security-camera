# Hướng 1 – Module ESP32-CAM

Dùng camera trên module **ESP32-CAM (AI-Thinker)** làm nguồn video. ESP32 tự chạy
web server stream MJPEG; máy tính chạy YOLO đọc luồng đó để nhận diện và gửi lệnh
bật/tắt đèn LED về ESP32.

## Thành phần

| File | Mô tả |
|------|-------|
| `firmware/ESP32_CAM_HAS_DONE.ino` | Firmware Arduino nạp cho ESP32-CAM (IP tĩnh, stream `/stream`) |
| `firmware/app_httpd.cpp` + `*.h` | Web server & định nghĩa chân camera (dựa trên CameraWebServer của Espressif) |
| `detect_esp32_ddns.py` | Kết nối ESP32 **qua Internet bằng DDNS** (No-IP), có console điều khiển `on/off/auto`, tự bật đèn khi thấy người/chai |
| `detect_esp32_local.py` | Kết nối ESP32 **trong mạng LAN**, chỉ hiển thị nhận diện người |
| `run_esp32_ddns.bat` / `run_esp32_local.bat` | Kích hoạt `yolo_env` và chạy script tương ứng |

## Chuẩn bị

1. **Nạp firmware:** mở `firmware/ESP32_CAM_HAS_DONE.ino` bằng Arduino IDE, sửa
   `ssid` / `password` WiFi và IP tĩnh cho phù hợp mạng của bạn, rồi nạp cho ESP32-CAM.
2. Ghi lại địa chỉ IP mà ESP32 in ra Serial Monitor.
3. **Sửa cấu hình trong script Python:**
   - `detect_esp32_local.py`: đổi `stream_url` thành `http://<IP-ESP32>:81/stream`.
   - `detect_esp32_ddns.py`: đổi `DDNS_HOSTNAME`, và các cổng `8080` (điều khiển) /
     `8181` (stream) theo cấu hình Port Forwarding của router.

## Chạy

```bat
run_esp32_ddns.bat      REM truy cap tu xa qua Internet
run_esp32_local.bat     REM trong mang LAN
```

## ⚠️ Bảo mật
Firmware `.ino` đang hardcode SSID/mật khẩu WiFi. Không commit thông tin thật lên
GitHub — thay bằng giá trị mẫu hoặc tách ra file cấu hình riêng.
