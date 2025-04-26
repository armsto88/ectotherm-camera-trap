#include "esp_camera.h"
#include "Wire.h"
#include "VL53L0X.h"
#include "RTClib.h"
#include "FS.h"
#include "SD.h"
#include "SPI.h"

// ==== Camera Pin Mapping (Freenove ESP32-WROVER-CAM) ====
#define PWDN_GPIO_NUM    -1
#define RESET_GPIO_NUM   -1
#define XCLK_GPIO_NUM    21
#define SIOD_GPIO_NUM    26
#define SIOC_GPIO_NUM    27

#define Y9_GPIO_NUM      35
#define Y8_GPIO_NUM      34
#define Y7_GPIO_NUM      39
#define Y6_GPIO_NUM      36
#define Y5_GPIO_NUM      19
#define Y4_GPIO_NUM      18
#define Y3_GPIO_NUM      5
#define Y2_GPIO_NUM      4
#define VSYNC_GPIO_NUM   25
#define HREF_GPIO_NUM    23
#define PCLK_GPIO_NUM    22

// ==== SD Card SPI Pins ====
#define SD_CS    15
#define SD_MOSI  13
#define SD_MISO  12
#define SD_SCK   14

// ==== ToF Sensor + RTC I2C Pins ====
#define I2C_SDA 32
#define I2C_SCL 33

// ==== Distance Trigger Setting ====
#define DISTANCE_TRIGGER_MM 100
#define TRIGGER_DELAY_MS 5000 // 5 second pause after capture

// ==== Onboard LED Pin ====
#define LED_PIN 2

VL53L0X sensor;      // ToF distance sensor
RTC_DS3231 rtc;      // Real Time Clock

void setup() {
  Serial.begin(115200);
  Serial.setDebugOutput(true);
  Serial.println();
  Serial.println("🦎 Starting Wildlife Camera Trap v0.8 (Stable QVGA Mode)...");

  // ==== Setup Onboard LED ====
  pinMode(LED_PIN, OUTPUT);
  digitalWrite(LED_PIN, LOW);

  // ==== Camera Setup ====
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
  config.xclk_freq_hz = 16000000; // Lowered clock for stability
  config.pixel_format = PIXFORMAT_JPEG;

  if (psramFound()) {
    config.frame_size = FRAMESIZE_QVGA;     // 320x240 resolution
    config.jpeg_quality = 8;               // Stable good quality
    config.fb_count = 1;
    config.fb_location = CAMERA_FB_IN_PSRAM;
    config.grab_mode = CAMERA_GRAB_LATEST;
  } else {
    config.frame_size = FRAMESIZE_QQVGA;
    config.jpeg_quality = 12;
    config.fb_count = 1;
    config.fb_location = CAMERA_FB_IN_DRAM;
    config.grab_mode = CAMERA_GRAB_WHEN_EMPTY;
  }

  esp_err_t err = esp_camera_init(&config);
  if (err != ESP_OK) {
    Serial.printf("❌ Camera init failed with error 0x%x\n", err);
    while (true);
  }
  Serial.println("✅ Camera initialized successfully!");

  delay(500); // Important: allow hardware to stabilize

  // ==== SD Card Setup ====
  Serial.println("💾 Mounting SD card...");
  SPI.begin(SD_SCK, SD_MISO, SD_MOSI, SD_CS);
  if (!SD.begin(SD_CS, SPI, 5000000)) {
    Serial.println("❌ SD Card Mount Failed");
    while (true);
  }
  Serial.println("✅ SD Card Mounted!");

  // ==== Create base folder if missing ====
  if (!SD.exists("/images")) {
    if (SD.mkdir("/images")) {
      Serial.println("✅ Created /images base folder");
    } else {
      Serial.println("❌ Failed to create /images base folder");
    }
  }

  // ==== Wire Setup for ToF + RTC ====
  Wire.begin(I2C_SDA, I2C_SCL);

  // ==== RTC Setup ====
  Serial.println("🕰️ Setting up RTC...");
  if (!rtc.begin()) {
    Serial.println("❌ Couldn't find RTC!");
    while (true);
  }
  if (rtc.lostPower()) {
    Serial.println("⚡ RTC lost power, setting time to compile time!");
    rtc.adjust(DateTime(F(__DATE__), F(__TIME__)));
  }
  Serial.println("✅ RTC running.");

  // ==== ToF Sensor Setup ====
  Serial.println("📏 Setting up VL53L0X Sensor...");
  sensor.setBus(&Wire);
  sensor.setTimeout(500);

  if (!sensor.init()) {
    Serial.println("❌ VL53L0X Sensor not detected!");
    while (true);
  }
  sensor.startContinuous();
  Serial.println("✅ VL53L0X ready, continuous mode!");
}

void loop() {
  int dist = sensor.readRangeContinuousMillimeters();

  if (sensor.timeoutOccurred()) {
    Serial.println("⚠️ VL53L0X timeout");
  } else {
    Serial.print("📏 Distance: ");
    Serial.print(dist);
    Serial.println(" mm");

    if (dist > 0 && dist < DISTANCE_TRIGGER_MM) {
      Serial.println("🚨 Object detected! Capturing HQ photo...");

      // ==== Capture photo ====
      camera_fb_t * fb = esp_camera_fb_get();
      if (!fb) {
        Serial.println("❌ Camera capture failed (fb == NULL)");
        return;
      }

      // ==== Build organized folder path and filename ====
      DateTime now = rtc.now();

      char folderPath[30];
      sprintf(folderPath, "/images/%04d-%02d-%02d", now.year(), now.month(), now.day());

      if (!SD.exists(folderPath)) {
        if (SD.mkdir(folderPath)) {
          Serial.print("✅ Created folder: ");
          Serial.println(folderPath);
        } else {
          Serial.println("❌ Failed to create folder!");
        }
      }

      char filename[60];
      sprintf(filename, "%s/photo_%02d-%02d-%02d.jpg", folderPath,
              now.hour(), now.minute(), now.second());

      // ==== Save photo ====
      File file = SD.open(filename, FILE_WRITE);
      if (!file) {
        Serial.println("❌ Failed to open file for writing");
      } else {
        file.write(fb->buf, fb->len);
        Serial.print("💾 Photo saved to: ");
        Serial.println(filename);
      }

      file.close();
      esp_camera_fb_return(fb);

      // ==== Blink LED ====
      digitalWrite(LED_PIN, HIGH);
      delay(200);
      digitalWrite(LED_PIN, LOW);

      // ==== Delay to prevent rapid retriggering ====
      delay(TRIGGER_DELAY_MS);
    }
  }

  delay(200); // Poll sensor every 200ms
}
