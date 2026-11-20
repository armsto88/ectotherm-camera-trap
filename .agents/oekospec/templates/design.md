# Design for <what the change does, in a few plain words>

## Decisions

### <one choice the change makes, as a short statement>
<the choice and a short reason; decisions.md and the ADRs hold the full reasoning>
Rejected: <each option turned down, with its reason in brackets>

## Interfaces

### New

#### <a part the change adds, such as a command, module or type; Interfaces is needed only when the change adds, modifies or removes code, shows only that code and is deleted otherwise>
<one or two plain sentences on what this part is for and where it fits>

```
<only the signatures the change adds, without function bodies: every function and type with a one-line docstring on what goes in, what comes out and when it refuses, and a comment only on a field whose meaning is not obvious>
```

### Modified

#### <a part the change modifies; leave out each subsection of Interfaces that stays empty>
<one or two plain sentences on what changes in it>

```
<its new signatures only, each with the old one in a `# was:` comment line above it, renames included>
```

### Removed
- <a part the change removes: why it goes and what replaces it>

## Formats
<optional, for a change that reads or writes files: what each file holds and its layout; delete this section otherwise, and add any other section the change needs in the same way>

## Migration plan
<optional, when existing repos or data have to move: the numbered steps that move them; delete this section otherwise>

## Impact

### New
- <a file or folder the change adds; list only what the implementation touches, not what archiving adds to docs/specs, docs/adr and the archive, nor effects on other changes, people or repos>

### Modified
- <a file the change edits; leave out each subsection of Impact that stays empty>

### Renamed
- <`old path` → `new path`>

### Removed
- <a file or folder the change deletes>
