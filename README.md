# Ectotherm camera trap

A camera trap for small reptiles and amphibians that replaces the pitfall bucket in drift-fence
surveys. Animals that follow the fence cross it through a short passage instead of falling into a
bucket. Infrared laser beams notice every pass, whatever the animal's temperature, and a camera
photographs it from above under its own infrared light, by day and by night. A small model on the
trap labels each pass with a type of animal. The trap runs a season of three to six months without
a visit and keeps its records on a memory card; once a day it sends its pass records and a short
state summary to FieldMesh over the mobile network, never its pictures. After collection, a sorting
tool marks empty pictures, and people sort the rest into broad groups and name the species.

The aim is animal welfare: fewer wild animals caught and handled in routine surveys.

## Status
In development; there is no trap to build yet. What the trap must do is set out in
[`docs/specs/`](docs/specs/index.md) and its lasting design decisions in
[`docs/adr/`](docs/adr/index.md); work in progress, with its design and tasks, is in
[`docs/changes/`](docs/changes/).

## How it works
- **Passage:** an upturned bucket of about 30 cm diameter with a 3D-printed insert that carries a
  passage 15 cm wide across it. Its floor is flush with the ground, and the fence ends meet openings
  in the bucket's sides. The trap sits in the fence line or at a fence end (see Setting up a trap).
- **Noticing passes:** a beam point near each end of the passage, with beams at 4, 12 and 25 mm
  above the floor. The lasers are pulsed and the light is compared with and without them, so
  daylight cancels out. A PIR sensor is an extra trigger for warm animals. The order in which an
  animal crosses the beam points gives the direction of its pass.
- **Pictures:** an OV5640 camera without infrared filter, lit by 940 nm LEDs, takes up to six
  pictures per pass, and once a day a picture of the empty passage.
- **Electronics:** an ATtiny3216 watches the beams all the time and wakes an ESP32-S3, which takes
  the pictures and writes the records. A Quectel EG810M-EU modem, switched off between sends,
  connects the trap to the mobile network.
- **Model:** after each pass the ESP32-S3 runs a small image model that labels the pass as frog or
  toad, lizard, snake, other animal or empty, with how sure it is. It only labels and deletes
  nothing; without a model the trap records as before.
- **Power:** a small solar panel on a stake beside the trap, which also carries the modem's
  antenna, and two 18650 cells.
- **Records:** one CSV file of passes per survey day (noon to noon), the pictures, a fault log, and
  a daily state summary in the reading format of FieldMesh. The card is the full record; without
  coverage the trap works on and sends what is waiting at the next send that gets through.

## Setting up a trap
The same trap serves two placements; the survey chooses. In both, the passage crosses the line of
the fence, so an animal following the fence on one side can walk through to the other side.

```
  In the fence line                      At a fence end

          side A                                 side A
            │                                      │
  ══════════◯══════════                  ══════════◯════
            │                                      │
          side B                                 side B

  ═ fence   ◯ trap   │ the passage, from side A to side B
```

- **In the fence line:** the fence runs on both sides of the trap and meets it on two opposite
  sides of the bucket.
- **At a fence end:** the trap sits the same way, with a short piece of fence, about a bucket's
  width, beyond it. Animals on either side of the fence are still led to an opening of the passage,
  and side A and side B keep their meaning.

**Side A.** Side A is one side of the fence, chosen by the surveyor when the trap is set up and
described in `trap.cfg` in words someone at the fence would recognise, such as "pond side". The
end of the passage marked A faces it. A pass from side A to side B is recorded as `AtoB`, so the
records can only be read with side A known.

**Settings.** The trap reads `trap.cfg` on its memory card, one `key=value` per line; lines
starting with `#` are comments, and keys left out keep their defaults. For a trap at a fence end
whose side A faces a pond:

```
trap_id=ECT_0A1B2C
utc_offset_min=60
placement=end
side_a=pond side
latitude=49.4521
longitude=7.7541
pilot_mode=true
send_every_h=24
```

| Key | Meaning | Default |
|---|---|---|
| `trap_id` | the trap's name, also its node in FieldMesh | `ECT_UNSET`; set it |
| `utc_offset_min` | local time minus UTC in minutes, for survey days and daily times | `0` |
| `placement` | `line` in the fence line, `end` at a fence end | `line` |
| `side_a` | side A in words, up to 31 characters | empty |
| `latitude`, `longitude` | where the trap stands, in decimal degrees; needed for the export | not set |
| `pilot_mode` | `true` marks pictures the filter judges empty instead of dropping them, and hides the model's type while people sort | `true` |
| `empty_view_hour` | local hour of the daily empty-view picture and summary | `12` |
| `drop_threshold` | the filter's largest difference from the empty view still counted as empty | `0.03` |
| `send_every_h` | hours between sends, 1 to 168 | `24` |
| `link_timeout_s` | longest try per send in seconds, 30 to 600 | `180` |
| `config_version` | raised by the trap each time it takes new settings from FieldMesh; leave it | `0` |

Settings sent from FieldMesh are checked by the same rules and written back to `trap.cfg`.

**The link.** Each trap is registered in FieldMesh as a hub of its own, with its own upload key.
Before its first start, put a nano-SIM in the trap and a `link.cfg` on the card with the mobile
network's access point name and the upload address and connection key FieldMesh gave when the
trap was registered:

```
apn=<access point name of the SIM's network>
fieldmesh_url=<upload address>
fieldmesh_key=fm_<connection key>
```

At its first start the trap moves these into its own memory and empties the file, so a lost card
does not give away the upload key.

## Folders
Folders are added as the trap is built.

| Folder | Contents |
|---|---|
| `firmware/` | PlatformIO projects: `watcher/` for the ATtiny3216 beam watcher, `camera/` for the ESP32-S3 camera controller, and `shared/` for the link between them |
| `model/` | `trapmodel`, the Python project that trains the trap's image model on published pictures and bench pictures, exports it for the trap and signs a release |
| `sorting/` | `trapsort`, the Python tool that reads a copy of the card, sorts the pictures, serves the review page for naming species, and summarises, exports and evaluates a season |
| `bench/` | the model-animal rig and the checks run on its records |
| `hardware/` | the FreeCAD script for the bucket insert and the EasyEDA boards |
| `docs/testing/` | written check procedures, the controlled-test plan and the field-phase procedure |
| [`prototype/`](prototype/) | the earlier prototype, kept as a test bench |

## The earlier prototype
The first version used an ESP32 board, an OV2640 camera and a VL53L0X laser distance sensor. Its
code, description and development blog are in [`prototype/`](prototype/).
