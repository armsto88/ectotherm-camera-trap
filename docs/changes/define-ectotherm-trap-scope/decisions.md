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

## 52. Where does the solar panel sit?
- **Date:** 2026-11-20
- **Step:** propose
- **Decision:** On a short stake a little away from the bucket, angled to the sun, with a cable to
  the trap.
- **Reason:** Keeps the panel's heat off the passage, lets it stand in the sunniest spot nearby, and
  leaves the bucket top free for the daylight option of entry 38. The accepted cost: a cable that
  animals may chew and people may trip on, and one more thing to set up.
- **Rejected:** On the bucket top on spacers (warms the hood in sun, sits wherever the fence puts
  it, rules out daylight through the top); on a fence post (drift fences often have no post tall or
  firm enough).

## 53. How large is the battery pack?
- **Date:** 2026-11-20
- **Step:** propose
- **Decision:** Two 18650 lithium-ion cells in parallel, about 7 Ah.
- **Reason:** By the estimate of about 25 mAh a day at 200 passes a day (entry 46), the trap lasts a
  whole season without sun, so it survives a shaded or covered panel and a load well above the
  estimate. The accepted cost: more cost, weight and space than one cell.
- **Rejected:** One 18650 cell of about 3.4 Ah (little margin if the real load is several times the
  estimate, or in frost).

## 54. How wide is the passage?
- **Date:** 2026-11-20
- **Step:** propose
- **Decision:** 15 cm.
- **Reason:** Chosen on the round 2 page of propose, without a note; it lets larger animals through
  as well. The accepted weaknesses: longer beams, a larger view with less detail per animal (still
  an estimated 8 to 10 pixels per millimetre), and a bucket of about 30 cm diameter, in which the
  passage is about 26 cm long.
- **Rejected:** 6 cm (large toads and large skinks do not fit or will not enter); 10 cm (no reason
  given).

## 55. How does the passage floor meet the ground?
- **Date:** 2026-11-20
- **Step:** propose
- **Decision:** The floor lies flush with the ground at both ends, with no raised threshold.
- **Reason:** Animals walk in without climbing; it also differs from the raised threshold of the
  Hobbs patent (entry 11).
- **Rejected:** A raised threshold, as in HALT (beams sit above debris, but animals must climb).

## 56. Which pictures may the filter on the trap drop?
- **Date:** 2026-11-20
- **Step:** propose
- **Decision:** Only pictures of passes that only the PIR sensor noticed and that look the same as
  the daily empty view; any pass the lasers noticed keeps all its pictures.
- **Reason:** A laser interruption is strong evidence of something real, so the filter can only err
  on the side of keeping (entry 23).
- **Rejected:** Judging every picture by how much it differs from the empty view (a filter on all
  passes could drop real animals the lasers saw).

## 57. How many pictures does a pass get?
- **Date:** 2026-11-20
- **Step:** propose
- **Decision:** One as soon as the camera is ready, then one every half second while the animal is
  in the passage, at most six.
- **Reason:** Several chances at a sharp picture without filling the card; fits the 200 passes a day
  of entry 46.
- **Rejected:** One picture per pass (a single blurred or badly timed picture loses the
  identification).

## 58. What if the camera wakes too slowly?
- **Date:** 2026-11-20
- **Step:** propose
- **Decision:** If the bench test shows the camera wakes too slowly for the target speeds, the
  camera is kept on standby rather than switched off.
- **Reason:** Entry 39 relies on the camera waking in time; standby is the fallback, at the cost of
  more power.
- **Rejected:** A longer passage (more hesitation at the entrance, and a 30 cm bucket leaves no
  room).

## 59. Which controller is the beam watcher?
- **Date:** 2026-11-20
- **Step:** propose
- **Decision:** An ATtiny3216, built with PlatformIO and the Arduino framework (megaTinyCore).
- **Reason:** Sleeps on about a microamp, wakes on its own timer to pulse the beams, and fits the
  tools of entry 47.
- **Rejected:** An STM32L0 (more capable, but more setup).

## 60. What is the state summary's format?
- **Date:** 2026-11-20
- **Step:** propose
- **Decision:** One FieldMesh reading per day: the usual fields such as time, trap number, battery
  voltage and temperature, plus trap fields for passes, free storage and a clear view, which the
  FieldMesh backend stores although it does not model them yet.
- **Reason:** Valid against today's FieldMesh upload contract, with no FieldMesh change needed for
  version 1; issue #1 can add the fields to the contract later.
- **Rejected:** Putting the trap's values into the generic aux1 and aux2 fields (their meaning would
  live only in documents).

## 61. How is the pack charged?
- **Date:** 2026-11-20
- **Step:** propose
- **Decision:** Solar charging reuses the FieldHub's 6 V charger design (CN3791), with charging
  stopped below freezing.
- **Reason:** A tested design the user already has; lithium-ion must not charge in frost.
- **Rejected:** A new charger design (more work and testing for no gain).

## 62. Which tools draw the hardware?
- **Date:** 2026-11-20
- **Step:** propose
- **Decision:** The bucket insert is a FreeCAD Python script with the bucket's size as parameters,
  like FieldMesh's sensor housings; the boards are drawn in EasyEDA, like the FieldMesh boards.
- **Reason:** The same tools as the user's other hardware; one script makes inserts for different
  buckets (entry 43).
- **Rejected:** KiCad for the boards and OpenSCAD for the insert (new tools for no gain).

## 63. How is the broad-group model made?
- **Date:** 2026-11-20
- **Step:** propose
- **Decision:** A small pretrained image model, fine-tuned with PyTorch on the trap's labelled
  pictures; until enough labels exist, the tool only marks empty pictures and people sort the rest.
- **Reason:** No ready model knows small animals seen from above in a passage; the labels of entries
  22 and 15 train it.
- **Rejected:** An existing camera-trap detector such as MegaDetector (trained on side views of
  larger animals).

## 64. How is the trap tested?
- **Date:** 2026-11-20
- **Step:** propose
- **Decision:** At three levels: unit tests run on a computer for firmware logic and the sorting
  tool; bench runs with a model-animal rig whose records are checked by scripts; and written check
  procedures for what only a person can check, such as gaps beside the trap.
- **Reason:** Most scenarios are about hardware meeting animals; each still gets a test that names
  its scenario.
- **Rejected:** Unit tests only, with bench results noted by hand (no repeatable check for most
  scenarios).

## 65. Does the change ignore build output in git?
- **Date:** 2026-11-20
- **Step:** implement
- **Decision:** Yes. The design's Impact gains `.gitignore`, which task 1.1 extends with PlatformIO
  and Python build output; it already ignores Python's cache folders since oekospec was installed.
- **Reason:** Task 1.1 asks for the file, but the design's Impact left it out; the design was wrong,
  not the task.
- **Rejected:** Dropping the `.gitignore` from task 1.1 (build output would show up in every
  commit).

## 66. How does the camera know a pass is under way?
- **Date:** 2026-11-20
- **Step:** implement
- **Decision:** `PassBuilder` gains `bool open() const`, true while a pass is open; the design's
  interface for `passes` lists it.
- **Reason:** The camera takes a picture every half second while the animal is in the passage, and
  cannot tell from its crossings alone whether a pass is open, since crossings on ignored beams open
  none. Building the pass library brought it up.
- **Rejected:** The camera working out an open pass itself (it would repeat the builder's rules).

## 67. Where does the sorting tool keep a season and its own results?
- **Date:** 2026-11-20
- **Step:** implement
- **Decision:** A season is a folder on the computer that holds the card copy in `card/` and the
  tool's own files beside it: `sorting.csv` for the model's results, `labels.csv` and
  `season.cfg`. `trapsort import` checks a card and copies it into a season folder; every other
  command takes the season folder.
- **Reason:** The model's results must last between commands, people's labels must never mix with
  machine output, and sorting again must never touch people's work. The design said only that
  labels lie "beside the season"; building the sorting tool brought it up.
- **Rejected:** Keeping the model's results as rows in `labels.csv`, one log for people and model
  (mixes machine and human entries; sorting again appends thousands of rows).

## 68. How are labels written and read back?
- **Date:** 2026-11-20
- **Step:** implement
- **Decision:** `LabelStore` opens a season's `labels.csv` and also reads labels back: a picture's
  name, group and empty mark, and a pass's bucket labels. People can correct an empty mark. Each
  group correction keeps the model's group at that moment in a new column `model_group`.
  `add_bucket_label` takes the group as well.
- **Reason:** The summary, export, evaluation and training read labels back; a corrected group must
  be stored together with the model's original group; the specs let people correct an empty mark.
  The design listed only the writing methods.
- **Rejected:** Each reader parsing `labels.csv` itself, and taking the model's original group from
  `sorting.csv` (sorting again would overwrite it).

## 69. How is a trained group model loaded, and is PyTorch required?
- **Date:** 2026-11-20
- **Step:** implement
- **Decision:** A trained group model is loaded with `load_group_model(path)`. PyTorch is an
  optional extra of the tool, `trapsort[model]`, and the training test runs where it is installed.
- **Reason:** `trapsort sort` has to load what `trapsort train` saved; PyTorch is a large download
  that reading, reviewing and exporting do not need.
- **Rejected:** PyTorch as a required dependency (a large download for every user).

## 70. What time does a picture get in the Camtrap DP export?
- **Date:** 2026-11-20
- **Step:** implement
- **Decision:** Each picture's time is the pass's start plus half a second per picture before it,
  noted as estimated in the media comments; observations use the pass's exact start and end.
- **Reason:** Camtrap DP requires a time for every picture, and the pass file records only the
  pass's start and end.
- **Rejected:** The firmware writing each picture's time into the pass file (a new column; changes
  the records library already built).

## 71. How is an animal in the bucket matched to a pass?
- **Date:** 2026-11-20
- **Step:** implement
- **Decision:** In the field phase, a bucket animal matches the earliest unmatched pass since the
  previous check whose pictures show its group; passes that went through the trap come before
  turned-back ones.
- **Reason:** Bucket checks give only the check time and the animal, so group and time are what can
  be matched.
- **Rejected:** Also requiring the direction toward the bucket (needs the bucket's side recorded in
  `season.cfg`).

## 72. Where do the trap's parts come from?
- **Date:** 2026-11-20
- **Step:** discuss
- **Decision:** Every chip on the trap's own boards comes from LCSC, so that JLCPCB can assemble the
  boards; plug-in parts such as the camera module may come from elsewhere.
- **Reason:** The user's boards are drawn in EasyEDA and made at JLCPCB, which assembles from
  LCSC's stock. LCSC carries no ready OV5640 module with lens and cable, only the bare sensor, so a
  rule covering the camera too would mean a 2 or 3 megapixel camera.
- **Rejected:** Everything from LCSC, camera included (only 2 or 3 megapixel camera boards; a 3 cm
  animal would be about 180 instead of about 300 pixels long).

## 73. Where may the trap's chips come from?
- **Date:** 2026-11-20
- **Step:** discuss
- **Decision:** Every chip on the trap's own boards must be one JLCPCB can assemble: from LCSC's
  stock where it has it, otherwise ordered in through JLCPCB's global sourcing from suppliers such
  as DigiKey and Mouser. Plug-in parts such as the camera module may come from anywhere.
- **Reason:** The user pointed out that JLCPCB orders in parts LCSC lacks. LCSC stock stays the
  first choice, since parts ordered in add about two to four weeks, cannot be returned once ordered
  and some carry customs fees of 3 to 30%.
- **Rejected:** LCSC's stock only (rules out most chips that run image models, which LCSC lacks or
  holds only a few of).
- **Replaces:** 72, in that chips may also be ordered in through JLCPCB.

## 74. What must the camera controller allow for a vision model later?
- **Date:** 2026-11-20
- **Step:** discuss
- **Decision:** The ESP32-S3 stays the camera controller and is enough: a vision model would run on
  it after the pictures of a pass are taken. A separate chip for models comes only with a later
  board revision, and only if a test shows the ESP32-S3 is not enough.
- **Reason:** The user wants a vision model that sorts pictures on the trap. The decision is not
  timing-critical, since the model can judge the pictures after they are taken, in a second or two
  per pass. The ESP32-S3 runs small image models in about 0.1 to 0.2 s per picture and, with its
  extra memory, can run larger ones slowly; at about 200 passes a day the model's energy is roughly
  2 mAh a day against about 30 mAh for the rest (estimates). The v1 boards will be revised after the
  bench tests anyway.
- **Rejected:** The ESP32-S3 with a free slot for a helper chip (designed for a chip not yet
  known); a helper chip such as the MAX78000 (far less energy and faster, but holds only small
  models, needs its own tools and its long-term supply is uncertain; its strengths do not matter
  when timing does not); switching to a vision chip such as the STM32N6 now (scarce, costly, new
  tools before the trap has taken a picture).

## 75. Does this change include a learned image model?
- **Date:** 2026-11-20
- **Step:** discuss
- **Decision:** No. Version 1 sorts pictures without a learned model: the trap's cautious filter,
  the computer marking pictures that look like the day's empty view, and people sorting and naming
  the rest, whose names are kept as labels for training later. A learned model, run on the trap
  after each pass, is a later change.
- **Reason:** The user's first priority is a trap that works on its own as a laser-triggered camera
  trap; a model on a computer is not their concern now. No model can be trained before people have
  named a season or so of pictures, so version 1 loses nothing and is finished sooner.
- **Rejected:** A model on the computer in this change (its tools could not be used before the first
  season is named); a model on the computer and on the trap in this change (version 1 would wait
  for a season of named pictures and a checked model).
- **Replaces:** 17, 22, 63 and 69, and 23 as far as a full model on a computer goes.

## 76. Does the camera focus itself?
- **Date:** 2026-11-20
- **Step:** discuss
- **Decision:** No. The camera has fixed focus, with a lens whose focal length is chosen for the
  passage and the camera's height, focused once at the trap and fixed in place. The camera's height
  and the module are settled in propose and on the bench.
- **Reason:** The distance to the floor never changes. With the view just covering the passage, a
  5 megapixel camera gives about 10 pixels per millimetre, and at f/2 the depth of field reaches
  about 3 cm above the floor with the camera at 20 cm, about 4 cm at 25 cm and about 4.5 cm at 30 cm
  (estimates). No moving parts in a damp hood and no focusing delay. The accepted cost: animals
  taller than that are slightly soft on top.
- **Rejected:** Autofocus (a delay on every picture, a small motor in the damp, mixed reports with
  the ESP32, and in dim infrared light it may focus on the floor instead of the animal).

## 77. Which infrared light lights the pictures?
- **Date:** 2026-11-20
- **Step:** discuss
- **Decision:** Decided on the bench, with 940 nm as the default: the board takes infrared LEDs of
  either 940 or 850 nm in the same place, and the controlled tests compare picture quality and power
  and watch whether animals react to the faint glow of 850 nm.
- **Reason:** Ordinary sensors such as the OV5640 are far less sensitive at 940 nm; 850 nm likely
  gives two to three times the picture for the same light (estimate), but whether reptiles and
  amphibians notice its glow at a few centimetres in a dark passage is unknown. The user accepts
  the extra power of 940 nm: if the trap needs more, it gets larger batteries.
- **Rejected:** Staying with 940 nm without testing 850 nm (stronger LEDs and more power per picture
  for an untested gain); switching to 850 nm now (its effect on the animals is untested).
- **Replaces:** 45, in that 850 nm is tested on the bench instead of ruled out.

## 78. Do turtles count as a group of their own?
- **Date:** 2026-11-20
- **Step:** discuss
- **Decision:** Yes. Turtle becomes a broad group beside frog, toad, newt, lizard, snake and other;
  the trap is not sized for large turtles, so only small ones pass.
- **Reason:** The user named turtles among the animals to tell apart. Small turtles get counted and
  named like every other animal at no cost; large turtles are usually surveyed by other methods. The
  accepted cost: shells taller than the depth of field are slightly soft on top.
- **Rejected:** Turtles as a design target (a passage of 20 cm or more and a higher camera: a bigger
  bucket, longer beams and less detail on the small animals the trap is mainly for); turtles under
  "other" (they could not be counted apart).
- **Replaces:** 22, in its list of broad groups.

## 79. When does a pass count as having a usable picture, and as identified?
- **Date:** 2026-11-20
- **Step:** discuss
- **Decision:** A pass has a usable picture when a person sorting the pictures gave any of its
  pictures a group or a name; marking a picture "can't tell" or "empty" does not count. A pass is
  identified when the name given matches the animal the test plan or the bucket check names.
- **Reason:** The evaluation reports the share of animals with a usable picture, but the specs did
  not say who judges it. A usable picture is one from which a person can tell at least the group,
  which is what entry 18 asks of a picture, and it costs no extra click. The accepted cost: a test
  run must be sorted in full before it is evaluated.
- **Rejected:** A separate "good enough" mark on each picture (one more click that mostly repeats
  choosing the group); every picture not marked empty counting as usable (blurred pictures would
  count, which flatters the trap).

## 80. How does a picture get its broad group?
- **Date:** 2026-11-20
- **Step:** discuss
- **Decision:** The person sorting picks the group of each picture that shows an animal, and adds
  the species name where the picture allows. Bucket animals take their group from the bucket check
  sheet.
- **Reason:** Counts per survey day, matching bucket animals and a later model all work with
  groups, and without a model no group is guessed in advance. One click gives every animal a group,
  even when its species cannot be named.
- **Rejected:** A list that gives each species name its group (every new species needs an entry
  first; one more file to keep right).
- **Replaces:** 68, in that there is no model's group to keep beside a person's group.

## 81. Where do a trap's coordinates come from?
- **Date:** 2026-11-20
- **Step:** discuss
- **Decision:** From the trap's settings file on its card: its latitude and longitude are entered
  in `trap.cfg` when the trap is set up, and the trap keeps them with its records.
- **Reason:** The Camtrap DP export requires the coordinates of every trap site, and the trap does
  not know where it stands. With the coordinates on the card they travel with the trap's records,
  and the daily summary can carry them as the FieldMesh readings table has fields for them. The
  accepted costs: the coordinates must be known before the card goes into the trap, and the trap's
  settings reader, which rejects keys it does not know, must learn them.
- **Rejected:** A settings file for the season on the computer, beside the card copy (no firmware
  change, but the coordinates live apart from the trap's records); typing them in at each export
  (typed again every time, easy to get wrong).
- **Replaces:** 67, in that the season folder holds no `season.cfg`.

## 82. Do people sort a pass at once, or each picture on its own?
- **Date:** 2026-11-20
- **Step:** propose
- **Decision:** A pass at once: the review page shows a pass's pictures side by side, the person
  picks the group and adds the name once, and both are stored for every picture of the pass. A
  single picture can still be marked empty or "can't tell", and a pass with two different animals
  can be labelled picture by picture.
- **Reason:** A pass has up to six pictures, about three on average; labelling once saves about two
  thirds of the clicks, and every picture still carries the label a later model learns from.
- **Rejected:** Each picture on its own (about three times the clicks, mostly repeating the same
  answer).

## 83. What do the daily summary and the export do with the trap's coordinates?
- **Date:** 2026-11-20
- **Step:** propose
- **Decision:** The daily summary carries the latitude and longitude from the trap's settings in
  FieldMesh's fields for them, empty when not set. A trap without coordinates still runs; only the
  export of its season stops and says what is missing.
- **Reason:** FieldMesh readings have latitude and longitude fields, so the summary can place the
  trap without a change to FieldMesh; Camtrap DP requires the coordinates, but missing ones must not
  stop a trap from recording.
- **Rejected:** Leaving the coordinates out of the summary (FieldMesh would not know where the trap
  stands); a trap that refuses to start without coordinates (a forgotten entry would cost a season).

## 84. Is "can't tell" kept as a label?
- **Date:** 2026-11-20
- **Step:** propose
- **Decision:** Yes. A picture a person marks "can't tell" is stored as reviewed without a group.
- **Reason:** A test run must be sorted in full before it is evaluated (entry 79); without this
  mark, a picture nobody looked at and one nobody could tell look the same.
- **Rejected:** Not storing it (an unfinished run cannot be told from a finished one).

## 85. Does every trap have a link from the start?
- **Date:** 2026-11-21
- **Step:** discuss
- **Decision:** Yes. Every trap has a mobile-network modem from version 1, built after the user's
  Auris recorder, and sends to FieldMesh on its own, with no hub on the site. Letting the trap feed
  FieldMesh on its own, until now a later change (issue #1), becomes part of this change.
- **Reason:** Raised by the user after the stakeholder summary: the trap needs connectivity from the
  start, with a modem in each trap as in Auris. A trap that reports shows a fault within a day
  instead of at the end of the season, and its results reach FieldMesh without a visit. The accepted
  cost: each trap gains a modem, a SIM and a data plan in its cost, and power for every connection;
  at sites without coverage it gains nothing.
- **Rejected:** Version 1 without radio (a fault early in the season goes unseen until the visit).
- **Replaces:** 51 (in the radio: no radio in version 1 becomes a mobile-network modem in every
  trap; the daily state summary on the memory card stays).

## 86. How often does the trap send?
- **Date:** 2026-11-21
- **Step:** discuss
- **Decision:** Once a day: the day's pass records and the state summary in one connection. How
  often can be changed in the trap's settings, for example to send more often during the pilot.
- **Reason:** Enough to catch a fault within a day and keep results current. By rough estimate, not
  measured, a connection in good coverage costs about 1 to 2 mAh, so once a day adds a few percent
  to the trap's daily use of about 25 to 30 mAh, where every hour would roughly double or triple
  it. The accepted cost: results reach FieldMesh up to a day late.
- **Rejected:** Every hour (roughly doubles or triples the trap's daily energy by estimate, more in
  weak coverage, and needs a larger pack and panel).

## 87. Does the trap take anything back over the link?
- **Date:** 2026-11-21
- **Step:** discuss
- **Decision:** Yes: new settings, such as how often to send and pilot mode, and signed firmware
  updates, as in Auris.
- **Reason:** A trap stands three to six months without a visit, and version 1 firmware will have
  faults that only the pilot finds; updates over the air fix them without visits, and the model on
  the trap reaches the traps the same way. The accepted cost: the most work of the options, and an
  update needs a safe way back to the firmware before it, or a bad one stops a trap in mid-season.
- **Rejected:** Settings only (every firmware fix and every new model needs a visit to every trap);
  nothing (nothing can be corrected from afar for a whole season).

## 88. What leaves the trap over the link?
- **Date:** 2026-11-21
- **Step:** discuss
- **Decision:** Only results: the pass records and the daily state summary, never pictures. The
  pictures stay on the memory card.
- **Reason:** The user's choice in the brainstorm: send the inference, not photos. Results are
  small, so each connection stays short. The accepted cost: nobody far away can check the trap's
  own judgement that its view is clear, or look at a surprising record.
- **Rejected:** Also sending one small picture of the empty passage a day, a few kilobytes, so a
  person can see a dirty lens or a blocked passage from afar (turned down without a note).

## 89. What happens where there is no coverage?
- **Date:** 2026-11-21
- **Step:** discuss
- **Decision:** The memory card stays the full record. Without coverage the trap works exactly as
  without a modem, and sends what is waiting once it gets through.
- **Reason:** Survey sites are anywhere (entry 12), many with patchy coverage; nothing is lost when
  the link fails.
- **Rejected:** The link as the main store, with the card only as a buffer (records would be lost
  at sites with poor coverage).

## 90. Does the trap have a satellite link?
- **Date:** 2026-11-21
- **Step:** discuss
- **Decision:** Not in this change; sites with no coverage at all rely on the memory card.
- **Reason:** A satellite modem adds cost and power; the California bucket-trap trial shows that
  one can be added later where needed.
- **Rejected:** Room on the board for a satellite modem from the start (cost and board space for a
  part not yet needed).

## 91. Where does the trap sit in the fence?
- **Date:** 2026-11-21
- **Step:** discuss
- **Decision:** In the fence line or at a fence end; the same unit serves both, and the survey
  chooses.
- **Reason:** The user: the concept is the same wherever the bucket sits; animals walk through it
  and trigger the camera. Cameras at fence ends (AHDriFT) are a layout surveys already use. The
  accepted cost: two placements to test and to report, and a pass's direction means something
  different in each: which side of the fence, or along the fence.
- **Rejected:** In the fence line only (as planned until now; the user does not want the placement
  tied down).
- **Replaces:** 27 (the passage set into the fence line becomes a choice between the fence line and
  a fence end).

## 92. How is a pass's direction read in either placement?
- **Date:** 2026-11-21
- **Step:** discuss
- **Decision:** The trap's settings note whether it sits in the fence line or at a fence end, and
  which way its first opening faces, so each pass's direction can be read.
- **Reason:** With one unit for both places, a direction means nothing without its placement.
- **Rejected:** The placement noted only on the field sheet (it gets separated from the records).

## 93. Does the model on the trap come into this change?
- **Date:** 2026-11-21
- **Step:** discuss
- **Decision:** Yes. A first model on the trap gives each pass a type of animal, not a species, and
  how sure it is. It is trained on pictures from others, such as the pictures from above that
  California's wildlife agency took in upturned buckets at drift fences, and checked on the trap's
  own bench pictures before it goes on the traps. Its result travels with the pass records. A model
  on a computer stays out.
- **Reason:** Chosen on the round 1 page against the recommendation, without a note. The user sees
  the model on the trap as part of the idea, and the link is to send its results rather than
  pictures; training on others' pictures gets round the lack of named pictures of the trap's own.
  The accepted cost: it depends on pictures not yet known to be available, colour daylight pictures
  may not carry over to the trap's infrared ones, and version 1 takes longer.
- **Rejected:** The model in a later change, with the link leaving room for its result (until then
  the link would report only that something passed, which way and how big, not what it was).
- **Replaces:** 75 (in part: a learned model on the trap comes into this change; a model on a
  computer stays out).

## 94. How large are the pack and the panel?
- **Date:** 2026-11-21
- **Step:** discuss
- **Decision:** They grow as far as the modem and the model need; their size is set in the design
  step.
- **Reason:** The modem adds power for every connection, and the user said bigger batteries are
  fine.
- **Rejected:** Keeping the two-cell pack and limiting how often the trap sends (the battery would
  decide how useful the link is).
- **Replaces:** 53 (two 18650 cells becomes a pack sized in the design step for the modem and the
  model).

## 95. What does the proposal say about the closest existing traps?
- **Date:** 2026-11-21
- **Step:** discuss
- **Decision:** It adds the California upturned-bucket cameras (Pepperwood Preserve, UC Nature,
  California's wildlife agency) to the prior art, and states what this trap adds: lasers that
  notice cold animals, the direction and size of each pass, months on solar, a modem in every
  trap, and a model on the trap.
- **Reason:** They are the closest traps known, found in the brainstorm after the stakeholder
  summary; a reviewer who knows them would ask. As with the light-beam trigger (entry 8), the
  proposal states what this trap adds and claims no first.
- **Rejected:** Leaving the prior art as it is (the closest traps would be missing).

## 96. Which types does the first model tell apart?
- **Date:** 2026-11-21
- **Step:** discuss
- **Decision:** Frog or toad, lizard, snake, other animal, and empty. Newts, salamanders and turtles
  count as other until the trap's own named pictures teach the model them, by a later update.
- **Reason:** The free pictures from others, taken from above at drift fences, hold thousands of
  each of these types (about 130,000 lizard, 67,000 snake and 22,000 frog or toad pictures), but no
  newts, about 300 salamanders and about 900 turtles; each type the first model learns can be
  checked fairly. The accepted cost: newts, central to European surveys, show only as other in the
  first model, and frog and toad stay together.
- **Rejected:** The seven groups people use, plus empty (the model would be weakest exactly where
  pictures are missing, or wait for the trap's own).

## 97. What may the model's result do on the trap?
- **Date:** 2026-11-21
- **Step:** discuss
- **Decision:** It only labels: the type and how sure the model is go into the pass record and over
  the link. The model deletes nothing, and the filter on the trap stays as planned.
- **Reason:** A model checked only on bench pictures should not decide what is kept; its mistakes
  can be counted against the pictures. The accepted cost: the card keeps empty pictures the model
  could have recognised.
- **Rejected:** Also dropping pictures the model is sure are empty, outside pilot mode (its
  mistakes would delete animals that nobody can count afterwards).

## 98. Do people see the model's type while they sort?
- **Date:** 2026-11-21
- **Step:** discuss
- **Decision:** Not in pilot mode: there people sort without seeing it, so their groups check the
  model. Outside the pilot it shows as a suggestion that people confirm or change.
- **Reason:** People tend to follow a suggestion; hiding it in the pilot gives an honest measure of
  the model, and later surveys get the time saved. The accepted cost: sorting the pilot takes as
  long as without a model.
- **Rejected:** Always shown (the pilot could no longer tell how good the model is); never shown
  (sorting would never get faster).

## 99. What if the model is not good enough in time?
- **Date:** 2026-11-21
- **Step:** discuss
- **Decision:** The trap goes into the field without a model, and the model follows by update once
  it passes its check, trained further on the trap's own named pictures.
- **Reason:** The trap first, as the user set the order; with updates over the air (entry 87), a
  later model costs no visit. The infrared gap may hold the model back: in the pictures from others,
  lizards and snakes are almost only in daytime colour, while the trap takes infrared. The accepted
  cost: the first field weeks may report no animal types.
- **Rejected:** Version 1 waits for the model (the field season, and with it the pictures that
  would improve the model, slips).

## 100. When is the model good enough to go on the traps?
- **Date:** 2026-11-21
- **Step:** discuss
- **Decision:** The model's targets are set from the controlled tests and fixed before the field
  phase, like the trap's own (entry 36).
- **Reason:** The same rule as for the trap; a number set now would be a guess.
- **Rejected:** A fixed bar now, such as the right type for nine in ten usable pictures (set
  without any data on what is reachable).

## 101. Do the results measure the model?
- **Date:** 2026-11-21
- **Step:** discuss
- **Decision:** Yes. Beside trigger, usable picture and identification, the results report how
  often the model's type matches the group a person gave.
- **Reason:** The model's quality is measured the same way as the rest of the trap.
- **Rejected:** Measuring the model outside the trap's results (two places to look, and the model
  could pass unmeasured).

## 102. Does a pass record say which model judged it?
- **Date:** 2026-11-21
- **Step:** discuss
- **Decision:** Yes. Each pass record names the model version that judged it.
- **Reason:** Results stay traceable after a model update.
- **Rejected:** The version only in the daily summary (a pass could not be tied to its model when
  an update arrives in mid-day).

## 103. Who trains the first model, and where?
- **Date:** 2026-11-21
- **Step:** discuss
- **Decision:** The project trains it on a computer. The FieldMesh tools to check data, train
  models and upload them to devices stay a later change (FieldMesh issue 97). A model that sorts
  pictures on a computer stays out too (entry 93).
- **Reason:** Keeps this change to the trap; the FieldMesh issue already holds those tools.
- **Rejected:** Building the FieldMesh tools in this change (a second system to build before the
  trap has run a season).

## 104. Which modem goes in the trap?
- **Date:** 2026-11-21
- **Step:** propose
- **Decision:** The Quectel EG810M-EU, Auris's modem, with Auris's 3.9 V supply, nano-SIM holder and
  antenna design. A driver for it is written for the trap, so that Auris can share it later.
- **Reason:** Chosen on the round 1 page of propose against the recommendation, without a note. It
  keeps the trap and Auris on one modem, as entry 85 has the modem built after Auris. The accepted
  cost: no driver for it exists in the user's projects, so one must be written before the trap can
  send; the FieldHub's upload rules (batches, confirmation, retries) are reused above it. It is
  approved for Europe, Australia and New Zealand only.
- **Rejected:** The SIMCom A7670G, the FieldHub's modem with a working driver and a global module
  (the trap and Auris would differ).

## 105. How do pass records reach FieldMesh?
- **Date:** 2026-11-21
- **Step:** propose
- **Decision:** As readings, from the start: each pass is a reading of the trap with its own time
  and sequence number and trap keys with flat values (direction, beam heights, what noticed it, the
  model's type, how sure it is, the model version). FieldMesh models these keys later.
- **Reason:** FieldMesh has no place for pass records but stores reading keys it does not model, so
  the trap can send from its first day. The trap sends right after its daily summary, so the summary
  stays the trap's newest reading. The accepted cost: until FieldMesh models the keys, passes are
  missing from its CSV export and its views treat them like sensor values.
- **Rejected:** A pass type in FieldMesh first (the trap's link would wait for FieldMesh work in
  another repository).

## 106. How does a new model reach the trap?
- **Date:** 2026-11-21
- **Step:** propose
- **Decision:** As a separate model file on the memory card, signed with the release key and checked
  before use, with its own update path over the link. The trap keeps the model it has when a new
  one fails its check or does not load. Until FieldMesh can release model files to devices, a model
  is copied onto the card at a visit or on the bench.
- **Reason:** Chosen on the round 1 page of propose against the recommendation, without a note. A
  model file of its own can change without a firmware release, and the model version stays
  separate from the firmware's. The accepted cost: a second update path, in the trap and in
  FieldMesh, built before any model exists; FieldMesh can release only firmware today.
- **Rejected:** The model built into the camera controller's firmware, a new model being a signed
  firmware update (every new model a whole firmware download of about 2 MB, model and firmware
  released together).

## 107. How is a trap known to FieldMesh?
- **Date:** 2026-11-21
- **Step:** propose
- **Decision:** Each trap is registered as a hub of its own, with its own upload key and one node,
  itself.
- **Reason:** Works with FieldMesh's devices as they are.
- **Rejected:** A new kind of device in FieldMesh for traps (FieldMesh work before the trap can
  send).

## 108. How do settings come back to the trap?
- **Date:** 2026-11-21
- **Step:** propose
- **Decision:** As FieldMesh commands in the reply to an upload, confirmed the way the FieldHub
  confirms them. FieldMesh needs a new command type for trap settings.
- **Reason:** FieldMesh's existing way back to devices; no second channel.
- **Rejected:** A settings file the trap fetches from a web address (a second channel to secure and
  keep).

## 109. How are firmware updates installed?
- **Date:** 2026-11-21
- **Step:** propose
- **Decision:** As on the FieldHub: a manifest signed with the release key, the image written to the
  spare slot and checked, and a fall-back to the old firmware when the new one does not confirm
  itself. The fall-back is proven on the ESP32-S3 on the bench.
- **Reason:** The user's existing signed path; only the chip is new. It has run on the classic ESP32
  but not on the ESP32-S3 or over the mobile network with the real key.
- **Rejected:** A new update scheme for the trap (more to build and prove).

## 110. Does the trap check FieldMesh's server certificate?
- **Date:** 2026-11-21
- **Step:** propose
- **Decision:** Yes, unlike the FieldHub today.
- **Reason:** Otherwise the upload key and the update path can be intercepted.
- **Rejected:** No check, as on the FieldHub (an intercepted key lets others upload as the trap).

## 111. Where does the FieldMesh side get built?
- **Date:** 2026-11-21
- **Step:** propose
- **Decision:** One FieldMesh issue collects what the trap needs there: a command for trap settings,
  a release role for trap firmware, a way to release model files to traps (entry 106), and modelling
  the pass keys. Until it is done, the trap sends but takes nothing back.
- **Reason:** Keeps FieldMesh work in its own repository; the trap is not blocked from sending.
- **Rejected:** Building the FieldMesh side in this change (another repository, with its own
  workflow).

## 112. How long does the trap try to connect?
- **Date:** 2026-11-21
- **Step:** propose
- **Decision:** About three minutes; then it records a link fault and tries again at the next
  sending time.
- **Reason:** Weak coverage must not drain the battery.
- **Rejected:** Trying until it gets through (a trap at the edge of coverage could empty its pack).

## 113. Where does the trap's clock come from?
- **Date:** 2026-11-21
- **Step:** propose
- **Decision:** The trap sets its clock from FieldMesh's server time at each send.
- **Reason:** FieldMesh sends the time with every reply, so the clock no longer drifts over a
  season.
- **Rejected:** Setting the clock only at setup (drift over six months shifts pass times).

## 114. Where does the modem's antenna sit?
- **Date:** 2026-11-21
- **Step:** propose
- **Decision:** On the solar panel's stake, above the vegetation, with a cable to the trap.
- **Reason:** Inside the bucket at ground level the signal is weakest.
- **Rejected:** A flexible antenna inside the hood, as in Auris (weak signal at ground level).

## 115. Which firmware is updated over the link?
- **Date:** 2026-11-21
- **Step:** propose
- **Decision:** Only the camera controller's; the beam watcher's firmware changes at a visit.
- **Reason:** The watcher's logic is small and tested; updating it remotely needs extra wiring and a
  second fall-back.
- **Rejected:** The camera controller also reprogramming the watcher (wiring and a fall-back for a
  rarely changed part).

## 116. How large is the pack?
- **Date:** 2026-11-21
- **Step:** propose
- **Decision:** Two 18650 cells in parallel, as before. With the modem and the model the estimate
  rises to about 35 to 45 mAh a day, still more than five months without sun; the bench measures
  it.
- **Reason:** The same pack as Auris; the estimate leaves room, and entry 94 lets it grow if the
  bench measures more.
- **Rejected:** Three or four cells now (cost and space for a load not yet measured).

## 117. What runs the model on the trap?
- **Date:** 2026-11-21
- **Step:** propose
- **Decision:** TensorFlow Lite Micro, with the model in 8-bit form, which works with the Arduino
  framework on the ESP32-S3.
- **Reason:** Fits the firmware's tools.
- **Rejected:** Espressif's ESP-DL (needs ESP-IDF, against the firmware's framework).

## 118. How is the first model trained?
- **Date:** 2026-11-21
- **Step:** propose
- **Decision:** With Keras in a new `model/` folder, on the free pictures from California, Ohio,
  Indiana and the Australian set turned grey, then fine-tuned and checked on named bench pictures
  kept apart from training.
- **Reason:** Keras gives the 8-bit model for the trap directly; the bench pictures close the gap
  between others' colour pictures and the trap's infrared ones.
- **Rejected:** PyTorch, converted for the trap (an extra conversion step that can change the
  model).

## 119. How does the trap sit at a fence end?
- **Date:** 2026-11-21
- **Step:** propose
- **Decision:** As in the fence line, with a short piece of fence, about a bucket's width, beyond
  it; the sides of the fence keep their meaning.
- **Reason:** The same joints and the same directions in both placements; animals on either side
  are led to an opening.
- **Rejected:** The passage continuing the fence, with two short wings leading into one end
  (different joints, and directions that mean something else).

## 120. How do the settings describe the placement?
- **Date:** 2026-11-21
- **Step:** propose
- **Decision:** The settings note the placement as in the fence line or at a fence end, and describe
  side A in words, such as "pond side".
- **Reason:** Words are what surveyors write down; a bearing means little for "which side".
- **Rejected:** Side A as a compass bearing.

## 121. How does the review page know a pass was recorded in pilot mode?
- **Date:** 2026-11-21
- **Step:** propose
- **Decision:** Each pass record notes whether the trap was in pilot mode; the review page hides the
  model's type for those passes.
- **Reason:** Pilot mode can change over the link in mid-season.
- **Rejected:** Reading pilot mode once for the whole season from the card's settings (wrong for a
  season that changed mode).

## 122. What does the Camtrap DP export do with the model's types?
- **Date:** 2026-11-21
- **Step:** propose
- **Decision:** It uses people's groups and names; a pass nobody has sorted gets the model's type,
  marked as classified by machine with how sure the model was.
- **Reason:** Camtrap DP has fields for machine classifications, so nothing is passed off as a
  person's.
- **Rejected:** People's labels only, with unsorted passes left unclassified.
