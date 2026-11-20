// Unit tests of the pass library: directions, pass ends and what noticed a pass.
#include <unity.h>

#include "passes.h"

void setUp() {}
void tearDown() {}

static const uint32_t QUIET_MS = 5000;

static Crossing entered(uint32_t t, uint8_t point, uint8_t heights = HEIGHT_LOWEST) {
  return Crossing{t, point, heights, 1};
}
static Crossing left(uint32_t t, uint8_t point, uint8_t heights = HEIGHT_LOWEST) {
  return Crossing{t, point, heights, 0};
}

// Crosses beam point `from` and then the other one, starting at t; true when the last crossing
// completed the pass.
static bool walk_through(PassBuilder& b, uint32_t t, uint8_t from) {
  const uint8_t to = from == 0 ? 1 : 0;
  b.tick(t);
  b.add(entered(t, from));
  b.add(left(t + 300, from));
  b.add(entered(t + 2000, to));
  return b.add(left(t + 2300, to));
}

// spec: b3059cbe
static void test_pass_from_side_a_to_side_b() {
  PassBuilder b(QUIET_MS, 0, 0);
  TEST_ASSERT_TRUE(walk_through(b, 1000, 0));
  const Pass& p = b.pass();
  TEST_ASSERT_EQUAL(static_cast<int>(Direction::AtoB), static_cast<int>(p.direction));
  TEST_ASSERT_EQUAL_UINT32(1000, p.start_ms);
  TEST_ASSERT_EQUAL_UINT32(3300, p.end_ms);
  TEST_ASSERT_EQUAL_UINT8(HEIGHT_LOWEST, p.heights_a);
  TEST_ASSERT_EQUAL_UINT8(HEIGHT_LOWEST, p.heights_b);
  TEST_ASSERT_TRUE(p.by_lasers);
  TEST_ASSERT_FALSE(p.by_pir);
  TEST_ASSERT_FALSE(b.open());
}

// spec: 49a98a46
static void test_pass_from_side_b_to_side_a() {
  PassBuilder b(QUIET_MS, 0, 0);
  TEST_ASSERT_TRUE(walk_through(b, 1000, 1));
  TEST_ASSERT_EQUAL(static_cast<int>(Direction::BtoA), static_cast<int>(b.pass().direction));
}

// spec: 978712b4
static void test_animal_turns_back_on_side_a() {
  PassBuilder b(QUIET_MS, 0, 0);
  TEST_ASSERT_FALSE(b.add(entered(1000, 0)));
  TEST_ASSERT_FALSE(b.add(left(1400, 0)));
  // It may still walk on to the other point, so the pass stays open until quiet_ms has passed.
  TEST_ASSERT_FALSE(b.tick(1400 + QUIET_MS - 1));
  TEST_ASSERT_TRUE(b.open());
  TEST_ASSERT_TRUE(b.tick(1400 + QUIET_MS));
  TEST_ASSERT_EQUAL(static_cast<int>(Direction::BackA), static_cast<int>(b.pass().direction));
  TEST_ASSERT_EQUAL_UINT32(1400, b.pass().end_ms);
}

static void test_animal_turns_back_on_side_b() {
  PassBuilder b(QUIET_MS, 0, 0);
  b.add(entered(1000, 1));
  b.add(left(1400, 1));
  TEST_ASSERT_TRUE(b.tick(1400 + QUIET_MS));
  TEST_ASSERT_EQUAL(static_cast<int>(Direction::BackB), static_cast<int>(b.pass().direction));
}

static void test_reaching_far_point_and_returning_is_turned_back() {
  PassBuilder b(QUIET_MS, 0, 0);
  b.add(entered(1000, 0));
  b.add(entered(1500, 1));  // a long animal reaches the far point while still in the first
  b.add(left(1800, 1));     // and backs out of it
  b.add(left(2600, 0));
  TEST_ASSERT_TRUE(b.tick(2600 + QUIET_MS));
  TEST_ASSERT_EQUAL(static_cast<int>(Direction::BackA), static_cast<int>(b.pass().direction));
}

static void test_long_animal_spanning_both_points_goes_through() {
  PassBuilder b(QUIET_MS, 0, 0);
  b.add(entered(1000, 0));
  b.add(entered(1500, 1));
  TEST_ASSERT_FALSE(b.add(left(2500, 0)));
  TEST_ASSERT_TRUE(b.add(left(3000, 1)));
  TEST_ASSERT_EQUAL(static_cast<int>(Direction::AtoB), static_cast<int>(b.pass().direction));
}

// spec: e6a90220
static void test_animal_goes_through_and_comes_back() {
  PassBuilder b(QUIET_MS, 0, 0);
  TEST_ASSERT_TRUE(walk_through(b, 1000, 0));
  const Pass first = b.pass();
  TEST_ASSERT_TRUE(walk_through(b, 61000, 1));
  const Pass second = b.pass();

  TEST_ASSERT_EQUAL(static_cast<int>(Direction::AtoB), static_cast<int>(first.direction));
  TEST_ASSERT_EQUAL(static_cast<int>(Direction::BtoA), static_cast<int>(second.direction));
  TEST_ASSERT_EQUAL_UINT32(1000, first.start_ms);
  TEST_ASSERT_EQUAL_UINT32(61000, second.start_ms);
}

static void test_pir_alone_gives_unknown_direction() {
  PassBuilder b(QUIET_MS, 0, 0);
  b.add_pir(1000);
  TEST_ASSERT_TRUE(b.open());
  TEST_ASSERT_TRUE(b.tick(1000 + QUIET_MS));
  const Pass& p = b.pass();
  TEST_ASSERT_EQUAL(static_cast<int>(Direction::Unknown), static_cast<int>(p.direction));
  TEST_ASSERT_TRUE(p.by_pir);
  TEST_ASSERT_FALSE(p.by_lasers);
}

static void test_pir_during_a_laser_pass_marks_both() {
  PassBuilder b(QUIET_MS, 0, 0);
  b.add(entered(1000, 0));
  b.add_pir(1200);
  b.add(left(1400, 0));
  b.add(entered(3000, 1));
  TEST_ASSERT_TRUE(b.add(left(3300, 1)));
  TEST_ASSERT_TRUE(b.pass().by_lasers);
  TEST_ASSERT_TRUE(b.pass().by_pir);
  TEST_ASSERT_EQUAL(static_cast<int>(Direction::AtoB), static_cast<int>(b.pass().direction));
}

static void test_pass_records_all_heights_interrupted() {
  PassBuilder b(QUIET_MS, 0, 0);
  b.add(entered(1000, 0, HEIGHT_LOWEST));
  b.add(left(1400, 0, HEIGHT_LOWEST | HEIGHT_MIDDLE));
  b.add(entered(3000, 1, HEIGHT_MIDDLE));
  b.add(left(3300, 1, HEIGHT_LOWEST | HEIGHT_MIDDLE | HEIGHT_TOP));
  TEST_ASSERT_EQUAL_UINT8(HEIGHT_LOWEST | HEIGHT_MIDDLE, b.pass().heights_a);
  TEST_ASSERT_EQUAL_UINT8(HEIGHT_LOWEST | HEIGHT_MIDDLE | HEIGHT_TOP, b.pass().heights_b);
}

static void test_ignored_beams_are_left_out() {
  PassBuilder b(QUIET_MS, HEIGHT_LOWEST, 0);
  // Only the ignored beam at point 0 changes: no pass.
  TEST_ASSERT_FALSE(b.add(entered(1000, 0, HEIGHT_LOWEST)));
  TEST_ASSERT_FALSE(b.open());
  // A taller animal is still noticed by the beams above.
  b.add(entered(2000, 0, HEIGHT_LOWEST | HEIGHT_MIDDLE));
  b.add(left(2300, 0, HEIGHT_LOWEST | HEIGHT_MIDDLE));
  b.add(entered(4000, 1, HEIGHT_LOWEST | HEIGHT_MIDDLE));
  TEST_ASSERT_TRUE(b.add(left(4300, 1, HEIGHT_LOWEST | HEIGHT_MIDDLE)));
  TEST_ASSERT_EQUAL_UINT8(HEIGHT_MIDDLE, b.pass().heights_a);
  TEST_ASSERT_EQUAL_UINT8(HEIGHT_LOWEST | HEIGHT_MIDDLE, b.pass().heights_b);
  TEST_ASSERT_EQUAL_UINT32(2000, b.pass().start_ms);
}

static void test_quiet_time_survives_clock_wrap() {
  PassBuilder b(QUIET_MS, 0, 0);
  b.add_pir(0xFFFFFF00u);
  TEST_ASSERT_FALSE(b.tick(0x00000100u));
  TEST_ASSERT_TRUE(b.tick(0xFFFFFF00u + QUIET_MS));
}

int main() {
  UNITY_BEGIN();
  RUN_TEST(test_pass_from_side_a_to_side_b);
  RUN_TEST(test_pass_from_side_b_to_side_a);
  RUN_TEST(test_animal_turns_back_on_side_a);
  RUN_TEST(test_animal_turns_back_on_side_b);
  RUN_TEST(test_reaching_far_point_and_returning_is_turned_back);
  RUN_TEST(test_long_animal_spanning_both_points_goes_through);
  RUN_TEST(test_animal_goes_through_and_comes_back);
  RUN_TEST(test_pir_alone_gives_unknown_direction);
  RUN_TEST(test_pir_during_a_laser_pass_marks_both);
  RUN_TEST(test_pass_records_all_heights_interrupted);
  RUN_TEST(test_ignored_beams_are_left_out);
  RUN_TEST(test_quiet_time_survives_clock_wrap);
  return UNITY_END();
}
