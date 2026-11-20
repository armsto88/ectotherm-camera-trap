---
areas: [detection]
---
# Animals are noticed by pulsed infrared laser beams, not by body heat

## Context
Heat-sensing triggers miss cold-blooded animals. The trap must notice animals from 3 cm body length
whatever their temperature, by day and night, tell the direction of each pass, and keep watching
for a whole season on a small battery.

## Options considered
- Pulsed infrared laser beams across the passage, a laser diode on one wall and a photodiode on the
  other.
- Laser distance sensors measuring across the passage: rejected, several times the power for a
  season.
- A camera watching its own picture for movement: rejected, far too much power and many false
  recordings.
- A heat sensor as the main trigger: rejected, fails for cold-blooded animals.

## Decision
Each beam point has 940 nm laser beams at three heights. Each laser is switched on for about 20
microseconds 250 times a second, and its photodiode is read with and without the laser, so steady
daylight cancels out. A PIR sensor is kept only as an extra trigger for warm animals.

## Consequences
- Watching costs an estimated 0.25 mA for six beams.
- Both passage walls carry electronics, and the beams must stay aligned through a season.
- Insects, rain and debris can break beams; a beam blocked for long is reported as stuck.
- Lasers across a passage are close to what US patent 10,258,029 describes; its check stays open.
