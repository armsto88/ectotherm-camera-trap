---
areas: [hardware]
---
# Hardware is drawn in FreeCAD and EasyEDA

## Context
The insert must fit buckets of different makers, and the boards must be ordered and assembled like
the user's FieldMesh boards.

## Options considered
- A FreeCAD Python script for the insert, like FieldMesh's sensor housings, and EasyEDA for the
  boards, like the FieldMesh boards.
- OpenSCAD for the insert and KiCad for the boards: rejected, new tools for no gain.

## Decision
The insert is a FreeCAD Python script, run with `freecadcmd`, with the bucket's inner diameter,
height and wall angle as parameters, generating the STL files. The boards are drawn in EasyEDA, and
their exports (Gerber, BOM, pick-and-place) are kept in the repository.

## Consequences
- One script makes inserts for different buckets.
- EasyEDA sources live in EasyEDA; the repository keeps the exports, as in FieldMesh.
