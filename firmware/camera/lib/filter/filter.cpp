#include "filter.h"

namespace {

const size_t kPatch = 8;
const size_t kStep = 4;

// Where the next patch along a side of the given size starts after the one at start; size when
// none is left. Patches step by kStep, and the last one ends at the side's end.
size_t next_patch(size_t start, size_t size) {
  if (size <= kPatch || start + kPatch >= size) return size;
  return start + kStep + kPatch <= size ? start + kStep : size - kPatch;
}

}  // namespace

float thumbnail_difference(const uint8_t* a, const uint8_t* b, size_t width, size_t height) {
  if (width == 0 || height == 0 || a == nullptr || b == nullptr) return 1.0f;
  const size_t patch_w = width < kPatch ? width : kPatch;
  const size_t patch_h = height < kPatch ? height : kPatch;
  uint32_t largest = 0;
  for (size_t top = 0; top < height; top = next_patch(top, height)) {
    for (size_t left = 0; left < width; left = next_patch(left, width)) {
      uint32_t sum = 0;
      for (size_t y = top; y < top + patch_h; ++y) {
        const uint8_t* pa = a + y * width + left;
        const uint8_t* pb = b + y * width + left;
        for (size_t x = 0; x < patch_w; ++x) sum += pa[x] > pb[x] ? pa[x] - pb[x] : pb[x] - pa[x];
      }
      if (sum > largest) largest = sum;
    }
  }
  return static_cast<float>(static_cast<double>(largest) /
                            (255.0 * static_cast<double>(patch_w * patch_h)));
}

FilterResult judge(const Pass& p, float difference, float threshold, bool pilot_mode) {
  const bool pir_alone = p.by_pir && !p.by_lasers;
  // Written so that a difference that is not a number counts as unsure, and is kept.
  const bool looks_empty = difference < threshold;
  if (!pir_alone || !looks_empty) return FilterResult::Keep;
  return pilot_mode ? FilterResult::MarkEmpty : FilterResult::Drop;
}
