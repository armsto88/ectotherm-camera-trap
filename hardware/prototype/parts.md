# Prototype parts list

The prototype runs the whole chain on development boards with the trap's own chips, so that the
bench tests answer for the trap: beams, beam watcher, waking the camera controller, pictures and the
memory card. [wiring.md](wiring.md) says how the parts connect, and [bring-up.md](bring-up.md) checks
each part in turn.

Part numbers are examples that fit; any part with the same values does too.

## Camera controller

| Part | Number | Notes |
|---|---|---|
| ESP32-S3-WROOM camera board with microSD slot and 24-pin camera connector | 1 | the user's; the module must have octal PSRAM (N8R8 or N16R8 on its metal can) |
| OV2640 camera module, 24-pin ribbon | 1 | the user's; for first light only, no bench result comes from it |
| OV5640 camera module, 24-pin ribbon, without infrared-cut filter | 1 | the user's, if it fits and has no filter (bring-up step 4); otherwise order one sold as "no IR filter" or "night vision" for ESP32 boards |
| microSD card, 32 GB or less, FAT32 | 1 | |

## Beam watcher

| Part | Number | Notes |
|---|---|---|
| ATtiny3216-SN (SOIC-20) | 2 | one spare |
| SOIC-20 to DIP-20 adapter board | 2 | |
| 100 nF ceramic capacitor | 2 | across the chip's supply pins |
| USB-serial adapter with 3.3 V logic (CH340 or CP2102) | 2 | one programs the chip over UPDI, one shows its serial output |
| 4.7 kΩ resistor | 1 | turns one adapter into a UPDI programmer |

## Beams

Six beams, three heights at each of two points, and one for the roof-laser test.

| Part | Number | Notes |
|---|---|---|
| Laser dot module, 6 mm barrel, 940 nm, 3 to 5 V, 5 mW or less | 7 + 2 spare | 850 or 980 nm if 940 nm cannot be found; the photodiodes see all three |
| Red laser dot module, 650 nm, 6 mm barrel | 1 | optional, for aiming by eye before fitting an infrared one |
| Photodiode, 5 mm, with daylight filter (Osram SFH 203 FA) | 7 + 2 spare | |
| Resistors 1 kΩ, 2.2 kΩ, 4.7 kΩ, 10 kΩ | 7 of each | photodiode loads, chosen at bring-up |
| NPN transistor (BC337 or 2N2222) | 3 | laser switches: point A, point B, roof |
| 1 kΩ resistor | 3 | transistor bases |
| 10 kΩ resistor | 3 | keep the lasers off while the watcher is not running |
| 100 µF electrolytic capacitor, 10 V | 1 | on the lasers' supply |
| Strip board | 3 small pieces | one per wall, one for the watcher |
| Black tape or card | | a 1.5 mm hole in front of each photodiode |

## Infrared light

| Part | Number | Notes |
|---|---|---|
| Infrared LED, 5 mm, 940 nm (Vishay TSAL6200) | 4 | |
| Infrared LED, 5 mm, 850 nm (Vishay TSHG6200) | 4 | for the 940 against 850 nm test; fit one set at a time |
| 39 Ω resistor, 0.5 W | 4 | one per LED, about 100 mA each from 5 V |
| Logic-level N-channel MOSFET (IRLZ44N) | 1 | switches the LEDs from a 3.3 V pin |
| 100 Ω and 100 kΩ resistors | 1 each | gate resistor and gate pull-down |
| 470 µF electrolytic capacitor, 10 V | 1 | on the LEDs' supply |

## Other parts

| Part | Number | Notes |
|---|---|---|
| PIR sensor module (AM312) | 1 | runs on 3.3 V; an HC-SR501 also works, fed from 5 V, as its output is 3.3 V |
| DS3231 clock module (ZS-042 or alike) with a CR2032 cell | 1 | fed from 3.3 V, its cell-charging path stays harmless |
| 100 kΩ resistor | 1 | holds the wake line low while the watcher is off |
| 5 V supply, 2 A | 1 | lasers and infrared LEDs; a bench supply or a USB power bank with a USB breakout |
| Breadboard, jumper wires, multimeter | | |
