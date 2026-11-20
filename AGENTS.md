<!-- oekospec:start -->
## oekospec workflow
This repository uses oekospec, a spec-driven workflow. Every change that alters behaviour goes
through its steps discuss → propose → implement → archive, using the skills of the same names.
Each step starts only when a person asks for it; you may suggest the next one. When the goal of
a request is unclear, or it mixes several topics, suggest starting with discuss.

Each change gets its own branch and goes through a pull request.

What holds today, in this order:
1. Accepted specs in `docs/specs/` and ADRs in `docs/adr/`; start from their `index.md`.
2. Where no spec covers a behaviour, the code is the authority, and its tests pin that
   behaviour down. Where code contradicts a spec or an accepted ADR, don't pick a side: ask
   the user.
3. Open changes, the folders in `docs/changes/` outside `archive`, are proposals, not accepted.
4. Archived changes in `docs/changes/archive/` are history: they explain why something came
   about, never what holds today.

The oekospec skills in `.agents/skills/` and the library in `.agents/oekospec/` are installed
from the oekospec repo and are not edited here; `python3 .agents/oekospec check` reports
edits. Send changes to the oekospec repo as feedback, and update by running the install command
again.
<!-- oekospec:end -->
