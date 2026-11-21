---
areas: [firmware, hardware]
---
# The camera controller runs the image model after each pass

## Context
A model on the trap gives each pass a type of animal and how sure it is, and the link sends that
type instead of pictures. The decision is not timing-critical: the pictures are already taken, and
the model has until the next pass. The model changes more often than the firmware and must reach
traps already in the field.

## Options considered
- The ESP32-S3 camera controller runs the model with TensorFlow Lite Micro, 8-bit, after the
  pictures of a pass are written; small models take about 0.1 to 0.2 s per picture there.
- Espressif's ESP-DL: rejected, it needs ESP-IDF, while the firmware uses the Arduino framework.
- The model built into the firmware: rejected, every new model would be a whole firmware release.
- A helper chip such as the MAX78000: rejected, its low energy and speed do not matter when timing
  does not, it holds only small models, needs its own tools, and its supply is uncertain.
- A vision chip such as the STM32N6 as camera controller: rejected, scarce, costly and new tools.

## Decision
The ESP32-S3 runs the model with TensorFlow Lite Micro after each pass. The model is a separate
file on the memory card with a manifest signed with the release key, loaded at start and checked
before use; without a valid model the trap records as before, with the type left empty. The model
only labels and never deletes pictures. A separate chip for models comes only with a later board
revision, and only if a test shows the ESP32-S3 is not enough.

## Consequences
- A model needs no new hardware, and a new model needs no new firmware.
- At about 200 passes a day the model adds roughly 2 mAh a day against about 30 mAh for the rest
  (estimates).
- The trap has two signed update paths, one for firmware and one for models.
- A model too large or too slow for the ESP32-S3 means a board revision.
