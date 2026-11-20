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

static void test_thumbnail_difference() {
  uint8_t a[4] = {10, 20, 30, 40};
  uint8_t b[4] = {10, 20, 30, 40};
  TEST_ASSERT_EQUAL_FLOAT(0.0f, thumbnail_difference(a, b, 4));
  uint8_t black[4] = {0, 0, 0, 0};
  uint8_t white[4] = {255, 255, 255, 255};
  TEST_ASSERT_EQUAL_FLOAT(1.0f, thumbnail_difference(black, white, 4));
  TEST_ASSERT_EQUAL_FLOAT(1.0f, thumbnail_difference(white, black, 4));
  b[0] = 61;  // one pixel 51 brighter: 51 / (255 * 4)
  TEST_ASSERT_FLOAT_WITHIN(1e-6f, 0.05f, thumbnail_difference(a, b, 4));
  // Nothing to compare: counts as different, so the picture is kept.
  TEST_ASSERT_EQUAL_FLOAT(1.0f, thumbnail_difference(a, b, 0));
}

// spec: 5c654b74
static void test_obviously_empty_picture_is_dropped() {
  TEST_ASSERT_EQUAL(static_cast<int>(FilterResult::Drop),
                    static_cast<int>(judge(PIR_ONLY, 0.005f, THRESHOLD, false)));

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
