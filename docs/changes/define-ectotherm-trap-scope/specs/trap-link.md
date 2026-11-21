# trap-link

## Purpose
Every trap sends its pass records and its daily state summary to FieldMesh over the mobile network,
never its pictures, and takes new settings, firmware and models back, so that a fault shows within
a day and results arrive without a visit, while the memory card stays the full record.

## Terms
- **Send:** one connection of the trap to FieldMesh, by default once a day right after the daily
  state summary.
- **Confirmed:** a pass record or summary that FieldMesh has acknowledged receiving.
- **Release key:** the key with which the project signs firmware and models; the trap holds only
  the part that checks signatures.

## ADDED Requirements

### Requirement: Results sent once a day
At each send the trap shall send every pass record and state summary not yet confirmed, and no
pictures. By default it sends once a day; how often shall be set in its settings.

#### Scenario: The day's results are sent <!-- id: 7dcfb88b -->
- **Given** the trap has recorded passes since its last send
- **When** the daily state summary has been written
- **Then** the trap sends those pass records and the summary to FieldMesh
- **And** marks them as confirmed once FieldMesh acknowledges them

#### Scenario: No pictures leave the trap <!-- id: 09d3c9de -->
- **Given** passes with pictures on the memory card
- **When** the trap sends
- **Then** what it sends holds no pictures

#### Scenario: Sending more often <!-- id: 6da2648a -->
- **Given** the trap's settings say to send every six hours
- **When** six hours have passed since the last send
- **Then** the trap sends what is not yet confirmed

#### Scenario: FieldMesh accepts a pass record <!-- id: 08ab3418 -->
- **Given** a pass record as the trap sends it
- **When** it is checked against the FieldMesh upload contract
- **Then** it is a valid reading

### Requirement: Nothing lost without coverage
The memory card shall stay the full record. A send that fails shall leave its records unconfirmed,
so that the next send that gets through carries them; recording passes shall never wait for a
send.

#### Scenario: A day without coverage <!-- id: 8f7fa060 -->
- **Given** the trap could not get through at yesterday's send
- **When** it gets through at today's send
- **Then** it sends yesterday's and today's pass records and summaries

#### Scenario: A send breaks off <!-- id: 03f27597 -->
- **Given** a send broke off before FieldMesh acknowledged its records
- **When** the next send gets through
- **Then** the trap sends those records again

#### Scenario: No network found <!-- id: a9ce007a -->
- **Given** the trap finds no network at a send
- **When** it has tried for the time its settings allow
- **Then** it stops trying until the next send, records a link fault, and keeps recording passes

### Requirement: Settings from FieldMesh
The trap shall take new settings that FieldMesh holds for it at a send, check them, use and keep
valid ones on its memory card, refuse invalid ones, and tell FieldMesh which it did.

#### Scenario: New settings arrive <!-- id: ca7e69c7 -->
- **Given** FieldMesh holds new settings for the trap
- **When** the trap sends
- **Then** it takes the settings, keeps them on its memory card and uses them from then on
- **And** it tells FieldMesh at its next send that it took them

#### Scenario: Invalid settings are refused <!-- id: 356af091 -->
- **Given** FieldMesh holds settings for the trap with a value out of range
- **When** the trap sends
- **Then** it keeps its settings as they were and tells FieldMesh that it refused the new ones

### Requirement: Signed firmware updates
The trap shall install only firmware signed with the release key, and return to its earlier
firmware when new firmware does not start properly.

#### Scenario: A signed firmware update is installed <!-- id: 75d2c838 -->
- **Given** FieldMesh offers the trap firmware signed with the release key
- **When** the trap sends
- **Then** it downloads, checks and installs the firmware and runs it
- **And** its next send names the new firmware version

#### Scenario: An unsigned firmware update is refused <!-- id: 2a4e75f4 -->
- **Given** FieldMesh offers the trap firmware whose signature does not match the release key
- **When** the trap has downloaded it
- **Then** it does not install it, keeps running its firmware, and records a failed update

#### Scenario: A failed update falls back <!-- id: 0352d927 -->
- **Given** the trap has installed new firmware
- **When** the new firmware does not start properly
- **Then** the trap returns to its earlier firmware and records a failed update

### Requirement: Signed model updates
The trap shall use only a model file signed with the release key, whether it comes over the link or
is copied onto its memory card, and keep its current model when a new one fails its check or does
not load.

#### Scenario: A signed model arrives <!-- id: cc5f8062 -->
- **Given** a model file signed with the release key reaches the trap
- **When** the trap has checked it
- **Then** it uses the new model for the next pass, and pass records name the new model version

#### Scenario: A model that fails its check is refused <!-- id: c3876d58 -->
- **Given** a model file whose signature does not match the release key reaches the trap
- **When** the trap checks it
- **Then** it keeps its current model, or none, and records a failed update

#### Scenario: A model that does not load <!-- id: 28f560d3 -->
- **Given** a signed model file that the trap cannot load
- **When** the trap tries to use it
- **Then** it keeps its current model, or none, and records a failed update

### Requirement: The clock follows FieldMesh
At each send that gets through, the trap shall set its clock from the time FieldMesh gives.

#### Scenario: The clock has drifted <!-- id: 81b45c6f -->
- **Given** the trap's clock is a minute behind FieldMesh's time
- **When** a send gets through
- **Then** the trap's clock shows FieldMesh's time
