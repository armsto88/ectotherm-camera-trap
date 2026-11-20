# trap-evaluation

## Purpose
The trap's performance is measured in two stages and reported as three separate outcomes, with
targets set from measurements before the field phase, so that claims about the trap rest on counts
of the animals it misses and not on numbers of pictures.

## Terms
- **The three outcomes:** whether the trap noticed a pass, whether it took a usable picture of it,
  and whether the animal was identified from the pictures.
- **Controlled tests:** the first stage, with model animals and known animals passed through the
  trap; no wild animals are handled.
- **Field phase:** the second stage, short and time-limited, at a few drift fences with a bucket
  behind the trap.
- **Missed animal:** an animal that reached the bucket behind the trap without a matching pass with
  a usable picture.

## ADDED Requirements

### Requirement: Three outcomes reported separately
Every evaluation result shall report the three outcomes separately, each as a share of the animals
that passed; a number of pictures or triggers shall never stand for a number of animals detected.

#### Scenario: Results of a test run <!-- id: 36e16dab -->
- **Given** a test run in which a known number of animals passed through the trap
- **When** its results are reported
- **Then** the report gives, separately, the share noticed, the share with a usable picture and the
  share identified

### Requirement: Controlled tests first
The controlled tests shall pass model animals and known animals through the trap across the sizes,
speeds and temperatures of the target animals, by day and by night, before any wild animal is
handled for the evaluation.

#### Scenario: Model animals across sizes and speeds <!-- id: b0c045b3 -->
- **Given** model animals from 3 cm body length upwards
- **When** they are moved through the trap at the speeds and temperatures the test plan lists, by
  day and by night
- **Then** the three outcomes are reported for each size, speed, temperature and light condition

### Requirement: Field phase with a bucket behind the trap
The field phase shall place a bucket behind the trap at a few fences for a limited time and count
every animal in the bucket without a matching pass with a usable picture as missed.

#### Scenario: An animal in the bucket without a matching picture <!-- id: fb3c43de -->
- **Given** a bucket behind the trap during the field phase
- **When** an animal is found in the bucket and no pass since the last check has a usable picture
  of an animal of its group
- **Then** it is counted as missed

#### Scenario: An animal in the bucket with a matching picture <!-- id: 9df1ab87 -->
- **Given** a bucket behind the trap during the field phase
- **When** an animal is found in the bucket and a pass since the last check has a usable picture of
  it
- **Then** it is counted as noticed and photographed, and its in-hand identification is stored as
  the label of that pass

### Requirement: Lasers and PIR compared
The evaluation shall report how many passes the lasers alone, the PIR sensor alone, and both
noticed.

#### Scenario: Passes by what noticed them <!-- id: f2e7b606 -->
- **Given** the pass records of a test run
- **When** its results are reported
- **Then** the report gives the number of passes noticed by the lasers only, by the PIR sensor only,
  and by both

### Requirement: Targets fixed before the field phase
Targets for each of the three outcomes shall be set from the results of the controlled tests and
fixed in writing, with their date, before the field phase begins; they shall not change during the
field phase.

#### Scenario: The field phase starts <!-- id: 5b37b9e3 -->
- **Given** the controlled tests are complete
- **When** the field phase begins
- **Then** written targets for each of the three outcomes exist, dated before the start of the field
  phase
