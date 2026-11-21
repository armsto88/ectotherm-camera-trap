# unattended-season

## Purpose
The trap runs a whole season of three to six months without a visit, also where there is no
coverage, and writes a short daily summary of its state to its memory card, which it also sends
over the link, so that the labour and handling of daily bucket checks fall away and the trap's
state can be followed during the season and read when it is collected.

## Terms
- **Season:** up to six months between setting a trap up and collecting it.
- **Expected load:** the number of passes per day the design plans for.
- **State summary:** the daily summary of the trap's state on its memory card, in the format the
  FieldMesh system takes.

## ADDED Requirements

### Requirement: A season without a visit
The trap shall keep noticing, photographing and recording passes for six months at the expected
load without a visit.

#### Scenario: Six months at the expected load <!-- id: d6bcd7cb -->
- **Given** a trap set up with fresh batteries and empty storage
- **When** it runs for six months with passes at the expected load
- **Then** it still notices, photographs and records passes at the end of the six months

### Requirement: Works without coverage
The trap shall notice, photograph and record passes without any connection; only sending waits for
coverage.

#### Scenario: A trap where there is no coverage <!-- id: 40ee900d -->
- **Given** a trap at a site without any coverage
- **When** animals pass through it over a season
- **Then** it notices, photographs and records every pass

### Requirement: Daily state summary
Once a day the trap shall write a state summary to its memory card with its battery level, free
storage, the number of passes since the last summary, whether the daily picture showed a clear
view, and the coordinates from its settings, in the format the FieldMesh system takes, so that the
link can send it unchanged.

#### Scenario: The daily summary is written <!-- id: e2024b9a -->
- **Given** the trap is running
- **When** the time of the daily summary comes
- **Then** it writes a state summary with its battery level, free storage, the number of passes
  since the last summary, and whether its view is clear
- **And** the summary gives the coordinates from the trap's settings

#### Scenario: A day without passes <!-- id: 45e3bf6c -->
- **Given** no animal has passed since the last summary
- **When** the time of the daily summary comes
- **Then** it writes a state summary that gives zero passes

#### Scenario: A trap set up without coordinates <!-- id: c7f873a0 -->
- **Given** the trap's settings hold no coordinates
- **When** the time of the daily summary comes
- **Then** it writes a state summary that leaves the coordinates empty
- **And** the trap keeps noticing, photographing and recording passes

#### Scenario: FieldMesh accepts the summary <!-- id: 94733795 -->
- **Given** a state summary written by the trap
- **When** it is checked against the FieldMesh upload contract
- **Then** it is a valid reading

### Requirement: The trap records its own faults
The trap shall record, with their times, every fault that can cost records or leave the trap
unreachable: a blocked beam, a low battery, nearly full storage, a camera that fails to take a
picture, a send that fails and an update that fails.

#### Scenario: A fault is recorded <!-- id: 5ac27b8b -->
- **Given** the trap is running
- **When** its battery falls below the level the design names as low
- **Then** the trap records a low battery with the time
