---
areas: [firmware, hardware]
---
# Image models later run on the camera controller after each pass

## Context
Version 1 has no learned image model, but a later one is to sort a pass's pictures by type of
animal on the trap itself. The decision is not timing-critical: the pictures are already taken,
and the model has until the next pass. The chip choice is made now, for version 1.

## Options considered
- The ESP32-S3 camera controller runs the model after the pictures of a pass are taken; small models
  take about 0.1 to 0.2 s per picture, and its extra memory holds larger ones that run slowly.
- The ESP32-S3 with a free slot for a helper chip: rejected, designed for a chip not yet known.
- A helper chip such as the MAX78000: rejected, its low energy and speed do not matter when timing
  does not, it holds only small models, needs its own tools, and its supply is uncertain.
- A vision chip such as the STM32N6 as camera controller: rejected, scarce, costly and new tools
  before the trap has taken a picture.

## Decision
The ESP32-S3 stays the camera controller and runs a later image model after each pass. A separate
chip for models comes only with a later board revision, and only if a test shows the ESP32-S3 is
not enough.

## Consequences
- A first model on the trap needs no new hardware.
- At about 200 passes a day the model adds roughly 2 mAh a day against about 30 mAh for the rest
  (estimates).
- A model too large or too slow for the ESP32-S3 means a board revision.
