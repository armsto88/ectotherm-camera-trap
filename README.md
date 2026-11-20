# Ectotherm camera trap

A camera trap for small reptiles and amphibians that replaces the pitfall bucket in drift-fence
surveys. Animals that follow the fence cross it through a short passage instead of falling into a
bucket. Infrared laser beams notice every pass, whatever the animal's temperature, and a camera
photographs it from above under its own infrared light, by day and by night. The trap runs a season
of three to six months without a visit and keeps its records on a memory card. After collection, a
sorting tool removes empty pictures and sorts the rest into broad groups, and people name the
species.

The aim is animal welfare: fewer wild animals caught and handled in routine surveys.

## Status
In development; there is no trap to build yet. What the trap must do is set out in
[`docs/specs/`](docs/specs/index.md) and its lasting design decisions in
[`docs/adr/`](docs/adr/index.md); work in progress, with its design and tasks, is in
[`docs/changes/`](docs/changes/).

## How it works
- **Passage:** an upturned bucket of about 30 cm diameter with a 3D-printed insert that carries a
  passage 15 cm wide across it. Its floor is flush with the ground, and the fence ends meet openings
  in the bucket's sides.
- **Noticing passes:** a beam point near each end of the passage, with beams at 4, 12 and 25 mm
  above the floor. The lasers are pulsed and the light is compared with and without them, so
  daylight cancels out. A PIR sensor is an extra trigger for warm animals. The order in which an
  animal crosses the beam points gives the direction of its pass.
- **Pictures:** an OV5640 camera without infrared filter, lit by 940 nm LEDs, takes up to six
  pictures per pass, and once a day a picture of the empty passage.
- **Electronics:** an ATtiny3216 watches the beams all the time and wakes an ESP32-S3, which takes
  the pictures and writes the records.
- **Power:** a small solar panel on a stake beside the trap, and two 18650 cells.
- **Records:** one CSV file of passes per survey day (noon to noon), the pictures, a fault log, and
  a daily state summary in the reading format of FieldMesh.

## Folders
Folders are added as the trap is built.

| Folder | Contents |
|---|---|
| `firmware/` | PlatformIO projects: `watcher/` for the ATtiny3216 beam watcher, `camera/` for the ESP32-S3 camera controller, and `shared/` for the link between them |
| `sorting/` | `trapsort`, the Python tool that reads a copy of the card, sorts the pictures, serves the review page for naming species, and summarises, exports and evaluates a season |
| `bench/` | the model-animal rig and the checks run on its records |
| `hardware/` | the FreeCAD script for the bucket insert and the EasyEDA boards |
| `docs/testing/` | written check procedures, the controlled-test plan and the field-phase procedure |
| [`prototype/`](prototype/) | the earlier prototype, kept as a test bench |

## The earlier prototype
The first version used an ESP32 board, an OV2640 camera and a VL53L0X laser distance sensor. Its
code, description and development blog are in [`prototype/`](prototype/).
