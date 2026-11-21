---
areas: [firmware, hardware, fieldmesh]
---
# The trap sends to FieldMesh as a hub of its own, over a mobile modem

## Context
Every trap reports from the start: once a day its pass records and its state summary go to
FieldMesh, never its pictures, and the memory card stays the full record. FieldMesh today knows
hubs that upload readings, confirms each upload by count, stores reading keys it does not model,
and has no place for pass records. The user's Auris recorder fixes a modem design; only the
FieldHub has working code that uploads to FieldMesh over a mobile network.

## Options considered
- A Quectel EG810M-EU modem as in Auris, with a driver written for the trap, sending each pass as
  a FieldMesh reading, the trap registered as a hub with one node, itself.
- The SIMCom A7670G with the FieldHub's driver: rejected by the user, so that the trap and Auris
  share one modem.
- A pass type in FieldMesh before the trap sends: rejected, the trap's link would wait for
  FieldMesh work.
- A new kind of device in FieldMesh for traps: rejected, FieldMesh work before the trap can send.

## Decision
The trap has a Quectel EG810M-EU modem on Auris's 3.9 V supply, switched off between sends, with
its antenna on the solar panel's stake. In FieldMesh each trap is a hub with its own upload key and
one node, itself. Once a day, right after its state summary, the trap uploads every unconfirmed
reading over HTTPS, checking FieldMesh's certificate: each pass as a reading with flat trap keys,
and the summary last. A reading counts as sent only when FieldMesh confirms it; the confirmed
position is kept on the card. A send gives up after about three minutes. Each reply sets the clock.

## Consequences
- The trap sends from its first day without a change to FieldMesh.
- A driver for the EG810M-EU must be written before the trap can send; Auris can share it.
- The modem is approved for Europe, Australia and New Zealand only.
- Until FieldMesh models the trap keys, passes are missing from its CSV export and its views treat
  them like sensor values.
- A trap without coverage loses nothing; its records go at the next send that gets through.
- A change to the FieldMesh upload contract may require a change here.
