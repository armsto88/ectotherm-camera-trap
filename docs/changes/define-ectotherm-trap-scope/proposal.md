# Define a passage camera trap that replaces drift-fence buckets

## Context and driving forces
Drift-fence surveys of small reptiles and amphibians lead animals along a low fence into buckets dug
in at ground level, which must be checked at least daily. Every animal is caught and handled, and
some come to harm in the buckets. Ordinary camera traps could avoid the catching, but they notice
animals by body heat, which often fails for cold-blooded animals, and pictures taken from above at
fence ends are often too blurred to tell similar small species apart.

Others have shown parts of an answer: a light-beam trigger for small animals in tunnels and along
fences (HALT, 2017, also covered by a US patent), a laser trigger over reptile paths (RepTrap,
2024), ordinary game cameras at fence ends (AHDriFT), and a cork tile that gives heat sensors the
contrast they need. None of them replaces the bucket in routine surveys: a trap that notices
cold-blooded animals whatever their temperature, takes pictures good enough to identify them, and
runs a season unattended.

This change defines that trap and what it must achieve, so that its design can follow. Its reason is
animal welfare: fewer wild animals caught and handled in surveys. It is meant for drift fences
anywhere, and for the ecological consultants and agency staff who run routine surveys. No funding
application is part of it. The earlier prototype (ESP32 board, OV2640 camera, VL53L0X laser sensor)
is kept only as a test bench. The first priority is a trap that works on its own as a
laser-triggered camera trap; a learned image model comes later.

## What changes
- The trap is a short passage set into the line of a drift fence. Animals cross the fence through it
  instead of falling into a bucket, so they are neither caught nor handled.
- It notices every pass with lasers across the passage at two points, each with beams at two or
  three heights, and does not rely on body heat. As in ordinary camera traps, a PIR sensor can also
  start the camera. Whether a laser looking down from the roof is added is decided by a bench test.
- It notices animals from about 3 cm body length without tail, by day and by night, and records the
  time and direction of each pass.
- It photographs each pass the same way every time, from above, with a fixed-focus camera and its
  own infrared light by day and by night, sharp enough to identify the animal to species wherever an
  expert could do so from a photo, and otherwise to the nearest group. The light is 940 nm infrared
  unless the bench shows that 850 nm gives better pictures without disturbing the animals. Whether a
  side view is added, and whether colour is added by daylight let in through the top or by a short
  white light as the animal leaves, is decided in the controlled tests. Once a day it also
  photographs its empty view, so a dirty lens or a blocked passage shows up in the records.
- It replaces the bucket for species lists, presence of a species, times of activity, and relative
  numbers: passes per fence per night, an index rather than a population size. Buckets stay for
  studies of population size, sex ratio or condition.
- A simple filter on the trap drops obviously empty pictures. After collection, the computer marks
  pictures that look like the day's empty view, and people sort the rest into broad groups (frog,
  toad, newt, lizard, snake, turtle, other), adding the species name where the picture allows. Their
  names are kept as labels from which a model can learn later. Small mammals and large invertebrates
  are recorded, but the trap is not designed for them, nor for large turtles.
- The trap has no learned image model in this version, but its own camera chip can run a small one
  after each pass, so a later model that sorts pictures by type of animal needs no new hardware.
- The trap runs a whole season, three to six months, without a visit, and needs no connection. Once
  a day it writes a short state summary to its memory card: battery, free storage, passes since the
  last summary, and whether its view is clear, in the format FieldMesh takes. Its coordinates are
  entered in its settings on the card when it is set up, so its records carry their place.
- Every chip on the trap's boards is one that JLCPCB can assemble, from LCSC's stock where it has
  it; plug-in parts such as the camera module may come from anywhere.
- Results report three things separately: whether the trigger fired, whether a usable picture was
  taken, and whether the animal was identified. A picture is usable when a person sorting it could
  give it a group or a name. Missed animals are counted in two stages: controlled tests with model
  animals and known animals, then a short field phase with a bucket behind the trap at a few fences.
  The filter deletes nothing in either stage. The targets for "the trap works" are set from the
  controlled tests and fixed before the field phase.
- Field tests run where the project team is based and, with a partner, elsewhere, to cover different
  animals, climates and fence types.

## Capabilities
New:
- fence-passage: the trap as a passage set into a drift fence, through which animals cross without
  being caught.
- pass-detection: noticing every pass of an animal from about 3 cm, by day and by night, without
  relying on body heat, and the direction of the pass.
- pass-pictures: identifiable pictures of each pass, taken the same way every time, and a daily
  picture of the empty view.
- pass-records: what each pass leaves behind (time, direction, pictures, which sensing noticed it),
  the relative numbers drawn from them, and the trap's place they carry.
- picture-sorting: the filter on the trap, marking empty pictures after collection, and people
  sorting the pictures into groups and naming the species.
- unattended-season: running a whole season without a visit, with a daily state summary on the
  memory card.
- trap-evaluation: how trigger, picture and identification success are measured, how missed animals
  are counted, and when the targets are set.

## Open questions
- Patents: does the US patent 10,258,029 "Drift fence camera trap" (Hobbs) cover this trap, and does
  it have counterparts in Europe or Australia? (entry 11)
- Roof laser: does it earn its power as a backup for blocked beams? Decided by a bench test. (entry
  35)
- Does a PIR sensor work a few centimetres from animals in a narrow passage, and how many false
  triggers does it add? (entry 33)
- Do lasers at two or three heights notice flat 3 cm animals reliably, and how often do insects,
  rain and debris set them off? (entries 24 and 34)
- Do animals enter the passage readily, or do its shape and floor make some species turn back?
  (entry 27)
- Does the infrared light change the animals' behaviour, and do they notice the faint glow of
  850 nm? (entries 19, 38 and 77)
- How high must the camera sit for the tallest target animals to stay sharp, and do fast animals
  come out slanted in pictures read line by line? (entry 76)
- Can a season without visits be powered with the trap's own lighting, two kinds of sensing and a
  filter on the trap, at a cost consultants will pay? (entries 4, 19, 23, 25, 33 and 38)
- Do the pictures from above reach the identification level of entry 18 for the main groups of
  animals, or is a side view needed? (entries 18 and 37)
- Is colour needed to tell species apart? If so, does daylight let in through the top make the
  passage too warm or keep basking animals inside, and does a short white light make animals turn
  back or hurry? (entry 38)
- Will people's labels and the bucket phase give enough labelled pictures to train a later model?
  (entry 75)
- What are the targets for "the trap works"? Set after the controlled tests. (entry 36)

## Out of scope
- A funding application; it becomes its own piece of work if funding is sought (entry 32).
- Studies of population size, sex ratio or condition; buckets stay for these (entry 16).
- Juveniles below about 3 cm, such as frogs and toads just out of the water (entry 24).
- Small mammals, invertebrates and large turtles as design targets (entries 26 and 78).
- Learned image models, on a computer or on the trap, and a FieldMesh interface to validate data,
  train models and upload them to devices; a later change,
  [armsto88/fieldMesh#97](https://github.com/armsto88/fieldMesh/issues/97) (entry 75).
- A separate chip for image models; only with a later board revision, if a test shows the trap's
  camera chip is not enough (entry 74).
- Parts, code and housing; they follow in the design step (propose) and the build (implement) (entry
  7).
- Feeding FieldMesh from the trap on its own, with its own uplink and no hub on the site; a later
  change, [issue #1](https://github.com/armsto88/ectotherm-camera-trap/issues/1) (entry 51).

## References
- [Hobbs & Brehme 2017, An improved camera trap for amphibians, reptiles, small mammals, and large
  invertebrates](https://pmc.ncbi.nlm.nih.gov/articles/PMC5628828/)
- [US patent 10,258,029, Drift fence camera trap](https://patents.google.com/patent/US10258029)
- [RepTrap, a laser trigger for reptile camera traps (Hackaday,
  2024)](https://hackaday.com/2024/05/07/reptrap-keeps-watch-over-our-cold-blooded-friends/)
- [Corva et al. 2022, A Smart Camera Trap for Detection of Endotherms and
  Ectotherms](https://pmc.ncbi.nlm.nih.gov/articles/PMC9185543/)
- [Welbourne et al. 2019, Improving Terrestrial Squamate Surveys with Camera-Trap Programming and
  Hardware Modifications](https://www.mdpi.com/2076-2615/9/6/388)
- [Martin et al. 2017, Set AHDriFT: Applying game cameras to drift fences for surveying herpetofauna
  and small mammals](https://doaj.org/article/91291eb4599b4834a9e831fceb8eb0aa)
- [Jarvis et al. 2019, amphibian road tunnels monitored with time-lapse cameras
(Froglife)](https://www.froglife.org/wp-content/uploads/2019/03/Jarvis2019_Article_RoadMitigationUsingTunnelsAndF-002.pdf)
- [Amphibian survey with fences and buckets,
  Rhineland-Palatinate](https://www.zobodat.at/pdf/Fauna-Flora-Rheinland-Pfalz_11_0191-0205.pdf)
- [Sand lizard relocations with fences and buckets,
  Berlin](https://www.lacerta.de/AF/Bibliografie/BIB_18247.pdf)
- [Gardiner et al. 2024, ultra-light image models as on-device triggers for insect camera traps,
  run on an ESP32-S3](https://arxiv.org/html/2411.14467v2)
- [Islam et al. 2023, sorting snakes, lizards and toads in camera-trap
  pictures](https://www.mdpi.com/2076-2615/13/9/1526)
- [Wild Animal Initiative grants, for when funding is
  sought](https://www.wildanimalinitiative.org/grants)
- The earlier prototype: `prototype/README.md`, `prototype/Dev-BLOG.md` and `prototype/code.ino` in
  this repository.
