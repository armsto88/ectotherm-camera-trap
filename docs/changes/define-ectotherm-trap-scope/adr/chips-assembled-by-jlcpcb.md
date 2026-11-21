---
areas: [hardware]
---
# Every chip on the trap's boards is one JLCPCB can assemble

## Context
The trap's boards are drawn in EasyEDA and made and assembled by JLCPCB, which assembles from
LCSC's stock and orders other parts in. Camera modules with a lens and cable are not on LCSC, and
several chips that run image models are missing there or held only in a few pieces.

## Options considered
- Chips from LCSC's stock where it has them, otherwise ordered in through JLCPCB's global sourcing;
  plug-in parts from anywhere.
- LCSC's stock only, plug-in parts included: rejected, no 5 megapixel camera module and most chips
  for image models would be ruled out.

## Decision
Every chip on the trap's boards is one JLCPCB can assemble: from LCSC's stock where it has it,
otherwise ordered in through JLCPCB. Plug-in parts such as the camera module and the cells may come
from anywhere.

## Consequences
- The boards can be ordered assembled in one place.
- Parts ordered in add about two to four weeks, cannot be returned, and some carry customs fees, so
  LCSC stock is the first choice whenever a part is picked.
- The camera module comes from a second supplier, whose lenses and filters vary between makers.
