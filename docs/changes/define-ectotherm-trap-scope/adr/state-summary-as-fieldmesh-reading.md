---
areas: [records, fieldmesh]
---
# The daily state summary is a FieldMesh reading

## Context
Version 1 has no radio, but a later change is to let the trap feed the FieldMesh system on its own
(issue #1). The daily summary should be sendable unchanged then.

## Options considered
- One FieldMesh reading per day with the contract's core fields plus trap fields, which the
  FieldMesh backend stores although it does not model them.
- The generic aux1 and aux2 fields: rejected, their meaning would live only in documents.
- Extending the FieldMesh upload contract now: rejected, a FieldMesh change for a version that does
  not send.

## Decision
Once a day the trap appends one reading to `state/summaries.jsonl`: `datetime`, `nodeId` (the trap
number), `seqNum`, `sensorPresent`, `qualityFlags`, `configVersion`, `batVoltage` and `airTemp`,
`latitude` and `longitude` from the trap's settings (null when not set), plus `trapPasses`,
`trapFreeMB` and `trapViewClear`. Bit 0 of `qualityFlags` marks an unclear view.

## Consequences
- The summary is valid against today's FieldMesh contract; the uplink of issue #1 can send it as is.
- FieldMesh shows the trap fields only once its contract and dashboard model them.
- A change to the FieldMesh contract may require a change here.
