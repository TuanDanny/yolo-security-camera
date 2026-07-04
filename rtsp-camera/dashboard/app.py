"""
Dashboard giam sat nhieu camera RTSP (toi da 4) bang YOLOv8.

- Doc cau hinh tu cameras.json (hoac cameras.example.json neu chua co).
- Moi camera chay tren 1 thread rieng: doc luong -> YOLO detect -> ve khung -> encode JPEG.
- Flask phuc vu:
    /                -> trang dashboard
    /video/<id>      -> luong MJPEG da annotate cua tung camera
    /api/stats       -> JSON thong ke realtime (FPS, so phat hien, trang thai...)
"""

import json
import time
import threading
from pathlib import Path

import cv2
import numpy as np
from flask import Flask, Response, render_template, jsonify
from ultralytics import YOLO

try:
    import requests
except ImportError:  # requests khong bat buoc neu khong dung ESP32
    requests = None

# ------------------------------------------------------------------
# Duong dan
# ------------------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent          # .../rtsp-camera/dashboard
ROOT_DIR = BASE_DIR.parent.parent                   # goc repo
MODELS_DIR = ROOT_DIR / "models"
MAX_CAMERAS = 4

# ------------------------------------------------------------------
# Doc cau hinh
# ------------------------------------------------------------------
def load_config():
    cfg_path = BASE_DIR / "cameras.json"
    if not cfg_path.exists():
        cfg_path = BASE_DIR / "cameras.example.json"
        print(f"[!] Khong tim thay cameras.json -> dung mac dinh '{cfg_path.name}'.")
        print("    Hay tao 'cameras.json' de cau hinh camera that cua ban.")
    with open(cfg_path, "r", encoding="utf-8") as f:
        return json.load(f)


CONFIG = load_config()
SETTINGS = CONFIG.get("settings", {})
CAMERAS_CFG = CONFIG.get("cameras", [])[:MAX_CAMERAS]

MODEL_NAME = SETTINGS.get("model", "yolov8n.pt")
CONF = float(SETTINGS.get("confidence", 0.4))
IMG_SIZE = int(SETTINGS.get("imgsz", 640))
PROCESS_EVERY = max(1, int(SETTINGS.get("process_every_n_frames", 1)))
_target = SETTINGS.get("target_classes", [0])          # 0 = person; [] hoac null = tat ca
TARGET_CLASSES = _target if _target else None

# ------------------------------------------------------------------
# Chon thiet bi (GPU neu co, nguoc lai CPU)
# ------------------------------------------------------------------
def resolve_device():
    want = str(SETTINGS.get("device", "0"))
    half = bool(SETTINGS.get("half", True))
    try:
        import torch
        if want != "cpu" and torch.cuda.is_available():
            return want, half
    except Exception:
        pass
    if want != "cpu":
        print("[i] Khong phat hien GPU CUDA -> chuyen sang CPU (half=False).")
    return "cpu", False


DEVICE, USE_HALF = resolve_device()

# ------------------------------------------------------------------
# Tai model (dung chung, khoa lai khi inference de an toan/tiet kiem VRAM)
# ------------------------------------------------------------------
print(f"[i] Dang tai model YOLOv8: {MODEL_NAME} ...")
model = YOLO(str(MODELS_DIR / MODEL_NAME))
model_lock = threading.Lock()
CLASS_NAMES = model.names


def make_placeholder(text, w=640, h=360):
    """Tao khung hinh 'khong tin hieu' de hien khi camera offline."""
    img = np.zeros((h, w, 3), dtype=np.uint8)
    img[:] = (28, 30, 38)
    cv2.putText(img, text, (int(w * 0.18), int(h * 0.5)),
                cv2.FONT_HERSHEY_SIMPLEX, 1.1, (90, 95, 110), 2, cv2.LINE_AA)
    ok, buf = cv2.imencode(".jpg", img)
    return buf.tobytes()


PLACEHOLDER_CONNECTING = make_placeholder("DANG KET NOI...")
PLACEHOLDER_OFFLINE = make_placeholder("MAT KET NOI")


# ------------------------------------------------------------------
# Worker cho tung camera
# ------------------------------------------------------------------
class CameraWorker(threading.Thread):
    def __init__(self, cam_id, cfg):
        super().__init__(daemon=True)
        self.id = cam_id
        self.name = cfg.get("name", f"Camera {cam_id + 1}")
        src = str(cfg.get("source", "")).strip()
        # source la so -> webcam/index; nguoc lai la URL RTSP/HTTP
        self.source = int(src) if src.isdigit() else src
        self.esp32_ip = cfg.get("esp32_ip", "").strip()
        self.reconnect_delay = float(cfg.get("reconnect_delay", 3.0))

        self.status = "connecting"      # connecting | online | offline
        self.fps = 0.0
        self.detections = 0             # so vat the o khung hinh hien tai
        self.total_alerts = 0           # so lan bat dau phat hien (canh bao)
        self.last_detection_ts = 0.0
        self.led_on = False

        self._frame = PLACEHOLDER_CONNECTING
        self._lock = threading.Lock()
        self.running = True

    # --- suy luan YOLO tren 1 khung hinh ---
    def _infer(self, frame):
        with model_lock:
            results = model(frame, conf=CONF, imgsz=IMG_SIZE, device=DEVICE,
                            half=USE_HALF, classes=TARGET_CLASSES, verbose=False)
        r = results[0]
        annotated = r.plot()
        return annotated, len(r.boxes)

    # --- dieu khien den ESP32 (tuy chon, chi khi co esp32_ip) ---
    def _set_led(self, state):
        if not self.esp32_ip or requests is None or state == self.led_on:
            return
        try:
            requests.get(f"http://{self.esp32_ip}/led/{'on' if state else 'off'}",
                         timeout=0.5)
        except Exception:
            pass
        self.led_on = state

    # --- ve overlay ten camera + gio len khung hinh ---
    def _overlay(self, frame):
        label = f"{self.name}  {time.strftime('%H:%M:%S')}"
        cv2.rectangle(frame, (0, 0), (frame.shape[1], 26), (0, 0, 0), -1)
        cv2.putText(frame, label, (8, 18), cv2.FONT_HERSHEY_SIMPLEX,
                    0.55, (235, 235, 235), 1, cv2.LINE_AA)
        return frame

    def run(self):
        while self.running:
            self.status = "connecting"
            with self._lock:
                self._frame = PLACEHOLDER_CONNECTING
            cap = cv2.VideoCapture(self.source)
            if not cap.isOpened():
                self.status = "offline"
                with self._lock:
                    self._frame = PLACEHOLDER_OFFLINE
                cap.release()
                time.sleep(self.reconnect_delay)
                continue

            self.status = "online"
            frame_idx = 0
            fcount, t0 = 0, time.time()
            last_ndet = 0

            while self.running:
                ret, frame = cap.read()
                if not ret:
                    self.status = "offline"
                    with self._lock:
                        self._frame = PLACEHOLDER_OFFLINE
                    break

                frame_idx += 1
                if frame_idx % PROCESS_EVERY == 0:
                    annotated, ndet = self._infer(frame)
                    last_ndet = ndet
                else:
                    annotated, ndet = frame, last_ndet

                # thong ke FPS (cap nhat moi ~1s)
                fcount += 1
                now = time.time()
                if now - t0 >= 1.0:
                    self.fps = round(fcount / (now - t0), 1)
                    fcount, t0 = 0, now

                # canh bao khi bat dau phat hien (canh len)
                if ndet > 0:
                    self.last_detection_ts = now
                    if self.detections == 0:
                        self.total_alerts += 1
                    self._set_led(True)
                else:
                    self._set_led(False)
                self.detections = ndet

                annotated = self._overlay(annotated)
                ok, buf = cv2.imencode(".jpg", annotated,
                                       [cv2.IMWRITE_JPEG_QUALITY, 72])
                if ok:
                    with self._lock:
                        self._frame = buf.tobytes()

            cap.release()
            if self.running:
                time.sleep(self.reconnect_delay)

    def get_frame(self):
        with self._lock:
            return self._frame

    def stats(self):
        last = None
        if self.last_detection_ts:
            last = round(time.time() - self.last_detection_ts, 1)
        return {
            "id": self.id,
            "name": self.name,
            "status": self.status,
            "fps": self.fps,
            "detections": self.detections,
            "alerts": self.total_alerts,
            "last_alert": last,
        }


# ------------------------------------------------------------------
# Khoi tao workers
# ------------------------------------------------------------------
workers = {}
for i, cam in enumerate(CAMERAS_CFG):
    w = CameraWorker(i, cam)
    workers[i] = w
    w.start()

CAM_META = [{"id": w.id, "name": w.name} for w in workers.values()]

# ------------------------------------------------------------------
# Flask
# ------------------------------------------------------------------
app = Flask(
    __name__,
    template_folder=str(BASE_DIR / "templates"),
    static_folder=str(BASE_DIR / "static"),
)


@app.route("/")
def index():
    return render_template("index.html", cameras=CAM_META, max_cameras=MAX_CAMERAS)


@app.route("/video/<int:cam_id>")
def video(cam_id):
    worker = workers.get(cam_id)
    if worker is None:
        return "Camera khong ton tai", 404

    def gen():
        while True:
            frame = worker.get_frame()
            yield (b"--frame\r\nContent-Type: image/jpeg\r\n\r\n" + frame + b"\r\n")
            time.sleep(0.04)  # ~25 fps toi da phia client

    return Response(gen(), mimetype="multipart/x-mixed-replace; boundary=frame")


@app.route("/api/stats")
def api_stats():
    cams = [w.stats() for w in workers.values()]
    online = sum(1 for c in cams if c["status"] == "online")
    fps_vals = [c["fps"] for c in cams if c["status"] == "online"]
    summary = {
        "online": online,
        "total": len(cams),
        "alerts": sum(c["alerts"] for c in cams),
        "avg_fps": round(sum(fps_vals) / len(fps_vals), 1) if fps_vals else 0.0,
    }
    return jsonify({"cameras": cams, "summary": summary})


if __name__ == "__main__":
    port = int(SETTINGS.get("port", 5000))
    print("=" * 55)
    print(f"  DASHBOARD dang chay tai:  http://127.0.0.1:{port}")
    print(f"  (trong mang LAN: http://<IP-may-nay>:{port})")
    print("=" * 55)
    app.run(host="0.0.0.0", port=port, threaded=True, debug=False)
