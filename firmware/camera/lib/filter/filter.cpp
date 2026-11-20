#include "filter.h"

float thumbnail_difference(const uint8_t* a, const uint8_t* b, size_t n) {
  if (n == 0 || a == nullptr || b == nullptr) return 1.0f;
  uint64_t sum = 0;
  for (size_t i = 0; i < n; ++i) sum += a[i] > b[i] ? a[i] - b[i] : b[i] - a[i];
  return static_cast<float>(static_cast<double>(sum) / (255.0 * static_cast<double>(n)));
}

FilterResult judge(const Pass& p, float difference, float threshold, bool pilot_mode) {
  const bool pir_alone = p.by_pir && !p.by_lasers;
  // Written so that a difference that is not a number counts as unsure, and is kept.
  const bool looks_empty = difference < threshold;
  if (!pir_alone || !looks_empty) return FilterResult::Keep;
  return pilot_mode ? FilterResult::MarkEmpty : FilterResult::Drop;
}
