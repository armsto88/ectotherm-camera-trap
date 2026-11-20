# Decisions

## 1. What is the project mainly for?
- **Date:** 2026-11-20
- **Step:** discuss
- **Decision:** The project solves one named monitoring problem where today's methods fail; the
  device serves that job.
- **Reason:** Earlier work already shows the general idea of a non-heat trigger for small
  cold-blooded animals (the light-beam trigger HALT, 2017; the laser trigger project RepTrap, 2024),
  so a general-purpose device would be a small step. A named job makes success measurable, suits
  conservation funders, and turns a narrow sensor into a strength where animals are funnelled past a
  fixed point.
- **Rejected:** An open, low-cost, stand-alone trap as the main result (looks like a small step
  beyond HALT; little ecological benefit for funders); a methods study comparing kinds of trigger
  (needs a large field design; the device gets little development); units cheap enough to deploy at
  large scale (failing units lose more data than they gain).

## 2. Where will the first units be used?
- **Date:** 2026-11-20
- **Step:** discuss
- **Decision:** In Europe and Australia from the start: design and field tests cover both regions in
  parallel.
- **Reason:** Chosen on the round 1 page, without a note. The accepted cost: species, climates,
  permits and partners double before the basic idea is proven.
- **Rejected:** Europe first; Australia first (both would leave one region for later; no further
  reason given).

## 3. How far along is the funding?
- **Date:** 2026-11-20
- **Step:** discuss
- **Decision:** No funder yet. The project is shaped first; a matching funder is looked for
  afterwards.
- **Reason:** Chosen on the round 1 page, without a note. The accepted risk: the shaped project may
  fit no open programme and need reshaping.
- **Rejected:** Shortlisting two or three candidate funders now (takes research time before the
  project is shaped); working to a known funder (none is in view).

## 4. Who should eventually be able to use the trap without help?
- **Date:** 2026-11-20
- **Step:** discuss
- **Decision:** Ecological consultants and agency staff: field ecologists without electronics skills
  who do routine surveys and monitoring duties. The first pilot is run by the project team.
- **Reason:** Routine survey work is where a reliable, affordable trap would be used most, and
  designing for these users keeps robustness and data quality honest. The accepted cost: sturdy
  housing, simple setup and clear manuals, so more development effort.
- **Rejected:** The project team and researchers only (limits later use; results may depend on
  expert handling); volunteers (highest demands on simplicity and on checking data; placement
  quality varies).

## 5. What becomes of the current prototype?
- **Date:** 2026-11-20
- **Step:** discuss
- **Decision:** The current prototype (ESP32 board, OV2640 camera, VL53L0X laser distance sensor) is
  a test bench and history, not a design to keep.
- **Reason:** Set in the project handover and confirmed on the round 1 page: the design must follow
  from the monitoring problem, not from the parts at hand.
- **Rejected:** Developing the existing prototype further step by step (would fix early choices
  before the problem is defined).

## 6. How are results counted?
- **Date:** 2026-11-20
- **Step:** discuss
- **Decision:** Results report three outcomes separately: whether the trigger fired, whether a
  usable image was taken, and whether the animal was detected and identified. More images do not
  count as better detection.
- **Reason:** Set in the project handover and confirmed on the round 1 page: the three outcomes fail
  for different reasons, and mixing them overstates performance. The accepted cost: counting missed
  animals needs a second, independent method in the field.
- **Rejected:** Judging the trap by the number of triggers or images (says nothing about animals
  missed or identified).

## 7. When are components chosen?
- **Date:** 2026-11-20
- **Step:** discuss
- **Decision:** No components, parts list or code until the purpose, target animals and placement
  are settled.
- **Reason:** Set in the project handover and confirmed on the round 1 page. The accepted cost: some
  questions, such as battery life or focus distance, wait although quick bench tests could answer
  them.
- **Rejected:** Building and testing in parallel with the discussion (would anchor the design on
  parts chosen before the requirements).

## 8. Does the proposal claim a non-heat trigger as new?
- **Date:** 2026-11-20
- **Step:** discuss
- **Decision:** No. The proposal cites the 2017 light-beam trigger (HALT, Hobbs & Brehme) and the
  2024 laser trigger project (RepTrap) and states what this project adds.
- **Reason:** Both are easy to find; a reviewer who knows them would reject a novelty claim.
- **Rejected:** Claiming novelty for using a laser distance sensor (RepTrap already uses one as a
  trigger).

## 9. Which monitoring job should the project solve?
- **Date:** 2026-11-20
- **Step:** discuss
- **Decision:** Drift-fence surveys: a camera at the fence end records small ground reptiles and
  amphibians in place of daily trap checks.
- **Reason:** Chosen on the round 2 page, without a note. The accepted weaknesses: ordinary game
  cameras already do this job (AHDriFT, the cork-tile method), and drift-fence surveys are rare in
  Europe.
- **Rejected:** Crossing structures such as amphibian tunnels and culverts (time-lapse cameras
  already work there; tunnels are dark and wet); refuges and burrows (animals rest in place, so a
  presence trigger fires all the time; seeing under a board is hard; often tied to one species); a
  different job per region (splits the effort, against the single named job of entry 1).

## 10. Who runs the field tests in each region?
- **Date:** 2026-11-20
- **Step:** discuss
- **Decision:** The project team runs the field tests in the region it is based in; a partner (a
  consultancy, agency or university) runs them in the other region. No partner is named yet.
- **Reason:** Keeps one region close for fast fixes, while a local partner brings sites, permits and
  species knowledge, and tests the trap with the kind of user named in entry 4. The accepted cost:
  it depends on finding a partner, and there is less control over placement and servicing in that
  region.
- **Rejected:** The project team in both regions (travel cost and long gaps between visits, so
  faults go unnoticed for weeks); partners in both regions (the developers see little of the field;
  slow feedback on faults and design flaws).

## 11. Are patents checked before design?
- **Date:** 2026-11-20
- **Step:** discuss
- **Decision:** The proposal lists a patent check as an open question: the US patent "Drift fence
  camera trap" (10,258,029) and any similar patents in Europe and Australia.
- **Reason:** Its claims are unread and patents only apply where they are granted; checking before
  design avoids building into a blocked corner.
- **Rejected:** Leaving patents until a design exists (a blocking claim found late would cost the
  design work done until then).

## 12. Is the trap tied to a region?
- **Date:** 2026-11-20
- **Step:** discuss
- **Decision:** No. The trap is designed for drift fences wherever they are used.
- **Reason:** Settled in the chat and confirmed on the round 4 page: the problem, catching
  cold-blooded animals in buckets, is the same wherever drift fences are used. The accepted cost:
  "works anywhere" can only be backed by tests across a range of animal sizes, speeds, climates and
  fence types.
- **Rejected:** Europe and Australia in parallel from the start (ties the design to two regions'
  animals instead of to the drift-fence method).
- **Replaces:** 2 (Europe and Australia from the start becomes no fixed region).

## 13. What must the trap do?
- **Date:** 2026-11-20
- **Step:** discuss
- **Decision:** The trap sits in line with a drift fence and replaces the bucket, so animals pass
  without being caught or handled. It must detect cold-blooded animals reliably and take pictures
  good enough for a person or an image-recognition model to classify.
- **Reason:** Settled in the chat and confirmed on the round 4 page: the problem is two-fold.
  Heat-sensing triggers miss cold-blooded animals, and buckets mean catching and handling every
  animal. The accepted weaknesses: pictures cannot give everything a bucket gives (entry 16), and a
  triggered camera at a fence-line threshold is close to what the Hobbs US patent describes (entry
  11).
- **Rejected:** A camera that only adds to the bucket (keeps the handling); detecting more animals
  without identifiable pictures (gives no species records); better pictures without a reliable
  trigger (still misses cold-blooded animals).

## 14. Who is the candidate funder?
- **Date:** 2026-11-20
- **Step:** discuss
- **Decision:** An animal-ethics funding body; the project is argued as reducing and refining the
  catching of wild animals in surveys. No specific body is named yet.
- **Reason:** Settled in the chat and confirmed on the round 4 page. The accepted risk: the body's
  rules, amount and duration are not known yet, and some animal-ethics programmes focus on
  laboratory animals rather than wildlife field work.
- **Rejected:** Shaping the project with no funder in view (entry 3; the funder's focus on animal
  welfare shapes how the project is argued).
- **Replaces:** 3 (no funder in view becomes an animal-ethics funder as the candidate).

## 15. How are missed animals counted?
- **Date:** 2026-11-20
- **Step:** discuss
- **Decision:** In two stages: first controlled tests with model animals and known animals, with no
  wild animals handled; then a short, time-limited field phase with a bucket behind the trap at a
  few fences, where each animal in the bucket without a matching picture counts as missed.
- **Reason:** Settled in the chat and confirmed on the round 4 page. Entry 6 needs an independent
  count of the animals that really passed, and a project argued on animal welfare must keep handling
  small: the limited, time-bound handling in the field phase is what earns the case that later
  surveys need none. The accepted cost: the field phase still handles wild animals and needs
  permits, and animals that turn back before the bucket are not counted.
- **Rejected:** Time-lapse as the reference (misses fast animals and has its own blind spots);
  controlled tests only (never shows what the trap misses with free-moving animals).

## 16. For which survey purposes does the trap replace the bucket?
- **Date:** 2026-11-20
- **Step:** discuss
- **Decision:** Species lists, presence of a species, when animals are active, and relative numbers:
  passes per fence per night as a measure of how common a species is. Buckets stay for studies of
  population size, sex ratio or condition.
- **Reason:** Chosen on the round 4 page, without a note. The accepted weakness: one animal passing
  several times counts several times, so pass counts are an index, not population sizes.
- **Rejected:** Species lists, presence and activity only (no reason given); everything buckets do,
  including size, sex and individual patterns (the largest claim and the hardest to prove; works
  only for species with visible patterns and sex marks).

## 17. Who classifies the pictures first?
- **Date:** 2026-11-20
- **Step:** discuss
- **Decision:** An image-recognition model sorts the pictures from the start; people check its
  results.
- **Reason:** Chosen on the round 4 page, without a note. The accepted weaknesses: a trained model
  is needed before the trap is fully useful, the training pictures do not exist yet, and rare
  species are where models err most.
- **Rejected:** People first and a model later (no reason given); developing the trap and a model as
  two separate strands in parallel (roughly doubles the scope).

## 18. How far must the pictures allow an animal to be identified?
- **Date:** 2026-11-20
- **Step:** discuss
- **Decision:** To species wherever an expert could tell the species apart from a sharp photo of a
  free animal; otherwise to the nearest group, recorded as such.
- **Reason:** Honest and testable: look-alike species become a known, stated limit instead of a
  hidden error. The accepted cost: for some groups the result will be "skink" or "newt", not a
  species.
- **Rejected:** Species for every animal (impossible for species that differ only in details checked
  in the hand; would bring catching back); broad groups only (too coarse for species lists and
  protected-species surveys).

## 19. Must the trap work by day and by night?
- **Date:** 2026-11-20
- **Step:** discuss
- **Decision:** Yes: the trap detects and photographs animals around the clock.
- **Reason:** Replacing a bucket means matching its round-the-clock coverage; otherwise night-active
  species, such as most amphibians, drop out of the results. The accepted cost: lighting at night,
  likely infrared, adds power use and cost, and needs a check that it does not change the animals'
  behaviour.
- **Rejected:** Day only at first (misses most amphibians and night-active reptiles, so it cannot
  claim to replace the bucket).

## 20. Who runs the field tests, now that the trap is not tied to a region?
- **Date:** 2026-11-20
- **Step:** discuss
- **Decision:** Entry 10 stays: the project team tests where it is based and a partner tests
  elsewhere. The partner's role is now to cover different animals, climates and fence types.
- **Reason:** A trap meant for any drift fence needs tests beyond one region's animals and soils.
- **Rejected:** Only the project team, at sites near its base (covers too narrow a range of animals
  and conditions).

## 21. Does the trap record which way each animal was moving?
- **Date:** 2026-11-20
- **Step:** discuss
- **Decision:** Yes: each pass is recorded with its time and the direction the animal was moving.
- **Reason:** Makes the relative numbers of entry 16 easier to defend, since back-and-forth movement
  can be paired, and gives movement direction, which surveys at ponds and habitat edges need. The
  accepted cost: two detection points or a short series of pictures per pass, so more sensing, more
  pictures and more power.
- **Rejected:** Time only (back-and-forth movement cannot be told from several animals, so pass
  counts are weaker).

## 22. What is the model's first job?
- **Date:** 2026-11-20
- **Step:** discuss
- **Decision:** The model removes empty pictures and sorts the rest into broad groups (frog, toad,
  newt, lizard, snake, other). People name the species and check the sorting. Species-level
  recognition is added once enough labelled pictures exist.
- **Reason:** Achievable with few labelled pictures, saves most of the reviewing time from the
  start, and people's species labels, together with the animals identified in the hand during the
  bucket phase of entry 15, become the training data for species later. The accepted cost: people
  still identify species in the first version.
- **Rejected:** Naming species directly from the start, with people checking a sample (needs many
  labelled pictures per species; rare species get misnamed and sample checks let those errors
  through).

## 23. Where does the model run?
- **Date:** 2026-11-20
- **Step:** discuss
- **Decision:** The trap runs only a simple filter that drops obviously empty pictures; the full
  model runs afterwards on a computer once the pictures are collected.
- **Reason:** Chosen on the round 5 page, without a note; it fits the season-long runs of entry 25,
  where storing every empty picture would fill the trap. The accepted weaknesses: two pieces of
  software to build and test, and a filter that is too keen deletes real animals.
- **Rejected:** Everything afterwards on a computer, with the trap storing every picture (no reason
  given); the full model on the trap (more power, cost and complexity in the field; hard to update;
  wrong decisions delete pictures that cannot be checked later).

## 24. What is the smallest animal the trap must detect and photograph identifiably?
- **Date:** 2026-11-20
- **Step:** discuss
- **Decision:** Adults of small species, from roughly 3 cm body length without tail; juveniles below
  that, such as frogs and toads just out of the water, are a stated limit.
- **Reason:** Covers small skinks, newts, frogs and toads as adults, the core of most drift-fence
  species lists, at a size sensing and pictures can handle. The accepted cost: surveys of juveniles
  leaving a pond, a common use of pond fences, are not covered.
- **Rejected:** Juveniles from about 1 cm (the hardest case for sensing and pictures; mass movements
  give huge numbers of passes); only animals from about 8 cm (misses most small species, the main
  reason buckets are used).

## 25. How long must the trap run between visits?
- **Date:** 2026-11-20
- **Step:** discuss
- **Decision:** A whole season: three to six months without a visit.
- **Reason:** Chosen on the round 5 page, without a note. The accepted weaknesses: large batteries
  or solar power, and dirt on the lens and faults that go unnoticed for months.
- **Rejected:** About a week (loses much of the labour gain over daily bucket checks); about a month
  (no reason given).

## 26. Are small mammals and large invertebrates in scope?
- **Date:** 2026-11-20
- **Step:** discuss
- **Decision:** Small mammals and large invertebrates that pass are recorded too, but the trap is
  not designed for them.
- **Reason:** A non-heat trigger notices them anyway, and buckets record them as well; recording
  them costs nothing, designing for them would.
- **Rejected:** Designing for small mammals and invertebrates as targets too (widens the size range
  and the identification task).

## 27. What shape does the trap have in the fence?
- **Date:** 2026-11-20
- **Step:** discuss
- **Decision:** The trap is a short passage set into the fence line; animals cross the fence through
  it, and direction means which side of the fence they came from.
- **Reason:** Without a bucket the fence stands for a whole season (entry 25); a passage lets
  animals still cross where they need to, as at amphibian tunnels with guide fences, and "which
  side" is what pond and habitat surveys ask. The accepted cost: some animals hesitate to enter
  passages, so the passage's shape and floor matter, and the layout differs from today's survey
  fences with buckets.
- **Rejected:** At the fence end (the fence stays a barrier for the whole season, and direction
  along a fence says little about where animals are heading); one unit for both placements (two
  placements to test and report, with compromises in both).

## 28. Does the trap report its state while it runs?
- **Date:** 2026-11-20
- **Step:** discuss
- **Decision:** The trap works fully without a connection. Where coverage exists, an add-on sends a
  short daily message: battery, storage, number of passes, and whether its view is clear.
- **Reason:** Entry 12 means sites anywhere, many without mobile or long-range radio coverage, so
  the trap must work alone; where coverage exists, a daily message can save a season (entry 25). The
  accepted cost: two variants to build and test, and sites without coverage still risk a lost
  season.
- **Rejected:** Every trap always reports (needs coverage many survey sites lack; adds cost and
  power); no reports (a fault early in the season goes unnoticed for months).

## 29. Does the filter on the trap delete pictures during the pilot?
- **Date:** 2026-11-20
- **Step:** discuss
- **Decision:** No. During both pilot stages the filter only marks pictures and deletes nothing, so
  its mistakes can be counted as misses (entries 6 and 15).
- **Reason:** Otherwise animals the filter wrongly drops would vanish without a trace and the miss
  count would be too low.
- **Rejected:** The filter deletes pictures in the pilot too (its misses could not be counted).

## 30. How does the trap show that its view is still clear?
- **Date:** 2026-11-20
- **Step:** discuss
- **Decision:** Once a day the trap takes a picture of its empty view, so lens dirt, spider webs,
  flooding or a blocked passage show up in the records with a date.
- **Reason:** Over a season unattended (entry 25), this tells when the trap stopped seeing well and
  which passes may be missing.
- **Rejected:** No check pictures (a trap that stopped seeing well would look like a quiet site).

## 31. How does the trap notice an animal?
- **Date:** 2026-11-20
- **Step:** discuss
- **Decision:** Lasers across the passage at two points, a few centimetres apart, notice every pass
  and give its direction by their order; the trap does not rely on body heat to notice an animal.
- **Reason:** Proposed in the chat and confirmed on the round 7 page. It is the only way considered
  that ignores body temperature (entry 13), works day and night (19), gives direction (21), notices
  a 3 cm animal (24) and waits on little power for a season (25), and it puts the animal at a known
  spot for sharp pictures. The accepted weaknesses: beams low enough for a flat 3 cm animal sit
  where debris collects (entry 34), and lasers across a raised threshold are what the Hobbs US
  patent describes (entry 11).
- **Rejected:** A camera watching its own picture for movement (too much power for a season, many
  false recordings); timed pictures (miss fast animals, no reliable direction); a heat sensor as the
  main trigger (fails for cold-blooded animals).

## 32. Is a funding application part of this change?
- **Date:** 2026-11-20
- **Step:** discuss
- **Decision:** No. The goal of this change is a design. The welfare case, fewer wild animals caught
  and handled, stays as the reason for the design.
- **Reason:** From the user's note on the round 6 page, confirmed on the round 7 page. The accepted
  risk: if funding is sought later, the funder's rules may ask for changes to the design or the
  pilot, such as the bucket phase of entry 15.
- **Rejected:** Aiming the work at a funder now, such as Wild Animal Initiative (shapes the work
  around a call before the design exists).
- **Replaces:** 14 (an animal-ethics funder as the candidate becomes no funder targeted in this
  change).

## 33. What does the infrared part do, besides the lasers?
- **Date:** 2026-11-20
- **Step:** discuss
- **Decision:** As in ordinary camera traps, a PIR sensor also starts the camera: either the lasers
  or the PIR sensor is enough. Infrared lighting gives the night pictures (entry 19).
- **Reason:** It cannot make cold animals worse off, since the lasers still catch them; it waits on
  very little power; it catches warm animals that slip past the beams; and in the pilot it shows
  which passes only one kind of sensing noticed. The accepted weaknesses: false triggers from
  sun-warmed surfaces and wind, untested behaviour a few centimetres away in a narrow passage, and
  no temperature reading.
- **Rejected:** Infrared lighting only, with no PIR sensor (loses the cheap second trigger and the
  pilot cross-check); a heat-picture sensor recording each animal's surface temperature (noticeably
  more power and cost for a season).

## 34. How many laser beams are there at each of the two points?
- **Date:** 2026-11-20
- **Step:** discuss
- **Decision:** Beams at two or three heights at each point.
- **Reason:** Gives a rough height, so size, besides direction, and the trap keeps working when
  debris blocks the lowest beam over a season. The accepted cost: more beams to align, power and
  keep clean.
- **Rejected:** One low beam per point (one blocked beam blinds that point for the rest of the
  season; gives no size).

## 35. Does the trap also have a laser looking down from the roof?
- **Date:** 2026-11-20
- **Step:** discuss
- **Decision:** Decided by a bench test in the design step: the roof laser is tested against blocked
  beams and power use, and kept only if it earns its place.
- **Reason:** Its strongest case is as a backup when floor debris blocks the low beams; whether that
  is worth its power is a question of measurement, and the fundamentals are now settled enough to
  test (entry 7). The accepted cost: the design stays open on this point until the test is done.
- **Rejected:** A roof laser in any case (more power and cost for a season before its value is
  shown); beams only (no backup beyond the extra heights of entry 34).

## 36. When are the targets for "the trap works" set?
- **Date:** 2026-11-20
- **Step:** discuss
- **Decision:** From the results of the controlled tests (entry 15, stage 1), and fixed before the
  field phase begins.
- **Reason:** The numbers rest on measurements, but are fixed before the field phase, so the field
  result is a fair test and not adjusted afterwards. The accepted cost: the design has no pass mark
  until the controlled tests are done.
- **Rejected:** Fixing numbers now (guesses without measurements); no fixed targets, only reported
  rates (never a clear point at which the design counts as working).

## 37. From how many angles is each animal photographed?
- **Date:** 2026-11-20
- **Step:** discuss
- **Decision:** Decided in the controlled tests: the trap starts with a top view and leaves room for
  a side view; a side view, by mirror or by a second camera, is added only if the main groups miss
  the identification level of entry 18 with known animals (entry 15).
- **Reason:** Raised by the user's note on the review page. Which views identify which species is a
  matter of testing with known animals, not of argument, as with the roof laser (entry 35). The
  accepted cost: the passage must leave room for a side view that may never be used, and the design
  stays open on this point until the tests.
- **Rejected:** Top view only (flanks, the side of the head and the belly are not seen; a dirty lens
  means no pictures at all); top and side view by mirror from the start (the mirror gets dirty or
  fogged; each view gets only part of the detail); two cameras from the start (about twice the
  power, storage and cost; two windows to keep clean); a view from below through a clear floor (the
  floor gets muddy over a season, and some animals may avoid walking on it).

## 38. How is the inside of the passage lit for the pictures?
- **Date:** 2026-11-20
- **Step:** discuss
- **Decision:** Infrared for every picture to start, day and night. Whether colour is added is
  decided in the controlled tests (entry 15): either daylight let in through the top of the passage
  during daylight hours, or one colour picture with a short white light as the animal leaves the
  passage. The tests also check how warm the passage gets with daylight let in through the top, and
  whether white light makes animals turn back or hurry.
- **Reason:** Raised by the user's note on the review page, that there will not be much light inside
  the enclosure unless it is designed for, and settled in the chat. The enclosure is dark by day
  too, so a white light disturbs as much at noon as at night; a design argued on animal welfare
  starts with the light animals notice least, and infrared gives the most uniform pictures for the
  sorting model (entry 22). The user would like colour, so both ways of getting it stay candidates
  for the tests. The accepted cost: grey pictures until the tests, and some species may need colour
  to be told apart.
- **Rejected:** Own light always, white by day and infrared at night (inside a dark enclosure day
  and night look the same to the animal, so the white light disturbs by day too); white light for
  every picture (startles animals during the pass, which can make them turn back and inflate the
  pass counts of entry 16, and costs more power over a season); relying on daylight without
  designing for it (too little light inside the enclosure).

## 39. Where do the two beam points sit?
- **Date:** 2026-11-20
- **Step:** propose
- **Decision:** One beam point near each end of a passage about 25 to 30 cm long, with the camera's
  view between them. The order in which an animal crosses them still gives the direction, and an
  animal that turns back crosses only the first.
- **Reason:** A camera woken from sleep needs time before its first picture, estimated at 0.3 to 1
  second; with a point at each end, the animal is still walking towards the middle of the view when
  the camera is ready, without keeping the camera on all season. The accepted cost: a longer
  passage, which some animals may hesitate to enter (entry 27), and more material; sprinting animals
  may still outrun the camera, which the bench test measures.
- **Rejected:** Both points a few centimetres apart in the middle (the camera would have to be on
  already when the animal is noticed, which costs power all season).
- **Replaces:** 31 (in the spacing of the beam points: a few centimetres apart becomes one near each
  end of the passage).

## 40. What kind of laser sensing makes the beams?
- **Date:** 2026-11-20
- **Step:** propose
- **Decision:** Pulsed infrared laser beams: a small infrared laser on one wall and a light sensor
  on the other for each beam, pulsed and checked a few hundred times a second; an interrupted beam
  means something is there.
- **Reason:** By far the least power for a season of watching, estimated at about 0.2 mA for six
  beams, and a clear yes or no per beam; at 250 pulses a second a 3 cm animal running at 1 m/s is
  still seen several times. The accepted cost: electronics on both walls, beams that must stay
  aligned, and light sensors that must not be fooled by sunlight at the passage ends.
- **Rejected:** Laser distance sensors measuring across the passage (several times the power for a
  season; slower and larger).

## 41. What watches the beams while the camera sleeps?
- **Date:** 2026-11-20
- **Step:** propose
- **Decision:** A separate small low-power controller runs the beams and the PIR sensor, times every
  crossing, and wakes the camera controller, an ESP32-S3, when a pass starts.
- **Reason:** Watching never pauses, even while pictures are written, and the always-on part uses
  very little power. The accepted cost: two pieces of firmware and a link between them to build and
  test.
- **Rejected:** The ESP32-S3 alone, with its low-power co-processor watching the beams (the
  co-processor is limited, and watching may pause while the main part works with the camera); the
  prototype's ESP32-WROVER and OV2640 (entry 5 keeps it as a test bench only; weaker camera, no
  low-power watching).

## 42. What powers the trap for a season?
- **Date:** 2026-11-20
- **Step:** propose
- **Decision:** A small solar panel keeps a smaller rechargeable pack charged.
- **Reason:** Chosen on the round 1 page of propose, without a note. It also guards against a load
  higher than estimated, for example from false triggers, since the estimate of about 4 to 5 Ah for
  six months at 200 passes a day is not yet measured. The accepted weaknesses: fences often stand in
  shade or tall vegetation; a panel near the ground gets dirty, broken or stolen; more electronics.
- **Rejected:** A rechargeable lithium-ion pack of about 12 Ah without solar (no reason given);
  non-rechargeable lithium AA cells (new cells every season cost money and make waste).

## 43. What is the passage body made of?
- **Date:** 2026-11-20
- **Step:** propose
- **Decision:** An upturned standard bucket forms the dark hood; a 3D-printed insert inside carries
  the floor, the beam walls, the camera and the electronics; the fence ends meet openings cut in two
  opposite sides.
- **Reason:** Buckets are cheap, sold everywhere (entry 12) and known to survey teams; the insert
  keeps beams and camera aligned whatever bucket is used, and leaves room for a side view (entry
  37). The accepted cost: bucket sizes differ between makers and countries, so the insert must fit a
  range, and the round shape wastes space.
- **Rejected:** A purpose-built housing printed or moulded as one piece (costlier in small numbers;
  repairable only with the maker's parts); a channel with a separate box on top (more cutting and
  fitting per trap; more joints to seal).

## 44. Which camera does the trap use?
- **Date:** 2026-11-20
- **Step:** propose
- **Decision:** An OV5640 camera module without an infrared-cut filter, with a fixed-focus lens set
  to the passage floor.
- **Reason:** Works with the ESP32-S3, has five megapixels, sees infrared light, and a fixed focus
  suits the fixed distance to the floor.
- **Rejected:** The prototype's OV2640 (two megapixels, weaker in low light).

## 45. Which infrared light does the trap use?
- **Date:** 2026-11-20
- **Step:** propose
- **Decision:** 940 nm infrared light, which shows no red glow.
- **Reason:** Least visible to animals, in line with entry 38; at a few centimetres there is light
  enough for the camera.
- **Rejected:** 850 nm (brighter pictures, but a faint red glow some animals may see).

## 46. What load does the design plan for?
- **Date:** 2026-11-20
- **Step:** propose
- **Decision:** An average of 200 passes a day over a season, false triggers included; short peaks
  above that are fine.
- **Reason:** Sets the size of battery, solar panel and memory card with room for busy nights; the
  bench and field tests check it.
- **Rejected:** 50 passes a day (a smaller battery, but busy sites would run out).

## 47. How are the firmwares built?
- **Date:** 2026-11-20
- **Step:** propose
- **Decision:** Both firmwares, the beam watcher's and the camera controller's, are built with
  PlatformIO and the Arduino framework, as in FieldMesh.
- **Reason:** The same tools and habits as the user's other ESP32 work.
- **Rejected:** ESP-IDF directly (a second toolchain to learn and maintain).

## 48. How are pass records stored and exported?
- **Date:** 2026-11-20
- **Step:** propose
- **Decision:** Pass records are kept as one CSV file per survey day next to the JPEG pictures on
  the memory card; the computer tool exports a season as a Camera Trap Data Package (Camtrap DP).
- **Reason:** Readable with any tool, and Camtrap DP is the open standard that other camera-trap
  software and data portals read.
- **Rejected:** Only the trap's own format (data would need converting before others could use it).

## 49. What does the sorting run on?
- **Date:** 2026-11-20
- **Step:** propose
- **Decision:** A Python tool on a computer, with a small local page in the browser where people
  name species and correct the model.
- **Reason:** Fits the pass records and the bucket labels exactly, and needs no account or server.
- **Rejected:** A general labelling tool such as Label Studio (does not know passes, directions or
  bucket labels; needs setting up and adapting).

## 50. Where do the prototype files go?
- **Date:** 2026-11-20
- **Step:** propose
- **Decision:** The prototype files move unchanged to a `prototype` folder; the new trap gets
  `firmware`, `sorting`, `hardware` and `docs` folders.
- **Reason:** Keeps the prototype as the test bench of entry 5 without mixing it with the new trap.
- **Rejected:** Leaving the prototype files where they are (mixes the old test bench with the new
  trap at the top of the repository).

## 51. What happens to the daily state message in version 1?
- **Date:** 2026-11-20
- **Step:** discuss
- **Decision:** Version 1 has no radio. Once a day the trap works out a short state summary (battery
  level, free storage, passes since the last summary, and whether the daily picture showed a clear
  view) and writes it to the memory card in the format FieldMesh takes. Letting the trap feed
  FieldMesh on its own, with its own uplink and no hub on the site, is a later change.
- **Reason:** Raised in propose: sending the message over ESP-NOW needs a FieldHub or node on every
  site, a second piece of hardware for one daily message. The user would rather the trap fed
  FieldMesh on its own, but not in version 1. Preparing the summary now keeps that later change
  small, and a daily state line on the card is useful when the trap is collected. The accepted cost:
  in version 1 a fault early in the season goes unnoticed until the visit; the daily check picture
  (entry 30) and the fault records only explain afterwards what went wrong.
- **Rejected:** The trap as a FieldMesh node over ESP-NOW in version 1 (works only where a FieldHub
  stands within range, so one is needed on every site); leaving the state summary out of version 1
  entirely (the later change would start from nothing); a mobile-network or LoRaWAN radio in version
  1 (a SIM or a gateway per site, and not wanted for version 1).
- **Replaces:** 28 (an optional add-on that sends a daily message where coverage exists becomes a
  daily state summary on the memory card, with no radio in version 1).
