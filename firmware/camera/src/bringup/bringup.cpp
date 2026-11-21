// Bring-up of the camera controller, following hardware/prototype/bring-up.md.
//
// A menu over the serial port: type a letter and press Enter. Each check reports what it found;
// pictures go to /bringup/ on the memory card, to be looked at on a computer.

#include <Arduino.h>
#include <FS.h>
#include <SD_MMC.h>
#include <Wire.h>
#include <esp_camera.h>
#include <esp_sleep.h>

#include "link.h"
#include BOARD_HEADER

namespace {

constexpr uint8_t CLOCK_ADDRESS = 0x68;   // DS3231
constexpr uint8_t EEPROM_ADDRESS = 0x57;  // the EEPROM on common DS3231 modules
constexpr uint32_t SLEEP_LIMIT_S = 60;
constexpr int FRAMES_TO_SETTLE = 2;  // frames dropped after the light changes

bool card_ready = false;
bool camera_ready = false;
const char* sensor_name = "camera";

void help() {
  Serial.println();
  Serial.println("p  chip, flash and PSRAM");
  Serial.println("s  memory card: mount, write, read back");
  Serial.println("c  one picture to the card");
  Serial.println("b  five pictures, 0.3 s apart (infrared remote check)");
  Serial.println("f  a picture without, then with the infrared LEDs");
  Serial.println("i  look for the clock and the watcher on I2C");
  Serial.println("t  read the clock");
  Serial.println("T YYYY-MM-DD HH:MM:SS  set the clock");
  Serial.println("a  read the watcher's status");
  Serial.println("w  watch the wake line for 10 s");
  Serial.println("z  deep sleep until the watcher wakes the board, at most 60 s");
}

void chip() {
  Serial.printf("board %s, %s rev %d, %d cores at %d MHz\n", board::NAME, ESP.getChipModel(),
                ESP.getChipRevision(), ESP.getChipCores(), ESP.getCpuFreqMHz());
  Serial.printf("flash %u bytes\n", ESP.getFlashChipSize());
  Serial.printf("PSRAM %u bytes, %u free\n", ESP.getPsramSize(), ESP.getFreePsram());
  if (ESP.getPsramSize() == 0) Serial.println("FAIL: no PSRAM found");
}

bool mount_card() {
  if (card_ready) return true;
  SD_MMC.setPins(board::SD_CLK, board::SD_CMD, board::SD_D0);
  if (!SD_MMC.begin("/sdcard", true)) {
    Serial.println("FAIL: no memory card mounted (is one in, formatted FAT32?)");
    return false;
  }
  SD_MMC.mkdir("/bringup");
  card_ready = true;
  return true;
}

void card() {
  if (!mount_card()) return;
  Serial.printf("card %llu MB, %llu MB used\n", SD_MMC.cardSize() >> 20, SD_MMC.usedBytes() >> 20);
  const char* path = "/bringup/card-check.txt";
  const char* text = "written by the camera board's bring-up\n";
  File out = SD_MMC.open(path, FILE_WRITE);
  if (!out || out.print(text) != strlen(text)) {
    Serial.println("FAIL: could not write to the card");
    return;
  }
  out.close();
  File in = SD_MMC.open(path, FILE_READ);
  String back = in ? in.readString() : String();
  in.close();
  Serial.println(back == text ? "card written and read back" : "FAIL: read back differs");
}

bool start_camera() {
  if (camera_ready) return true;
  camera_config_t config = {};
  config.pin_pwdn = board::CAM_PWDN;
  config.pin_reset = board::CAM_RESET;
  config.pin_xclk = board::CAM_XCLK;
  config.pin_sccb_sda = board::CAM_SIOD;
  config.pin_sccb_scl = board::CAM_SIOC;
  config.pin_d0 = board::CAM_D[0];
  config.pin_d1 = board::CAM_D[1];
  config.pin_d2 = board::CAM_D[2];
  config.pin_d3 = board::CAM_D[3];
  config.pin_d4 = board::CAM_D[4];
  config.pin_d5 = board::CAM_D[5];
  config.pin_d6 = board::CAM_D[6];
  config.pin_d7 = board::CAM_D[7];
  config.pin_vsync = board::CAM_VSYNC;
  config.pin_href = board::CAM_HREF;
  config.pin_pclk = board::CAM_PCLK;
  config.xclk_freq_hz = 20000000;
  config.ledc_timer = LEDC_TIMER_0;
  config.ledc_channel = LEDC_CHANNEL_0;
  config.pixel_format = PIXFORMAT_JPEG;
  config.frame_size = FRAMESIZE_QSXGA;  // the driver lowers it to the sensor's largest
  config.jpeg_quality = 10;
  config.fb_count = 1;
  config.fb_location = CAMERA_FB_IN_PSRAM;
  config.grab_mode = CAMERA_GRAB_LATEST;
  esp_err_t err = esp_camera_init(&config);
  if (err != ESP_OK) {
    Serial.printf("FAIL: camera did not start (error 0x%x); check the ribbon and the pin map\n",
                  err);
    return false;
  }
  sensor_t* sensor = esp_camera_sensor_get();
  camera_sensor_info_t* info = esp_camera_sensor_get_info(&sensor->id);
  sensor_name = info ? info->name : "unknown";
  Serial.printf("camera %s (id 0x%x)\n", sensor_name, sensor->id.PID);
  camera_ready = true;
  return true;
}

void drop_frames(int n) {
  for (int i = 0; i < n; ++i) {
    camera_fb_t* frame = esp_camera_fb_get();
    if (frame) esp_camera_fb_return(frame);
  }
}

String next_path(const char* label) {
  for (int n = 1;; ++n) {
    String path = String("/bringup/") + sensor_name + "-" + label + "-" + n + ".jpg";
    if (!SD_MMC.exists(path)) return path;
  }
}

bool take_picture(const char* label) {
  uint32_t start = millis();
  camera_fb_t* frame = esp_camera_fb_get();
  if (!frame) {
    Serial.println("FAIL: no picture from the camera");
    return false;
  }
  uint32_t taken = millis();
  String path = next_path(label);
  File out = SD_MMC.open(path, FILE_WRITE);
  size_t written = out ? out.write(frame->buf, frame->len) : 0;
  out.close();
  uint32_t saved = millis();
  Serial.printf("%s: %ux%u, %u bytes, taken in %u ms, saved in %u ms\n", path.c_str(), frame->width,
                frame->height, frame->len, taken - start, saved - taken);
  bool ok = written == frame->len;
  esp_camera_fb_return(frame);
  if (!ok) Serial.println("FAIL: picture not fully written");
  return ok;
}

void picture() {
  if (!mount_card() || !start_camera()) return;
  drop_frames(FRAMES_TO_SETTLE);
  take_picture("picture");
}

void burst() {
  if (!mount_card() || !start_camera()) return;
  Serial.println("hold a remote control's button down, pointed at the lens");
  for (int i = 0; i < 5; ++i) {
    if (!take_picture("remote")) return;
    delay(300);
  }
}

void flash() {
  if (!mount_card() || !start_camera()) return;
  digitalWrite(board::IR_LEDS, LOW);
  drop_frames(FRAMES_TO_SETTLE);
  take_picture("unlit");
  digitalWrite(board::IR_LEDS, HIGH);
  drop_frames(FRAMES_TO_SETTLE);
  take_picture("lit");
  digitalWrite(board::IR_LEDS, LOW);
  Serial.println("compare the two pictures: in the dark only the lit one should show the floor");
}

void scan() {
  int found = 0;
  for (uint8_t address = 1; address < 127; ++address) {
    Wire.beginTransmission(address);
    if (Wire.endTransmission() != 0) continue;
    ++found;
    const char* what = address == CLOCK_ADDRESS    ? "clock (DS3231)"
                       : address == EEPROM_ADDRESS ? "the clock module's EEPROM"
                       : address == LINK_ADDRESS   ? "watcher"
                                                   : "unknown";
    Serial.printf("0x%02x %s\n", address, what);
  }
  if (found == 0) Serial.println("FAIL: nothing answers on I2C");
}

uint8_t from_bcd(uint8_t v) { return (v >> 4) * 10 + (v & 0x0f); }
uint8_t to_bcd(int v) { return static_cast<uint8_t>(((v / 10) << 4) | (v % 10)); }

bool read_clock_registers(uint8_t first, uint8_t* out, size_t n) {
  Wire.beginTransmission(CLOCK_ADDRESS);
  Wire.write(first);
  if (Wire.endTransmission(false) != 0) return false;
  if (Wire.requestFrom(CLOCK_ADDRESS, static_cast<uint8_t>(n)) != n) return false;
  for (size_t i = 0; i < n; ++i) out[i] = Wire.read();
  return true;
}

void read_clock() {
  uint8_t r[7];
  uint8_t status = 0;
  if (!read_clock_registers(0x00, r, sizeof r) || !read_clock_registers(0x0f, &status, 1)) {
    Serial.println("FAIL: the clock does not answer");
    return;
  }
  Serial.printf("clock 20%02u-%02u-%02u %02u:%02u:%02u\n", from_bcd(r[6]), from_bcd(r[5] & 0x1f),
                from_bcd(r[4]), from_bcd(r[2] & 0x3f), from_bcd(r[1]), from_bcd(r[0] & 0x7f));
  if (status & 0x80) Serial.println("the clock stopped since it was last set: set it with T");
}

void set_clock(const String& line) {
  int year, month, day, hour, minute, second;
  if (sscanf(line.c_str(), "T %d-%d-%d %d:%d:%d", &year, &month, &day, &hour, &minute, &second) !=
      6) {
    Serial.println("write it as: T 2026-11-21 14:05:00");
    return;
  }
  Wire.beginTransmission(CLOCK_ADDRESS);
  Wire.write(0x00);
  Wire.write(to_bcd(second));
  Wire.write(to_bcd(minute));
  Wire.write(to_bcd(hour));  // 24-hour mode
  Wire.write(1);             // day of the week, unused
  Wire.write(to_bcd(day));
  Wire.write(to_bcd(month));
  Wire.write(to_bcd(year % 100));
  bool ok = Wire.endTransmission() == 0;
  uint8_t status = 0;
  ok = ok && read_clock_registers(0x0f, &status, 1);
  Wire.beginTransmission(CLOCK_ADDRESS);
  Wire.write(0x0f);
  Wire.write(status & 0x7f);  // clear the oscillator-stopped flag
  ok = ok && Wire.endTransmission() == 0;
  if (!ok) {
    Serial.println("FAIL: the clock does not answer");
    return;
  }
  read_clock();
}

void watcher_status() {
  WatcherStatus status;
  Wire.beginTransmission(LINK_ADDRESS);
  Wire.write(REG_STATUS);
  if (Wire.endTransmission(false) != 0 ||
      Wire.requestFrom(LINK_ADDRESS, static_cast<uint8_t>(sizeof status)) != sizeof status) {
    Serial.println("FAIL: the watcher does not answer");
    return;
  }
  Wire.readBytes(reinterpret_cast<uint8_t*>(&status), sizeof status);
  Serial.printf("watcher clock %u ms, PIR fired since last read: %s\n", status.now_ms,
                status.pir_since_read ? "yes" : "no");
}

void watch_wake_line() {
  Serial.println("break a beam or move in front of the PIR sensor");
  uint32_t start = millis();
  bool before = digitalRead(board::WAKE);
  int rises = 0;
  while (millis() - start < 10000) {
    bool now = digitalRead(board::WAKE);
    if (now && !before) {
      ++rises;
      uint32_t at = millis() - start;
      Serial.printf("wake line raised at %u ms\n", at);
    }
    before = now;
  }
  if (rises == 0) Serial.println("the wake line was not raised");
}

void sleep_until_woken() {
  Serial.println("sleeping; break a beam to wake the board");
  Serial.flush();
  if (camera_ready) esp_camera_deinit();
  if (card_ready) SD_MMC.end();
  esp_sleep_enable_ext0_wakeup(static_cast<gpio_num_t>(board::WAKE), 1);
  esp_sleep_enable_timer_wakeup(SLEEP_LIMIT_S * 1000000ULL);
  esp_deep_sleep_start();
}

void report_wake_cause() {
  switch (esp_sleep_get_wakeup_cause()) {
    case ESP_SLEEP_WAKEUP_EXT0:
      Serial.println("woken by the watcher's wake line");
      break;
    case ESP_SLEEP_WAKEUP_TIMER:
      Serial.println("FAIL: woken by the time limit, not by the watcher");
      break;
    default:
      break;
  }
}

}  // namespace

void setup() {
  digitalWrite(board::IR_LEDS, LOW);
  pinMode(board::IR_LEDS, OUTPUT);
  pinMode(board::WAKE, INPUT);
  pinMode(board::CLOCK_ALARM, INPUT_PULLUP);
  Serial.begin(115200);
  Wire.begin(board::I2C_SDA, board::I2C_SCL, 100000);
  delay(500);
  Serial.println();
  Serial.printf("camera board bring-up on board %s\n", board::NAME);
  report_wake_cause();
  help();
}

void loop() {
  if (!Serial.available()) return;
  String line = Serial.readStringUntil('\n');
  line.trim();
  if (line.isEmpty()) return;
  switch (line[0]) {
    case 'p': chip(); break;
    case 's': card(); break;
    case 'c': picture(); break;
    case 'b': burst(); break;
    case 'f': flash(); break;
    case 'i': scan(); break;
    case 't': read_clock(); break;
    case 'T': set_clock(line); break;
    case 'a': watcher_status(); break;
    case 'w': watch_wake_line(); break;
    case 'z': sleep_until_woken(); break;
    default: help(); break;
  }
}
