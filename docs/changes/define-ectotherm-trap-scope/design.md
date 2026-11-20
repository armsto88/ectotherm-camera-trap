# Design for a passage camera trap that replaces drift-fence buckets

## Decisions

### A passage through an upturned bucket, set into the fence line
An upturned standard bucket of about 30 cm diameter (about 20 litres) forms the dark hood. A
3D-printed insert carries a passage 15 cm wide and about 26 cm long across the bucket, its floor
flush with the ground at both ends, the beam walls, the camera, the light and the electronics. The
fence ends meet openings cut in two opposite sides of the bucket. Entries 27, 43, 54 and 55;
[ADR](adr/bucket-with-printed-insert.md).
Rejected: a purpose-built housing (costly in small numbers, repairable only with the maker's
parts); a channel with a box on top (more fitting and sealing); a raised threshold (animals must
climb).

### Beam points at both ends, beams at three heights
One beam point about 2 cm inside each end of the passage, each with beams at 4, 12 and 25 mm above
the floor. The camera looks at the floor between the points, so it has the walk from one point to
the middle to wake. Entries 34 and 39.
Rejected: both points a few centimetres apart in the middle (the camera would have to be on
already); one beam per point (one blocked beam blinds the point).

### Pulsed infrared laser beams, and a PIR sensor as an extra trigger
Each beam is a 940 nm laser diode on one wall and a photodiode on the other. The watcher switches
each laser on for about 20 microseconds 250 times a second and compares the photodiode with and
without the laser, so daylight at the passage ends cancels out. A PIR sensor in the hood looking
down at the floor also starts a pass. Entries 31, 33 and 40;
[ADR](adr/pulsed-laser-beams.md).
Rejected: laser distance sensors across the passage (several times the power); a heat sensor as the
main trigger (fails for cold-blooded animals).

### A separate beam watcher wakes the camera controller
An ATtiny3216 runs the beams and the PIR sensor without pause, turns beam changes into timed
crossings, and raises a wake line to an ESP32-S3, which reads the crossings over I2C, takes the
pictures and writes the records. Entries 41 and 59; [ADR](adr/separate-beam-watcher.md).
Rejected: the ESP32-S3's co-processor alone (limited; watching may pause); the prototype's board
(test bench only, entry 5).

### Camera, light and pictures
An OV5640 module without an infrared-cut filter, with a fixed-focus lens of about 75 degrees set to
the floor about 20 cm below, gives an estimated 8 to 10 pixels per millimetre across the 15 by 26 cm
floor. Every picture is lit by 940 nm LEDs flashed with the exposure, with fixed exposure settings,
so pictures do not depend on daylight and no visible light is used. A pass gets a picture as soon
as the camera is ready, then one every half second while the animal is in the passage, at most six.
If the bench shows the camera wakes too slowly, it stays on standby instead. Entries 38, 44, 45, 57
and 58.
Rejected: the OV2640 (two megapixels, weak in low light); 850 nm light (faint red glow); white
light (startles animals); one picture per pass.

### What the bench decides
The roof laser (entry 35), a side view by mirror or second camera (entry 37) and colour by daylight
through the top or by a short white light at the end of a pass (entry 38) are tested in the
controlled tests. The insert leaves a mount above the passage for a roof laser, a slot in one wall
for a mirror or second camera, and the bucket top free.

### The filter on the trap
The camera controller drops a picture only if the pass was noticed by the PIR sensor alone and the
picture differs from the day's empty-view picture by less than a set threshold; every pass the
lasers noticed keeps all its pictures. In pilot mode, set in the trap's configuration file, it
marks such pictures instead and drops nothing. Entries 23, 29 and 56.
Rejected: judging every picture by its difference from the empty view (could drop animals the
lasers saw).

### Records on the card, exported as Camtrap DP
One CSV file of pass records per survey day, the JPEG pictures in a folder per survey day, a fault
log and the daily state summaries, all on the memory card; times in UTC, survey days from the
trap's configured UTC offset. The sorting tool exports a season as a Camera Trap Data Package.
Entry 48; [ADR](adr/records-as-csv-and-camtrap-dp.md).
Rejected: only the trap's own format.

### The state summary is a FieldMesh reading
Once a day, after the empty-view picture, the camera controller appends one FieldMesh reading to the
state file: the contract's core fields plus `trapPasses`, `trapFreeMB` and `trapViewClear`, which
the FieldMesh backend stores although it does not model them. No radio in version 1. Entries 51 and
60; [ADR](adr/state-summary-as-fieldmesh-reading.md).
Rejected: a FieldMesh node over ESP-NOW (needs a hub on every site); the aux1 and aux2 fields.

### Power
A 6 V solar panel of about 1 W on a short stake beside the trap charges two 18650 cells in parallel
(about 7 Ah) through the FieldHub's CN3791 charger design, with charging stopped below 0 °C by a
thermistor on the pack. The design plans for 200 passes a day; see the power estimate below.
Entries 42, 46, 52, 53 and 61.
Rejected: a 12 Ah pack without solar; lithium AA cells; a panel on the bucket top or a fence post;
one cell.

### Firmware with PlatformIO and the Arduino framework
Both firmwares are PlatformIO projects with the Arduino framework: the watcher on megaTinyCore, the
camera controller on the espressif32 platform. Their logic sits in libraries without hardware
calls, tested on the computer in a `native` environment. Entry 47;
[ADR](adr/firmware-with-platformio-and-arduino.md).
Rejected: ESP-IDF directly; an STM32L0 for the watcher.

### Hardware drawn in FreeCAD and EasyEDA
The insert is a FreeCAD Python script with the bucket's inner diameter, height and wall angle as
parameters, generating STL files; the boards are drawn in EasyEDA. Entry 62;
[ADR](adr/hardware-in-freecad-and-easyeda.md).
Rejected: KiCad and OpenSCAD.

### Sorting as a Python tool with a local review page
A Python package with a command line reads a copy of the card, marks empty pictures against the
day's empty view, sorts the rest into broad groups once a model exists, serves a local review page
where people name species, and exports and evaluates. The group model is a small pretrained image
model fine-tuned with PyTorch. Entries 22, 49 and 63; [ADR](adr/sorting-tool-in-python.md).
Rejected: a general labelling tool; an existing camera-trap detector.

### Three levels of tests
Unit tests on the computer for firmware logic and the sorting tool; bench runs with a model-animal
rig whose records are checked by pytest scripts marked `bench`; and written check procedures in
`docs/testing/` for what only a person can check. Every test names its scenario with
`spec: <id>`. Entry 64; [ADR](adr/three-levels-of-tests.md).
Rejected: unit tests only.

### The prototype moves aside
`code.ino`, `README.md` and `Dev-BLOG.md` move unchanged to `prototype/`; a new top-level
`README.md` describes the trap. Entry 50.
Rejected: leaving them at the top.

## Power and storage estimate
Estimates to be replaced by bench measurements (task 5.2):

| Part | Estimate |
|---|---|
| Watcher with six pulsed beams | about 0.25 mA all the time |
| PIR sensor, ESP32-S3 asleep, clock | about 0.05 mA all the time |
| One pass: wake, up to six pictures with light, writing | about 0.12 mAh |
| A day at 200 passes | about 30 mAh |
| Two 18650 cells, about 7 Ah | about 200 days without sun |
| Pictures: about 250 kB, on average three per pass | about 150 MB a day, 27 GB a season; a 128 GB card |

## Interfaces

### New

#### The link between watcher and camera controller
A header shared by both firmwares: what the watcher reports and how it is read over I2C.

```cpp
// firmware/shared/include/link.h
const uint8_t LINK_ADDRESS = 0x42;           // watcher's I2C address

struct Crossing {                             // one beam point entered or left
  uint32_t t_ms;                              // watcher clock, ms since its start
  uint8_t point;                              // 0 = nearer side A, 1 = nearer side B
  uint8_t heights;                            // bit 0 lowest, bit 1 middle, bit 2 top
  uint8_t entered;                            // 1 = first beam broken, 0 = all clear again
};

struct WatcherStatus {
  uint32_t now_ms;                            // watcher clock when read, to map onto the RTC
  uint8_t stuck[2];                           // per point, beams blocked longer than stuck_ms
  uint8_t pending;                            // events waiting to be read
  uint8_t pir_since_read;                     // 1 if the PIR sensor fired since the last read
};

enum LinkRegister : uint8_t { REG_STATUS = 0x00, REG_EVENTS = 0x10, REG_CONFIG = 0x20 };
```

#### Beam watching (watcher library `beams`)
Turns raw photodiode samples into crossings and stuck beams; no hardware calls.

```cpp
// firmware/watcher/lib/beams/beams.h
class BeamFilter {
 public:
  /// Takes one pulse: the photodiode level with and without the laser; true when interrupted.
  bool update(uint16_t lit, uint16_t dark);
};

class PointTracker {
 public:
  explicit PointTracker(uint8_t point);
  /// Takes one sample of the point's interrupted-beam mask; true when out holds a crossing.
  bool update(uint32_t t_ms, uint8_t mask, Crossing* out);
};

class StuckBeams {
 public:
  explicit StuckBeams(uint32_t stuck_ms);
  /// Updates with the point's mask; returns the beams interrupted longer than stuck_ms.
  uint8_t update(uint32_t t_ms, uint8_t mask);
};
```

#### Passes (camera library `passes`)
Builds passes from crossings and PIR events; no hardware calls.

```cpp
// firmware/camera/lib/passes/passes.h
enum class Direction : uint8_t { AtoB, BtoA, BackA, BackB, Unknown };  // Unknown: PIR only

struct Pass {
  uint32_t start_ms, end_ms;                  // watcher clock
  Direction direction;
  uint8_t heights_a, heights_b;               // heights interrupted at each point
  bool by_lasers, by_pir;
};

class PassBuilder {
 public:
  explicit PassBuilder(uint32_t quiet_ms, uint8_t ignore_a, uint8_t ignore_b);
  /// Adds a crossing in time order; true when it completes a pass, now in pass().
  bool add(const Crossing& c);
  /// Adds a PIR event; starts a pass if none is open.
  void add_pir(uint32_t t_ms);
  /// Closes an open pass after quiet_ms without events; true when a pass completed.
  bool tick(uint32_t now_ms);
  const Pass& pass() const;
};
```

#### Records, summary and configuration (camera library `records`)
Text for everything written to the card; no hardware calls.

```cpp
// firmware/camera/lib/records/records.h
struct TrapConfig {
  char trap_id[16];                           // also the FieldMesh nodeId, e.g. ECT_0A1B2C
  int16_t utc_offset_min;                     // for survey days and the daily times
  bool pilot_mode;
  uint8_t empty_view_hour;                    // local hour of the daily picture and summary
  float drop_threshold;                       // filter: largest difference still "empty"
};

struct PassRecord {                           // one row of a survey day's pass file
  char pass_id[40];                           // <trap_id>-<survey day>-<number>
  uint32_t start_utc_s, end_utc_s;
  Pass pass;
  const char* pictures;                       // ';'-separated file names
  uint8_t dropped_empty;                      // pictures the filter dropped
  const char* judged_empty;                   // ';'-separated names marked in pilot mode
};

enum class FaultKind : uint8_t { BeamBlocked, BeamClear, BatteryLow, StorageLow, CameraFailed };

struct StateSummary {                         // the values of one daily summary
  uint32_t utc_s, seq;
  float battery_v, temperature_c;
  uint32_t passes, free_mb;                   // passes since the last summary
  bool view_clear;                            // from the daily empty-view picture
};

/// Reads trap.cfg text into out, keeping defaults for missing keys; false on a malformed line.
bool parse_config(const char* text, TrapConfig* out);

/// Survey day (noon to noon, local) of a UTC time, as "YYYY-MM-DD" of its first noon.
void survey_day(uint32_t utc_s, int16_t utc_offset_min, char out[11]);

/// CSV header of a survey day's pass file.
const char* pass_csv_header();

/// One pass record as a CSV line; pictures and judged-empty marks as ';'-separated names.
size_t pass_csv_line(const PassRecord& r, char* out, size_t size);

/// One fault as a CSV line for faults.csv.
size_t fault_csv_line(uint32_t utc_s, FaultKind kind, const char* detail, char* out, size_t size);

/// The day's state summary as one FieldMesh reading, JSON on one line.
size_t summary_json(const StateSummary& s, const TrapConfig& c, char* out, size_t size);
```

#### Filter (camera library `filter`)
Decides whether a picture may be dropped; no hardware calls.

```cpp
// firmware/camera/lib/filter/filter.h
/// Mean absolute difference of two greyscale thumbnails of n pixels, from 0 to 1.
float thumbnail_difference(const uint8_t* a, const uint8_t* b, size_t n);

enum class FilterResult : uint8_t { Keep, Drop, MarkEmpty };

/// Keep unless the PIR alone noticed the pass and difference < threshold;
/// MarkEmpty instead of Drop in pilot mode.
FilterResult judge(const Pass& p, float difference, float threshold, bool pilot_mode);
```

#### The sorting tool (`sorting/trapsort`)
A Python package with the command `trapsort`.

```python
# sorting/trapsort/model.py
@dataclass
class Picture:
    """One stored picture: file, pass_id, survey day, empty mark, group and confidence."""
@dataclass
class PassRecord:
    """One row of a pass file, with its pictures."""
@dataclass
class Season:
    """Everything read from one card copy: passes, pictures, empty views, faults, summaries."""
@dataclass
class LabelledPicture:
    """A picture with a group from a person's name or a bucket label."""
class GroupModel:
    """A trained group model: predict(picture) gives a group and a confidence."""
@dataclass
class DayCount:
    """Passes in one survey day for one name or group and one direction."""

# sorting/trapsort/card.py
def read_card(card: Path) -> Season:
    """Reads pass records, pictures, faults and summaries from a card copy; raises CardError."""

# sorting/trapsort/empty.py
def mark_empty(season: Season, threshold: float) -> None:
    """Marks pictures that differ from their survey day's empty view by less than threshold."""

# sorting/trapsort/groups.py
Group = Literal["frog", "toad", "newt", "lizard", "snake", "other"]
def sort_groups(season: Season, model: GroupModel | None) -> None:
    """Gives each picture not marked empty a group and confidence; none without a model."""
def train_group_model(pictures: Iterable[LabelledPicture], out: Path,
                      min_per_group: int = 50) -> GroupModel:
    """Fine-tunes a small pretrained model; raises TooFewLabels below min_per_group."""

# sorting/trapsort/labels.py
class LabelStore:
    """Names, group corrections and bucket labels in labels.csv beside the season."""
    def set_name(self, picture: str, name: str, by: str) -> None: ...
    def set_group(self, picture: str, group: Group, by: str) -> None: ...
    def add_bucket_label(self, pass_id: str, name: str, checked_at: datetime) -> None: ...

# sorting/trapsort/review.py
def serve_review(season: Season, labels: LabelStore, port: int = 8765) -> None:
    """Serves the local review page until stopped; each name or correction is saved at once."""

# sorting/trapsort/summary.py
def passes_per_survey_day(season: Season, labels: LabelStore) -> list[DayCount]:
    """Passes per survey day by group or species and direction; never called animals."""

# sorting/trapsort/camtrapdp.py
def export_camtrap_dp(season: Season, labels: LabelStore, out: Path) -> None:
    """Writes datapackage.json, deployments.csv, media.csv and observations.csv."""

# sorting/trapsort/evaluate.py
@dataclass
class BenchPlan:
    """Rows of a bench run's plan.csv: what passed when, at which size, speed and light."""
@dataclass
class BucketChecks:
    """Rows of bucket_checks.csv: the animals found in the bucket at each check."""
@dataclass
class Report:
    """Shares noticed, photographed and identified; missed animals; passes by sensing."""
def read_plan(path: Path) -> BenchPlan:
    """Reads plan.csv; raises PlanError on a malformed row."""
def read_bucket_checks(path: Path) -> BucketChecks:
    """Reads bucket_checks.csv; raises PlanError on a malformed row."""
def evaluate(season: Season, labels: LabelStore,
             reference: BenchPlan | BucketChecks) -> Report:
    """The three outcomes as shares of the animals the reference says passed, the missed
    animals, and the passes noticed by the lasers only, the PIR sensor only and both."""
```

#### Bench checks (`bench/checks`)
pytest checks run on the records of a bench run, marked `bench`.

```python
# bench/checks/run.py
@dataclass
class BenchRun:
    """A bench run: its plan and the season read from its card copy."""
@dataclass
class PlannedPass:
    """One planned passage with the pass record and pictures it produced, or none."""
def load_bench_run(run: Path) -> BenchRun:
    """Reads plan.csv and the card copy in run with trapsort; raises on either error."""
def match_plan(run: BenchRun, window_s: float = 2.0) -> list[PlannedPass]:
    """Pairs each planned passage with the pass that started within window_s of it."""
```

## Formats

### On the memory card
```
trap.cfg                       key=value lines: trap_id, utc_offset_min, pilot_mode,
                               empty_view_hour, drop_threshold
passes/2026-05-14.csv          one file per survey day (noon to noon, local)
pictures/2026-05-14/           <pass_id>_<n>.jpg, and empty_<HHMM>.jpg for the daily picture
faults.csv                     time_utc,fault,detail
state/summaries.jsonl          one FieldMesh reading per line, one line per day
```

Pass file columns, times in ISO 8601 UTC:
`pass_id,start_utc,end_utc,direction,heights_a,heights_b,noticed_by,pictures,dropped_empty,judged_empty`,
with `direction` one of `AtoB`, `BtoA`, `backA`, `backB`, `unknown`, `noticed_by` one of `lasers`,
`pir`, `both`, and `pass_id` as `<trap_id>-<survey day>-<number>`.

Fault kinds: `beam_blocked`, `beam_clear`, `battery_low`, `storage_low`, `camera_failed`.

A state summary line:
```json
{"datetime":"2026-05-14T10:00:00Z","nodeId":"ECT_0A1B2C","seqNum":12,"sensorPresent":0,
 "qualityFlags":0,"configVersion":1,"batVoltage":3.98,"airTemp":17.5,
 "trapPasses":143,"trapFreeMB":98112,"trapViewClear":true}
```
`airTemp` comes from the clock chip in the hood; `qualityFlags` bit 0 is set when the view is not
clear.

### Beside a season on the computer
- `labels.csv`: `picture,pass_id,kind,value,by,at`, where `kind` is `name`, `group` or `bucket`.
- `bucket_checks.csv`: `checked_at,trap_id,animal,name,group`, one row per animal found in the
  bucket during the field phase.
- The Camtrap DP export: one deployment per trap season; one media row per picture; one
  event-level observation per pass, with `observationType` `animal`, `blank` or `unclassified`,
  the name from the labels, `classificationMethod` `human` or `machine`, and the direction in
  `observationComments`.

### A bench run
`plan.csv`: `planned_at,model,body_length_mm,height_mm,speed_mm_s,temperature_c,light,direction`,
next to a copy of the trap's card from that run.

## Impact

### New
- `README.md`: what the trap is, how to build, set up and collect it
- `firmware/shared/include/link.h`
- `firmware/watcher/`: PlatformIO project for the ATtiny3216, with `lib/beams` and `test/`
- `firmware/camera/`: PlatformIO project for the ESP32-S3, with `lib/passes`, `lib/records`,
  `lib/filter` and `test/`
- `sorting/`: the `trapsort` package, its `pyproject.toml` and `tests/`
- `bench/rig/`: the model-animal rig (a belt pulling model animals along the floor at set speeds)
- `bench/checks/`: pytest checks on bench runs
- `hardware/insert/`: the FreeCAD script and generated STL files
- `hardware/boards/`: EasyEDA exports of the watcher and beam boards and the main board
- `docs/testing/`: written check procedures, the controlled-test plan and the field-phase procedure

### Renamed
- `code.ino` → `prototype/code.ino`
- `README.md` → `prototype/README.md`
- `Dev-BLOG.md` → `prototype/Dev-BLOG.md`
