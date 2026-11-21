# pass-records

## Purpose
Each pass leaves a record of when it happened, which way the animal went, what noticed it, the
type the model on the trap gave it and its pictures, and a season's records carry the trap's place
and placement, so that species lists, presence, times of activity and relative numbers can be
drawn from them and shared.

## Terms
- **Pass record:** the record one pass leaves behind.
- **Survey day:** the 24 hours from noon to noon, so that a night is never split between two days.
- **Passes per survey day:** the number of passes in a survey day, an index of how common animals
  are; it is not a number of animals, since one animal can pass several times.

## ADDED Requirements

### Requirement: One record per pass
The trap shall keep one pass record for each pass, holding the time the pass started, its direction,
the beam heights it interrupted at each beam point, whether the lasers, the PIR sensor or both
noticed it, whether the trap was in pilot mode, the model type with how sure the model is and its
version where the trap has a model, and the names of its pictures.

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

### Requirement: Records carry the trap's place
The trap's coordinates, its placement and the words describing side A shall be entered in its
settings on its card when it is set up, and a season exported from the card shall carry them; a
season whose card holds no coordinates shall not be exported.

#### Scenario: A season is exported with its place <!-- id: f746b277 -->
- **Given** a trap whose settings hold its latitude and longitude
- **When** its season is exported
- **Then** the export places the trap at those coordinates

#### Scenario: A season without coordinates is not exported <!-- id: 2f5cb71e -->
- **Given** a trap whose settings hold no coordinates
- **When** its season is exported
- **Then** the export stops and says that the coordinates are missing

#### Scenario: A season is exported with its placement <!-- id: dd89b648 -->
- **Given** a trap whose settings place it at a fence end, with side A described as "pond side"
- **When** its season is exported
- **Then** the export notes that the trap stood at a fence end and that side A is the pond side

### Requirement: Exported classifications say who made them
An exported season shall give each pass the group or name a person gave it, marked as classified
by a person; a pass nobody has sorted shall get the model type, marked as classified by machine
with how sure the model was.

#### Scenario: A sorted pass is exported <!-- id: c6aae0b1 -->
- **Given** a pass whose model type is snake and to which a person gave the group lizard
- **When** its season is exported
- **Then** the pass is exported as lizard, classified by a person

#### Scenario: An unsorted pass is exported <!-- id: 3267db9c -->
- **Given** a pass nobody has sorted, whose model type is snake with the model 80 % sure
- **When** its season is exported
- **Then** the pass is exported as snake, classified by machine, 80 % sure
