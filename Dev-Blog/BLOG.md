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
📅 26.04.2025 – Full System Integration and Laser-Triggered Capture with Organized Storage

---

## 🎯 Today's Goal

- Integrate **ESP32-WROVER**, **VL53L0X ToF sensor**, **camera module**, **SD card**, and **RTC module** into one fully working wildlife camera trap system.
- Capture a photo automatically when an object is detected within **100mm** range.
- Save captured images **organized by date** into `/images/YYYY-MM-DD/` folders on the SD card.
- Provide a **visual confirmation** via LED blink after each successful capture.
- Ensure **stable operation** (no crashes, no image glitches) at **QVGA resolution** for long-term field deployment.

---

## ⚙️ Major Achievements

✅ **Camera initialized reliably with clean frame captures**  
✅ **SD card mounted and structured folder organization working**  
✅ **VL53L0X ToF sensor reads continuous distance data**  
✅ **DS3231 RTC providing real-time timestamps for filenames and folder organization**  
✅ **System triggers and saves capture cleanly when distance < 100mm**  
✅ **Onboard LED blinks after each successful photo capture**  
✅ **Stable memory handling at QVGA resolution**  
✅ **Full separation of buses:**
- Camera uses dedicated parallel bus
- SD card uses HSPI bus (GPIO14/12/13/15)
- VL53L0X and RTC share Software I²C bus on GPIO32/33

✅ **No conflicts between Camera, SD card, ToF sensor, or RTC.**

---

## 😬 Problems Encountered and Solutions

| Problem | Solution |
|---------|----------|
| ❌ I2C/SPI bus conflict with camera and SD card | Carefully separated SD card to HSPI, VL53L0X and RTC to Software I²C |
| ❌ SPI bus conflict when using default VSPI pins | Moved SD card to HSPI (GPIO14,12,13,15) |
| ❌ Camera image glitches (horizontal line artifacts) | Lowered camera XCLK frequency from 20 MHz ➔ 16 MHz |
| ❌ SD card mount failures during fast boot | Added a 300 ms stabilization delay after SPI begin |
| ❌ Large frame memory overflow at VGA resolution | Reduced frame size to **QVGA** for long-term stability |
| ❌ Failed folder creation for date organization | Auto-create `/images` base folder during setup |

---

## 🔥 Final Working Architecture

| Peripheral | GPIO Pins | Notes |
|------------|-----------|-------|
| Camera data bus | 4, 5, 18, 19, 21, 22, 23, 25, 35, 34, 36, 39 | Full 8-bit parallel + SCCB on 26/27 |
| SD card SPI bus | 14 (SCK), 12 (MISO), 13 (MOSI), 15 (CS) | HSPI bus, safe 5 MHz speed |
| VL53L0X ToF sensor | 32 (SDA), 33 (SCL) | Software I²C bus |
| DS3231 RTC module | 32 (SDA), 33 (SCL) | Shared Software I²C |
| Onboard LED | 2 | Visual capture confirmation |

---

## 🛠️ Summary of Final System Behavior

- VL53L0X continuously monitors distance every 200 ms.
- When an object approaches within **100mm**:
  - 📸 Camera captures a JPEG frame (QVGA 320x240 resolution)
  - 💾 Saves photo into `/images/YYYY-MM-DD/photo_HH-MM-SS.jpg`
  - 📂 Automatically creates dated folders for clean organization
  - 💡 LED blinks briefly after each capture
- System pauses for 5 seconds to prevent repeated triggers.
- Fully autonomous loop for long-term remote deployment.

---

## ✨ Possible Future Improvements

- [ ] Add **photo counters** to filenames for easier analysis (e.g., `/photo_001.jpg`)
- [ ] Implement **burst mode** (multiple photos per trigger)
- [ ] Add **Deep Sleep Mode** to massively extend battery life
- [ ] Add **solar panel + battery management** for remote operation
- [ ] Implement **Wi-Fi based photo retrieval** over a local access point

---





---


