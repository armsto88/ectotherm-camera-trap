# trap-evaluation

## Purpose
The trap's performance is measured in two stages and reported as three separate outcomes, together
with how well the model on the trap agrees with people, with targets set from measurements before
the field phase, so that claims about the trap rest on counts of the animals it misses and not on
numbers of pictures.

## Terms
- **The three outcomes:** whether the trap noticed a pass, whether it took a usable picture of it,
  and whether the animal was identified from the pictures.
- **Controlled tests:** the first stage, with model animals and known animals passed through the
  trap; no wild animals are handled.
- **Field phase:** the second stage, short and time-limited, at a few drift fences with a bucket
  behind the trap.
- **Missed animal:** an animal that reached the bucket behind the trap without a matching pass with
  a usable picture.
- **Usable picture:** a picture to which a person sorting the pictures gave a group or a name; a
  picture marked empty or "can't tell" is not usable.
- **Identified:** a pass whose name, given by a person, matches the animal the test plan or the
  bucket check names.
- **Model agreement:** the share of passes with a usable picture whose model type matches the
  group a person gave, counting frog and toad as frog or toad, and newt, turtle and other as other
  animal.

## ADDED Requirements

### Requirement: Three outcomes reported separately
Every evaluation result shall report the three outcomes separately, each as a share of the animals
that passed; a number of pictures or triggers shall never stand for a number of animals detected.

#### Scenario: Results of a test run <!-- id: 36e16dab -->
- **Given** a test run in which a known number of animals passed through the trap
- **When** its results are reported
- **Then** the report gives, separately, the share noticed, the share with a usable picture and the
  share identified

### Requirement: The model measured against people
Every evaluation result for passes with model types shall report the model agreement, in total and
for each model type, from passes whose model type people did not see while sorting.

#### Scenario: Model agreement of a test run <!-- id: 9426c4fa -->
- **Given** a test run whose passes have model types and were sorted in pilot mode
- **When** its results are reported
- **Then** the report gives the model agreement in total and for each model type

#### Scenario: Passes sorted with the suggestion shown <!-- id: d7c82910 -->
- **Given** a test run whose passes were sorted with the model type shown as a suggestion
- **When** its results are reported
- **Then** the report gives no model agreement for those passes and says why

### Requirement: The model checked before it goes on the traps
A model shall go on the traps only once its agreement on named bench pictures, kept apart from its
training, meets the targets set for it.

#### Scenario: A model is checked on bench pictures <!-- id: aff15e4e -->
- **Given** a model trained on others' pictures and named bench pictures kept apart from its
  training
- **When** the model is checked on those bench pictures
- **Then** its agreement is reported in total and for each model type, and compared with its
  targets

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
Targets for each of the three outcomes and for the model agreement shall be set from the results of
the controlled tests and fixed in writing, with their date, before the field phase begins; they
shall not change during the field phase.

#### Scenario: The field phase starts <!-- id: 5b37b9e3 -->
- **Given** the controlled tests are complete
- **When** the field phase begins
- **Then** written targets for each of the three outcomes exist, dated before the start of the field
  phase
- **And** written targets for the model agreement exist, dated before the start of the field
  phase
