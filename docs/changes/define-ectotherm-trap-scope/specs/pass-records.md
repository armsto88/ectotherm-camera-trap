# pass-records

## Purpose
Each pass leaves a record of when it happened, which way the animal went, what noticed it and its
pictures, so that species lists, presence, times of activity and relative numbers can be drawn from
a season's records.

## Terms
- **Pass record:** the record one pass leaves behind.
- **Survey day:** the 24 hours from noon to noon, so that a night is never split between two days.
- **Passes per survey day:** the number of passes in a survey day, an index of how common animals
  are; it is not a number of animals, since one animal can pass several times.

## ADDED Requirements

### Requirement: One record per pass
The trap shall keep one pass record for each pass, holding the time the pass started, its direction,
the beam heights it interrupted at each beam point, whether the lasers, the PIR sensor or both
noticed it, and the names of its pictures.

#### Scenario: A pass leaves its record <!-- id: c2ab65dd -->
- **Given** the trap is waiting
- **When** an animal passes from side A to side B, interrupting the lowest beam at both beam points
- **Then** the trap keeps a pass record with the start time, the direction "side A to side B", the
  lowest beam at both points, the lasers as what noticed it, and the names of its pictures

### Requirement: Back-and-forth passes kept apart
Each pass shall have a record of its own, so that an animal moving back and forth leaves one record
per pass with its own time and direction.

#### Scenario: An animal goes through and comes back <!-- id: e6a90220 -->
- **Given** an animal has passed from side A to side B
- **When** it passes back from side B to side A a minute later
- **Then** the trap keeps two pass records, with opposite directions and their own times

### Requirement: Every animal recorded alike
The trap shall keep pass records for small mammals, large invertebrates and any other animal that
passes, in the same way as for reptiles and amphibians.

#### Scenario: A mouse passes through <!-- id: abc0c8ed -->
- **Given** the trap is waiting
- **When** a mouse passes through the passage
- **Then** the trap keeps a pass record and pictures for it as for any other pass

### Requirement: Relative numbers as passes
Summaries of a season's records shall count passes per survey day, by direction and by group or
species where pictures have been named, and shall call them passes, never animals.

#### Scenario: A season is summarised <!-- id: 0930417b -->
- **Given** the pass records of a season, with the pictures named
- **When** the passes are summarised
- **Then** the summary gives the passes per survey day for each group or species and direction
- **And** it labels them as passes, not as numbers of animals
