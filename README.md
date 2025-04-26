# ESP32 Camera Trap for Ectotherm Detection

A low-cost, DIY wildlife camera trap designed to improve the monitoring of **ectothermic animals** (such as reptiles and amphibians) by using a **Time-of-Flight (ToF) distance sensor** instead of a traditional PIR sensor.  
This system ensures better reliability when detecting animals that do not emit significant body heat.

---

## 🎯 Project Goals

- Use an OV2640 camera module to capture images when an animal is detected.
- Store captured photos on a microSD card, organized by date.
- Detect nearby movement using a **VL53L0X** Time-of-Flight sensor.
- Improve detection success for ectotherms over standard PIR-based systems.
- Ensure stable, low-power operation for extended field deployments.
- Allow for future expansion (e.g., deep sleep modes, burst capture, wireless file access).

---

## 📦 Hardware

- **ESP32-WROVER Dev Module**
  - Built-in PSRAM (required for high-resolution camera frames)
  - Stable USB Serial for debugging
- **OV2640 Camera Module** (external connection)
- **MicroSD Card Module** (SPI interface)
- **VL53L0X Time-of-Flight Distance Sensor**
- **DS3231 RTC Module** (for timestamping and folder organization)

**Optional Additions:**
- XSHUT line for power-cycling the VL53L0X sensor
- GPIO-based external interrupts for deep sleep wake-up
- Solar panel and battery system for remote, long-term deployment

---

## 🧠 System Overview

1. **VL53L0X** continuously monitors distance to detect nearby animals.
2. When an object is detected within a configurable range (e.g., <100 mm):
   - The ESP32 captures an image using the OV2640 camera.
   - The photo is saved on the microSD card inside a folder `/images/YYYY-MM-DD/`.
   - A visual confirmation is given via onboard LED flash.
   - A 5-second cooldown prevents rapid re-triggering.
3. **DS3231 RTC** provides real timestamps for file and folder organization.
4. Future versions will focus on deep sleep modes, photo bursts, and solar-charging field versions.

---

## 🔧 Current Features and Status

- ✅ VL53L0X live distance readings over Software I²C (GPIO32/33)
- ✅ Camera stable image capture at QVGA (320x240) resolution
- ✅ Photos stored reliably on SD card, organized by date
- ✅ DS3231 RTC integration for accurate timestamps
- ✅ Onboard LED blinks after each successful capture
- ✅ Automatic folder creation on SD card
- ✅ Fully autonomous distance-triggered operation
- ⚠️ ESP32-CAM board deprecated for this project due to GPIO and stability limitations

---

## 🚀 Planned Future Improvements

- Improve photo quality by optimizing camera parameters and memory handling.
- Implement **Deep Sleep Mode** to drastically reduce power consumption between triggers.
- Add support for **off-grid solar-powered battery operation** for remote deployments.
- Integrate **additional PIR sensor option** alongside the Time-of-Flight sensor:
  - Allow user-selectable triggers: Laser (ToF) / PIR / Both.
- Expand burst capture functionality: take multiple consecutive images on trigger.
- Explore Wi-Fi capabilities for wireless photo access or telemetry.

