// Beam watching: turns raw photodiode samples into crossings and stuck beams.
// No hardware calls, so it is tested on the computer.
#pragma once

#include <stdint.h>

#include "link.h"

// One beam: a pulsed laser on one wall and a photodiode on the other. Each pulse gives the
// photodiode level with the laser on (lit) and off (dark). Only their difference counts, so steady
// daylight cancels out.
class BeamFilter {
 public:
  /// Takes one pulse: the photodiode level with and without the laser; true when interrupted.
  bool update(uint16_t lit, uint16_t dark);

  // A clear beam gives at least this much more light with the laser on (10-bit readings).
  static constexpr uint16_t MIN_CLEAR_SIGNAL = 64;
  // At or above this dark level the photodiode is near full scale and the laser cannot show.
  static constexpr uint16_t SATURATED = 1000;
  // Pulses in a row that must disagree with the current state before it changes.
  static constexpr uint8_t PULSES_TO_CHANGE = 2;

 private:
  bool interrupted_ = false;
  uint8_t disagreeing_ = 0;
  uint16_t clear_level_ = 0;  // running average of a clear beam's signal; 0 until first seen
};

// One beam point: the beams at its two or three heights, given as a mask of interrupted beams.
class PointTracker {
 public:
  explicit PointTracker(uint8_t point);
  /// Takes one sample of the point's interrupted-beam mask; true when out holds a crossing.
  /// The entered crossing carries the heights interrupted at that moment, the left crossing all
  /// heights interrupted while the point was occupied.
  bool update(uint32_t t_ms, uint8_t mask, Crossing* out);

 private:
  uint8_t point_;
  uint8_t occupied_heights_ = 0;  // heights seen since the point was entered; 0 when clear
};

// Beams interrupted for longer than any pass takes, such as by debris.
class StuckBeams {
 public:
  explicit StuckBeams(uint32_t stuck_ms);
  /// Updates with the point's mask; returns the beams interrupted longer than stuck_ms.
  uint8_t update(uint32_t t_ms, uint8_t mask);

  static constexpr uint8_t MAX_BEAMS = 8;

 private:
  uint32_t stuck_ms_;
  uint8_t interrupted_ = 0;
  uint32_t since_[MAX_BEAMS] = {};  // when each interrupted beam became interrupted
};
