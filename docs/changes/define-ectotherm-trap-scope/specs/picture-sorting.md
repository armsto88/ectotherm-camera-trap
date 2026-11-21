# picture-sorting

## Purpose
On the trap, a simple filter drops pictures that are obviously empty, and a small model gives each
pass a type of animal without deleting anything. After collection the computer marks pictures that
look like the empty passage, and people sort each remaining pass into a broad group and name the
species as far as its pictures allow. People's groups and names become the labels from which the
model keeps learning.

## Terms
- **Empty picture:** a picture showing no animal.
- **Broad group:** frog, toad, newt, lizard, snake, turtle or other.
- **Pilot mode:** the setting the trap runs in during the controlled tests and the field phase of
  the evaluation.
- **Can't tell:** the mark a person gives a picture that shows something they cannot sort into a
  group.
- **Model type:** the type of animal the model on the trap gives a pass: frog or toad, lizard,
  snake, other animal, or empty. Newts, salamanders and turtles count as other animal until the
  trap's own named pictures teach the model them.

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

### Requirement: The model on the trap labels each pass
When the trap has a model, it shall give each pass a model type and how sure it is after the
pass's pictures are taken, and keep both with the model's version in the pass record. The model
shall delete nothing; which pictures are kept stays the filter's decision alone.

#### Scenario: The model gives a pass its type <!-- id: 5c00e1eb -->
- **Given** a model on the trap
- **When** the pictures of a pass have been taken
- **Then** the pass record holds the model type, how sure the model is, and the model's version

#### Scenario: The model deletes nothing <!-- id: be4d4900 -->
- **Given** a model on the trap that judges a pass empty
- **When** the filter keeps the pass's pictures
- **Then** the pictures are stored and the pass record holds the model type empty

#### Scenario: A trap without a model <!-- id: b83ecc08 -->
- **Given** no model on the trap
- **When** a pass is recorded
- **Then** the pass record leaves the model type empty and holds everything else as before

### Requirement: Empty pictures marked after collection
After the pictures are collected, the computer shall mark each stored picture that looks like the
daily picture of the empty view from its survey day as empty, and leave every other picture for a
person.

#### Scenario: Pictures like the empty view are marked <!-- id: 6e42dbca -->
- **Given** the pictures and pass records collected from a trap, with its daily pictures of the
  empty view
- **When** the pictures are sorted
- **Then** each picture that looks like the empty view of its survey day is marked as empty
- **And** every other picture is left for a person to sort

### Requirement: People sort the passes and name the species
Every pass with a picture not marked empty shall be shown to a person with all its pictures side by
side. The person picks the pass's broad group and adds the species name as far as the pictures
allow, and both are stored with every picture of the pass. The person can mark a single picture
empty or "can't tell", correct an empty mark, and label the pictures of a pass one by one when they
show different animals. For a pass recorded in pilot mode the model type shall not be shown; for
any other pass it shall be shown as a suggestion, and only what the person picks is stored as
their label.

#### Scenario: A person sorts and names a pass <!-- id: 016374dd -->
- **Given** a pass whose pictures show a lizard
- **When** a person picks the group lizard and names the species
- **Then** the group and the name are stored with every picture of the pass and with its pass
  record

#### Scenario: A person can't tell <!-- id: f93d49ef -->
- **Given** a pass whose only picture is too blurred to sort
- **When** the person marks the picture "can't tell"
- **Then** the picture is stored as looked at, without a group

#### Scenario: A person corrects an empty mark <!-- id: 2cde2e6f -->
- **Given** a picture marked as empty that shows an animal
- **When** the person corrects the mark
- **Then** the picture is stored as not empty and shown with its pass to be sorted

#### Scenario: A pass with two different animals <!-- id: 251da24f -->
- **Given** a pass whose pictures show a toad and then a newt
- **When** the person labels the pictures one by one
- **Then** each picture keeps its own group and name

#### Scenario: The model type is hidden in the pilot <!-- id: 4296a7e0 -->
- **Given** a pass recorded in pilot mode, with the model type lizard
- **When** the pass is shown to a person to sort
- **Then** the page does not show the model type

#### Scenario: The model type is suggested after the pilot <!-- id: 37dd1930 -->
- **Given** a pass recorded outside pilot mode, with the model type lizard
- **When** the pass is shown to a person to sort
- **Then** the page suggests lizard
- **And** only the group the person picks is stored as their label

### Requirement: Labels for learning
The groups and names people give, and the in-hand identifications of animals caught in the bucket
during the field phase, shall be stored with the pictures of the matching pass, so that the model
on the trap can learn from them.

#### Scenario: A bucket animal labels its pictures <!-- id: 2a1668f9 -->
- **Given** a pass whose pictures match an animal caught in the bucket behind the trap
- **When** the person checking the bucket identifies the animal in the hand
- **Then** that identification is stored with the pictures of the pass as a label
- **And** the label carries the group the bucket check gives for the animal
