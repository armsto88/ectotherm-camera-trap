---
areas: [sorting]
---
# Pictures are sorted by a Python tool with a local review page

## Context
After collection, empty pictures must be removed, the rest sorted into broad groups, and people
must name species and correct the sorting; their names and the bucket identifications must become
training labels. No ready model knows small animals seen from above in a passage.

## Options considered
- A Python package with a command line and a small local page in the browser, with a small
  pretrained image model fine-tuned with PyTorch on the trap's labelled pictures.
- A general labelling tool such as Label Studio: rejected, it does not know passes, directions or
  bucket labels and needs setting up and adapting.
- An existing camera-trap detector such as MegaDetector: rejected, trained on side views of larger
  animals.

## Decision
The `trapsort` package reads a card copy, marks empty pictures against the day's empty view, sorts
the rest into broad groups once a model exists, serves a local review page, keeps labels in
`labels.csv`, summarises passes per survey day, exports Camtrap DP and evaluates bench runs and the
field phase.

## Consequences
- Works offline on one computer, with no account or server.
- Until enough labelled pictures exist, people sort all pictures not marked empty.
- PyTorch is a large dependency; it is needed only for training and sorting by group.
