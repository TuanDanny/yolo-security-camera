import cv2
from ultralytics import YOLO
import time
from pathlib import Path

# Thu muc chua model dung chung (yolo/models), doc theo vi tri file nay
MODELS_DIR = Path(__file__).resolve().parent.parent / "models"

# --- CẤU HÌNH CUỐI CÙNG ---
# URL stream truc tiep tu ESP32-CAM trong mang LAN
stream_url = 'http://1.53.19.77:81/stream'

# Tải mô hình YOLOv8 (yolov8n.pt là mô hình nhỏ và nhanh)
model = YOLO(str(MODELS_DIR / 'yolov8n.pt'))

# Đảm bảo model chạy trên GPU (nếu có)
model.to('cuda')

print(f"--- CHUONG TRINH PHAT HIEN NGUOI QUA MANG ---")
print(f"Dang ket noi den Camera tai: {stream_url}")

# --- KẾT NỐI VÀ XỬ LÝ ---
cap = cv2.VideoCapture(stream_url, cv2.CAP_FFMPEG)

if not cap.isOpened():
    print("Lỗi: Khong the ket noi den video stream.")
    print("Hay dam bao ESP32-CAM van dang duoc cap nguon va ket noi Wi-Fi.")
    exit()

print("THANH CONG! Da ket noi den stream. Bat dau xu ly YOLO...")

frame_count = 0
start_time = time.time()
display_fps = 0

while True:
    ret, frame = cap.read()
    if not ret:
        print("Loi: Mat ket noi voi stream. Dang thu ket noi lai...")
        cap.release()
        time.sleep(2)
        cap = cv2.VideoCapture(stream_url, cv2.CAP_FFMPEG)
        continue

    # Đưa khung hình vào mô hình YOLO để phát hiện người (class 0)
    results = model(frame, classes=0, verbose=False)

    # Vẽ các hộp nhận diện lên khung hình
    annotated_frame = results[0].plot()

    # Tính toán và hiển thị FPS
    frame_count += 1
    elapsed_time = time.time() - start_time
    if elapsed_time > 1: # Cập nhật FPS mỗi giây
        display_fps = frame_count / elapsed_time
        frame_count = 0
        start_time = time.time()

    cv2.putText(annotated_frame, f'FPS: {display_fps:.2f}', (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

    # Hiển thị kết quả
    cv2.imshow("YOLO Detection Stream", annotated_frame)

    # Nhấn 'q' để thoát
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
