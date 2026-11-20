# picture-sorting

## Purpose
Pictures are sorted in two steps: a simple filter on the trap drops pictures that are obviously
empty, and after collection a model removes empty pictures and sorts the rest into broad groups,
after which people name the species and check the sorting. People's names become the labels from
which species-level recognition can later be learned.

## Terms
- **Empty picture:** a picture showing no animal.
- **Broad group:** frog, toad, newt, lizard, snake or other.
- **Pilot mode:** the setting the trap runs in during the controlled tests and the field phase of
  the evaluation.

## ADDED Requirements

### Requirement: Filter on the trap
The trap shall drop pictures that are obviously empty and keep every other picture; when unsure, it
shall keep the picture. A dropped picture shall leave a note in its pass record.

#### Scenario: An obviously empty picture is dropped <!-- id: 5c654b74 -->
- **Given** the trap is not in pilot mode
- **When** a picture of a pass is obviously empty
- **Then** the trap does not store the picture
- **And** the pass record notes that a picture was dropped as empty

#### Scenario: An unsure picture is kept <!-- id: 3007f937 -->
- **Given** the trap is not in pilot mode
- **When** the filter cannot tell whether a picture is empty
- **Then** the trap stores the picture

### Requirement: The filter deletes nothing in pilot mode
In pilot mode the filter shall only mark pictures it judges empty and delete none, so that its
mistakes can be counted.

#### Scenario: The filter marks a picture in pilot mode <!-- id: f4c14891 -->
- **Given** the trap is in pilot mode
- **When** the filter judges a picture empty
- **Then** the trap stores the picture and marks it as judged empty

### Requirement: Sorting after collection
After the pictures are collected, a model shall sort each stored picture as empty or into one broad
group.

#### Scenario: A season's pictures are sorted <!-- id: 46091a85 -->
- **Given** the pictures and pass records collected from a trap
- **When** the model sorts them
- **Then** each picture is marked as empty or with one broad group

### Requirement: People name the species
Every picture the model does not mark as empty shall be shown to a person, who names the species or
the nearest group as far as the picture allows and can correct the model's broad group or empty
mark.

#### Scenario: A person names a species <!-- id: e9570a6f -->
- **Given** a picture the model sorted as lizard
- **When** a person looks at it and names the species
- **Then** the name is stored with the picture and its pass record

#### Scenario: A person corrects the model <!-- id: bf27198f -->
- **Given** a picture the model sorted as frog that shows a toad
- **When** the person corrects the group
- **Then** the corrected group is stored with the picture, together with the model's original group

### Requirement: Labels for learning
The names people give, and the in-hand identifications of animals caught in the bucket during the
field phase, shall be stored with the pictures of the matching pass, so that they can train the
model later.

#### Scenario: A bucket animal labels its pictures <!-- id: 2a1668f9 -->
- **Given** a pass whose pictures match an animal caught in the bucket behind the trap
- **When** the person checking the bucket identifies the animal in the hand
- **Then** that identification is stored with the pictures of the pass as a label
