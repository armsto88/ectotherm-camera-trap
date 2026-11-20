---
areas: [sorting]
---
# Pictures are sorted by a Python tool with a local review page

## Context
After collection, empty pictures must be set aside, and people must sort the rest into broad
groups and name the species; their groups and names, and the bucket identifications of the field
phase, must be kept as labels a model can learn from later. No ready model knows small animals seen
from above in a passage, and none can be trained before people have sorted a season.

## Options considered
- A Python package with a command line and a small local page in the browser, without a learned
  model.
- The same package with a small pretrained image model fine-tuned with PyTorch to sort pictures
  into groups: rejected, nothing to train it on before the first season is sorted, and a learned
  model is a later change.
- A general labelling tool such as Label Studio: rejected, it does not know passes, directions or
  bucket labels and needs setting up and adapting.

## Decision
The `trapsort` package copies a card into a season folder, marks pictures that look like their
survey day's empty view, and serves a local review page that shows each remaining pass with its
pictures side by side, where a person picks the broad group and adds the species name once for the
pass. It keeps labels in `labels.csv`, summarises passes per survey day, exports Camtrap DP and
evaluates bench runs and the field phase.

## Consequences
- Works offline on one computer, with no account or server, and without a large machine-learning
  dependency.
- People sort every pass that is not marked empty, about three pictures at a time.
- The labels are kept per picture, so a later model can learn from every picture of a sorted pass.
