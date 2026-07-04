import cv2
from ultralytics import YOLO
import time
import requests # Thư viện để gửi yêu cầu HTTP
from pathlib import Path

# Thu muc chua model dung chung (yolo/models), doc theo vi tri file nay
MODELS_DIR = Path(__file__).resolve().parent.parent / "models"

# --- CẤU HÌNH ---
MODEL_NAME = 'yolov8l.pt'
DISPLAY_WIDTH = 1280
DISPLAY_HEIGHT = 720

# --- THÔNG SỐ KẾT NỐI CAMERA EZVIZ (MẠNG NGOÀI) ---
# GOI Y BAO MAT: nen dua USERNAME/PASSWORD/PUBLIC_IP ra bien moi truong
# hoac file config rieng thay vi hardcode trong ma nguon.
USERNAME = "admin"
PASSWORD = "YOUR_CAMERA_PASSWORD"
PUBLIC_IP = "YOUR_PUBLIC_IP"
# Chú ý: Sửa lại port đích là 554 cho đúng với cấu hình Port Forwarding của bạn
EXTERNAL_PORT = "554"
STREAM_URL = f"rtsp://{USERNAME}:{PASSWORD}@{PUBLIC_IP}:{EXTERNAL_PORT}/"

# --- THÔNG SỐ ĐIỀU KHIỂN ESP32-CAM ---
# !!! THAY THẾ BẰNG ĐỊA CHỈ IP CỦA ESP32-CAM MÀ BẠN LẤY ĐƯỢC TỪ ARDUINO IDE !!!
ESP32_IP = "192.168.1.200" # <--- THAY IP CỦA BẠN VÀO ĐÂY

# --- THÔNG SỐ NHẬN DIỆN ---
CONFIDENCE_THRESHOLD = 0.37
TARGET_CLASS_ID = 0  # Chỉ phát hiện 'person'

# Biến trạng thái để tránh gửi lệnh liên tục
led_is_on = False

# --- HÀM GỬI LỆNH ĐẾN ESP32 ---
def control_led(state):
    """Gửi lệnh 'on' hoặc 'off' đến ESP32-CAM."""
    url = f"http://{ESP32_IP}/led/{state}"
    try:
        # Gửi yêu cầu với timeout ngắn để không làm chương trình bị treo
        requests.get(url, timeout=0.5)
        print(f"Da gui lenh BAT LED" if state == "on" else f"Da gui lenh TAT LED")
    except requests.exceptions.RequestException as e:
        # Bỏ qua lỗi nếu không kết nối được với ESP32 (ví dụ: mất kết nối Wi-Fi)
        # print(f"Loi khi gui lenh den ESP32: {e}")
        pass

# --- KHỞI TẠO ---
print(f"Dang tai mo hinh YOLOv8: {MODEL_NAME}...")
model = YOLO(str(MODELS_DIR / MODEL_NAME))

print(f"Dang thu ket noi toi camera tu xa: {PUBLIC_IP}:{EXTERNAL_PORT}...")
cap = cv2.VideoCapture(STREAM_URL)

if not cap.isOpened():
    print(f"LOI: Khong the ket noi toi luong stream.")
    exit()

print("Ket noi thanh cong. Bat dau xu ly...")

# --- VÒNG LẶP XỬ LÝ CHÍNH ---
while True:
    ret, frame = cap.read()

    if not ret:
        print("Mat ket noi voi Camera. Dang thu ket noi lai...")
        time.sleep(2)
        cap.release()
        cap = cv2.VideoCapture(STREAM_URL)
        continue

    # Xử lý YOLO
    results = model(frame, conf=CONFIDENCE_THRESHOLD, device='0', classes=[TARGET_CLASS_ID], half=True, verbose=False)
    annotated_frame = results[0].plot()

    # --- LOGIC ĐIỀU KHIỂN ĐÈN LED ---
    person_detected = any(int(box.cls[0]) == TARGET_CLASS_ID for box in results[0].boxes)

    # Nếu phát hiện người VÀ đèn đang tắt -> BẬT ĐÈN
    if person_detected and not led_is_on:
        control_led("on")
        led_is_on = True
    # Nếu KHÔNG phát hiện người VÀ đèn đang bật -> TẮT ĐÈN
    elif not person_detected and led_is_on:
        control_led("off")
        led_is_on = False

    # Hiển thị
    resized_frame = cv2.resize(annotated_frame, (DISPLAY_WIDTH, DISPLAY_HEIGHT))
    cv2.imshow("He Thong Giam Sat An Ninh", resized_frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        # Tắt đèn trước khi thoát
        if led_is_on:
            control_led("off")
        break

# Giải phóng tài nguyên
cap.release()
cv2.destroyAllWindows()
print("Chuong trinh da dong.")
