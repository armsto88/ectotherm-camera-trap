# 🧪 Dev Blog – ESP32 Camera Trap (VL53L0X + Camera + SD)

## 📅 18.04.2025 – Trials & Tribulations with the ESP32-CAM

### 🎯 Goal
Build a wildlife camera trap that uses an alternative to traditional PIR sensors,
improving detection accuracy for ectothermic animals such as reptiles and amphibians.
The device should:
- Use an ESP32-based board with built-in or external camera
- Include a VL53L0X ToF distance sensor to detect nearby animals
- Store captured photos to an SD card
- Trigger on a set distance threshold (e.g., < 400 mm)
- Support future additions like interrupts or wireless transmission

---

## 😬 Initial Hurdles

### 🧠 I²C with Camera and SD Card
- ESP32-CAM uses GPIOs 12–15, 2, 4 for the built-in camera and SD card functions.
- Attempted to run the VL53L0X on GPIO 14/15 → **conflicted with SD card**.
- Tried Software I²C on GPIO 0/3 → **disabled Serial Monitor** (essential for debugging).
- Sensor worked in isolation but failed when camera was initialized.

### ❌ Camera Initialization Fails
- Tried using `TwoWire(1)` for VL53L0X → **conflicted with the SCCB interface** used by the OV2640 camera.
- Error shown: `Camera probe failed with error 0x105`.

### 🧨 Sensor Reading Issues
- VL53L0X reported constant 65535 mm → a known sign of failed I²C communication or sensor lock-up.
- Likely caused by timing issues or I²C bus contention.
- Sensor had to be re-initialized after camera setup to recover.

### ⚠️ Boot Issues on GPIO 12
- GPIO 12 used for I²C caused flash upload errors:  
  `Failed to communicate with flash chip`
- Root cause: GPIO 12 is **boot-mode sensitive** and can disrupt booting when pulled HIGH.

---

## 🧪 Experiments Tried

- Sharing I²C between camera and VL53L0X — failed due to bus collision.
- Controlling VL53L0X with XSHUT pin — lacked GPIOs to support this **and** an interrupt line.
- Swapped between various GPIOs for I²C (0, 3, 12, 13, 14, 15) — all had trade-offs.
- Temporarily disabled SD card to isolate camera and sensor logic.

---

## 🔄 Final Realization

> 🧠 The ESP32-CAM is **not suitable** for simultaneously running a camera, SD card, I²C sensor, interrupt line, and serial debug. It simply doesn’t have enough flexible GPIO or hardware independence to support everything cleanly.

---

## ✅ Final Decision

**Switch to the ESP32-WROVER Dev Module**, which offers:
- ✅ Built-in PSRAM (essential for camera)
- ✅ Support for external SPI SD card
- ✅ Full control over I²C pin assignment
- ✅ Plenty of spare GPIOs for XSHUT, interrupts, and debugging
- ✅ Stable Serial Monitor via USB

---

## 🛠️ Next Steps

- Migrate code to the ESP32-WROVER Dev board
- Set up camera and SD card on dedicated, conflict-free pins
- Reconnect VL53L0X on `TwoWire(0)` or `TwoWire(1)`
- Integrate optional interrupt/XSHUT pin for sleep + trigger support
- Create full wiring diagrams and configuration documentation in `/docs`
- Begin field testing with real-world deployment setup

---

📝 Stay tuned for `v0.2` — full WROVER integration and system test!
