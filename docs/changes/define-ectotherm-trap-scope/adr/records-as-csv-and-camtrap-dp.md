---
areas: [records]
---
# Pass records are CSV per survey day, exported as Camtrap DP

## Context
Each pass leaves a record and pictures. People must be able to read a season's records without the
trap's own software, and others' camera-trap tools and data portals must be able to take them.

## Options considered
- One CSV file per survey day beside the JPEG pictures on the card, exported by the sorting tool as
  a Camera Trap Data Package (Camtrap DP).
- Only the trap's own format: rejected, data would need converting before others could use it.

## Decision
The card holds one pass file per survey day (noon to noon, local), a picture folder per survey day,
a fault log and the state summaries, with times in UTC. The sorting tool exports a season as a
Camtrap DP package, one event-level observation per pass.

## Consequences
- Records open in any spreadsheet; nothing on the card needs the tool to be read.
- Changing a column means changing the firmware, the sorting tool and this description together.
- Direction has no own field in Camtrap DP and travels in the observation comments.
