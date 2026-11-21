// The prototype's beam watcher: an ATtiny3216 (SOIC-20) on an adapter board, at 3.3 V and 10 MHz,
// wired as hardware/prototype/wiring.md lists it. Pins by port name, as megaTinyCore numbers them.
//
// Fixed by the chip and not listed here: I2C SDA on PB1 and SCL on PB0, serial TX on PB2 and RX on
// PB3, UPDI on PA0.
#pragma once

#include <Arduino.h>

namespace board {

constexpr const char* NAME = "prototype";

constexpr uint8_t POINTS = 2;   // beam points: 0 nearer side A, 1 nearer side B
constexpr uint8_t HEIGHTS = 3;  // beams per point: lowest, middle, top

// Photodiodes, analog inputs of ADC0, by point and height.
constexpr uint8_t PHOTODIODE[POINTS][HEIGHTS] = {
    {PIN_PA1, PIN_PA2, PIN_PA3},
    {PIN_PA4, PIN_PA5, PIN_PA6},
};
constexpr uint8_t ROOF_PHOTODIODE = PIN_PA7;

// Laser switches, high = on. One switch per point lights its three lasers together; each
// photodiode is read in turn while they are on.
constexpr uint8_t LASERS[POINTS] = {PIN_PC0, PIN_PC1};
constexpr uint8_t ROOF_LASER = PIN_PC2;

constexpr uint8_t WAKE = PIN_PC3;  // to the camera controller, high to wake it
constexpr uint8_t PIR = PIN_PB4;   // from the PIR sensor module, high on movement

}  // namespace board
