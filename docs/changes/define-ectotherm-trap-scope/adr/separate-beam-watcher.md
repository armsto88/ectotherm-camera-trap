---
areas: [firmware, hardware]
---
# A separate low-power controller watches the beams

## Context
The beams must be pulsed and read without pause, with timing to a few milliseconds for direction,
while the camera controller sleeps to save power or is busy taking and writing pictures.

## Options considered
- A separate small controller for the beams and the PIR sensor that wakes the camera controller.
- The camera controller's own low-power co-processor: rejected, limited, and watching may pause
  while the main core uses the camera.
- The prototype's ESP32-WROVER: rejected, kept as a test bench only and without low-power watching.

## Decision
An ATtiny3216 runs the beams and the PIR sensor, turns beam changes into timed crossings, keeps them
in a small buffer and raises a wake line. An ESP32-S3 wakes, reads crossings and status over I2C at
address 0x42, takes the pictures and writes the records. Both share one link header.

## Consequences
- Watching never pauses, and the always-on part uses very little power.
- Two firmwares and a link between them to build and test; the link header is their contract.
- The watcher's clock is mapped onto the camera controller's real-time clock at each read.
