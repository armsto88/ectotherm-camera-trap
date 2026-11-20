// The I2C link between the beam watcher (ATtiny3216) and the camera controller (ESP32-S3).
//
// The watcher raises its wake line when it has something to report; the camera controller then
// reads WatcherStatus from REG_STATUS and the waiting crossings from REG_EVENTS. The structs are
// packed so that both chips lay them out byte for byte the same.
#pragma once

#include <stdint.h>

const uint8_t LINK_ADDRESS = 0x42;  // watcher's I2C address

struct __attribute__((packed)) Crossing {  // one beam point entered or left
  uint32_t t_ms;                           // watcher clock, ms since its start
  uint8_t point;                           // 0 = nearer side A, 1 = nearer side B
  uint8_t heights;                         // bit 0 lowest, bit 1 middle, bit 2 top
  uint8_t entered;                         // 1 = first beam broken, 0 = all clear again
};

struct __attribute__((packed)) WatcherStatus {
  uint32_t now_ms;         // watcher clock when read, to map onto the RTC
  uint8_t stuck[2];        // per point, beams blocked longer than stuck_ms
  uint8_t pending;         // events waiting to be read
  uint8_t pir_since_read;  // 1 if the PIR sensor fired since the last read
};

enum LinkRegister : uint8_t { REG_STATUS = 0x00, REG_EVENTS = 0x10, REG_CONFIG = 0x20 };

// Bits of Crossing::heights and of the beam masks.
const uint8_t HEIGHT_LOWEST = 1 << 0;
const uint8_t HEIGHT_MIDDLE = 1 << 1;
const uint8_t HEIGHT_TOP = 1 << 2;
