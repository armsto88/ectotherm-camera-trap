// The prototype's camera controller: an ESP32-S3-WROOM camera board with octal PSRAM, its camera
// connector wired like the ESP32-S3-EYE (as on Freenove's ESP32-S3-WROOM CAM board) and its
// microSD slot in 1-bit SD mode, with the parts wired to its free pins as
// hardware/prototype/wiring.md lists them.
//
// Taken on the board and not free: the camera (4 to 13, 15 to 18), the microSD slot (38 to 40), the
// PSRAM (35 to 37), USB (19, 20) and the serial port (43, 44).
#pragma once

namespace board {

constexpr const char* NAME = "prototype";

// Camera connector. PWDN and RESET are not wired on such boards.
constexpr int CAM_PWDN = -1;
constexpr int CAM_RESET = -1;
constexpr int CAM_XCLK = 15;
constexpr int CAM_SIOD = 4;
constexpr int CAM_SIOC = 5;
constexpr int CAM_D[8] = {11, 9, 8, 10, 12, 18, 17, 16};  // Y2 to Y9
constexpr int CAM_VSYNC = 6;
constexpr int CAM_HREF = 7;
constexpr int CAM_PCLK = 13;

// microSD slot, 1-bit SD mode.
constexpr int SD_CLK = 39;
constexpr int SD_CMD = 38;
constexpr int SD_D0 = 40;

// The wired parts. WAKE and CLOCK_ALARM are RTC pins, so either can wake the chip from deep sleep.
constexpr int I2C_SDA = 41;      // to the clock module and the watcher
constexpr int I2C_SCL = 42;
constexpr int WAKE = 14;         // from the watcher, high to wake
constexpr int CLOCK_ALARM = 21;  // from the clock module's INT/SQW, low on an alarm
constexpr int IR_LEDS = 1;       // gate of the infrared LEDs' switch, high = on

}  // namespace board
