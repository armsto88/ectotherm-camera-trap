---
areas: [testing]
---
# The trap is tested at three levels

## Context
Most scenarios are about hardware meeting animals: beams, light, pictures and the passage. Only part
of the behaviour is logic that runs on a computer.

## Options considered
- Unit tests, bench runs checked by scripts, and written check procedures.
- Unit tests only, with bench results noted by hand: rejected, no repeatable check for most
  scenarios.

## Decision
Firmware logic and the sorting tool have unit tests that run on a computer. Bench runs pass model
animals through a trap on a rig, following a plan, first through the prototype on development
boards and later through traps on their own boards, and pytest checks marked `bench` compare the
card's records with the plan. What only a person can check is a written procedure in
`docs/testing/`. Every test, bench check and procedure step names its scenario with `spec: <id>`.

## Consequences
- Unit tests run anywhere; bench checks need the rig and a trap; procedures need a person.
- A bench run is repeatable from its plan, and its records stay as evidence.
