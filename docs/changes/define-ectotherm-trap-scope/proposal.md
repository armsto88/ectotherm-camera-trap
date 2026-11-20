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
is kept only as a test bench.

## What changes
- The trap is a short passage set into the line of a drift fence. Animals cross the fence through it
  instead of falling into a bucket, so they are neither caught nor handled.
- It notices every pass with lasers across the passage at two points, each with beams at two or
  three heights, and does not rely on body heat. As in ordinary camera traps, a PIR sensor can also
  start the camera. Whether a laser looking down from the roof is added is decided by a bench test.
- It notices animals from about 3 cm body length without tail, by day and by night, and records the
  time and direction of each pass.
- It photographs each pass the same way every time, from above and lit by its own infrared light by
  day and by night, sharp enough to identify the animal to species wherever an expert could do so
  from a photo, and otherwise to the nearest group. Whether a side view is added, and whether colour
  is added by daylight let in through the top or by a short white light as the animal leaves, is
  decided in the controlled tests. Once a day it also photographs its empty view, so a dirty lens or
  a blocked passage shows up in the records.
- It replaces the bucket for species lists, presence of a species, times of activity, and relative
  numbers: passes per fence per night, an index rather than a population size. Buckets stay for
  studies of population size, sex ratio or condition.
- A simple filter on the trap drops obviously empty pictures. After collection, an image-recognition
  model removes empty pictures and sorts the rest into broad groups; people name the species and
  check the sorting. Small mammals and large invertebrates are recorded, but the trap is not
  designed for them.
- The trap runs a whole season, three to six months, without a visit. It works without any
  connection; where coverage exists, an add-on sends a daily message with battery, storage, number
  of passes, and whether its view is clear.
- Results report three things separately: whether the trigger fired, whether a usable picture was
  taken, and whether the animal was identified. Missed animals are counted in two stages: controlled
  tests with model animals and known animals, then a short field phase with a bucket behind the trap
  at a few fences. The filter deletes nothing in either stage. The targets for "the trap works" are
  set from the controlled tests and fixed before the field phase.
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
- pass-records: what each pass leaves behind (time, direction, pictures, which sensing noticed it)
  and the relative numbers drawn from them.
- picture-sorting: the filter on the trap, the model that sorts the pictures afterwards, and people
  naming the species.
- unattended-season: running a whole season without a visit, with optional daily state messages.
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
- Does the infrared light change the animals' behaviour? (entries 19 and 38)
- Can a season without visits be powered with the trap's own lighting, two kinds of sensing and a
  filter on the trap, at a cost consultants will pay? (entries 4, 19, 23, 25, 33 and 38)
- Do the pictures from above reach the identification level of entry 18 for the main groups of
  animals, or is a side view needed? (entries 18 and 37)
- Is colour needed to tell species apart? If so, does daylight let in through the top make the
  passage too warm or keep basking animals inside, and does a short white light make animals turn
  back or hurry? (entry 38)
- Will people's labels and the bucket phase give enough labelled pictures to train the sorting
  model? (entry 22)
- What are the targets for "the trap works"? Set after the controlled tests. (entry 36)

## Out of scope
- A funding application; it becomes its own piece of work if funding is sought (entry 32).
- Studies of population size, sex ratio or condition; buckets stay for these (entry 16).
- Juveniles below about 3 cm, such as frogs and toads just out of the water (entry 24).
- Small mammals and invertebrates as design targets (entry 26).
- Species-level recognition by the model; a later change, once enough labelled pictures exist (entry
  22).
- Parts, code and housing; they follow in the design step (propose) and the build (implement) (entry
  7).

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
- [Wild Animal Initiative grants, for when funding is
  sought](https://www.wildanimalinitiative.org/grants)
- The earlier prototype: `README.md`, `Dev-BLOG.md` and `code.ino` in this repository.
