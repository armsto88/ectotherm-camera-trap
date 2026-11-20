# pass-pictures

## Purpose
The trap photographs every pass it notices, the same way every time and sharp enough to identify the
animal as far as a good photo allows, and photographs its empty view once a day, so that species can
be named from pictures instead of from animals in a bucket.

## Terms
- **View:** the part of the passage floor the camera sees from above.
- **Identifiable:** sharp and lit well enough that an expert could name the species from the picture
  wherever the species can be told apart from a sharp photo of a free animal from above, and
  otherwise the nearest group.
- **Empty view:** the view with no animal in the passage.

## ADDED Requirements

### Requirement: Pictures of every pass
The trap shall take pictures of each pass it notices while the animal is inside the view.

#### Scenario: An animal walking through is photographed <!-- id: 0f31246f -->
- **Given** the trap is waiting
- **When** an animal crosses a beam point and walks on through the passage
- **Then** at least one picture of the pass shows the whole animal inside the view

### Requirement: The same way every time
The trap shall take every picture from the same place above the passage floor and light it with its
own infrared light, by day and by night, so that pictures do not depend on daylight, weather or the
time of day.

#### Scenario: The same animal at noon and at midnight <!-- id: 4d3defba -->
- **Given** the same model animal at the same spot in the view
- **When** the trap photographs it at noon and at midnight
- **Then** both pictures show the animal at the same scale and equally sharp
- **And** neither picture is too dark or too bright to see the animal's pattern

### Requirement: Identifiable pictures
Pictures shall be identifiable for animals from 3 cm body length upwards.

#### Scenario: An expert names a known animal from its picture <!-- id: d3749ed6 -->
- **Given** a known animal of 3 cm body length or more, of a species that can be told apart from a
  sharp photo from above
- **When** it passes through the trap
- **Then** an expert who does not know which animal it was names its species from the trap's
  pictures

### Requirement: No visible light
The trap shall emit no visible light when it takes pictures, unless the controlled tests add colour.

#### Scenario: Pictures taken without visible light <!-- id: 64488b5b -->
- **Given** a trap built without colour pictures
- **When** it photographs a pass by day or by night
- **Then** no visible light comes from the trap

### Requirement: Daily picture of the empty view
Once a day the trap shall photograph its empty view and store the picture with its date and time,
so that a dirty lens, spider webs, flooding or a blocked passage show up in the records.

#### Scenario: The daily picture is taken <!-- id: 5bcc1dab -->
- **Given** the passage is empty at the time of the daily picture
- **When** that time comes
- **Then** the trap photographs the empty view and stores the picture with its date and time

#### Scenario: An animal is in the passage at the time of the daily picture <!-- id: cc78920a -->
- **Given** an animal is in the passage at the time of the daily picture
- **When** that time comes
- **Then** the trap waits until the passage is empty before it takes the daily picture
