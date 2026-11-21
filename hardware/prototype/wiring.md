# Prototype wiring

Every connection between the prototype's parts. The pins are the ones in
`firmware/camera/include/board_prototype.h` and `firmware/watcher/include/board_prototype.h`; change
both a header and this list together.

## Where the parts sit

- **Beams:** the lasers on one wall of the passage, the photodiodes facing them on the other, 150 mm
  apart; at 4, 12 and 25 mm above the floor; one beam point about 20 mm in from each end. In the
  printed insert these are the beam walls' sockets ([../insert/](../insert/)); in a simpler box, holes
  of 6.2 mm (lasers) and 5.2 mm (photodiodes) at the same places. A piece of black tape with a
  1.5 mm hole over each photodiode keeps out daylight and the neighbouring beams.
- **Roof beam:** where the roof-laser test puts it; it can wait until that test.
- **Camera:** looking straight down at the floor between the beam points, 200 to 300 mm above it,
  with the four infrared LEDs beside the lens, pointing down.
- **PIR sensor:** above the passage, looking down at the floor.
- **Boards:** outside the passage, wired in.

Point A is the beam point nearer side A, point B the one nearer side B.

## Supplies

| Rail | From | Feeds |
|---|---|---|
| 3.3 V | the camera board's 3V3 pin | watcher, clock module, PIR sensor, photodiodes |
| 5 V | the separate 5 V supply | laser modules, infrared LEDs |
| Ground | all grounds joined | the camera board, the 5 V supply and every part |

The camera board itself runs from its USB port, the one wired to its USB-serial chip, which also
uploads its program and shows its output.

## Camera board

| Board pin | Connects to |
|---|---|
| 3V3 | 3.3 V rail |
| GND | ground |
| GPIO 41 (I2C SDA) | clock module SDA; watcher pin 10 (PB1) |
| GPIO 42 (I2C SCL) | clock module SCL; watcher pin 11 (PB0) |
| GPIO 14 (wake, input) | watcher pin 15 (PC3); 100 kΩ to ground |
| GPIO 21 (clock alarm, input) | clock module SQW (also marked INT) |
| GPIO 1 (infrared LEDs) | 100 Ω to the MOSFET's gate |

The camera plugs into the 24-pin connector, the memory card into the slot.

## Watcher (ATtiny3216, SOIC-20)

Pin numbers are the SOIC-20 package's, as the adapter board's pads follow them. Check pin 1 (VDD)
and pin 20 (GND) against the datasheet's pinout before first power.

| Pin | Port | Connects to |
|---|---|---|
| 1 | VDD | 3.3 V rail; 100 nF to pin 20 |
| 2 | PA4 | point B, lowest photodiode |
| 3 | PA5 | point B, middle photodiode |
| 4 | PA6 | point B, top photodiode |
| 5 | PA7 | roof photodiode |
| 6 | PB5 | free |
| 7 | PB4 | PIR sensor output |
| 8 | PB3 (serial RX) | free, or the serial adapter's TX |
| 9 | PB2 (serial TX) | the serial adapter's RX |
| 10 | PB1 (I2C SDA) | camera board GPIO 41 |
| 11 | PB0 (I2C SCL) | camera board GPIO 42 |
| 12 | PC0 | point A laser switch, through 1 kΩ to the transistor's base |
| 13 | PC1 | point B laser switch, likewise |
| 14 | PC2 | roof laser switch, likewise |
| 15 | PC3 | wake line, to camera board GPIO 14 |
| 16 | PA0 (UPDI) | the UPDI adapter |
| 17 | PA1 | point A, lowest photodiode |
| 18 | PA2 | point A, middle photodiode |
| 19 | PA3 | point A, top photodiode |
| 20 | GND | ground |

## Photodiodes (each of seven)

- Cathode to the 3.3 V rail (reverse biased; the cathode as its datasheet marks it).
- Anode to its watcher pin, and through its load resistor to ground. Start with 2.2 kΩ; bring-up
  step 8 says when to change it.

## Laser switches (one per point, one for the roof)

- Each laser module's + to the 5 V rail (or its rated supply, if lower), its − to the transistor's
  collector. A point's three modules share one transistor.
- Emitter to ground.
- Base through 1 kΩ to the watcher pin, and through 10 kΩ to ground, so the lasers stay off while
  the watcher is not running.
- 100 µF across the 5 V rail near the switches.

## Infrared LEDs

- Each LED's anode through its own 39 Ω resistor to the 5 V rail; the four cathodes together to the
  MOSFET's drain.
- Source to ground.
- Gate through 100 Ω to camera board GPIO 1, and through 100 kΩ to ground.
- 470 µF across the 5 V rail near the LEDs.

The 850 nm LEDs take the same resistors.

## Clock module

| Module pin | Connects to |
|---|---|
| VCC | 3.3 V rail |
| GND | ground |
| SDA | camera board GPIO 41 |
| SCL | camera board GPIO 42 |
| SQW (INT) | camera board GPIO 21 |

The module's own pull-up resistors serve the whole I2C bus.

## PIR sensor

| Sensor pin | Connects to |
|---|---|
| VCC | 3.3 V rail (an HC-SR501: the 5 V rail) |
| GND | ground |
| OUT | watcher pin 7 (PB4) |

## USB-serial adapters (for the watcher)

| Adapter | Pin | Connects to |
|---|---|---|
| UPDI programmer | GND | ground |
| | RX | watcher pin 16 (UPDI), directly |
| | TX | watcher pin 16 (UPDI), through 4.7 kΩ |
| Serial output | GND | ground |
| | RX | watcher pin 9 (PB2) |

Neither adapter's 3.3 V or 5 V pin is connected; the watcher runs from the 3.3 V rail.
