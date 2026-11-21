# fence-passage

## Purpose
The trap is a short passage set into a drift fence, in its line or at its end, through which animals
pass without being caught or handled, so that it can take the place of the bucket at drift fences
wherever they are used.

## Terms
- **Passage:** the trap's walled, roofed channel through the fence line, open at both ends.
- **Side A, side B:** the two sides of the fence line; each trap marks which of its ends faces side
  A, and its settings describe side A in words, such as "pond side".
- **Placement:** in the fence line, with fence on both sides of the trap, or at a fence end, with
  a short piece of fence, about a bucket's width, beyond the trap; the trap's settings note which.
- **Pass:** an animal entering the passage at one end and leaving it at either end.

## ADDED Requirements

### Requirement: Crossing the fence line through the passage
The trap shall be set into a drift fence, in its line or at its end, so that the fence leads
animals to it, and an animal following the fence can cross to the other side through the passage.
The same trap shall serve both placements.

#### Scenario: An animal following the fence crosses through the passage <!-- id: fd2c5b0e -->
- **Given** a trap set into a drift fence
- **When** an animal following the fence on side A reaches the trap
- **Then** it can walk through the passage and leave it on side B

#### Scenario: A trap at a fence end <!-- id: d3137709 -->
- **Given** a trap set at the end of a drift fence, with a short piece of fence beyond it
- **When** an animal following the fence on side A reaches the trap
- **Then** it can walk through the passage and leave it on side B

### Requirement: No gap beside the trap
The joints between the trap and the fence shall leave no gap through which an animal of 3 cm body
length could cross the fence line beside the passage.

#### Scenario: A small animal cannot slip past the trap <!-- id: c7531d9b -->
- **Given** a trap set into a drift fence of a kind commonly used in surveys, as its instructions
  describe
- **When** a model animal of 3 cm body length is moved along the fence and the trap's joints
- **Then** it finds no way to the other side except through the passage

### Requirement: Nothing holds the animal
The passage shall let every animal leave on its own at either end, with no pit, flap, door or
barrier that catches or holds it.

#### Scenario: An animal turns back inside the passage <!-- id: 3662828d -->
- **Given** an animal that has entered the passage from side A
- **When** it turns round
- **Then** it can leave the passage on side A without anything stopping it

#### Scenario: An animal stays in the passage <!-- id: 746fea6c -->
- **Given** an animal resting in the passage
- **When** it starts moving again in either direction
- **Then** nothing in the passage stops it
