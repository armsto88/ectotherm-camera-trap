# 🦎 ESP32 Camera Trap for Ectotherm Detection

A low-cost, DIY wildlife camera trap that detects and photographs **ectothermic animals** (such as reptiles and amphibians) using a **Time-of-Flight (ToF) distance sensor** instead of a traditional PIR sensor. Designed for better reliability when monitoring animals that do not emit significant body heat.

---

## 🎯 Project Goals

- 📸 Use a camera (OV2640) to capture high-resolution images
- 💾 Store photos on a microSD card
- 🧠 Detect animals using a **VL53L0X** Time-of-Flight sensor
- 🦎 Improve detection of ectotherms over PIR-based systems
- 🔋 Run efficiently for field deployment
- 🛠️ Allow future expansion (e.g., wireless transmission, interrupt triggers)

---

## 📦 Hardware

- **ESP32-WROVER Dev Module**
  - Built-in PSRAM (required for camera)
  - USB Serial for easy debugging
- **OV2640 Camera Module** (external)
- **MicroSD card module** (SPI)
- **VL53L0X ToF Distance Sensor**
- **Optional:**
  - XSHUT line to power-cycle sensor
  - GPIO-based interrupt trigger for low-power modes

---

## 🧠 How It Works

1. The **VL53L0X** continuously measures distance.
2. When an object is detected within a configurable range (e.g. < 400 mm), the ESP32:
   - Captures a photo using the camera
   - Saves it to the SD card
   - Logs the event over Serial (and optionally to a file)
3. Future versions will support deep sleep and interrupt wakeups for ultra-low power deployment.

---

## 🔧 Status

- ✅ VL53L0X live distance reading via I²C
- ✅ Camera capture working on ESP32-WROVER
- ✅ Photos saved to SD card
- ⚠️ ESP32-CAM board deprecated for this project due to GPIO limitations

---
