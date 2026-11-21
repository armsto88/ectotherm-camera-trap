---
areas: [firmware, fieldmesh]
---
# Settings, firmware and models reach the trap over the link, signed

## Context
A trap stands three to six months without a visit. Version 1 firmware will have faults that only
the pilot finds, and the model on the trap will be retrained as people name more pictures. The
FieldHub already takes commands in FieldMesh's reply to an upload and installs firmware signed with
the user's release key, falling back when new firmware fails; that fall-back is proven on the
classic ESP32 only. FieldMesh can release only FieldHub firmware today.

## Options considered
- Settings as FieldMesh commands; firmware updates as on the FieldHub; models as separate signed
  files on the card with their own update path.
- The model inside the firmware: rejected by the user, so that a model changes without a firmware
  release.
- A settings file fetched from a web address: rejected, a second channel to secure and keep.
- A new update scheme for the trap: rejected, more to build and prove.
- The camera controller also reprogramming the beam watcher: rejected, wiring and a second
  fall-back for a rarely changed part.

## Decision
Settings arrive as a FieldMesh command, are checked by the rules of the trap's settings file, used
and kept on the card when valid, and the result is reported at the next upload. Firmware arrives
as on the FieldHub: a manifest signed with the release key (Ed25519), the image written to the
spare slot and checked by size and SHA-256, and the bootloader's fall-back when the new firmware
does not confirm itself. A model arrives as a signed manifest and file, checked the same way and
swapped in only after the check; the trap keeps its model when a new one fails. Only the camera
controller is updated over the link.

## Consequences
- Faults found in the pilot are fixed, and new models reach the traps, without visits.
- FieldMesh needs a command type for trap settings and release roles for trap firmware and models;
  until then the trap sends but takes nothing back, and a model is copied onto the card.
- The fall-back must be proven on the ESP32-S3 before traps go into the field.
- The release key's private part must stay offline; the trap holds only the public part.
- The beam watcher's firmware changes only at a visit.
