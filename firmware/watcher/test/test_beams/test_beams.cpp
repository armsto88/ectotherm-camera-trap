// Unit tests of the beam library: steady light, crossings and stuck beams.
#include <unity.h>

#include "beams.h"

void setUp() {}
void tearDown() {}

// Feeds a filter the same pulse n times; returns its last answer.
static bool feed(BeamFilter& f, uint16_t lit, uint16_t dark, int n) {
  bool interrupted = false;
  for (int i = 0; i < n; ++i) interrupted = f.update(lit, dark);
  return interrupted;
}

static void test_steady_light_cancels_out() {
  // Clear beam: the laser adds 400 counts whatever the daylight level.
  const uint16_t daylight[] = {0, 200, 400, 600};
  for (uint16_t dark : daylight) {
    BeamFilter f;
    TEST_ASSERT_FALSE(feed(f, dark + 400, dark, 10));
    // Interrupted: the laser adds almost nothing, even with bright light at the photodiode.
    TEST_ASSERT_TRUE(feed(f, dark + 10, dark, 3));
    TEST_ASSERT_FALSE(feed(f, dark + 400, dark, 3));
  }
}

static void test_daylight_changing_does_not_interrupt() {
  BeamFilter f;
  feed(f, 400, 0, 10);
  // The sun comes out: the dark level climbs, the laser still adds its 400 counts.
  for (uint16_t dark = 0; dark < 600; dark += 20) TEST_ASSERT_FALSE(f.update(dark + 400, dark));
}

static void test_single_noisy_pulse_is_ignored() {
  BeamFilter f;
  feed(f, 400, 0, 10);
  TEST_ASSERT_FALSE(f.update(5, 0));
  TEST_ASSERT_FALSE(f.update(400, 0));
}

static void test_saturated_photodiode_keeps_state() {
  BeamFilter f;
  feed(f, 400, 0, 10);
  TEST_ASSERT_FALSE(feed(f, 1023, 1023, 5));
  TEST_ASSERT_TRUE(feed(f, 5, 0, 3));
  TEST_ASSERT_TRUE(feed(f, 1023, 1023, 5));
}

static void test_dimmed_laser_still_counts_as_clear() {
  BeamFilter f;
  // Dirt on the lens halves the signal over many pulses.
  for (int signal = 400; signal >= 200; signal -= 2) TEST_ASSERT_FALSE(f.update(signal, 0));
  TEST_ASSERT_FALSE(feed(f, 200, 0, 50));
  TEST_ASSERT_TRUE(feed(f, 40, 0, 3));
}

static void test_one_entered_and_one_left_crossing() {
  PointTracker tracker(1);
  Crossing c{};
  TEST_ASSERT_FALSE(tracker.update(0, 0, &c));

  TEST_ASSERT_TRUE(tracker.update(100, HEIGHT_LOWEST, &c));
  TEST_ASSERT_EQUAL_UINT32(100, c.t_ms);
  TEST_ASSERT_EQUAL_UINT8(1, c.point);
  TEST_ASSERT_EQUAL_UINT8(HEIGHT_LOWEST, c.heights);
  TEST_ASSERT_EQUAL_UINT8(1, c.entered);

  // The animal stays in the beams and also breaks the middle one: no new crossing.
  TEST_ASSERT_FALSE(tracker.update(104, HEIGHT_LOWEST, &c));
  TEST_ASSERT_FALSE(tracker.update(108, HEIGHT_LOWEST | HEIGHT_MIDDLE, &c));
  TEST_ASSERT_FALSE(tracker.update(112, HEIGHT_MIDDLE, &c));

  TEST_ASSERT_TRUE(tracker.update(116, 0, &c));
  TEST_ASSERT_EQUAL_UINT32(116, c.t_ms);
  TEST_ASSERT_EQUAL_UINT8(1, c.point);
  TEST_ASSERT_EQUAL_UINT8(HEIGHT_LOWEST | HEIGHT_MIDDLE, c.heights);
  TEST_ASSERT_EQUAL_UINT8(0, c.entered);

  TEST_ASSERT_FALSE(tracker.update(120, 0, &c));
}

static void test_next_crossing_starts_with_its_own_heights() {
  PointTracker tracker(0);
  Crossing c{};
  tracker.update(0, HEIGHT_LOWEST | HEIGHT_MIDDLE | HEIGHT_TOP, &c);
  tracker.update(10, 0, &c);
  TEST_ASSERT_TRUE(tracker.update(20, HEIGHT_LOWEST, &c));
  TEST_ASSERT_TRUE(tracker.update(30, 0, &c));
  TEST_ASSERT_EQUAL_UINT8(HEIGHT_LOWEST, c.heights);
  TEST_ASSERT_EQUAL_UINT8(0, c.point);
}

static void test_beam_reported_stuck_only_after_stuck_ms() {
  StuckBeams stuck(5000);
  TEST_ASSERT_EQUAL_UINT8(0, stuck.update(1000, HEIGHT_LOWEST));
  TEST_ASSERT_EQUAL_UINT8(0, stuck.update(6000, HEIGHT_LOWEST));
  TEST_ASSERT_EQUAL_UINT8(HEIGHT_LOWEST, stuck.update(6001, HEIGHT_LOWEST));
  // A second beam joins later and has its own time.
  TEST_ASSERT_EQUAL_UINT8(HEIGHT_LOWEST, stuck.update(7000, HEIGHT_LOWEST | HEIGHT_MIDDLE));
  TEST_ASSERT_EQUAL_UINT8(HEIGHT_LOWEST | HEIGHT_MIDDLE,
                          stuck.update(12001, HEIGHT_LOWEST | HEIGHT_MIDDLE));
  // Cleared and blocked again: the time starts over.
  TEST_ASSERT_EQUAL_UINT8(HEIGHT_MIDDLE, stuck.update(12002, HEIGHT_MIDDLE));
  TEST_ASSERT_EQUAL_UINT8(HEIGHT_MIDDLE, stuck.update(12003, HEIGHT_LOWEST | HEIGHT_MIDDLE));
}

static void test_stuck_survives_clock_wrap() {
  StuckBeams stuck(5000);
  stuck.update(0xFFFFF000u, HEIGHT_TOP);
  TEST_ASSERT_EQUAL_UINT8(0, stuck.update(0x00000100u, HEIGHT_TOP));
  TEST_ASSERT_EQUAL_UINT8(HEIGHT_TOP, stuck.update(0x00001000u, HEIGHT_TOP));
}

static void test_link_structs_have_fixed_sizes() {
  TEST_ASSERT_EQUAL(7, sizeof(Crossing));
  TEST_ASSERT_EQUAL(8, sizeof(WatcherStatus));
}

int main() {
  UNITY_BEGIN();
  RUN_TEST(test_steady_light_cancels_out);
  RUN_TEST(test_daylight_changing_does_not_interrupt);
  RUN_TEST(test_single_noisy_pulse_is_ignored);
  RUN_TEST(test_saturated_photodiode_keeps_state);
  RUN_TEST(test_dimmed_laser_still_counts_as_clear);
  RUN_TEST(test_one_entered_and_one_left_crossing);
  RUN_TEST(test_next_crossing_starts_with_its_own_heights);
  RUN_TEST(test_beam_reported_stuck_only_after_stuck_ms);
  RUN_TEST(test_stuck_survives_clock_wrap);
  RUN_TEST(test_link_structs_have_fixed_sizes);
  return UNITY_END();
}
