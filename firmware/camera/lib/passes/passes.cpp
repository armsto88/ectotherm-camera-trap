#include "passes.h"

PassBuilder::PassBuilder(uint32_t quiet_ms, uint8_t ignore_a, uint8_t ignore_b)
    : quiet_ms_(quiet_ms), ignore_{ignore_a, ignore_b} {}

void PassBuilder::start(uint32_t t_ms) {
  open_ = true;
  current_ = Pass{t_ms, t_ms, Direction::Unknown, 0, 0, false, false};
  first_point_ = -1;
  last_point_ = -1;
  seen_[0] = seen_[1] = false;
  occupied_[0] = occupied_[1] = false;
}

Direction PassBuilder::direction() const {
  if (first_point_ < 0) return Direction::Unknown;
  const bool through = seen_[0] && seen_[1] && last_point_ != first_point_;
  if (first_point_ == 0) return through ? Direction::AtoB : Direction::BackA;
  return through ? Direction::BtoA : Direction::BackB;
}

void PassBuilder::complete() {
  current_.direction = direction();
  done_ = current_;
  open_ = false;
}

bool PassBuilder::add(const Crossing& c) {
  if (c.point > 1) return false;
  const uint8_t heights = c.heights & static_cast<uint8_t>(~ignore_[c.point]);
  if (heights == 0) return false;  // only ignored beams changed

  if (!open_) start(c.t_ms);
  last_event_ms_ = c.t_ms;
  current_.end_ms = c.t_ms;
  current_.by_lasers = true;
  if (c.point == 0) {
    current_.heights_a |= heights;
  } else {
    current_.heights_b |= heights;
  }
  if (first_point_ < 0) first_point_ = static_cast<int8_t>(c.point);
  last_point_ = static_cast<int8_t>(c.point);
  seen_[c.point] = true;
  occupied_[c.point] = c.entered != 0;

  // Leaving the second point with the first one clear: the animal went through.
  const bool left_far_point = !c.entered && c.point != first_point_;
  if (left_far_point && seen_[0] && seen_[1] && !occupied_[0] && !occupied_[1]) {
    complete();
    return true;
  }
  return false;
}

void PassBuilder::add_pir(uint32_t t_ms) {
  if (!open_) start(t_ms);
  last_event_ms_ = t_ms;
  current_.end_ms = t_ms;
  current_.by_pir = true;
}

bool PassBuilder::tick(uint32_t now_ms) {
  if (!open_) return false;
  // Unsigned subtraction keeps working when the watcher clock wraps.
  if (now_ms - last_event_ms_ < quiet_ms_) return false;
  complete();
  return true;
}

const Pass& PassBuilder::pass() const { return done_; }
