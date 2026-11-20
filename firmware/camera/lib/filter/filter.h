// Filter: decides whether a picture may be dropped as empty.
// No hardware calls, so it is tested on the computer.
//
// Only a pass that the PIR sensor alone noticed can lose pictures, and only pictures that look
// like the day's empty view. Every pass the lasers noticed keeps all its pictures, so the filter
// can only err on the side of keeping.
#pragma once

#include <stddef.h>
#include <stdint.h>

#include "passes.h"

/// Mean absolute difference of two greyscale thumbnails of n pixels, from 0 to 1.
/// Gives 1 for empty thumbnails, so that a picture that cannot be compared is kept.
float thumbnail_difference(const uint8_t* a, const uint8_t* b, size_t n);

enum class FilterResult : uint8_t { Keep, Drop, MarkEmpty };

/// Keep unless the PIR alone noticed the pass and difference < threshold;
/// MarkEmpty instead of Drop in pilot mode.
FilterResult judge(const Pass& p, float difference, float threshold, bool pilot_mode);
