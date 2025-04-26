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


-----------------------



# 🧪 Dev Blog – ESP32 Camera Trap (VL53L0X + Camera + SD)
📅 26.04.2025 – Full System Integration and Laser-Triggered Capture Working

---

## 🎯 Today's Goal

- Integrate **ESP32-WROVER**, **VL53L0X sensor**, **camera module**, and **SD card** into one stable working system.
- Capture a photo automatically when an object is detected within **100mm** range.
- Save the captured image to the SD card.
- Provide a **visual confirmation** via LED blink after each successful capture.

---

## ⚙️ Major Achievements

✅ **Camera initialized and captures photos reliably**  
✅ **SD card mounted and saves JPEG images**  
✅ **VL53L0X ToF sensor reads continuous distance data**  
✅ **System triggers capture when distance < 100mm**  
✅ **Onboard LED blinks after photo capture**  
✅ **Full separation of buses:**
- Camera uses dedicated parallel bus
- SD card uses HSPI bus (GPIO14/12/13/15)
- VL53L0X moved to Software I²C bus on GPIO32/33

✅ **No conflicts between Camera, SD card, and Sensor**.

---

## 😬 Problems Encountered and Solutions

| Problem | Solution |
|---------|----------|
| ❌ I2C/SPI bus conflict with camera and SD card | Carefully separated SD card to HSPI, VL53L0X to Software I²C |
| ❌ SPI bus conflict when using default VSPI pins | Moved SD card to HSPI (GPIO14,12,13,15) |
| ❌ I²C initialization failures (bus acquisition errors) | Corrected setup order: reassign default Wire bus instead of creating a new TwoWire instance |
| ❌ Camera and SD card wiring collision risk | Carefully mapped correct GPIOs to camera and SD independently |
| ❌ Sensor timeout (no device detected) | Fixed wiring: SDA and SCL moved to clean GPIO32/33 lines |
| ❌ Camera capture failed randomly | Slowed SPI clock to SD card to 5 MHz, optimized PSRAM usage for double frame buffering |

---

## 🔥 Final Working Architecture

| Peripheral | GPIO Pins | Notes |
|------------|-----------|-------|
| Camera data bus | 4, 5, 18, 19, 21, 22, 23, 25, 35, 34, 36, 39 | Full 8-bit parallel + SCCB on 26/27 |
| SD card SPI bus | 14 (SCK), 12 (MISO), 13 (MOSI), 15 (CS) | HSPI bus, slower SPI clock for stability |
| VL53L0X ToF sensor | 32 (SDA), 33 (SCL) | Software I²C, clean separation |
| Onboard LED | 2 | Visual capture confirmation |

---

## 🛠️ Summary of Final System Behavior

- VL53L0X continuously monitors distance every 200 ms.
- When an object comes closer than 100mm:
  - 📸 Camera captures a JPEG frame
  - 💾 Photo is saved to SD card with filename based on `millis()`
  - 💡 LED blinks briefly to confirm capture
  - System pauses for 5 seconds to prevent repeated rapid captures
- Loop repeats indefinitely.

---

## ✨ Next Improvements (Optional)

- [ ] Use filename counters (e.g., `/photo_001.jpg`) instead of `millis()`
- [ ] Add timestamp to photo filenames
- [ ] Add battery + solar panel support
- [ ] Implement Deep Sleep mode for ultra-low power
- [ ] Serve photos over Wi-Fi for remote access

---



---


