// Code hoàn chỉnh cho dự án ESP32-CAM Stream Video với IP Tĩnh
// Dựa trên ví dụ CameraWebServer của Espressif

#include "esp_camera.h"
#include <WiFi.h>
#include "soc/soc.h"
#include "soc/rtc_cntl_reg.h"
#include "driver/rtc_io.h"

// --- BƯỚC 1: CẤU HÌNH ---

// --- CHỌN ĐÚNG LOẠI CAMERA ---
// Đảm bảo dòng này đã được bỏ comment (không có // ở đầu)
#define CAMERA_MODEL_AI_THINKER

// --- THÔNG TIN WI-FI CỦA BẠN ---
const char* ssid = "YOUR_WIFI_SSID";
const char* password = "YOUR_WIFI_PASSWORD";

// --- CẤU HÌNH IP TĨNH ---
IPAddress local_IP(192, 168, 100, 201);
IPAddress gateway(192, 168, 100, 1);
IPAddress subnet(255, 255, 255, 0);
IPAddress primaryDNS(8, 8, 8, 8);   // DNS của Google
IPAddress secondaryDNS(8, 8, 4, 4); // DNS dự phòng của Google

// --- PHẦN ĐỊNH NGHĨA CHÂN GPIO (Không cần sửa) ---
#if defined(CAMERA_MODEL_AI_THINKER)
  #define PWDN_GPIO_NUM     32
  #define RESET_GPIO_NUM    -1
  #define XCLK_GPIO_NUM      0
  #define SIOD_GPIO_NUM     26
  #define SIOC_GPIO_NUM     27
  #define Y9_GPIO_NUM       35
  #define Y8_GPIO_NUM       34
  #define Y7_GPIO_NUM       39
  #define Y6_GPIO_NUM       36
  #define Y5_GPIO_NUM       21
  #define Y4_GPIO_NUM       19
  #define Y3_GPIO_NUM       18
  #define Y2_GPIO_NUM        5
  #define VSYNC_GPIO_NUM    25
  #define HREF_GPIO_NUM     23
  #define PCLK_GPIO_NUM     22
#else
  #error "Camera model not selected"
#endif

// Khai báo hàm startCameraServer() từ file app_httpd.cpp đi kèm
void startCameraServer();

// --- BƯỚC 2: HÀM SETUP CHÍNH ---
void setup() {
  WRITE_PERI_REG(RTC_CNTL_BROWN_OUT_REG, 0); // Tắt bộ dò sụt áp

  Serial.begin(115200);
  Serial.setDebugOutput(true);
  Serial.println();

  // Cấu hình camera
  camera_config_t config;
  config.ledc_channel = LEDC_CHANNEL_0;
  config.ledc_timer = LEDC_TIMER_0;
  config.pin_d0 = Y2_GPIO_NUM;
  config.pin_d1 = Y3_GPIO_NUM;
  config.pin_d2 = Y4_GPIO_NUM;
  config.pin_d3 = Y5_GPIO_NUM;
  config.pin_d4 = Y6_GPIO_NUM;
  config.pin_d5 = Y7_GPIO_NUM;
  config.pin_d6 = Y8_GPIO_NUM;
  config.pin_d7 = Y9_GPIO_NUM;
  config.pin_xclk = XCLK_GPIO_NUM;
  config.pin_pclk = PCLK_GPIO_NUM;
  config.pin_vsync = VSYNC_GPIO_NUM;
  config.pin_href = HREF_GPIO_NUM;
  config.pin_sscb_sda = SIOD_GPIO_NUM;
  config.pin_sscb_scl = SIOC_GPIO_NUM;
  config.pin_pwdn = PWDN_GPIO_NUM;
  config.pin_reset = RESET_GPIO_NUM;
  config.xclk_freq_hz = 20000000;
  config.pixel_format = PIXFORMAT_JPEG;
  
  // Để có tốc độ nhanh nhất, hãy dùng độ phân giải thấp
  config.frame_size = FRAMESIZE_VGA; // 640x480. Tốt cho YOLO
  config.jpeg_quality = 12; // 0-63, số càng nhỏ chất lượng càng cao
  config.fb_count = 2;

  // Khởi tạo camera
  esp_err_t err = esp_camera_init(&config);
  if (err != ESP_OK) {
    Serial.printf("Khoi tao Camera that bai, loi: 0x%x", err);
    return;
  }

  // Áp dụng cấu hình IP tĩnh TRƯỚC khi kết nối WiFi
  if (!WiFi.config(local_IP, gateway, subnet, primaryDNS, secondaryDNS)) {
    Serial.println("Cau hinh IP tinh that bai!");
  }

  // Bắt đầu kết nối WiFi
  Serial.print("Dang ket noi toi Wi-Fi: ");
  Serial.println(ssid);
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("");
  Serial.println("Da ket noi Wi-Fi thanh cong!");

  Serial.print("Dia chi IP Tinh cua Camera: http://");
  Serial.println(WiFi.localIP());

  // Bắt đầu Web Server để stream video
  startCameraServer();

  Serial.print("Luong video (stream) san sang tai: http://");
  Serial.print(WiFi.localIP());
  Serial.println("/stream");
}

// --- BƯỚC 3: HÀM LOOP ---
void loop() {
  // Để trống, server chạy trên một core khác
}