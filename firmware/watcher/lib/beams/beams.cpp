#include "beams.h"

bool BeamFilter::update(uint16_t lit, uint16_t dark) {
  // A saturated photodiode shows no difference whether the beam is clear or not: keep the state.
  if (dark >= SATURATED) {
    disagreeing_ = 0;
    return interrupted_;
  }

  const uint16_t signal = lit > dark ? lit - dark : 0;
  // Half the usual clear signal, so a laser dimmed by dirt over the season still counts as clear.
  uint16_t threshold = clear_level_ / 2;
  if (threshold < MIN_CLEAR_SIGNAL) threshold = MIN_CLEAR_SIGNAL;
  const bool looks_interrupted = signal < threshold;

  if (looks_interrupted == interrupted_) {
    disagreeing_ = 0;
  } else if (++disagreeing_ >= PULSES_TO_CHANGE) {
    interrupted_ = looks_interrupted;
    disagreeing_ = 0;
  }

  if (!interrupted_ && !looks_interrupted) {
    if (clear_level_ == 0) {
      clear_level_ = signal;
    } else {
      clear_level_ = static_cast<uint16_t>(clear_level_ + (static_cast<int32_t>(signal) - clear_level_) / 16);
    }
  }
  return interrupted_;
}

PointTracker::PointTracker(uint8_t point) : point_(point) {}

bool PointTracker::update(uint32_t t_ms, uint8_t mask, Crossing* out) {
  if (occupied_heights_ == 0) {
    if (mask == 0) return false;
    occupied_heights_ = mask;
    *out = Crossing{t_ms, point_, mask, 1};
    return true;
  }
  if (mask != 0) {
    occupied_heights_ |= mask;
    return false;
  }
  *out = Crossing{t_ms, point_, occupied_heights_, 0};
  occupied_heights_ = 0;
  return true;
}

StuckBeams::StuckBeams(uint32_t stuck_ms) : stuck_ms_(stuck_ms) {}

uint8_t StuckBeams::update(uint32_t t_ms, uint8_t mask) {
  uint8_t stuck = 0;
  for (uint8_t beam = 0; beam < MAX_BEAMS; ++beam) {
    const uint8_t bit = static_cast<uint8_t>(1u << beam);
    if (!(mask & bit)) continue;
    if (!(interrupted_ & bit)) since_[beam] = t_ms;
    // Unsigned subtraction keeps working when the watcher clock wraps.
    if (t_ms - since_[beam] > stuck_ms_) stuck |= bit;
  }
  interrupted_ = mask;
  return stuck;
}
