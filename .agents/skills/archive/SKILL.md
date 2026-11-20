---
name: archive
description: Archive a finished oekospec change in its last implementation PR, merging its specs and ADRs into the project and moving it to the archive. Use only when the user asks for archive. You may suggest it once implement has checked off the last task, but never start it on your own.
disable-model-invocation: true
---

# archive

You close a finished change: the library merges its specs and ADRs into `docs/specs` and
`docs/adr` and moves its folder to `docs/changes/archive/`. This happens in the change's last
implementation PR, before that PR is merged, so the specs on the default branch change together
with the code.

The workflow runs discuss → propose → implement → archive. Each step starts only when a person
asks for it.

## Where things live
- The library: `python3 .agents/oekospec <command>`.
- The change: `docs/changes/<name>/`; once archived, `docs/changes/archive/<date>-<name>/`.

## Start
1. If the change folder is not on the default branch, outside the archive (after `git fetch`,
   `git ls-tree origin/<default branch> docs/changes/<name>/` shows nothing), it had no change
   folder PR of its own and is reviewed in this same PR. Ask the user whether that review is
   done; if not, ask for it first and stop, without switching branches. Don't decide by the
   `specs/` folder: a change without spec deltas can gain one on the way.
2. Work on the branch of the change's last implementation PR, which is still open. Never run
   archive on the default branch or after the PR is merged.
3. Bring the branch up to date with the default branch, following the project's git rules, so
   that the library compares the change with the current project specs.

## Archive
Run `python3 .agents/oekospec archive <change>`. It validates the change, merges its specs and
ADRs, rebuilds both indexes and moves the folder. If any problem is left, it refuses, lists the
problems and changes nothing.

## When the library refuses
Don't resolve a refusal on your own. Show the user every problem the library lists, and ask how
to go on, with your recommended answer. Typical problems:
- **An unchecked task or another gap in the change:** the change isn't finished; suggest going
  back to implement or fixing the gap, as the user decides.
- **A requirement someone else changed:** the project spec changed a requirement after the
  delta took it in. Show the user both versions: the project requirement as it is now, and what
  the delta makes of it. Find what changed in the project spec since then, such as with
  `git log -p -- docs/specs/<spec>.md` from the commit that added the delta. Ask how to bring the
  two together. Once the user has decided and the delta holds the agreed text, run
  `python3 .agents/oekospec refresh <change>` to record the current version, then run `archive`
  again.

## Finish
1. Commit the archived change and push it to the PR's branch, following the project's git
   rules.
2. Change the first line of the PR description to link to the archived folder on the default
   branch, and leave the rest as it is:
   `Change folder: [docs/changes/archive/<date>-<name>](<repo URL>/tree/<default branch>/docs/changes/archive/<date>-<name>)`.
   Update it with `gh api -X PATCH repos/<owner>/<repo>/pulls/<number> -F body=@<file>`;
   `gh pr edit` fails in some repos.
3. Tell the user the PR is ready for review and merge.
