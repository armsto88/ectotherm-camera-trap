// Passes: builds passes from the watcher's crossings and the PIR sensor's events.
// No hardware calls, so it is tested on the computer.
#pragma once

#include <stdint.h>

#include "link.h"

// Side A is the end nearer beam point 0, side B the end nearer beam point 1.
// BackA: entered on side A and left on side A without going through; BackB likewise.
// Unknown: only the PIR sensor noticed the pass, so its direction is not known.
enum class Direction : uint8_t { AtoB, BtoA, BackA, BackB, Unknown };

struct Pass {
  uint32_t start_ms, end_ms;     // watcher clock
  Direction direction;
  uint8_t heights_a, heights_b;  // heights interrupted at each point
  bool by_lasers, by_pir;
};

// Events go in in time order. A pass ends when the animal leaves the second beam point it crossed
// with the first one clear, or after quiet_ms without any event. Turned-back and PIR-only passes
// can only end the second way, since a beam point alone cannot tell which way an animal left it.
class PassBuilder {
 public:
  /// ignore_a and ignore_b are heights left out at each point, such as beams blocked by debris.
  explicit PassBuilder(uint32_t quiet_ms, uint8_t ignore_a, uint8_t ignore_b);
  /// Adds a crossing in time order; true when it completes a pass, now in pass().
  /// Call tick() with the crossing's time first, so that a pass that has ended is not extended.
  bool add(const Crossing& c);
  /// Adds a PIR event; starts a pass if none is open. Call tick() with its time first.
  void add_pir(uint32_t t_ms);
  /// Closes an open pass after quiet_ms without events; true when a pass completed.
  bool tick(uint32_t now_ms);
  /// The pass completed last.
  const Pass& pass() const;
  /// True while a pass is open.
  bool open() const { return open_; }

 private:
  void start(uint32_t t_ms);
  Direction direction() const;
  void complete();

  uint32_t quiet_ms_;
  uint8_t ignore_[2];

  bool open_ = false;
  Pass current_{};
  Pass done_{};
  uint32_t last_event_ms_ = 0;
  int8_t first_point_ = -1;  // first beam point crossed in the open pass; -1 for none yet
  int8_t last_point_ = -1;   // beam point of the latest crossing
  bool seen_[2] = {false, false};
  bool occupied_[2] = {false, false};
};
