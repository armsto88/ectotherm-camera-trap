---
areas: [model]
---
# The model is trained with Keras on free pictures, then on the trap's own

## Context
No pictures from the trap are named yet, but others have published several million labelled
pictures taken from above at drift fences (California, Ohio and Indiana on LILA, and an Australian
set), free with credit. They hold many lizards, snakes, frogs and toads, almost no salamanders or
turtles and no newts, and their lizards and snakes are almost all daytime colour pictures, while
the trap takes infrared. The model must run 8-bit with TensorFlow Lite Micro on the ESP32-S3.

## Options considered
- Keras, trained on the published pictures turned grey, then fine-tuned and checked on named bench
  pictures from the trap.
- PyTorch, converted for the trap: rejected, an extra conversion step that can change the model.
- Training only on the published pictures: rejected, the infrared gap would go unmeasured.

## Decision
A Python project in `model/`, separate from the sorting tool, trains the model with Keras on the
published pictures mapped to the model types (frog or toad, lizard, snake, other animal, empty) and
turned grey, fine-tunes it on named bench pictures from the trap, checks it on bench pictures kept
apart from training, and exports it 8-bit. A model goes on the traps only once it meets its targets.
Each model has a model card naming its sources and their licences, and is signed with the release
key.

## Consequences
- A first model is possible before the trap's first season is named.
- Newts, salamanders and turtles count as other animal until the trap's own named pictures teach
  the model them.
- The model project carries TensorFlow; the sorting tool stays light.
- Published pictures licensed for credit must be credited wherever the model is shared.
