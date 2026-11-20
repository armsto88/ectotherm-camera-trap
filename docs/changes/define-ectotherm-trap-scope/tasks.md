# Tasks for a passage camera trap that replaces drift-fence buckets

Each task is one commit with its tests. Every scenario in a task's Tests list gets at least one
test carrying `# spec: <id>`.

## 1. Repository layout
- [x] 1.1 Move `code.ino`, `README.md` and `Dev-BLOG.md` unchanged to `prototype/`; add a new
  top-level `README.md` describing the trap, the folders `firmware/`, `sorting/`, `bench/`,
  `hardware/` and `docs/testing/`, and a `.gitignore` for PlatformIO and Python build output.
  Done when: git shows the three files as renamed, and the new `README.md` describes the trap and
  links to `prototype/`.

## 2. Firmware logic, tested on the computer
- [x] 2.1 Build the link header `firmware/shared/include/link.h` and the watcher library `beams`
  (`BeamFilter`, `PointTracker`, `StuckBeams`), with a PlatformIO `native` environment for its unit
  tests.
  Done when: unit tests show steady light cancelled, one entered and one left crossing per broken
  beam with the right heights, and a beam reported stuck only after `stuck_ms`.
- [x] 2.2 Build the camera library `passes` (`PassBuilder`, `Pass`, `Direction`).
  Tests:
  - `b3059cbe` A pass from side A to side B
  - `49a98a46` A pass from side B to side A
  - `978712b4` An animal turns back
  - `e6a90220` An animal goes through and comes back
- [x] 2.3 Build the camera library `records` (`TrapConfig`, `parse_config`, `survey_day`,
  `PassRecord`, `pass_csv_header`, `pass_csv_line`, `FaultKind`, `fault_csv_line`, `StateSummary`,
  `summary_json`), checking summaries against the readings table of the FieldMesh upload contract,
  version 1 of 2026-11-16.
  Tests:
  - `c2ab65dd` A pass leaves its record
  - `45e3bf6c` A day without passes
  - `94733795` FieldMesh accepts the summary
  Done when: `survey_day` puts 23:00 and 01:00 local time into the same survey day, and
  `parse_config` keeps defaults for missing keys.
- [x] 2.4 Build the camera library `filter` (`thumbnail_difference`, `FilterResult`, `judge`).
  Tests:
  - `5c654b74` An obviously empty picture is dropped
  - `3007f937` An unsure picture is kept
  - `f4c14891` The filter marks a picture in pilot mode
- [ ] 2.5 Add the trap's coordinates to `records`: `latitude` and `longitude` in `TrapConfig` (not
  set by default), read by `parse_config` and rejected out of range, and written by `summary_json`
  in FieldMesh's fields for them, null when not set (changes what 2.3 built).
  Tests:
  - `94733795` FieldMesh accepts the summary
  Done when: unit tests show coordinates read from `trap.cfg`, a latitude of 91 rejected, and a
  summary with and without coordinates both valid against the FieldMesh contract.

## 3. Hardware
- [ ] 3.1 Write the insert script in `hardware/insert/`: a passage 15 cm wide across a bucket of
  about 30 cm diameter, the floor flush with the ground at both ends, beam walls with beam holes at
  4, 12 and 25 mm at a point about 2 cm inside each end, a camera mount that can be set between
  about 20 and 30 cm above the floor, a mount for a roof laser, a slot for a side view, and bays for
  the boards and cells.
  Done when: `freecadcmd` generates the STL files for two bucket sizes, and a printed insert fits a
  20 litre bucket with the fence ends meeting its openings.
- [ ] 3.2 Draw and build the boards in EasyEDA: one beam board per wall (three 940 nm laser diodes
  or three photodiodes) and the main board (ATtiny3216, ESP32-S3 module, a 24-pin camera connector
  and an SPI camera header so that either kind of camera module plugs in, infrared LEDs and driver
  with one footprint for 940 nm or 850 nm LEDs, PIR sensor, DS3231 clock, microSD slot, the
  FieldHub's CN3791 charger with a thermistor that stops charging below 0 °C, and a holder for two
  18650 cells); every chip one JLCPCB can assemble, from LCSC's stock where it has it; keep the
  exports in `hardware/boards/` with a bring-up checklist.
  Done when: the boards are assembled and every part answers on the bring-up checklist.
- [ ] 3.3 Build the model-animal rig in `bench/rig/`: a belt that pulls model animals along the
  passage floor at the speeds of a `plan.csv`, a light box for darkness and daylight, a
  visible-light sensor in the passage, and model animals (flat 3 cm, taller than the second beam,
  mouse-sized and warmed, and at room temperature).
  Done when: the rig runs a `plan.csv` and logs the time of each planned passage.

## 4. Firmware on the boards
- [ ] 4.1 Write the watcher firmware in `firmware/watcher/`: pulse each laser 250 times a second,
  read the PIR sensor, keep crossings in a buffer, raise the wake line, answer on I2C as `link.h`
  describes, and sleep between pulses.
  Done when: a hand breaking a beam wakes the camera controller, and the crossing it reads back has
  the right point and heights.
- [ ] 4.2 Write the pass capture in `firmware/camera/`: wake, read crossings and status, map the
  watcher clock onto the clock chip, build passes, take the picture burst with the infrared flash
  and fixed exposure, apply the filter, write pictures and pass records, and read `trap.cfg`,
  including pilot mode and the coordinates.
  Done when: an object passed through by hand leaves a row in the survey day's pass file and its
  pictures on the card.
- [ ] 4.3 Write the daily jobs: the empty-view picture, taken once the passage is empty, the state
  summary with the coordinates from `trap.cfg`, and the fault log for blocked beams, low battery,
  low storage and camera failures.
  Tests:
  - `5bcc1dab` The daily picture is taken
  - `cc78920a` An animal is in the passage at the time of the daily picture
  - `e2024b9a` The daily summary is written
  - `c7f873a0` A trap set up without coordinates
  - `5ac27b8b` A fault is recorded

## 5. Bench checks and bench runs
- [ ] 5.1 Build the bench checks in `bench/checks/` (`BenchRun`, `PlannedPass`, `load_bench_run`,
  `match_plan`), as pytest tests marked `bench`.
  Done when: the checks pair a recorded rig run with its plan, and an unmatched planned passage
  shows as missing.
- [ ] 5.2 Run and check the detection runs: temperatures, sizes, darkness and daylight, beam
  heights, a blocked lowest beam, cold and warm model animals, and a mouse-sized model.
  Tests:
  - `172ed05c` An animal as warm as its surroundings crosses a beam point
  - `808cb65b` A flat 3 cm animal crosses along the floor
  - `1f2dd41f` A pass in darkness
  - `169583a5` A pass in bright daylight
  - `53f0ff23` A taller animal interrupts more beams
  - `2697cd6b` Debris blocks the lowest beam
  - `dd5a2678` Only the lasers notice a cold animal
  - `58ebb8e3` Only the PIR sensor notices a warm animal
  - `abc0c8ed` A mouse passes through
- [ ] 5.3 Run and check the picture runs, with known animals for the expert check.
  Tests:
  - `0f31246f` An animal walking through is photographed
  - `4d3defba` The same animal at noon and at midnight
  - `d3749ed6` An expert names a known animal from its picture
  - `64488b5b` Pictures taken without visible light
- [ ] 5.4 Measure the camera's wake time against the target speeds; if too few passes at walking
  speed get a picture with the animal in view, keep the camera on standby (entry 58).
  Done when: wake times and the share of passes with an in-view picture per speed are in
  `docs/testing/bench-results.md`, and the standby choice is logged in `decisions.md`.
- [ ] 5.5 Test the roof laser against blocked beams and power use (entry 35).
  Done when: the results are in `docs/testing/bench-results.md` and keeping or dropping the roof
  laser is logged in `decisions.md`.
- [ ] 5.6 Test a side view, colour and the infrared wavelength with known animals (entries 37, 38
  and 77): identification from above alone, with a mirror and with a second camera; how warm the
  passage gets with daylight through the top; whether a short white light makes animals turn back
  or hurry; and 940 against 850 nm LEDs for picture quality, power and whether animals react to the
  faint glow of 850 nm.
  Done when: the results are in `docs/testing/bench-results.md` and the choices are logged in
  `decisions.md`.
- [ ] 5.7 Measure power use and picture sizes and replace the design's estimates.
  Done when: measured currents, energy per pass and picture sizes are in
  `docs/testing/bench-results.md`, and the pack is sized to the measured season budget, larger
  than two 18650 cells if needed (entry 77).
- [ ] 5.8 Run a trap for four weeks at the expected load with no connection, and extrapolate its
  charge use to six months; the field phase confirms it.
  Tests:
  - `d6bcd7cb` Six months at the expected load
  - `40ee900d` A trap where there is no coverage
- [ ] 5.9 Choose the camera module, its lens and the camera's height (entry 76): compare a module
  with a ribbon cable and one with a screw-in M12 lens, at about 20, 25 and 30 cm above the floor,
  with model animals of different heights, by darkness and by day, focusing each lens once and
  fixing it.
  Done when: sharpness at the floor and on the tallest model animal, pixels per millimetre and the
  light needed are in `docs/testing/bench-results.md` for each setup, and the choice is logged in
  `decisions.md`.

## 6. Sorting tool
- [x] 6.1 Build the `trapsort` package with its types in `model.py`, `read_card` and the command
  `trapsort import`.
  Done when: it reads the card copy of a bench run, and raises `CardError` on a malformed pass file.
- [ ] 6.2 Build `mark_empty` and the command `trapsort sort`, which marks the pictures that look
  like their survey day's empty view and writes `sorting.csv`.
  Tests:
  - `6e42dbca` Pictures like the empty view are marked
- [ ] 6.3 Build `LabelStore`, `serve_review` and the import of bucket identifications with their
  groups as labels. The review page shows each pass with a picture not marked empty, its pictures
  side by side, with buttons for the broad groups (frog, toad, newt, lizard, snake, turtle, other),
  a field for the species name, "Empty" and "Can't tell" under each picture, and a switch to label
  the pictures one by one.
  Tests:
  - `016374dd` A person sorts and names a pass
  - `f93d49ef` A person can't tell
  - `2cde2e6f` A person corrects an empty mark
  - `251da24f` A pass with two different animals
  - `2a1668f9` A bucket animal labels its pictures
- [ ] 6.4 Build `passes_per_survey_day` and `export_camtrap_dp`, with the commands `trapsort
  summarise` and `trapsort export`; the export places the deployment at the coordinates in the
  card's `trap.cfg` and stops without them.
  Tests:
  - `0930417b` A season is summarised
  - `f746b277` A season is exported with its place
  - `2f5cb71e` A season without coordinates is not exported
  Done when: an exported package passes the Camtrap DP validation.
- [ ] 6.5 Change `trapsort import` to check a card and copy it into a season folder's `card/` with
  `import_card`; add `read_season` and `write_sorting` for the empty marks; and move `Group` into
  `model.py` with turtle added, dropping `LabelledPicture` and `GroupModel` (changes what 6.1
  built).
  Done when: an imported card equals the original, a second import into the same season is
  refused, and `read_season` reads back what `write_sorting` wrote.

## 7. Evaluation
- [ ] 7.1 Build `read_plan`, `read_bucket_checks`, `evaluate` and the command `trapsort evaluate`,
  counting a pass as having a usable picture when a person gave any of its pictures a group or a
  name, and as identified when that name matches the animal the reference names; a run with
  pictures nobody has looked at is reported as not fully sorted.
  Tests:
  - `36e16dab` Results of a test run
  - `fb3c43de` An animal in the bucket without a matching picture
  - `9df1ab87` An animal in the bucket with a matching picture
  - `f2e7b606` Passes by what noticed them
- [ ] 7.2 Write the controlled-test plan in `docs/testing/controlled-tests.md` with its `plan.csv`
  files, run it on the rig with model and known animals, and report the three outcomes.
  Tests:
  - `b0c045b3` Model animals across sizes and speeds
- [ ] 7.3 Write `docs/testing/targets.md` from the controlled-test results, dated, and the field-phase
  procedure in `docs/testing/field-phase.md` with its bucket checks.
  Tests:
  - `5b37b9e3` The field phase starts

## 8. Written checks of the passage
- [ ] 8.1 Write the check procedures for the passage in `docs/testing/passage-checks.md`.
  Tests:
  - `fd2c5b0e` An animal following the fence crosses through the passage
  - `c7531d9b` A small animal cannot slip past the trap
  - `3662828d` An animal turns back inside the passage
  - `746fea6c` An animal stays in the passage

## Progress notes
- 2026-11-20: By the user's choice, the tasks that can be finished at a computer (6.1–6.4, 7.1,
  5.1, 8.1) are built ahead of the hardware tasks, which wait for bench work.
- 2026-11-20: 6.1 was checked against a card copy written by the tests in the format the
  firmware writes; the card of a real bench run follows with 5.2.
- 2026-11-20: 6.5 is built right after 6.1, since 6.2 to 6.4 take the season folder it brings.
- 2026-11-20: The change went back through discuss and propose (entries 72 to 84): no learned model
  in this change, turtle as a group, passes sorted at once, coordinates in `trap.cfg`. Tasks 2.5 and
  6.5 change code already built; 6.2 to 6.4, 3.1, 3.2, 4.2, 4.3, 5.6, 5.7 and 7.1 were rewritten
  before being built, and 5.9 is new.
