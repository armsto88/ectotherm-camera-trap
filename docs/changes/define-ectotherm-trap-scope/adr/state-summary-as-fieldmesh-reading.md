---
areas: [records, fieldmesh]
---
# The daily state summary is a FieldMesh reading

## Context
Every trap sends to the FieldMesh system on its own over a mobile modem, once a day, and also keeps
everything on its memory card. The daily summary should be the same on the card and in FieldMesh.

## Options considered
- One FieldMesh reading per day with the contract's core fields plus trap fields, which the
  FieldMesh backend stores although it does not model them.
- The generic aux1 and aux2 fields: rejected, their meaning would live only in documents.
- Extending the FieldMesh upload contract first: rejected, the trap could not send until FieldMesh
  changed.

## Decision
Once a day the trap appends one reading to `state/summaries.jsonl`: `datetime`, `nodeId` (the trap
number), `seqNum`, `sensorPresent`, `qualityFlags`, `configVersion`, `batVoltage` and `airTemp`,
`latitude` and `longitude` from the trap's settings (null when not set), plus `trapPasses`,
`trapFreeMB` and `trapViewClear`, and `trapKind` `state`, which tells it from the trap's pass
readings. Bit 0 of `qualityFlags` marks an unclear view. The link sends the line unchanged.

## Consequences
- The summary is valid against today's FieldMesh contract, so the link sends it as it is.
- FieldMesh shows the trap fields only once its contract and dashboard model them.
- A change to the FieldMesh contract may require a change here.
