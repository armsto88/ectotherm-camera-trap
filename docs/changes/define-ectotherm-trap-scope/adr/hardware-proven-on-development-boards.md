---
areas: [hardware, firmware, testing]
---
# The hardware is proven on development boards before the trap's own boards

## Context
The trap's own boards cost weeks of drawing, ordering and bring-up, and a fault the bench finds on
them means a new board. Whether the beams notice a flat cold 3 cm animal, whether the pictures can
be identified, whether the camera wakes in time and how long a model takes are all still estimates,
and several of their answers change the board. Ready-made development boards exist for the trap's
chips.

## Options considered
- The whole chain on development boards with the trap's chips, every bench test on it, then the
  trap's own boards.
- The trap's own boards first, with the bench tests on them: rejected, a fault found on the bench
  means a new board.
- Separate rigs for the risky parts: rejected, the wake time only shows end to end.
- The quickest boards at hand: rejected, results on other chips say little about the trap.

## Decision
Before the trap's own boards are drawn, the whole chain runs on development boards with the trap's
chips and camera, in the printed passage: an ESP32-S3 camera board with a microSD slot and an
OV5640, an ATtiny3216 on an adapter board, beams on strip board in the beam walls, infrared light,
a PIR sensor and a clock. Every bench test runs on it first, and so does a model's time per
picture; the battery is sized from the parts' measured currents. The modem and the season-long run
come with the trap's own boards. The firmware builds for both from the same code, with each
board's pins in one header.

## Consequences
- The trap's own boards are drawn from bench results, not estimates.
- Months pass on the bench before the first own board; the season's power is only added up from
  parts until then.
- The modem part is first tried on the trap's own board; a fault in it means a board revision.
- Each firmware project carries a `prototype` environment beside the boards' own.
