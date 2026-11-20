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
- [ ] 2.3 Build the camera library `records` (`TrapConfig`, `parse_config`, `survey_day`,
  `PassRecord`, `pass_csv_header`, `pass_csv_line`, `FaultKind`, `fault_csv_line`, `StateSummary`,
  `summary_json`), checking summaries against the readings table of the FieldMesh upload contract,
  version 1 of 2026-11-16.
  Tests:
  - `c2ab65dd` A pass leaves its record
  - `45e3bf6c` A day without passes
  - `94733795` FieldMesh accepts the summary
  Done when: `survey_day` puts 23:00 and 01:00 local time into the same survey day, and
  `parse_config` keeps defaults for missing keys.
- [ ] 2.4 Build the camera library `filter` (`thumbnail_difference`, `FilterResult`, `judge`).
  Tests:
  - `5c654b74` An obviously empty picture is dropped
  - `3007f937` An unsure picture is kept
  - `f4c14891` The filter marks a picture in pilot mode

## 3. Hardware
- [ ] 3.1 Write the insert script in `hardware/insert/`: a passage 15 cm wide across a bucket of
  about 30 cm diameter, the floor flush with the ground at both ends, beam walls with beam holes at
  4, 12 and 25 mm at a point about 2 cm inside each end, the camera mount about 20 cm above the
  floor, a mount for a roof laser, a slot for a side view, and bays for the boards and cells.
  Done when: `freecadcmd` generates the STL files for two bucket sizes, and a printed insert fits a
  20 litre bucket with the fence ends meeting its openings.
- [ ] 3.2 Draw and build the boards in EasyEDA: one beam board per wall (three 940 nm laser diodes
  or three photodiodes) and the main board (ATtiny3216, ESP32-S3 module, OV5640 connector, 940 nm
  LEDs and driver, PIR sensor, DS3231 clock, microSD slot, the FieldHub's CN3791 charger with a
  thermistor that stops charging below 0 °C, and a holder for two 18650 cells); keep the exports in
  `hardware/boards/` with a bring-up checklist.
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
  watcher clock onto the clock chip, build passes, take the picture burst with the 940 nm flash and
  fixed exposure, apply the filter, write pictures and pass records, and read `trap.cfg`, including
  pilot mode.
  Done when: an object passed through by hand leaves a row in the survey day's pass file and its
  pictures on the card.
- [ ] 4.3 Write the daily jobs: the empty-view picture, taken once the passage is empty, the state
  summary, and the fault log for blocked beams, low battery, low storage and camera failures.
  Tests:
  - `5bcc1dab` The daily picture is taken
  - `cc78920a` An animal is in the passage at the time of the daily picture
  - `e2024b9a` The daily summary is written
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
- [ ] 5.6 Test a side view and colour with known animals (entries 37 and 38): identification from
  above alone, with a mirror and with a second camera; how warm the passage gets with daylight
  through the top; and whether a short white light makes animals turn back or hurry.
  Done when: the results are in `docs/testing/bench-results.md` and the choices are logged in
  `decisions.md`.
- [ ] 5.7 Measure power use and picture sizes and replace the design's estimates.
  Done when: measured currents, energy per pass and picture sizes are in
  `docs/testing/bench-results.md`, and a season budget larger than the pack and panel is raised
  for discuss.
- [ ] 5.8 Run a trap for four weeks at the expected load with no connection, and extrapolate its
  charge use to six months; the field phase confirms it.
  Tests:
  - `d6bcd7cb` Six months at the expected load
  - `40ee900d` A trap where there is no coverage

## 6. Sorting tool
- [ ] 6.1 Build the `trapsort` package with its types in `model.py`, `read_card` and the command
  `trapsort import`.
  Done when: it reads the card copy of a bench run, and raises `CardError` on a malformed pass file.
- [ ] 6.2 Build `mark_empty`, `sort_groups`, `train_group_model` and the commands `trapsort sort`
  and `trapsort train`.
  Tests:
  - `46091a85` A season's pictures are sorted
- [ ] 6.3 Build `LabelStore`, `serve_review` and the import of bucket identifications as labels.
  Tests:
  - `e9570a6f` A person names a species
  - `bf27198f` A person corrects the model
  - `2a1668f9` A bucket animal labels its pictures
- [ ] 6.4 Build `passes_per_survey_day` and `export_camtrap_dp`, with the commands `trapsort
  summarise` and `trapsort export`.
  Tests:
  - `0930417b` A season is summarised
  Done when: an exported package passes the Camtrap DP validation.

## 7. Evaluation
- [ ] 7.1 Build `read_plan`, `read_bucket_checks`, `evaluate` and the command `trapsort evaluate`.
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
