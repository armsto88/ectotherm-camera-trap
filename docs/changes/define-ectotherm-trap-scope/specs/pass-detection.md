# pass-detection

## Purpose
The trap notices every animal of about 3 cm body length or more that passes through it, by day and
by night, without relying on body heat, and tells the direction of each pass, so that cold-blooded
animals are not missed and passes can be counted by direction.

## Terms
- **Beam point:** a place across the passage where laser beams at two or three heights cross it.
  The trap has two beam points; the order in which an animal crosses them gives the direction.
- **Lasers:** the beams at the beam points.
- **PIR sensor:** a passive infrared sensor, as in ordinary camera traps, that notices warm moving
  animals.
- **Body length:** the length of an animal from snout to vent, without tail.

## ADDED Requirements

### Requirement: Noticing animals whatever their temperature
The trap shall notice an animal crossing a beam point whatever the animal's temperature compared
with its surroundings.

#### Scenario: An animal as warm as its surroundings crosses a beam point <!-- id: 172ed05c -->
- **Given** an animal at the same temperature as the passage floor and air
- **When** it crosses a beam point
- **Then** the trap notices it

### Requirement: Smallest animal noticed
The trap shall notice animals from 3 cm body length upwards that move along the passage floor.

#### Scenario: A flat 3 cm animal crosses along the floor <!-- id: 808cb65b -->
- **Given** a flat model animal of 3 cm body length
- **When** it is moved through the passage along the floor
- **Then** the trap notices it at both beam points

### Requirement: Day and night
The trap shall notice animals in full darkness and in bright daylight alike.

#### Scenario: A pass in darkness <!-- id: 1f2dd41f -->
- **Given** no light reaches the passage
- **When** an animal crosses a beam point
- **Then** the trap notices it

#### Scenario: A pass in bright daylight <!-- id: 169583a5 -->
- **Given** sunlight falls on both ends of the passage
- **When** an animal crosses a beam point
- **Then** the trap notices it

### Requirement: Direction of each pass
The trap shall tell the direction of each pass from the order in which the animal crosses the beam
points: from side A to side B, from side B to side A, or turned back.

#### Scenario: A pass from side A to side B <!-- id: b3059cbe -->
- **Given** an animal entering the passage from side A
- **When** it crosses the beam point nearer side A and then the one nearer side B
- **Then** the trap records the pass as going from side A to side B

#### Scenario: A pass from side B to side A <!-- id: 49a98a46 -->
- **Given** an animal entering the passage from side B
- **When** it crosses the beam point nearer side B and then the one nearer side A
- **Then** the trap records the pass as going from side B to side A

#### Scenario: An animal turns back <!-- id: 978712b4 -->
- **Given** an animal that has crossed the beam point nearer side A
- **When** it leaves the passage on side A without crossing the other beam point
- **Then** the trap records the pass as turned back on side A

### Requirement: Beams at several heights
Each beam point shall have beams at two or three heights, and the trap shall record which heights a
pass interrupted, as a rough measure of the animal's height.

#### Scenario: A taller animal interrupts more beams <!-- id: 53f0ff23 -->
- **Given** a model animal taller than the second beam height
- **When** it crosses a beam point
- **Then** the trap records that the pass interrupted the lowest and the second beam at that point

### Requirement: Working with a blocked beam
The trap shall keep noticing passes with the beams still clear when one beam stays blocked, and
shall record that the beam is blocked and since when.

#### Scenario: Debris blocks the lowest beam <!-- id: 2697cd6b -->
- **Given** the lowest beam at one beam point has been blocked for longer than any pass takes
- **When** an animal taller than the lowest beam crosses that beam point
- **Then** the trap still notices the pass
- **And** the trap's records show the lowest beam at that point as blocked, with the time it became
  blocked

### Requirement: PIR sensor as an extra trigger
A PIR sensor shall also start a pass, so that either the lasers or the PIR sensor is enough; the
trap shall record which of them noticed each pass.

#### Scenario: Only the lasers notice a cold animal <!-- id: dd5a2678 -->
- **Given** an animal as warm as its surroundings, which the PIR sensor does not notice
- **When** it crosses the beam points
- **Then** the trap notices the pass and records that only the lasers noticed it

#### Scenario: Only the PIR sensor notices a warm animal <!-- id: 58ebb8e3 -->
- **Given** a warm animal that passes without interrupting any beam
- **When** the PIR sensor notices it
- **Then** the trap starts a pass and records that only the PIR sensor noticed it
