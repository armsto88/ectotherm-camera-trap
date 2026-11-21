// Unit tests of the typing library: a pass's type from the model's scores for its pictures.
#include <string.h>
#include <unity.h>

#include "typing.h"

void setUp() {}
void tearDown() {}

static void test_the_surest_animal_over_all_pictures() {
  // The first picture is unsure, the second sees a lizard clearly, the third a snake less so.
  const PictureScores pictures[] = {{0.50f, 0.10f, 0.20f, 0.10f, 0.10f},
                                    {0.05f, 0.02f, 0.85f, 0.05f, 0.03f},
                                    {0.20f, 0.00f, 0.10f, 0.60f, 0.10f}};
  const ModelResult r = pass_type(pictures, 3, 0.5f);
  TEST_ASSERT_EQUAL(ModelType::Lizard, r.type);
  TEST_ASSERT_EQUAL_FLOAT(0.85f, r.confidence);
}

static void test_empty_when_no_animal_score_reaches_the_minimum() {
  const PictureScores pictures[] = {{0.70f, 0.10f, 0.10f, 0.05f, 0.05f},
                                    {0.90f, 0.02f, 0.03f, 0.02f, 0.03f}};
  const ModelResult r = pass_type(pictures, 2, 0.5f);
  TEST_ASSERT_EQUAL(ModelType::Empty, r.type);
  TEST_ASSERT_EQUAL_FLOAT(0.90f, r.confidence);
}

static void test_an_animal_score_at_the_minimum_counts() {
  const PictureScores pictures[] = {{0.50f, 0.00f, 0.00f, 0.00f, 0.50f}};
  const ModelResult r = pass_type(pictures, 1, 0.5f);
  TEST_ASSERT_EQUAL(ModelType::Other, r.type);
  TEST_ASSERT_EQUAL_FLOAT(0.50f, r.confidence);
}

static void test_equal_scores_go_to_the_type_named_first() {
  const PictureScores pictures[] = {{0.00f, 0.00f, 0.00f, 0.50f, 0.50f},
                                    {0.00f, 0.50f, 0.50f, 0.00f, 0.00f}};
  TEST_ASSERT_EQUAL(ModelType::FrogToad, pass_type(pictures, 2, 0.5f).type);
}

static void test_no_pictures_give_no_type() {
  const ModelResult r = pass_type(nullptr, 0, 0.5f);
  TEST_ASSERT_EQUAL(ModelType::None, r.type);
  TEST_ASSERT_EQUAL_FLOAT(0.0f, r.confidence);
}

static void test_type_names() {
  TEST_ASSERT_EQUAL_STRING("", model_type_name(ModelType::None));
  TEST_ASSERT_EQUAL_STRING("empty", model_type_name(ModelType::Empty));
  TEST_ASSERT_EQUAL_STRING("frog_or_toad", model_type_name(ModelType::FrogToad));
  TEST_ASSERT_EQUAL_STRING("lizard", model_type_name(ModelType::Lizard));
  TEST_ASSERT_EQUAL_STRING("snake", model_type_name(ModelType::Snake));
  TEST_ASSERT_EQUAL_STRING("other", model_type_name(ModelType::Other));
}

int main() {
  UNITY_BEGIN();
  RUN_TEST(test_the_surest_animal_over_all_pictures);
  RUN_TEST(test_empty_when_no_animal_score_reaches_the_minimum);
  RUN_TEST(test_an_animal_score_at_the_minimum_counts);
  RUN_TEST(test_equal_scores_go_to_the_type_named_first);
  RUN_TEST(test_no_pictures_give_no_type);
  RUN_TEST(test_type_names);
  return UNITY_END();
}
