---
areas: [firmware]
---
# Firmware is built with PlatformIO and the Arduino framework

## Context
The trap has two firmwares, the beam watcher's and the camera controller's. The user's other ESP32
work, FieldMesh, uses PlatformIO with the Arduino framework.

## Options considered
- PlatformIO and the Arduino framework for both, megaTinyCore for the watcher.
- ESP-IDF directly: rejected, a second toolchain to learn and maintain.

## Decision
Both firmwares are PlatformIO projects with the Arduino framework. Their logic lives in libraries
without hardware calls, built and tested on the computer in a `native` environment.

## Consequences
- The same tools and habits as FieldMesh.
- Lower-level ESP32-S3 features are reached through the ESP-IDF calls the Arduino core exposes.
- Logic kept free of hardware calls is what makes it testable on the computer.
