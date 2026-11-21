# Prototype bring-up checklist

Brings the prototype up one part at a time, so that a fault shows in the part just added. The
camera board comes up first with the OV2640, a camera known to work on such boards, and only then
with the OV5640, so that a fault of the OV5640 is not taken for one of the board. No bench result
comes from the OV2640.

The prototype is done when every step passes. Tick the boxes in your copy and note the date.

[parts.md](parts.md) lists the parts, [wiring.md](wiring.md) every connection. The commands run
from the repository with PlatformIO's `pio` (`~/.platformio/penv/bin/pio` if it is not on the
path).

## Before you start: the lasers

The infrared laser modules give invisible beams of up to 5 mW, which can harm an eye without being
seen. The bring-up program switches them on only for the moment of each reading, and the resistors
on the switches keep them off while the watcher is not running, but a wiring fault can leave one on.
Never look along a beam or into a module, and keep the beams below eye level.

## 1. Camera board alone

Read the module's name on its metal can. N8R8 or N16R8 means octal PSRAM, which the `prototype`
build expects. For N8R2 or N16R2, set `board_build.arduino.memory_type = qio_qspi` in
`firmware/camera/platformio.ini`. A module without R in its name has no PSRAM and cannot hold a
5 megapixel picture.

```
cd firmware/camera
pio run -e prototype -t upload -t monitor
```

Type `p` and Enter.

- [ ] The menu appears and `p` shows PSRAM of about 8 MB (8388608 bytes).

## 2. Memory card

Put in a FAT32 card. Type `s`.

- [ ] `card written and read back`.

## 3. First light with the OV2640

Unplug the board. Open the connector's latch, slide the ribbon in with its contacts facing the
board's contacts, close the latch. Plug in, type `c`. Copy `/bringup/OV2640-picture-1.jpg` from the
card and look at it.

- [ ] `camera OV2640`, a picture saved, and it shows the scene.

If the camera does not start, reseat the ribbon. If it still fails, the board's camera pins differ
from `board_prototype.h`: compare them with the seller's pin map (often a file `camera_pins.h`).

## 4. The OV5640

Unplug the board and swap in the OV5640.

- [ ] Its ribbon fits the 24-pin connector, and the latch holds it.
- [ ] Type `c`: `camera OV5640`, a picture of 2560 × 1920 saved, and it shows the scene.
- [ ] In a dim room, hold down a button of a TV remote control pointed at the lens and type `b`. At
  least one of the five `OV5640-remote-*.jpg` pictures shows the remote's LED as a bright spot. A
  camera with an infrared-cut filter shows nothing or a faint dot.

If the module does not fit or shows no spot, order an OV5640 without infrared filter for the 24-pin
connector; the bench tests wait for it.

## 5. Clock

Wire the clock module. Type `i`, then set the clock to UTC (the trap's settings hold the offset to
local time), then read it:

```
T 2026-11-21 14:05:00
t
```

Unplug the board for a minute, plug it in again and type `t`.

- [ ] `i` shows `0x68 clock (DS3231)` (and `0x57` for the module's EEPROM).
- [ ] The clock is set, and after the minute without power it still runs, with no note that it
  stopped.

## 6. Infrared LEDs

Wire the 940 nm LEDs and their switch, and switch on the 5 V supply. In a dark room, with the
camera about 25 cm above a floor, type `f`.

- [ ] `OV5640-lit-*.jpg` shows the floor; `OV5640-unlit-*.jpg` is dark or only noise.

Seen through a phone camera, 850 nm LEDs glow dull red and 940 nm LEDs faintly or not at all.

## 7. Watcher

Solder the ATtiny3216 onto its adapter, with 100 nF across pins 1 and 20, and wire it to the 3.3 V
rail and the two USB-serial adapters. With the UPDI adapter on `/dev/ttyUSB0` and the serial
adapter on `/dev/ttyUSB1` (`pio device list` shows them):

```
cd firmware/watcher
pio run -e prototype -t fuses --upload-port /dev/ttyUSB0
pio run -e prototype -t upload --upload-port /dev/ttyUSB0
pio device monitor -e prototype --port /dev/ttyUSB1
```

The first command sets the chip's clock to 10 MHz and its brown-out level once; it is not needed
again.

- [ ] The upload succeeds and a line of readings appears four times a second, ending in the
  lasers' on-time (`pulse … us`).

## 8. Beams

Wire point A first: its three lasers on one switch and its three photodiodes, each with 2.2 kΩ.
Each beam shows as `dark/lit` and a mark: `.` clear, `X` interrupted, `!` swamped by outside
light.

Aim each laser at its photodiode until `lit` is well above `dark`. If `lit` reaches 1000 or more,
lower the photodiode's resistor (1 kΩ); if `lit` is less than about 100 above `dark`, raise it
(4.7 or 10 kΩ) or aim again. Then:

- [ ] Every beam of point A shows `.` when clear, with `lit` 100 or more above `dark`.
- [ ] Blocking one beam with a card, near the laser and then near the photodiode, shows `X` on that
  beam only.
- [ ] A torch or daylight shone in at the passage end raises `dark` but leaves the beams at `.`,
  with no `!`.

Repeat for point B, and for the roof beam once it is fitted.

- [ ] Point B passes the same three checks.
- [ ] The roof beam passes them (or waits for the roof-laser test).

## 9. PIR sensor

Wire the PIR sensor and move a hand about 30 cm below it.

- [ ] The watcher's line shows `pir 1`, and `pir 0` again a few seconds after the movement stops.

## 10. The link between the boards

With the watcher running, on the camera board's monitor:

- [ ] `i` shows `0x42 watcher` beside the clock.
- [ ] `a` twice: the watcher's clock has moved on between the reads; after a movement in front of
  the PIR sensor, `PIR fired since last read: yes`.
- [ ] `w`, then break a beam: `wake line raised`.
- [ ] `z`, then break a beam within a minute: the board restarts with `woken by the watcher's wake
  line`.
