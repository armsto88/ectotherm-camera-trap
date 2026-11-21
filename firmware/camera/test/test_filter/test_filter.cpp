// Unit tests of the filter: which pictures are kept, dropped or marked, and what the pass record
// then says about them.
#include <math.h>
#include <string.h>
#include <unity.h>

#include <string>

#include "filter.h"
#include "records.h"

void setUp() {}
void tearDown() {}

static const float THRESHOLD = 0.03f;
static const Pass PIR_ONLY{0, 4000, Direction::Unknown, 0, 0, false, true};
static const Pass LASERS{0, 4000, Direction::AtoB, HEIGHT_LOWEST, HEIGHT_LOWEST, true, false};
static const Pass BOTH{0, 4000, Direction::AtoB, HEIGHT_LOWEST, HEIGHT_LOWEST, true, true};

// The given field (0-based) of a pass CSV line.
static std::string field(const char* line, int index) {
  std::string s(line);
  size_t start = 0;
  for (int i = 0; i < index; ++i) start = s.find(',', start) + 1;
  const size_t end = s.find_first_of(",\n", start);
  return s.substr(start, end - start);
}

// Thumbnails of 64 by 48 pixels, as the camera controller makes them.
static const size_t W = 64, H = 48;

// The empty passage floor, with a little noise when asked, as two pictures of it differ.
static void floor_thumbnail(uint8_t* t, unsigned noise_seed) {
  unsigned state = noise_seed;
  for (size_t i = 0; i < W * H; ++i) {
    state = state * 1103515245u + 12345u;
    t[i] = static_cast<uint8_t>(128 + (noise_seed ? static_cast<int>((state >> 16) % 7) - 3 : 0));
  }
}

// A lizard 3 cm long and 1 cm wide in a view of 26 by 15 cm: 7 by 3 pixels of the thumbnail, a
// little darker than the floor.
static void add_small_lizard(uint8_t* t, size_t left, size_t top) {
  for (size_t y = top; y < top + 3; ++y)
    for (size_t x = left; x < left + 7; ++x) t[y * W + x] = 75;
}

static void test_thumbnail_difference() {
  uint8_t a[4] = {10, 20, 30, 40};
  uint8_t b[4] = {10, 20, 30, 40};
  TEST_ASSERT_EQUAL_FLOAT(0.0f, thumbnail_difference(a, b, 4, 1));
  uint8_t black[4] = {0, 0, 0, 0};
  uint8_t white[4] = {255, 255, 255, 255};
  TEST_ASSERT_EQUAL_FLOAT(1.0f, thumbnail_difference(black, white, 2, 2));
  TEST_ASSERT_EQUAL_FLOAT(1.0f, thumbnail_difference(white, black, 4, 1));
  b[0] = 61;  // one pixel 51 brighter in a thumbnail smaller than a patch: 51 / (255 * 4)
  TEST_ASSERT_FLOAT_WITHIN(1e-6f, 0.05f, thumbnail_difference(a, b, 4, 1));
  // Nothing to compare: counts as different, so the picture is kept.
  TEST_ASSERT_EQUAL_FLOAT(1.0f, thumbnail_difference(a, b, 0, 0));

  // In a full thumbnail one patch with a change counts, not the average over the picture.
  static uint8_t empty[W * H], shot[W * H];
  floor_thumbnail(empty, 0);
  floor_thumbnail(shot, 0);
  for (size_t y = 40; y < 48; ++y)
    for (size_t x = 56; x < 64; ++x) shot[y * W + x] = 0;  // the last patch, all dark
  TEST_ASSERT_FLOAT_WITHIN(1e-6f, 128.0f / 255.0f, thumbnail_difference(shot, empty, W, H));
}

// spec: 5c654b74
static void test_obviously_empty_picture_is_dropped() {
  TEST_ASSERT_EQUAL(static_cast<int>(FilterResult::Drop),
                    static_cast<int>(judge(PIR_ONLY, 0.005f, THRESHOLD, false)));

  // A picture of the empty floor differs from the empty view only by noise.
  static uint8_t empty[W * H], shot[W * H];
  floor_thumbnail(empty, 1);
  floor_thumbnail(shot, 2);
  const float d = thumbnail_difference(shot, empty, W, H);
  TEST_ASSERT_TRUE(d < THRESHOLD);
  TEST_ASSERT_EQUAL(static_cast<int>(FilterResult::Drop),
                    static_cast<int>(judge(PIR_ONLY, d, THRESHOLD, false)));

  // The pass record notes the dropped picture.
  PassRecord r{};
  strcpy(r.pass_id, "ECT_0A1B2C-2026-05-14-8");
  r.pass = PIR_ONLY;
  r.pictures = "ECT_0A1B2C-2026-05-14-8_2.jpg";
  r.dropped_empty = 1;
  r.judged_empty = "";
  char line[256];
  TEST_ASSERT_TRUE(pass_csv_line(r, line, sizeof line) > 0);
  TEST_ASSERT_EQUAL_STRING("1", field(line, 8).c_str());
  TEST_ASSERT_EQUAL_STRING("ECT_0A1B2C-2026-05-14-8_2.jpg", field(line, 7).c_str());
}

// spec: 3007f937
static void test_unsure_picture_is_kept() {
  // Differs from the empty view by the threshold or more: the filter cannot call it empty.
  TEST_ASSERT_EQUAL(static_cast<int>(FilterResult::Keep),
                    static_cast<int>(judge(PIR_ONLY, THRESHOLD, THRESHOLD, false)));
  TEST_ASSERT_EQUAL(static_cast<int>(FilterResult::Keep),
                    static_cast<int>(judge(PIR_ONLY, 0.4f, THRESHOLD, false)));
  // No usable difference at all.
  TEST_ASSERT_EQUAL(static_cast<int>(FilterResult::Keep),
                    static_cast<int>(judge(PIR_ONLY, NAN, THRESHOLD, false)));

  // A 3 cm lizard anywhere in the view, also across the border of two patches, is kept, though
  // it changes the picture's average by less than a fifth of the threshold.
  static uint8_t empty[W * H], shot[W * H];
  floor_thumbnail(empty, 1);
  float smallest = 1.0f;
  for (size_t top = 0; top + 3 <= H; ++top) {
    for (size_t left = 0; left + 7 <= W; ++left) {
      floor_thumbnail(shot, 2);
      add_small_lizard(shot, left, top);
      const float d = thumbnail_difference(shot, empty, W, H);
      if (d < smallest) smallest = d;
      TEST_ASSERT_EQUAL(static_cast<int>(FilterResult::Keep),
                        static_cast<int>(judge(PIR_ONLY, d, THRESHOLD, false)));
    }
  }
  TEST_ASSERT_TRUE(smallest > THRESHOLD);
  uint64_t sum = 0;
  floor_thumbnail(shot, 1);
  add_small_lizard(shot, 30, 20);
  for (size_t i = 0; i < W * H; ++i)
    sum += shot[i] > empty[i] ? shot[i] - empty[i] : empty[i] - shot[i];
  TEST_ASSERT_TRUE(static_cast<double>(sum) / (255.0 * W * H) < THRESHOLD / 5);
}

static void test_passes_the_lasers_noticed_keep_every_picture() {
  TEST_ASSERT_EQUAL(static_cast<int>(FilterResult::Keep),
                    static_cast<int>(judge(LASERS, 0.0f, THRESHOLD, false)));
  TEST_ASSERT_EQUAL(static_cast<int>(FilterResult::Keep),
                    static_cast<int>(judge(BOTH, 0.0f, THRESHOLD, false)));
  TEST_ASSERT_EQUAL(static_cast<int>(FilterResult::Keep),
                    static_cast<int>(judge(LASERS, 0.0f, THRESHOLD, true)));
}

// spec: f4c14891
static void test_filter_marks_picture_in_pilot_mode() {
  TEST_ASSERT_EQUAL(static_cast<int>(FilterResult::MarkEmpty),
                    static_cast<int>(judge(PIR_ONLY, 0.005f, THRESHOLD, true)));

  // The picture is stored, listed among the pass's pictures, and marked as judged empty.
  PassRecord r{};
  strcpy(r.pass_id, "ECT_0A1B2C-2026-05-14-9");
  r.pass = PIR_ONLY;
  r.pictures = "ECT_0A1B2C-2026-05-14-9_1.jpg;ECT_0A1B2C-2026-05-14-9_2.jpg";
  r.dropped_empty = 0;
  r.judged_empty = "ECT_0A1B2C-2026-05-14-9_2.jpg";
  char line[256];
  TEST_ASSERT_TRUE(pass_csv_line(r, line, sizeof line) > 0);
  TEST_ASSERT_EQUAL_STRING("ECT_0A1B2C-2026-05-14-9_1.jpg;ECT_0A1B2C-2026-05-14-9_2.jpg",
                           field(line, 7).c_str());
  TEST_ASSERT_EQUAL_STRING("0", field(line, 8).c_str());
  TEST_ASSERT_EQUAL_STRING("ECT_0A1B2C-2026-05-14-9_2.jpg", field(line, 9).c_str());
}

int main() {
  UNITY_BEGIN();
  RUN_TEST(test_thumbnail_difference);
  RUN_TEST(test_obviously_empty_picture_is_dropped);
  RUN_TEST(test_unsure_picture_is_kept);
  RUN_TEST(test_passes_the_lasers_noticed_keep_every_picture);
  RUN_TEST(test_filter_marks_picture_in_pilot_mode);
  return UNITY_END();
}
