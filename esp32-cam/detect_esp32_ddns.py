import cv2
from ultralytics import YOLO
import time
import requests
import threading
from pathlib import Path

# ===================================================================
# === CAU HINH TRUY CAP TU XA QUA INTERNET (PHIEN BAN CUOI CUNG) ===
# ===================================================================

# Thu muc chua model dung chung (yolo/models), doc theo vi tri file nay
MODELS_DIR = Path(__file__).resolve().parent.parent / "models"

# --- CẤU HÌNH TÊN MIỀN DDNS ---
# Sử dụng tên miền cố định bạn đã tạo trên No-IP
DDNS_HOSTNAME = "esp32-cam.ddns.net"

# --- CẤU HÌNH YOLO ---
MODEL_NAME = 'yolov8m.pt'
CONFIDENCE_THRESHOLD = 0.7  # Ngưỡng tin cậy cân bằng cho model Medium
TARGET_CLASS_IDS = [0, 39] # Nhận diện 'person' (ID 0) và 'bottle' (ID 39)

# --- CẤU HÌNH KẾT NỐI (Tự động tạo URL từ tên miền và cổng đã mở) ---
# URL điều khiển sẽ dùng cổng 8080
CONTROL_URL = f"http://{DDNS_HOSTNAME}:8080"
# URL stream sẽ dùng cổng 8181
STREAM_URL = f"http://{DDNS_HOSTNAME}:8181/stream"

LED_ON_URL = f"{CONTROL_URL}/led-on"
LED_OFF_URL = f"{CONTROL_URL}/led-off"
DETECTION_TIMEOUT = 1

# ===================================================================
# === CÁC HÀM VÀ BIẾN TRẠNG THÁI (Giữ nguyên) ===
# ===================================================================

led_status = False
auto_mode = True
last_target_detected_time = 0

def set_led(state):
    global led_status
    try:
        if state and not led_status:
            requests.get(LED_ON_URL, timeout=1)
            led_status = True
            print("Đèn BẬT (Phát hiện Người/Chai nước)")
        elif not state and led_status:
            requests.get(LED_OFF_URL, timeout=1)
            led_status = False
            print("Đèn TẮT")
    except requests.exceptions.RequestException as e:
        print(f"Lỗi kết nối đến ESP32: {e}")

def console_controller():
    global auto_mode
    print("\n--- Bảng điều khiển Đèn Thông Minh ---")
    print("Nhập 'on'/'off'/'auto'/'exit'")
    print("--------------------------------------")

    while True:
        try:
            command = input("> ").lower().strip()
            if command == "on": auto_mode = False; set_led(True)
            elif command == "off": auto_mode = False; set_led(False)
            elif command == "auto": auto_mode = True; print("Chuyển sang chế độ tự động.")
            elif command == "exit": break
        except (KeyboardInterrupt, EOFError): break

# ===================================================================
# === CHƯƠNG TRÌNH CHÍNH ===
# ===================================================================

def process_video_stream():
    global auto_mode, last_target_detected_time

    print(f"Đang tải mô hình YOLOv8: {MODEL_NAME}. Vui lòng đợi...")
    model = YOLO(str(MODELS_DIR / MODEL_NAME))

    print(f"Đang thử kết nối đến luồng stream tại: {STREAM_URL}")
    cap = cv2.VideoCapture(STREAM_URL)

    if not cap.isOpened():
        print(f"Lỗi: Không thể kết nối tới luồng stream.")
        print("Hãy kiểm tra lại cấu hình Port Forwarding, DDNS và đảm bảo ESP32-CAM đang hoạt động.")
        return

    print(f"Kết nối thành công! Bắt đầu xử lý YOLO bằng {MODEL_NAME}...")
    print(f"Mục tiêu nhận diện: Người (person), Chai nước (bottle)")

    frame_count = 0
    start_time = time.time()

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Mất kết nối. Đang thử lại...")
            time.sleep(2)
            cap.release(); cap = cv2.VideoCapture(STREAM_URL)
            continue

        results = model(frame, conf=CONFIDENCE_THRESHOLD, device='0', classes=TARGET_CLASS_IDS, half=True, verbose=False)

        target_detected_this_frame = False
        if len(results[0].boxes) > 0:
            target_detected_this_frame = True

        if auto_mode:
            if target_detected_this_frame:
                last_target_detected_time = time.time()
                set_led(True)
            elif time.time() - last_target_detected_time > DETECTION_TIMEOUT:
                set_led(False)

        annotated_frame = results[0].plot()
        cv2.imshow("YOLO Smart Lamp - Remote Access", annotated_frame)

        frame_count += 1
        if frame_count >= 30:
            end_time = time.time()
            fps = frame_count / (end_time - start_time)
            print(f"Tốc độ xử lý: {fps:.2f} FPS")
            start_time = time.time()
            frame_count = 0

        if cv2.waitKey(10) & 0xFF == ord('q'): break

    cap.release(); cv2.destroyAllWindows(); set_led(False)

if __name__ == "__main__":
    console_thread = threading.Thread(target=console_controller, daemon=True)
    console_thread.start()

    process_video_stream()

    print("Chương trình đã kết thúc.")
