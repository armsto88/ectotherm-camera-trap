// Bring-up of the beam watcher, following hardware/prototype/bring-up.md.
//
// Pulses each point's lasers 250 times a second, reads each photodiode with the lasers off and on,
// and prints the readings four times a second over the serial port, so beams can be aligned and
// load resistors chosen. Watches the PIR sensor, raises the wake line when a beam is broken or the
// PIR sensor fires, and answers the camera controller's status read over I2C, so the link can be
// checked from the camera board.
//
// The lasers are only ever on while a pulse is read; no command leaves them on.

#include <Arduino.h>
#include <Wire.h>

#include "beams.h"
#include "link.h"
#include BOARD_HEADER

namespace {

constexpr uint32_t PULSE_PERIOD_US = 4000;  // 250 pulses a second
constexpr uint16_t LASER_SETTLE_US = 4;     // from switching the lasers on to the first reading
constexpr uint32_t PRINT_PERIOD_MS = 250;
constexpr uint32_t WAKE_PULSE_MS = 10;

constexpr uint8_t GROUPS = board::POINTS + 1;  // the two points and the roof beam
constexpr uint8_t ROOF = board::POINTS;

struct Reading {
  uint16_t dark = 0;
  uint16_t lit = 0;
  bool interrupted = false;
};

BeamFilter filters[GROUPS][board::HEIGHTS];
Reading readings[GROUPS][board::HEIGHTS];
uint16_t pulse_us = 0;  // how long the last point's lasers were on

volatile uint8_t link_register = REG_STATUS;
volatile uint8_t pir_since_read = 0;

uint32_t last_pulse_us = 0;
uint32_t last_print_ms = 0;
uint32_t wake_until_ms = 0;
bool waking = false;
bool pir_before = false;

uint8_t beams_in(uint8_t group) { return group == ROOF ? 1 : board::HEIGHTS; }

uint8_t photodiode(uint8_t group, uint8_t height) {
  return group == ROOF ? board::ROOF_PHOTODIODE : board::PHOTODIODE[group][height];
}

uint8_t laser(uint8_t group) { return group == ROOF ? board::ROOF_LASER : board::LASERS[group]; }

void on_receive(int count) {
  if (count > 0) link_register = Wire.read();
  while (Wire.available()) Wire.read();
}

void on_request() {
  if (link_register != REG_STATUS) {
    Wire.write(static_cast<uint8_t>(0));
    return;
  }
  WatcherStatus status = {};
  status.now_ms = millis();
  status.pir_since_read = pir_since_read;
  pir_since_read = 0;
  Wire.write(reinterpret_cast<const uint8_t*>(&status), sizeof status);
}

void wake() {
  digitalWrite(board::WAKE, HIGH);
  wake_until_ms = millis() + WAKE_PULSE_MS;
  waking = true;
}

// Reads one group's photodiodes with its lasers off, then on; true when a beam became interrupted.
bool pulse(uint8_t group) {
  uint8_t n = beams_in(group);
  for (uint8_t h = 0; h < n; ++h) readings[group][h].dark = analogRead(photodiode(group, h));
  uint32_t on = micros();
  digitalWrite(laser(group), HIGH);
  delayMicroseconds(LASER_SETTLE_US);
  for (uint8_t h = 0; h < n; ++h) readings[group][h].lit = analogRead(photodiode(group, h));
  digitalWrite(laser(group), LOW);
  pulse_us = static_cast<uint16_t>(micros() - on);

  bool newly_interrupted = false;
  for (uint8_t h = 0; h < n; ++h) {
    Reading& r = readings[group][h];
    bool interrupted = filters[group][h].update(r.lit, r.dark);
    if (interrupted && !r.interrupted) newly_interrupted = true;
    r.interrupted = interrupted;
  }
  return newly_interrupted;
}

// One beam as "dark/lit" and a mark: . clear, X interrupted, ! saturated by outside light.
void print_beam(const Reading& r) {
  Serial.print(r.dark);
  Serial.print('/');
  Serial.print(r.lit);
  if (r.dark >= BeamFilter::SATURATED) {
    Serial.print("! ");
  } else {
    Serial.print(r.interrupted ? "X " : ". ");
  }
}

void print_readings() {
  static const char* const names[GROUPS] = {"A", "B", "roof"};
  for (uint8_t g = 0; g < GROUPS; ++g) {
    Serial.print(names[g]);
    Serial.print(": ");
    for (uint8_t h = 0; h < beams_in(g); ++h) print_beam(readings[g][h]);
    Serial.print(' ');
  }
  Serial.print("pir ");
  Serial.print(digitalRead(board::PIR) ? 1 : 0);
  Serial.print("  pulse ");
  Serial.print(pulse_us);
  Serial.println(" us");
}

}  // namespace

void setup() {
  for (uint8_t g = 0; g < GROUPS; ++g) {
    digitalWrite(laser(g), LOW);
    pinMode(laser(g), OUTPUT);
  }
  digitalWrite(board::WAKE, LOW);
  pinMode(board::WAKE, OUTPUT);
  pinMode(board::PIR, INPUT);

  Serial.begin(115200);
  Wire.begin(LINK_ADDRESS);
  Wire.onReceive(on_receive);
  Wire.onRequest(on_request);

  Serial.print("watcher bring-up on board ");
  Serial.println(board::NAME);
  Serial.println("each beam: dark/lit, then . clear, X interrupted, ! saturated");
}

void loop() {
  uint32_t now_us = micros();
  if (now_us - last_pulse_us >= PULSE_PERIOD_US) {
    last_pulse_us = now_us;
    bool broken = false;
    for (uint8_t g = 0; g < GROUPS; ++g) broken |= pulse(g);
    if (broken) wake();
  }

  bool pir = digitalRead(board::PIR);
  if (pir && !pir_before) {
    pir_since_read = 1;
    wake();
  }
  pir_before = pir;

  uint32_t now_ms = millis();
  if (waking && static_cast<int32_t>(now_ms - wake_until_ms) >= 0) {
    digitalWrite(board::WAKE, LOW);
    waking = false;
  }
  if (now_ms - last_print_ms >= PRINT_PERIOD_MS) {
    last_print_ms = now_ms;
    print_readings();
  }
}
