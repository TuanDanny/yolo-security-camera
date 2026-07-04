import cv2
from ultralytics import YOLO
import time
from pathlib import Path

# Thu muc chua model dung chung (yolo/models), doc theo vi tri file nay
MODELS_DIR = Path(__file__).resolve().parent.parent / "models"

# --- CẤU HÌNH CUỐI CÙNG: TỐI ƯU CHO ĐỘ CHÍNH XÁC (Vật thể xa) VÀ CÔNG SUẤT GPU ---
# CHỌN MÔ HÌNH: 'l' (Large) để có độ chính xác cao nhất (Tốt hơn cho vật thể xa)
MODEL_NAME = 'yolov8m.pt'

# THÔNG SỐ ĐẦU VÀO: luong video tu app IP Webcam tren dien thoai (HTTP MJPEG)
STREAM_URL = "http://10.40.1.28:8080/video"

# THÔNG SỐ NHẬN DIỆN
CONFIDENCE_THRESHOLD = 0.61
TARGET_CLASS_IDS = [0, 39, 41, 56, 60] # Người, Ly, Ghế, Bàn ăn

# --- KHỞI TẠO ---
print(f"Đang tải mô hình YOLOv8: {MODEL_NAME}. Vui lòng đợi...")
model = YOLO(str(MODELS_DIR / MODEL_NAME))

cap = cv2.VideoCapture(STREAM_URL)

if not cap.isOpened():
    print(f"Lỗi: Không thể kết nối tới luồng stream tại {STREAM_URL}")
    exit()

print(f"Kết nối thành công. Bắt đầu xử lý YOLO trên GPU RTX 3050Ti bằng {MODEL_NAME}...")

frame_count = 0
start_time = time.time()

while True:
    ret, frame = cap.read()

    if not ret:
        print("Mất kết nối với Camera hoặc luồng stream kết thúc.")
        time.sleep(2)
        cap = cv2.VideoCapture(STREAM_URL)
        continue

    # --- XỬ LÝ YOLO TRÊN GPU VỚI TỐI ƯU CÔNG SUẤT ---

    # half=True: Sử dụng độ chính xác nửa (FP16) để tăng FPS tối đa trên GPU NVIDIA
    results = model(frame,
                    conf=CONFIDENCE_THRESHOLD,
                    device='0',
                    classes=TARGET_CLASS_IDS,
                    iou=0.7,
                    half=True,  # <--- THÔNG SỐ QUAN TRỌNG ĐỂ TĂNG FPS
                    verbose=False)

    # --- HIỂN THỊ KẾT QUẢ VÀ FPS ---

    annotated_frame = results[0].plot()
    cv2.imshow("YOLO Detection - High Accuracy/High FPS", annotated_frame)

    frame_count += 1
    if frame_count % 30 == 0:
        end_time = time.time()
        fps = 30 / (end_time - start_time)
        print(f"Tốc độ xử lý: {fps:.2f} FPS")
        start_time = time.time()

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Giải phóng tài nguyên
cap.release()
cv2.destroyAllWindows()
