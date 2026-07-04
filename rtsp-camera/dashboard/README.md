# 📊 Security Camera Dashboard (RTSP)

Web dashboard giám sát **tối đa 4 camera RTSP cùng lúc** bằng YOLOv8. Mỗi camera có luồng
nhận diện realtime, trạng thái online/offline, FPS, số phát hiện và **highlight đỏ khi phát
hiện người**. Xem được trên trình duyệt máy tính hoặc điện thoại trong cùng mạng LAN.

## Kiến trúc

```
Camera RTSP ─┐
Camera RTSP ─┤→ CameraWorker (thread) ─ YOLOv8 detect ─┐
Webcam/URL  ─┤                                          ├→ Flask ─ MJPEG + /api/stats ─→ Trình duyệt (lưới 2×2)
Camera RTSP ─┘                                          ┘
```

- `app.py` — backend Flask: mỗi camera 1 thread đọc luồng → YOLO → encode JPEG; phục vụ
  `/video/<id>` (MJPEG) và `/api/stats` (JSON thống kê).
- `templates/index.html` + `static/` — giao diện dashboard (lưới 2×2, dark theme).
- `cameras.example.json` — cấu hình mẫu (copy thành `cameras.json` để dùng thật).

## Cấu hình

Tạo file `cameras.json` (copy từ `cameras.example.json`) — file này đã được `.gitignore`
bỏ qua nên **không lộ mật khẩu khi push**:

```jsonc
{
  "settings": {
    "model": "yolov8n.pt",        // n/m/l — n nhanh nhat, hop cho 4 luong
    "confidence": 0.4,
    "device": "0",                 // "0" = GPU NVIDIA, "cpu" neu khong co GPU
    "half": true,                  // FP16 tang FPS (tu tat khi chay CPU)
    "imgsz": 640,
    "process_every_n_frames": 1,   // tang len 2-3 de giam tai neu lag
    "target_classes": [0],         // 0 = person; [] = tat ca lop COCO
    "port": 5000
  },
  "cameras": [
    { "name": "Cong chinh", "source": "rtsp://admin:PASS@192.168.1.10:554/", "esp32_ip": "" },
    { "name": "Webcam test", "source": "0", "esp32_ip": "192.168.1.200" }
  ]
}
```

- **`source`**: URL RTSP/HTTP, hoặc số (`"0"`, `"1"`...) để dùng webcam — tiện test khi
  chưa có camera thật.
- **`esp32_ip`** (tùy chọn): nếu điền, dashboard sẽ tự gửi lệnh bật/tắt đèn tới ESP32
  (`http://<ip>/led/on|off`) khi phát hiện/hết người trên camera đó.
- Tối đa **4 camera** (dư sẽ bị bỏ qua). Ít hơn 4 thì ô trống hiển thị "Chưa cấu hình".

## Chạy

```bat
REM Tu thu muc goc repo:
rtsp-camera\run_dashboard.bat
```

Rồi mở trình duyệt tại **http://127.0.0.1:5000** (hoặc `http://<IP-máy>:5000` từ điện thoại
cùng mạng).

## Hiệu năng

Chạy 4 luồng YOLO đồng thời khá nặng. Nếu bị lag:
- Dùng `yolov8n.pt` (mặc định) thay vì `m`/`l`.
- Tăng `process_every_n_frames` lên `2`–`3` (nhận diện cách khung).
- Giảm `imgsz` xuống `480`.
- Đảm bảo đã cài `torch` bản CUDA để chạy trên GPU.
