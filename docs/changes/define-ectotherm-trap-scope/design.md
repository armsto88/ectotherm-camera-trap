# Design for a passage camera trap that replaces drift-fence buckets

## Decisions

### A passage through an upturned bucket, in the fence line or at a fence end
An upturned standard bucket of about 30 cm diameter (about 20 litres) forms the dark hood. A
3D-printed insert carries a passage 15 cm wide and about 26 cm long across the bucket, its floor
flush with the ground at both ends, the beam walls, the camera, the light and the electronics. The
fence ends meet openings cut in two opposite sides of the bucket. At a fence end the trap sits the
same way, with a short piece of fence, about a bucket's width, beyond it, so side A and side B keep
their meaning. `trap.cfg` notes the placement and describes side A in words. Entries 43, 54, 55,
91, 92, 119 and 120; [ADR](adr/bucket-with-printed-insert.md).
Rejected: a purpose-built housing (costly in small numbers, repairable only with the maker's
parts); a channel with a box on top (more fitting and sealing); a raised threshold (animals must
climb); at a fence end, the passage continuing the fence with two wings into one end (other joints,
other directions).

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
A 5 megapixel camera module without an infrared-cut filter, an OV5640, with a fixed-focus lens
whose focal length is chosen for the camera's height so that the view just covers the 15 by 26 cm
floor at about 10 pixels per millimetre; the lens is focused once at the trap and fixed. The
camera's height, between about 20 and 30 cm, and the module, one with a ribbon cable or one with a
screw-in M12 lens, are settled on the bench by depth of field and light: at f/2 the sharp zone
reaches about 3 cm above the floor at 20 cm and about 4.5 cm at 30 cm (estimates). Every picture is
lit by infrared LEDs flashed with the exposure, with fixed exposure settings, so pictures do not
depend on daylight and no visible light is used. The board takes 940 nm or 850 nm LEDs in the same
place; 940 nm is the default, and the bench decides. A pass gets a picture as soon as the camera is
ready, then one every half second while the animal is in the passage, at most six. If the bench
shows the camera wakes too slowly, it stays on standby instead. Entries 38, 44, 57, 58, 76 and 77.
Rejected: the OV2640 (two megapixels, weak in low light); autofocus (a delay on every picture, a
motor in the damp, unreliable in infrared light); white light (startles animals); one picture per
pass.

### A model on the camera controller types each pass
After the pictures of a pass are written, the ESP32-S3 runs the model with TensorFlow Lite Micro,
8-bit, on each stored picture shrunk to about 160 by 96 grey pixels (the bench may change the
size). Each picture gets a score for empty, frog or toad, lizard, snake and other animal. The pass
gets the surest animal type when any picture's animal score reaches a minimum, otherwise empty; its
score is how sure the model is. Type, score and model version go into the pass record; the model
deletes nothing, and the filter alone decides what is kept. The model is a file on the card,
`model/model.tflite` with its signed manifest, loaded at start; without one, or when it fails its
check or does not load, the type stays empty and the trap records as before. A separate chip for
models comes only with a later board revision, if a test shows the ESP32-S3 is not enough. Entries
74, 93, 96, 97, 99, 102, 106 and 117; [ADR](adr/image-models-on-the-camera-controller.md).
Rejected: ESP-DL (needs ESP-IDF); the model built into the firmware; the model dropping pictures; a
helper chip such as the MAX78000 or a vision chip such as the STM32N6.

### The first model is trained with Keras on free pictures
A Python project in `model/` downloads the drift-fence pictures from above that others published
(California, Ohio and Indiana Small Animals on LILA, and the Australian SAWIT set), maps their
labels onto the model types (newts, salamanders and turtles to other animal), turns them grey,
trains a small network with Keras, and exports it 8-bit for TensorFlow Lite Micro. It is then
fine-tuned on named bench pictures from `trapsort` seasons and checked on others kept apart from
training; it goes on the traps only once it meets its targets, set from the controlled tests. A
model card lists the sources and their licences, which ask for credit. The project signs a released
model with the release key, in the FieldHub's manifest format with the role `trap-model`. Entries
96, 100, 101 and 118; [ADR](adr/model-trained-with-keras.md).
Rejected: PyTorch converted for the trap (an extra step that can change the model); training only
on others' colour pictures (they barely show lizards and snakes in infrared).

### A mobile modem sends to FieldMesh once a day
The main board carries Auris's modem design: a Quectel EG810M-EU on a 3.9 V TPS63020 rail that is
switched off between sends, a nano-SIM holder, and an SMA socket for a cable to an antenna on the
solar panel's stake. A driver for the EG810M-EU is written for the trap; the FieldHub's upload rules
are reused above it. In FieldMesh the trap is a hub of its own with one node, itself, and its own
upload key. Right after the daily summary, the trap powers the modem, connects over HTTPS, checking
FieldMesh's certificate, and posts every unconfirmed reading in batches of at most 100: each pass as
a reading with trap keys, and the summary last, so the summary stays the newest reading. A batch
counts as confirmed only when FieldMesh's reply gives its full count; the position of the last
confirmed reading is kept on the card, so a failed or broken send is repeated at the next one.
Recording never waits for a send. A send gives up after `link_timeout_s` (180 s) and records a
link fault. Each reply sets the clock from FieldMesh's server time. How often to send is
`send_every_h` in `trap.cfg` (24). Entries 85, 86, 88, 89, 104, 105, 107, 110, 112, 113 and 114;
[ADR](adr/trap-sends-to-fieldmesh-as-a-hub.md).
Rejected: the SIMCom A7670G with the FieldHub's driver; a pass type in FieldMesh first; trying until
connected; no certificate check; an antenna inside the hood; a satellite link.

### Settings, firmware and models come back over the link
Commands arrive in the reply to an upload and are confirmed as the FieldHub confirms them. A trap
settings command is checked by the same rules as `trap.cfg`; valid settings are written to
`trap.cfg` and used, invalid ones refused, and the result goes with the next upload. Firmware
updates work as on the FieldHub: a manifest signed with the release key (Ed25519), the image
written to the spare app slot and checked by size and SHA-256, and the bootloader's fall-back when
the new firmware does not confirm itself after its first full wake. A model update downloads a
signed manifest and model file to the card and swaps it in only after the check passes. Only the
camera controller is updated; the beam watcher changes at a visit. Until FieldMesh has the settings
command and release roles for trap firmware and models (see Outside this repository), the trap sends
but takes nothing back, and a model reaches it on the card. Entries 87, 106, 108, 109, 111 and 115;
[ADR](adr/signed-updates-over-the-link.md).
Rejected: a settings file fetched from a web address; a new update scheme; the camera controller
reprogramming the watcher.

### Chips JLCPCB can assemble
Every chip on the trap's boards is one JLCPCB can assemble: from LCSC's stock where it has it,
otherwise ordered in through JLCPCB's global sourcing. Plug-in parts such as the camera module and
the cells may come from anywhere. Entries 72 and 73; [ADR](adr/chips-assembled-by-jlcpcb.md).
Rejected: LCSC's stock only (rules out most chips for image models; thin stock of some parts).

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
trap's configured UTC offset. The trap's coordinates are entered in `trap.cfg` when it is set up.
The sorting tool exports a season as a Camera Trap Data Package, placed at those coordinates;
without them the export stops and says so, while the trap itself runs on. Entries 48, 81 and 83;
[ADR](adr/records-as-csv-and-camtrap-dp.md).
Rejected: only the trap's own format; the coordinates in a file on the computer, or typed at each
export.

### The state summary is a FieldMesh reading
Once a day, after the empty-view picture, the camera controller appends one FieldMesh reading to the
state file: the contract's core fields, `latitude` and `longitude` from `trap.cfg` (null when not
set), and `trapKind` `state`, `trapPasses`, `trapFreeMB` and `trapViewClear`, which the FieldMesh
backend stores although it does not model them. The link sends it unchanged. Entries 60, 83 and 85;
[ADR](adr/state-summary-as-fieldmesh-reading.md).
Rejected: a FieldMesh node over ESP-NOW (needs a hub on every site); the aux1 and aux2 fields.

### Power
A 6 V solar panel of about 1 W on a short stake beside the trap charges two 18650 cells in parallel
(about 7 Ah) through the FieldHub's CN3791 charger design, with charging stopped below 0 °C by a
thermistor on the pack. The stake also carries the modem's antenna. The design plans for 200
passes a day, a daily send and a model run per pass; see the power estimate below. If the bench
measures more, the pack grows rather than features shrinking. Entries 42, 46, 52, 61, 77, 94 and
116.
Rejected: a 12 Ah pack without solar; lithium AA cells; a panel on the bucket top or a fence post;
one cell; three or four cells before the load is measured.

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
A Python package with a command line copies a card into a season folder, marks pictures that look
like their survey day's empty view, serves a local review page, and summarises, exports and
evaluates. The review page shows each pass with a picture not marked empty, its pictures side by
side; a person picks the broad group (frog, toad, newt, lizard, snake, turtle or other) and adds the
species name once for the pass, and can mark single pictures empty or "can't tell". For a pass
recorded outside pilot mode the page suggests the trap's model type; for one recorded in pilot mode
it hides it. No model runs on the computer; people's labels are kept so that the trap's model keeps
learning from them. The export gives people's labels, and a pass nobody sorted the model type,
marked as classified by machine. Entries 49, 67, 75, 78, 80, 82, 84, 98, 103, 121 and 122;
[ADR](adr/sorting-tool-in-python.md).
Rejected: a general labelling tool; a model on the computer; labelling each picture on its own
(about three times the clicks); the suggestion shown in the pilot.

### Outside this repository
The trap needs FieldMesh to have a command type for trap settings, release roles for trap firmware
(`trap`) and models (`trap-model`), and the trap keys modelled, so that passes reach its exports.
One FieldMesh issue collects them:
[armsto88/fieldMesh#99](https://github.com/armsto88/fieldMesh/issues/99). Entry 111.

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
| PIR sensor, ESP32-S3 asleep, clock, modem rail off | about 0.05 mA all the time |
| One pass: wake, up to six pictures with light, writing | about 0.12 mAh |
| The model on about three pictures per pass | about 0.01 mAh, 2 mAh a day |
| One daily send in good coverage (Auris budgets at most 180 J a day) | about 2 to 13 mAh |
| A day at 200 passes | about 35 to 45 mAh |
| Two 18650 cells, about 7 Ah | about 150 to 200 days without sun |
| Pictures: about 250 kB, on average three per pass | about 150 MB a day, 27 GB a season; a 128 GB card |
| Sent: about 300 bytes per pass reading | about 60 kB a day, 2 MB a month, plus updates |

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
  /// True while a pass is open.
  bool open() const;
};
```

#### Records, summary and configuration (camera library `records`)
Text for everything written to the card; no hardware calls.

```cpp
// firmware/camera/lib/records/records.h
enum class Placement : uint8_t { Line, End };   // in the fence line, or at a fence end

struct TrapConfig {
  char trap_id[16];                           // also the FieldMesh nodeId, e.g. ECT_0A1B2C
  int16_t utc_offset_min;                     // for survey days and the daily times
  bool pilot_mode;
  uint8_t empty_view_hour;                    // local hour of the daily picture and summary
  float drop_threshold;                       // filter: largest difference still "empty"
  float latitude, longitude;                  // decimal degrees from setup; NaN when not set
  Placement placement;                        // default Line
  char side_a[32];                            // side A in words, e.g. "pond side"; may be empty
  uint8_t send_every_h;                       // hours between sends, 1 to 168; default 24
  uint16_t link_timeout_s;                    // longest try per send, 30 to 600; default 180
  uint16_t config_version;                    // raised by each settings command taken
};

struct PassRecord {                           // one row of a survey day's pass file
  char pass_id[40];                           // <trap_id>-<survey day>-<number>
  uint32_t start_utc_s, end_utc_s;
  Pass pass;
  const char* pictures;                       // ';'-separated file names
  uint8_t dropped_empty;                      // pictures the filter dropped
  const char* judged_empty;                   // ';'-separated names marked in pilot mode
  bool pilot;                                 // the trap was in pilot mode
  ModelResult model;                          // type None when the trap has no model
  const char* model_version;                  // "" when the trap has no model
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

/// Writes c as trap.cfg text, which parse_config reads back to the same values.
size_t config_text(const TrapConfig& c, char* out, size_t size);

/// Survey day (noon to noon, local) of a UTC time, as "YYYY-MM-DD" of its first noon.
void survey_day(uint32_t utc_s, int16_t utc_offset_min, char out[11]);

/// CSV header of a survey day's pass file.
const char* pass_csv_header();

/// One pass record as a CSV line; pictures and judged-empty marks as ';'-separated names.
size_t pass_csv_line(const PassRecord& r, char* out, size_t size);

/// One fault as a CSV line for faults.csv.
size_t fault_csv_line(uint32_t utc_s, FaultKind kind, const char* detail, char* out, size_t size);

/// The day's state summary as one FieldMesh reading, JSON on one line, with the configured
/// latitude and longitude, or null for them when not set.
size_t summary_json(const StateSummary& s, const TrapConfig& c, char* out, size_t size);

/// One pass as a FieldMesh reading, JSON on one line, with flat trap keys and its own seqNum.
size_t pass_reading_json(const PassRecord& r, const TrapConfig& c, uint32_t seq, char* out,
                         size_t size);
```

#### Model types (camera library `typing`)
Turns the model's scores for a pass's pictures into the pass's type; no hardware calls.

```cpp
// firmware/camera/lib/typing/typing.h
enum class ModelType : uint8_t { None, Empty, FrogToad, Lizard, Snake, Other };  // None: no model

struct PictureScores { float empty, frog_toad, lizard, snake, other; };  // one picture, sum 1

struct ModelResult {
  ModelType type;
  float confidence;                           // 0 to 1; 0 for None
};

/// The surest animal type over the pictures if any animal score reaches min_animal, else Empty
/// with the highest empty score; None when n is 0.
ModelResult pass_type(const PictureScores* pictures, size_t n, float min_animal);

const char* model_type_name(ModelType t);     // "", "empty", "frog_or_toad", "lizard", ...
```

#### Sending (camera library `uplink`)
Upload bodies, the confirmed position and FieldMesh's replies; no hardware calls. Uses ArduinoJson.

```cpp
// firmware/camera/lib/uplink/uplink.h
struct SentPosition {                         // kept in state/sent.cfg on the card
  char pass_day[11];                          // survey day of the last confirmed pass file
  uint32_t pass_line;                         // last confirmed line in that file
  uint32_t summary_line;                      // last confirmed line in state/summaries.jsonl
  uint32_t next_seq;                          // seqNum for the next pass reading
};

class UploadBody {
 public:
  explicit UploadBody(size_t max_readings = 100);
  /// Adds one reading line; false when the body is full.
  bool add(const char* reading_json);
  /// The JSON body with readings, meta and status; status only on a session's first body.
  size_t write(const char* firmware_version, const char* status_json, char* out, size_t size);
  size_t count() const;
};

enum class ReplyAction : uint8_t { Confirm, ResendSmaller, Stop, RetryLater };

/// As the FieldHub: Confirm only on 200 with received == sent; 400 or 413 resend smaller;
/// 401 stop; 408, 429 and 5xx retry at the next send.
ReplyAction judge_reply(int http_status, uint32_t received, uint32_t sent);

struct Command { uint32_t cursor; char type[24]; const char* payload; };

struct Reply {
  uint32_t received;
  uint32_t server_time_unix;                  // 0 when absent
  Command commands[8];
  uint8_t n_commands;
};

/// Reads FieldMesh's reply body; false when it is not valid JSON.
bool parse_reply(const char* json, Reply* out);

enum class CommandResult : uint8_t { Accepted, Rejected };

/// Applies a trap settings command to a copy of c by the rules of parse_config.
CommandResult apply_settings(const char* payload, const TrapConfig& c, TrapConfig* out,
                             char* reason, size_t reason_size);

/// UTC time of the next send after the last one, every send_every_h hours.
uint32_t next_send(uint32_t last_send_utc_s, const TrapConfig& c);
```

#### Signed updates (camera library `updates`)
Checks manifests and files of firmware and model updates; no hardware calls. Follows the FieldHub's
`firmware_manifest.h` and uses rweather/Crypto for Ed25519 and SHA-256.

```cpp
// firmware/camera/lib/updates/updates.h
struct Manifest {
  char role[16];                              // "trap" for firmware, "trap-model" for models
  char version[16];
  uint32_t size;
  uint8_t sha256[32];
};

/// Reads manifest.json and checks its Ed25519 signature over the exact bytes against the
/// release key; false on a bad signature or a malformed manifest.
bool verify_manifest(const uint8_t* json, size_t n, const uint8_t signature[64],
                     const uint8_t release_key[32], Manifest* out);

/// Feeds a downloaded file in pieces and compares its size and SHA-256 with the manifest.
class FileCheck {
 public:
  explicit FileCheck(const Manifest& m);
  void update(const uint8_t* data, size_t n);
  bool matches();
};
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
Group = Literal["frog", "toad", "newt", "lizard", "snake", "turtle", "other"]
ModelType = Literal["empty", "frog_or_toad", "lizard", "snake", "other"]
def model_type_of(group: Group) -> ModelType:
    """The model type a person's group counts as: frog and toad as frog_or_toad; newt, turtle
    and other as other."""
@dataclass
class Picture:
    """One stored picture: file, pass_id, survey day and empty mark."""
@dataclass
class PassRecord:
    """One row of a pass file, with its pictures, whether it was recorded in pilot mode, and
    the model type, confidence and model version, None when the trap had no model."""
@dataclass
class Season:
    """Everything read from one card copy: passes, pictures, empty views, faults, summaries."""
@dataclass
class DayCount:
    """Passes in one survey day for one name or group and one direction."""

# sorting/trapsort/card.py
def read_card(card: Path) -> Season:
    """Reads pass records, pictures, faults and summaries from a card copy; raises CardError."""
def import_card(card: Path, season_dir: Path) -> Season:
    """Checks a card with read_card and copies it into season_dir/card; raises CardError, also
    when the season already holds a card."""
def read_season(season_dir: Path) -> Season:
    """Reads season_dir/card and, where present, the empty marks in sorting.csv."""
def write_sorting(season: Season, season_dir: Path) -> None:
    """Writes each picture's empty mark and difference to season_dir/sorting.csv."""

# sorting/trapsort/empty.py
def mark_empty(season: Season, threshold: float) -> None:
    """Marks pictures that differ from their survey day's empty view by less than threshold."""

# sorting/trapsort/labels.py
class LabelStore:
    """Names, groups, empty and can't-tell marks and bucket labels in a season's labels.csv;
    the latest label of each kind counts."""
    def __init__(self, path: Path) -> None: ...
    def set_name(self, picture: str, name: str, by: str) -> None: ...
    def set_group(self, picture: str, group: Group, by: str) -> None: ...
    def set_empty(self, picture: str, empty: bool, by: str) -> None: ...
    def set_unclear(self, picture: str, by: str) -> None: ...
    def add_bucket_label(self, pass_id: str, name: str, group: Group,
                         checked_at: datetime) -> None: ...
    def name(self, picture: str) -> str | None: ...
    def group(self, picture: str) -> Group | None: ...
    def empty(self, picture: str) -> bool | None: ...
    def unclear(self, picture: str) -> bool: ...
    def bucket_labels(self, pass_id: str) -> list[tuple[str, Group, datetime]]: ...

# sorting/trapsort/review.py
def serve_review(season: Season, labels: LabelStore, port: int = 8765) -> None:
    """Serves the local review page until stopped: each pass with a picture not marked empty,
    its pictures side by side; a group and name are saved for every picture of the pass at
    once, or picture by picture, and each mark is saved at once. A pass recorded outside pilot
    mode shows its model type as a suggestion; one recorded in pilot mode does not."""

# sorting/trapsort/summary.py
def passes_per_survey_day(season: Season, labels: LabelStore) -> list[DayCount]:
    """Passes per survey day by group or species and direction; never called animals."""

# sorting/trapsort/camtrapdp.py
def export_camtrap_dp(season: Season, labels: LabelStore, out: Path) -> None:
    """Writes datapackage.json, deployments.csv, media.csv and observations.csv, with the
    placement and side A in the deployment; people's labels as classified by a person, the
    model type of an unsorted pass as classified by machine; raises ExportError when the card's
    trap.cfg holds no coordinates."""

# sorting/trapsort/evaluate.py
@dataclass
class BenchPlan:
    """Rows of a bench run's plan.csv: what passed when, at which size, speed and light."""
@dataclass
class BucketChecks:
    """Rows of bucket_checks.csv: the animals found in the bucket at each check."""
@dataclass
class Report:
    """Shares noticed, with a usable picture and identified; missed animals; passes by sensing;
    model agreement in total and per model type, from passes sorted in pilot mode only.
    A pass has a usable picture when a person gave any of its pictures a group or a name, and is
    identified when that name matches the animal the reference names."""
def read_plan(path: Path) -> BenchPlan:
    """Reads plan.csv; raises PlanError on a malformed row."""
def read_bucket_checks(path: Path) -> BucketChecks:
    """Reads bucket_checks.csv; raises PlanError on a malformed row."""
def evaluate(season: Season, labels: LabelStore,
             reference: BenchPlan | BucketChecks) -> Report:
    """The three outcomes as shares of the animals the reference says passed, the missed
    animals, and the passes noticed by the lasers only, the PIR sensor only and both."""
```

#### The model project (`model/trapmodel`)
A Python package with TensorFlow and Keras, separate from `trapsort` so the sorting tool stays
light; it reads named bench pictures through `trapsort`.

```python
# model/trapmodel/data.py
def fetch_sources(out: Path) -> None:
    """Downloads the LILA and SAWIT pictures and labels used for training into out."""
def build_dataset(sources: Path, size: tuple[int, int]) -> Dataset:
    """Grey pictures at size with model types, mapped from each source's labels."""
def bench_dataset(seasons: list[Path], size: tuple[int, int]) -> Dataset:
    """Named bench pictures from trapsort seasons, with model_type_of their people's groups."""

# model/trapmodel/train.py
def train(data: Dataset, fine_tune: Dataset | None, out: Path) -> Path:
    """Trains, or fine-tunes on bench pictures, and writes a Keras model."""

# model/trapmodel/export.py
def export_int8(keras_model: Path, sample: Dataset, out: Path) -> Path:
    """Writes model.tflite, 8-bit for TensorFlow Lite Micro, and the model card."""

# model/trapmodel/check.py
def check(model_file: Path, held_out: Dataset) -> Agreement:
    """Agreement with people's types, in total and per model type."""

# model/trapmodel/sign.py
def sign_release(file: Path, version: str, key: Path, out: Path) -> None:
    """Writes manifest.json (role trap-model) and its Ed25519 signature with the release key."""
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
                               empty_view_hour, drop_threshold, latitude, longitude,
                               placement (line or end), side_a, send_every_h,
                               link_timeout_s, config_version
link.cfg                       first start only: apn, fieldmesh_url, fieldmesh_key; the
                               trap moves them into its own flash and empties the file
passes/2026-05-14.csv          one file per survey day (noon to noon, local)
pictures/2026-05-14/           <pass_id>_<n>.jpg, and empty_<HHMM>.jpg for the daily picture
faults.csv                     time_utc,fault,detail
state/summaries.jsonl          one FieldMesh reading per line, one line per day
state/sent.cfg                 the last confirmed pass and summary, and the next seqNum
model/model.tflite             the model in use, with manifest.json and manifest.sig
updates/                       downloads being checked; emptied after each update
```

Pass file columns, times in ISO 8601 UTC: `pass_id,start_utc,end_utc,direction,heights_a,`
`heights_b,noticed_by,pictures,dropped_empty,judged_empty,pilot,model_type,model_confidence,`
`model_version`, with `direction` one of `AtoB`, `BtoA`, `backA`, `backB`, `unknown`, `noticed_by`
one of `lasers`, `pir`, `both`, `pilot` `true` or `false`, `model_type` one of `empty`,
`frog_or_toad`, `lizard`, `snake`, `other` or empty without a model, and `pass_id` as
`<trap_id>-<survey day>-<number>`.

Fault kinds: `beam_blocked`, `beam_clear`, `battery_low`, `storage_low`, `camera_failed`.

A state summary line:
```json
{"datetime":"2026-05-14T10:00:00Z","nodeId":"ECT_0A1B2C","seqNum":12,"sensorPresent":0,
 "qualityFlags":0,"configVersion":1,"batVoltage":3.98,"airTemp":17.5,"latitude":49.4521,
 "longitude":7.7541,"trapPasses":143,"trapFreeMB":98112,"trapViewClear":true}
```
`airTemp` comes from the clock chip in the hood; `qualityFlags` bit 0 is set when the view is not
clear. The summary also carries `"trapKind":"state"`.

A pass as a reading, as the link sends it; `trapHeightsA` and `trapHeightsB` are the beam bits as
numbers, since FieldMesh refuses lists:
```json
{"datetime":"2026-05-14T21:13:05Z","nodeId":"ECT_0A1B2C","seqNum":1043,"sensorPresent":0,
 "qualityFlags":0,"configVersion":3,"batVoltage":null,"trapKind":"pass",
 "trapPassId":"ECT_0A1B2C-2026-05-14-17","trapDirection":"AtoB","trapHeightsA":1,
 "trapHeightsB":1,"trapNoticedBy":"lasers","trapPilot":false,"trapModelType":"lizard",
 "trapModelConf":0.87,"trapModelVersion":"m1.0.0","trapPictures":3}
```

An upload follows the FieldMesh upload contract: `readings`, `meta` with `firmwareVersion`, and on
a session's first body `status` with the hub keys that apply to a trap (`batVoltage`, `rtcUnix`,
`deviceId`, one entry in `nodes`, `upload`, `sdCard`, `control` with the command results, and
`firmware` with the model version). Fault kinds add `link_failed` and `update_failed`.

### A season on the computer
A season is a folder; every `trapsort` command except `import` takes it.
```
card/                          the card copy, as `trapsort import` copied it; never changed
sorting.csv                    the computer's empty marks, written again by each `trapsort sort`
labels.csv                     people's labels and bucket labels; only ever appended to
```

- `sorting.csv`: `picture,pass_id,survey_day,empty,difference`, one row per picture, with
  `difference` from the day's empty view.
- `labels.csv`: `picture,pass_id,kind,value,by,at`, where `kind` is `name`, `group`, `empty` (value
  `true` or `false`), `unclear` (a picture marked "can't tell"), `bucket` (a name) or
  `bucket_group`. Bucket rows name the pass and leave `picture` empty.
- `bucket_checks.csv`: `checked_at,trap_id,animal,name,group`, one row per animal found in the
  bucket during the field phase. An animal matches the earliest unmatched pass since the previous
  check whose pictures show its group; passes that went through come before turned-back ones.
- The Camtrap DP export: one deployment per trap season, placed at the coordinates in the card's
  `trap.cfg`; one media row per picture; one event-level observation per pass, with
  `observationType` `animal`, `blank` or `unclassified`, the group or name from the labels,
  `classificationMethod` `human`, and the direction in `observationComments`. A pass nobody sorted
  takes the model type with `classificationMethod` `machine`, `classifiedBy` the model version and
  `classificationProbability`. The deployment's `deploymentTags` carry `placement:line` or
  `placement:end` and `sideA:<words>`. A picture's time is the pass's start plus half a second per
  picture before it, noted as estimated in `mediaComments`.

### A bench run
`plan.csv`: `planned_at,model,body_length_mm,height_mm,speed_mm_s,temperature_c,light,direction`,
next to a copy of the trap's card from that run.

## Impact

### New
- `README.md`: what the trap is, how to build, set up and collect it
- `firmware/shared/include/link.h`
- `firmware/watcher/`: PlatformIO project for the ATtiny3216, with `lib/beams` and `test/`
- `firmware/camera/`: PlatformIO project for the ESP32-S3, with `lib/passes`, `lib/records`,
  `lib/filter`, `lib/typing`, `lib/uplink`, `lib/updates` and `test/`
- `model/`: the `trapmodel` package, its `pyproject.toml`, `tests/` and the model card
- `sorting/`: the `trapsort` package, its `pyproject.toml` and `tests/`
- `bench/rig/`: the model-animal rig (a belt pulling model animals along the floor at set speeds)
- `bench/checks/`: pytest checks on bench runs
- `hardware/insert/`: the FreeCAD script and generated STL files
- `hardware/boards/`: EasyEDA exports of the watcher and beam boards and the main board, with the
  modem
- `docs/testing/`: written check procedures, the controlled-test plan and the field-phase procedure

### Modified
- `.gitignore`: PlatformIO and Python build output

### Renamed
- `code.ino` → `prototype/code.ino`
- `README.md` → `prototype/README.md`
- `Dev-BLOG.md` → `prototype/Dev-BLOG.md`
