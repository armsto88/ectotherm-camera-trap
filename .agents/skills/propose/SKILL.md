---
name: propose
description: Turn the proposal and decision log of an oekospec change into specs, design, ADRs and tasks, and open the change folder's PR. Use only when the user asks for propose. You may suggest it once discuss has written a proposal, but never start it on your own.
disable-model-invocation: true
---

# propose

You turn a change's proposal into a plan that reviewers can check and implement can build:
spec deltas (what must hold), a design (how it is built), ADRs (lasting decisions) and tasks
(one commit each). Every choice is the user's.

The workflow runs discuss → propose → implement → archive. Each step starts only when a person
asks for it.

## Where things live
- The library: `python3 .agents/oekospec <command>`.
- Project specs: `docs/specs/index.md`; ADRs: `docs/adr/index.md`.
- The change: `docs/changes/<name>/`, with `proposal.md`, `decisions.md`, `specs/<spec>.md`,
  `design.md`, `adr/<name>.md` and `tasks.md`.
- The rules for asking in rounds and for decision pages: `.agents/oekospec/pages/asking.md`.

## Start
1. Read the change's `proposal.md` and `decisions.md`. These are your only input, so that
   propose works in a new session or for another person; don't rely on an earlier conversation.
2. Work on the change's branch, which discuss created. Switch to it if needed; create none.
3. Don't change the proposal's why and what. If it leaves open what the change must do, stop,
   name the gap, and suggest going back to discuss; don't fill it yourself.
4. If tasks in `tasks.md` are already checked off, the change is being implemented and came
   back through discuss. Work only on what the new decisions change: edit only the specs,
   design and ADRs they touch, leave every checked task exactly as it is, and put all new
   work into new tasks, including changes to code that is already built. A new task that
   changes what a done task built names it, such as "1.3 Log retries at info instead of
   warning (changes what 1.1 built)".

## How you work with the user
- Write each file straight to the change folder for the user to review in their own editor; don't
  show drafts in the conversation. After each step, name the files you wrote or changed.
- Make the changes the user asks for. Commit and push a file to the change's branch only once
  the user says it is fine, following the project's git rules.
- Put your questions to the user in rounds, as `.agents/oekospec/pages/asking.md` describes;
  read it before your first round. A round holds every question that can be answered now, such
  as design points and clashes with project scenarios or current ADRs, each with a recommended
  answer and one short reason. It goes on a decision page where it has two or more open
  questions or something visible changes, and otherwise in the chat. Check each design point
  against the current ADRs first (see 2. Design), also when it settles while the specs are
  still open.
- After each round, take the answers as `asking.md` describes. For each real choice that
  settles, one with realistic alternatives worth recording, append an entry to `decisions.md` in
  the format of `python3 .agents/oekospec template decision`, with Step propose, then write the
  text it affects and name the files you changed. Plain fixes get no entry. Never edit a
  settled entry; a changed choice gets a new entry with a Replaces line.
- Write the files strictly in this order: specs, design, ADRs, tasks, each built on the ones
  before it. A design point that settles while the specs are still open goes into the decision
  log at once, but the design waits until the specs are written.
- Each file follows the library's template for its kind: `python3 .agents/oekospec template`
  lists them. Follow its hints on content and wording.

## 1. Specs
1. Read `docs/specs/index.md` and pick the specs and requirements the decisions may touch.
   Read those candidates in full; when there are many, send subagents that each report whether
   a candidate is touched and why. Don't read the code behind a requirement you take from the
   project specs: the requirement is the source.
2. Before you write or edit any requirement, check each behaviour you plan to specify against
   the project scenarios. Where it contradicts one, so that both cannot hold, such as a project
   scenario that expects a retry where the change stops, stop and ask the user which behaviour
   holds, recommending one. Ask even when the proposal or the decision log seems to answer it:
   which behaviour is wanted is the user's call. Only after the answer modify the project
   requirement or change the new scenario. If the proposal doesn't say this behaviour changes,
   suggest going back to discuss.
3. For each touched requirement, run `python3 .agents/oekospec modify <change> <spec>
   "<requirement>"` and edit it in place in `specs/<spec>.md`; for one that goes, run `remove`
   and fill in the reason. Never write a modified requirement from scratch.
4. Behaviour the change alters that no requirement describes yet becomes an added requirement
   describing the new behaviour: `template delta` for an existing spec, `template spec` for a
   new one. First read the code behind that behaviour, through subagents where there is much
   of it, to learn what it does today. Write no specs for behaviour the change does not alter,
   even if the code has none.
5. Scenario IDs: run `python3 .agents/oekospec ids <change>` to fill in missing ones; never write
   an ID by hand and never reuse one. When you edit a scenario, ask: is a test written for its
   old version still correct? If yes (wording fixed, a term renamed, a stricter extra And), it
   keeps its ID. If no (a different outcome or a different case), delete its ID comment so that
   `ids` gives it a new one. An additional case is always a new scenario next to the old one.
6. Keep the proposal's Capabilities in line with the spec files: each new spec file under New,
   each existing spec the change touches under Modified, named in kebab-case. If the change
   already has an open PR, update its description once the edited proposal is pushed (see
   Finish).

## 2. Design
1. Read the code the change touches, through subagents where there is much of it, each
   reporting the files and interfaces the change affects. Impact and Interfaces build on what
   they find.
2. Read `docs/adr/index.md` and pick the current ADRs, those no other ADR supersedes, that the
   design decisions may touch. Read those candidates in full; when there are many, send
   subagents that each report whether a candidate is touched and why.
3. Check each design point against those ADRs before you settle it. Where it goes against a
   current ADR, so that both cannot hold, name the ADR and ask the user which holds,
   recommending one. Ask even when the user has told you to decide design points alone or the
   proposal or the decision log seems to answer it. Log the answer. If the change wins, the
   change needs a new ADR that supersedes the old one (see 3. ADRs), even if the design point
   would otherwise need none.
4. Run `template design` and write `design.md`. Decisions are cut to the choice, a short
   reason, what was rejected and the ADR link; the decision log and the ADRs hold the full
   reasoning.

## 3. ADRs
For each decision in the design that should outlast the change, run `template adr` and write
`adr/<name>.md`, named in kebab-case after the decision, such as `format-with-ruff`.

Where a new ADR touches a current ADR, ask the user whether it supersedes it, with a
recommended answer. Ask even when the user has told you to decide design points alone or the
decision log seems to answer it: which ADRs stay current is the user's call. A new ADR
supersedes an old one by naming it in its `supersedes` line, as the template shows; the old
file stays unchanged, and the ADR index marks it as superseded by the new one. So a new ADR
supersedes an old one completely: where only part of the old one stops holding, recommend
superseding it and repeating in the new ADR the part that still holds. Log the answer in
`decisions.md`.

## 4. Tasks
Run `template tasks` and write `tasks.md`. Every new, changed and removed scenario of the change
appears in the Tests list of exactly one task, by ID and name. After `ids` has run, compare each
scenario in the delta with the same requirement in `docs/specs`:

| Case | How to tell | In the Tests list |
|---|---|---|
| New | the ID is not in the project specs | yes |
| Changed | same ID, text differs once trailing whitespace and blank lines are ignored | yes; marked `(wording only)` if only the wording changed |
| Unchanged | same ID, same text | no, unless the task changes the code behind it |
| Removed | the ID is in the project requirement but not in the delta, or the requirement is removed | yes, marked `(remove its tests)` |

Every scenario of a new spec is new.

## Finish
1. Run `python3 .agents/oekospec validate <change>` and fix what it reports; finish only once it
   reports nothing.
2. Once the user is fine with every file, commit and push what is left.
3. If the change's branch already has an open PR (`gh pr list --head <branch>`), open none:
   push to it, and if you edited the proposal, update the PR description: keep its first line
   and replace the rest with the proposal as described below, using
   `gh api -X PATCH repos/<owner>/<repo>/pulls/<number> -F body=@<file>`; `gh pr edit` fails in some repos.
   Otherwise, if the change has spec deltas, a `specs/` folder, open the change folder's PR
   from the change's branch into the default branch with `gh pr create`. Write its description
   by hand:
   - the first line `Change folder: [docs/changes/<name>](<repo URL>/tree/<branch>/docs/changes/<name>)`,
   - a blank line, then the proposal without its title line, with wrapped lines joined, since
     GitHub keeps line breaks in PR descriptions, and relative links made absolute.

   The title follows the project's git rules.
4. If the change has no spec deltas and its branch has no open PR, open none: the change
   folder and the code share one PR, which implement opens.
5. If you opened the change folder's PR, say that implement starts once that PR is reviewed
   and merged. Otherwise suggest implement as the next step. Either way, don't start it.
