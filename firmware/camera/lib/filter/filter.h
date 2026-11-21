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

/// The largest mean absolute difference of two greyscale thumbnails, width by height pixels row
/// by row, over patches of 8 by 8 pixels stepping 4 (the whole thumbnail along a side shorter
/// than 8), from 0 to 1. Patch by patch, a small animal in one place counts as much as a large
/// one: a 3 cm animal covers about one percent of the view, which a difference averaged over the
/// whole picture would miss. Gives 1 for empty thumbnails, so that a picture that cannot be
/// compared is kept.
float thumbnail_difference(const uint8_t* a, const uint8_t* b, size_t width, size_t height);

enum class FilterResult : uint8_t { Keep, Drop, MarkEmpty };

/// Keep unless the PIR alone noticed the pass and difference < threshold;
/// MarkEmpty instead of Drop in pilot mode.
FilterResult judge(const Pass& p, float difference, float threshold, bool pilot_mode);
