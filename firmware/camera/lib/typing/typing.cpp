#include "typing.h"

ModelResult pass_type(const PictureScores* pictures, size_t n, float min_animal) {
  ModelResult best_animal{ModelType::None, -1.0f};
  float best_empty = 0.0f;
  for (size_t i = 0; i < n; ++i) {
    const PictureScores& p = pictures[i];
    const struct {
      ModelType type;
      float score;
    } animals[] = {{ModelType::FrogToad, p.frog_toad},
                   {ModelType::Lizard, p.lizard},
                   {ModelType::Snake, p.snake},
                   {ModelType::Other, p.other}};
    for (const auto& a : animals) {
      const bool surer = a.score > best_animal.confidence;
      const bool tie_named_earlier = a.score == best_animal.confidence && a.type < best_animal.type;
      if (surer || tie_named_earlier) best_animal = ModelResult{a.type, a.score};
    }
    if (p.empty > best_empty) best_empty = p.empty;
  }
  if (n == 0) return ModelResult{};
  if (best_animal.confidence >= min_animal) return best_animal;
  return ModelResult{ModelType::Empty, best_empty};
}

const char* model_type_name(ModelType t) {
  switch (t) {
    case ModelType::Empty: return "empty";
    case ModelType::FrogToad: return "frog_or_toad";
    case ModelType::Lizard: return "lizard";
    case ModelType::Snake: return "snake";
    case ModelType::Other: return "other";
    default: return "";
  }
}
