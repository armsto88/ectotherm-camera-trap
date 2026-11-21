---
areas: [sorting]
---
# Pictures are sorted by a Python tool with a local review page

## Context
After collection, empty pictures must be set aside, and people must sort the rest into broad groups
and name the species; their groups and names, and the bucket identifications of the field phase,
must be kept as labels the trap's model learns from. The trap's model types each pass; in the pilot
people must sort without seeing that type, so that their groups check the model.

## Options considered
- A Python package with a command line and a small local page in the browser, without a learned
  model.
- The same package with an image model of its own on the computer: rejected, the model runs on the
  trap, and its training lives in a separate project.
- A general labelling tool such as Label Studio: rejected, it does not know passes, directions or
  bucket labels and needs setting up and adapting.

## Decision
The `trapsort` package copies a card into a season folder, marks pictures that look like their
survey day's empty view, and serves a local review page that shows each remaining pass with its
pictures side by side, where a person picks the broad group and adds the species name once for the
pass. For passes recorded outside pilot mode the page suggests the trap's model type; for passes
recorded in pilot mode it hides it. It keeps labels in `labels.csv`, summarises passes per survey
day, exports Camtrap DP and evaluates bench runs and the field phase.

## Consequences
- Works offline on one computer, with no account or server, and without a large machine-learning
  dependency; training the model is the separate `model/` project's job.
- People sort every pass that is not marked empty, about three pictures at a time.
- The labels are kept per picture, so the model can learn from every picture of a sorted pass.
- Outside the pilot, sorting gets faster with the suggestion, but people may lean towards it.
