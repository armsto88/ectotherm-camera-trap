// Model types: turns the image model's scores for a pass's pictures into the pass's type.
// No hardware calls, so it is tested on the computer.
#pragma once

#include <stddef.h>
#include <stdint.h>

// The type of animal the model gives a pass. None: the trap has no model, or it did not run.
enum class ModelType : uint8_t { None, Empty, FrogToad, Lizard, Snake, Other };

// The model's scores for one picture, which add up to 1.
struct PictureScores {
  float empty, frog_toad, lizard, snake, other;
};

struct ModelResult {
  ModelType type = ModelType::None;
  float confidence = 0.0f;  // how sure the model is, 0 to 1; 0 for None
};

/// The surest animal type over the pictures if any picture's score for an animal type reaches
/// min_animal, with that score; otherwise Empty with the highest empty score; None when n is 0.
/// Equal scores go to the type named first: frog or toad, lizard, snake, other.
ModelResult pass_type(const PictureScores* pictures, size_t n, float min_animal);

/// The type as written to the pass file and sent: "" for None, "empty", "frog_or_toad",
/// "lizard", "snake" or "other".
const char* model_type_name(ModelType t);
