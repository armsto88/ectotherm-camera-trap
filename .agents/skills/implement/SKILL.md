---
name: implement
description: Build the tasks of an oekospec change, one commit each with its tests, and open the implementation PR. Use only when the user asks for implement. You may suggest it once propose has finished, but never start it on your own.
disable-model-invocation: true
---

# implement

You build a change's tasks so that the code matches its specs and design. Where the plan and
the code don't fit, the user decides which side is wrong; you never decide it alone.

The workflow runs discuss → propose → implement → archive. Each step starts only when a person
asks for it.

## Where things live
- The library: `python3 .agents/oekospec <command>`.
- The change: `docs/changes/<name>/`, with `proposal.md`, `specs/`, `design.md`, `adr/`,
  `tasks.md` and `decisions.md`.
- Project specs: `docs/specs/`.
- The rules for asking in rounds and for decision pages: `.agents/oekospec/pages/asking.md`.

## Start
1. Find the branch for the code. Don't decide by the `specs/` folder: a change without spec
   deltas can gain one on the way.
   - If the change has a `specs/` folder, its change folder is not on the default branch
     (after `git fetch`, `git ls-tree origin/<default branch> docs/changes/<name>/` shows
     nothing) and no task in `tasks.md` is checked off, its change folder PR is not merged
     yet. Build nothing; tell the user that implement starts once that PR is merged, and stop.
   - If the change already has an open PR, keep working on its branch; create none. List the
     open PRs with `gh pr list --state open --limit 1000 --json number,headRefName,body` and
     take only the one whose description's first line links exactly to `docs/changes/<name>`,
     as in `Change folder: [docs/changes/<name>](...)`. A PR that only mentions the name
     elsewhere belongs to another change.
   - Otherwise update the default branch. If the change folder is on it, outside the archive
     (`git ls-tree <default branch> docs/changes/<name>/`), its own change folder PR was merged
     and its branch deleted, so create a new branch from the default branch, named as the
     project's git rules say.
   - Otherwise keep working on the branch discuss created; create none.

   Never commit to the default branch.
2. Read the change's `proposal.md`, `design.md`, `tasks.md` and specs. Read `decisions.md` only
   where a task or a question needs it.

## Each task
Work through the tasks in order. For each:
1. Build what the task says, with the interfaces the design names, and its tests.
2. Each scenario in the task's Tests list gets at least one test that names its ID in a comment
   `spec: <id>`, as `# spec: 3f9a1c2e` in Python. A scenario marked `(remove its tests)` loses
   every test that names its ID.
3. Write code, tests and comments that say what they do in their own words. Never point to a
   decision log entry, a change or a task by its number or name: they become history once the
   change is archived. If a task says "the rules of decisions 1–3", name those rules instead.
4. Run the project's tests and checks.
5. Before checking the task off, search the tests for each ID in its Tests list, such as
   `grep -rn "spec: 3f9a1c2e"`. A listed scenario without a test gets one first; a test left
   for a removed scenario is removed first.
6. Check the task off in `tasks.md` and make one commit holding the code, the tests and the
   checked task, following the project's git rules. Push it.

After the first task, open the implementation PR (see below).

## Mismatches
A mismatch is a place where the specs or the design and the code disagree. Stop and ask when:
- making a listed scenario pass breaks a test of a scenario no task lists;
- a task needs a file outside the design's Impact, test files included: check each file
  against Impact before you change it;
- a task needs an interface that differs from the design's Interfaces, such as a different
  signature.

Don't build the change first. Ask the user whether the spec, the design or the code is wrong,
in one question per mismatch with your recommended answer and one short reason. Mismatches that
come up together go into one round, as `.agents/oekospec/pages/asking.md` describes; read it
before your first round. A round goes on a decision page where it has two or more open
questions or something visible changes, and otherwise in the chat. Then, for each answer:
- **Spec or design wrong:** update the delta or `design.md` in the same PR. After editing a
  delta, run `python3 .agents/oekospec ids <change>` and `validate <change>`. If the fix adds
  or removes a spec file, say so in your question, such as "this adds the spec file
  `report-export`, so Capabilities gains it". After the answer, bring the proposal's
  Capabilities in line with the spec files (new spec files under New, touched existing specs
  under Modified), and once pushed, update the PR description (see The implementation PR).
- **Code wrong, inside the change:** add a task to `tasks.md` for the fix.
- **Code wrong, outside the change:** offer a short GitHub issue, show the draft, and post it
  with `gh issue create` only after a go.

Log the answer in `decisions.md` in the format of `python3 .agents/oekospec template decision`,
with Step implement.

When something you find means the proposal's why or what no longer holds, such as behaviour
that needs a spec but that What changes doesn't name, don't change them: suggest going back to
discuss, which then hands over to propose. Capabilities is not part of this: it only follows
the spec files. A change without spec deltas that gains one stays in its one PR.

## The implementation PR
Open it with `gh pr create` from the branch for the code into the default branch. For a change
without spec deltas this is the change's only PR. Write its description by hand:
- the first line `Change folder: [docs/changes/<name>](<repo URL>/tree/<branch>/docs/changes/<name>)`,
- a blank line, then the proposal without its title line, with wrapped lines joined, since
  GitHub keeps line breaks in PR descriptions, and relative links made absolute.

The title follows the project's git rules.

When you change the proposal's Capabilities while the PR is open, keep the description's first
line and replace the rest with the proposal as above. Update it with
`gh api -X PATCH repos/<owner>/<repo>/pulls/<number> -F body=@<file>`; `gh pr edit` fails in some repos.

## Finish
Once every task is checked off, suggest running archive in this same PR, before it is merged,
but don't start it.
