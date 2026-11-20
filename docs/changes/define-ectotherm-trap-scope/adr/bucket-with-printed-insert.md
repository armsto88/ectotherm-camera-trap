---
areas: [hardware]
---
# The trap is an upturned bucket with a printed insert

## Context
The trap is a passage set into a drift-fence line that replaces the bucket. It must be dark inside,
hold the camera at a fixed height above the floor, keep the beams aligned, leave room for a side
view and a roof laser, and be buildable for drift fences anywhere, by people who are not
electronics specialists.

## Options considered
- An upturned standard bucket as the hood, with a 3D-printed insert carrying the floor, beam walls,
  camera and electronics.
- A purpose-built housing, printed or moulded in one piece: rejected, costly in small numbers and
  repairable only with the maker's parts.
- A plastic or metal channel with a separate box on top: rejected, more cutting, fitting and
  sealing per trap.

## Decision
The trap is an upturned standard bucket of about 30 cm diameter with openings in two opposite sides
for the fence ends. A printed insert, generated from a parametric script for the bucket's size,
carries a passage 15 cm wide whose floor lies flush with the ground at both ends, the beam walls,
the camera, the light and the electronics.

## Consequences
- Buckets are cheap and sold everywhere; a broken hood is replaced from any hardware store.
- The insert script must cover the range of bucket sizes in use; a new bucket may need new
  parameters.
- The round shape wastes space, and a 15 cm passage leaves a passage only about 26 cm long.
- With no raised threshold, soil and water reach the floor more easily.
