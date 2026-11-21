#include "records.h"

#include <inttypes.h>
#include <math.h>
#include <stdarg.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

namespace {

// Builds one line of text in a fixed buffer; once something does not fit, the line is empty and
// its length 0.
class Text {
 public:
  Text(char* out, size_t size) : out_(out), size_(size) {
    if (size_ > 0) out_[0] = '\0';
  }

  void add(const char* format, ...) __attribute__((format(printf, 2, 3))) {
    if (!ok_) return;
    va_list args;
    va_start(args, format);
    const int n = vsnprintf(out_ + n_, size_ - n_, format, args);
    va_end(args);
    if (n < 0 || n_ + static_cast<size_t>(n) >= size_) {
      ok_ = false;
    } else {
      n_ += static_cast<size_t>(n);
    }
  }

  void add_char(char ch) {
    if (!ok_) return;
    if (n_ + 1 >= size_) {
      ok_ = false;
      return;
    }
    out_[n_++] = ch;
    out_[n_] = '\0';
  }

  // A CSV field, quoted with quotes doubled when it holds a comma, quote or line break.
  void add_csv_field(const char* s) {
    const char* d = s ? s : "";
    const bool quote = strpbrk(d, ",\"\r\n") != nullptr;
    if (quote) add_char('"');
    for (; *d; ++d) {
      if (*d == '"') add_char('"');
      add_char(*d);
    }
    if (quote) add_char('"');
  }

  // A JSON string in quotes; quotes and backslashes escaped, control characters left out.
  void add_json_string(const char* s) {
    add_char('"');
    for (const char* d = s ? s : ""; *d; ++d) {
      if (static_cast<unsigned char>(*d) < 0x20) continue;
      if (*d == '"' || *d == '\\') add_char('\\');
      add_char(*d);
    }
    add_char('"');
  }

  size_t done() {
    if (ok_) return n_;
    if (size_ > 0) out_[0] = '\0';
    return 0;
  }

 private:
  char* out_;
  size_t size_;
  size_t n_ = 0;
  bool ok_ = true;
};

// Date of a day number counted from 1970-01-01 (proleptic Gregorian calendar).
void civil_from_days(int64_t z, int* year, unsigned* month, unsigned* day) {
  z += 719468;
  const int64_t era = (z >= 0 ? z : z - 146096) / 146097;
  const unsigned doe = static_cast<unsigned>(z - era * 146097);
  const unsigned yoe = (doe - doe / 1460 + doe / 36524 - doe / 146096) / 365;
  const unsigned doy = doe - (365 * yoe + yoe / 4 - yoe / 100);
  const unsigned mp = (5 * doy + 2) / 153;
  *day = doy - (153 * mp + 2) / 5 + 1;
  *month = mp < 10 ? mp + 3 : mp - 9;
  *year = static_cast<int>(static_cast<int64_t>(yoe) + era * 400 + (*month <= 2 ? 1 : 0));
}

void format_date(int64_t days, char out[11]) {
  int y;
  unsigned m, d;
  civil_from_days(days, &y, &m, &d);
  snprintf(out, 11, "%04d-%02u-%02u", y, m, d);
}

// ISO 8601 in UTC, such as 2026-05-14T21:05:09Z.
void format_utc(uint32_t utc_s, char out[21]) {
  const int64_t days = utc_s / 86400;
  const uint32_t secs = utc_s % 86400;
  char date[11];
  format_date(days, date);
  snprintf(out, 21, "%sT%02" PRIu32 ":%02" PRIu32 ":%02" PRIu32 "Z", date, secs / 3600,
           (secs / 60) % 60, secs % 60);
}

// Day number counted from 1970-01-01 of a date (proleptic Gregorian calendar).
int64_t days_from_civil(int year, unsigned month, unsigned day) {
  year -= month <= 2 ? 1 : 0;
  const int64_t era = (year >= 0 ? year : year - 399) / 400;
  const unsigned yoe = static_cast<unsigned>(year - era * 400);
  const unsigned doy = (153 * (month > 2 ? month - 3 : month + 9) + 2) / 5 + day - 1;
  const unsigned doe = yoe * 365 + yoe / 4 - yoe / 100 + doy;
  return era * 146097 + static_cast<int64_t>(doe) - 719468;
}

// Reads ISO 8601 in UTC, such as 2026-05-14T21:05:09Z, as format_utc writes it.
bool parse_utc(const char* t, uint32_t* out) {
  int y;
  unsigned mo, d, h, mi, se;
  int used = 0;
  if (strlen(t) != 20 || t[4] != '-' || t[7] != '-' || t[10] != 'T' || t[13] != ':' ||
      t[16] != ':')
    return false;
  if (sscanf(t, "%4d-%2u-%2uT%2u:%2u:%2uZ%n", &y, &mo, &d, &h, &mi, &se, &used) != 6 || used != 20)
    return false;
  if (y < 1970 || mo < 1 || mo > 12 || d < 1 || d > 31 || h > 23 || mi > 59 || se > 59)
    return false;
  const int64_t s = days_from_civil(y, mo, d) * 86400 + h * 3600 + mi * 60 + se;
  if (s > UINT32_MAX) return false;
  *out = static_cast<uint32_t>(s);
  return true;
}

const char* direction_text(Direction d) {
  switch (d) {
    case Direction::AtoB: return "AtoB";
    case Direction::BtoA: return "BtoA";
    case Direction::BackA: return "backA";
    case Direction::BackB: return "backB";
    default: return "unknown";
  }
}

// Heights as names joined by ';', such as "lowest;middle"; empty for none.
void heights_text(uint8_t heights, char out[20]) {
  out[0] = '\0';
  const char* names[] = {"lowest", "middle", "top"};
  for (int i = 0; i < 3; ++i) {
    if (!(heights & (1 << i))) continue;
    if (out[0]) strcat(out, ";");
    strcat(out, names[i]);
  }
}

bool parse_direction(const char* s, Direction* out) {
  const Direction all[] = {Direction::AtoB, Direction::BtoA, Direction::BackA, Direction::BackB,
                           Direction::Unknown};
  for (Direction d : all) {
    if (strcmp(s, direction_text(d)) == 0) {
      *out = d;
      return true;
    }
  }
  return false;
}

// Reads heights as heights_text writes them, such as "lowest;top".
bool parse_heights(const char* s, uint8_t* out) {
  uint8_t heights = 0;
  while (*s) {
    const char* end = strchr(s, ';');
    const size_t n = end ? static_cast<size_t>(end - s) : strlen(s);
    if (n == 6 && strncmp(s, "lowest", n) == 0) {
      heights |= HEIGHT_LOWEST;
    } else if (n == 6 && strncmp(s, "middle", n) == 0) {
      heights |= HEIGHT_MIDDLE;
    } else if (n == 3 && strncmp(s, "top", n) == 0) {
      heights |= HEIGHT_TOP;
    } else {
      return false;
    }
    if (!end) break;
    s = end + 1;
    if (!*s) return false;
  }
  *out = heights;
  return true;
}

bool parse_model_type(const char* s, ModelType* out) {
  const ModelType all[] = {ModelType::None, ModelType::Empty, ModelType::FrogToad,
                           ModelType::Lizard, ModelType::Snake, ModelType::Other};
  for (ModelType t : all) {
    if (strcmp(s, model_type_name(t)) == 0) {
      *out = t;
      return true;
    }
  }
  return false;
}

// Splits one CSV line into fields copied into text, each ending in '\0', with quoted fields
// unquoted. Returns the number of fields, or -1 when the line is malformed or text too small.
int split_csv(const char* line, char* text, size_t text_size, const char* fields[],
              int max_fields) {
  size_t n = 0;
  int count = 0;
  const char* p = line;
  for (;;) {
    if (count == max_fields || n >= text_size) return -1;
    fields[count++] = text + n;
    if (*p == '"') {
      for (++p;; ++p) {
        if (*p == '\0') return -1;
        if (*p == '"') {
          if (p[1] != '"') break;
          ++p;
        }
        if (n + 1 >= text_size) return -1;
        text[n++] = *p;
      }
      ++p;
      if (*p != ',' && *p != '\0' && *p != '\n' && *p != '\r') return -1;
    } else {
      for (; *p != ',' && *p != '\0' && *p != '\n' && *p != '\r'; ++p) {
        if (*p == '"' || n + 1 >= text_size) return -1;
        text[n++] = *p;
      }
    }
    text[n++] = '\0';
    if (*p != ',') break;
    ++p;
  }
  if (*p == '\r') ++p;
  if (*p == '\n') ++p;
  return *p == '\0' ? count : -1;
}

const char* noticed_by_text(const Pass& p) {
  if (p.by_lasers && p.by_pir) return "both";
  return p.by_pir ? "pir" : "lasers";
}

const char* fault_text(FaultKind k) {
  switch (k) {
    case FaultKind::BeamBlocked: return "beam_blocked";
    case FaultKind::BeamClear: return "beam_clear";
    case FaultKind::BatteryLow: return "battery_low";
    case FaultKind::StorageLow: return "storage_low";
    case FaultKind::LinkFailed: return "link_failed";
    case FaultKind::UpdateFailed: return "update_failed";
    default: return "camera_failed";
  }
}

// A value as a JSON number with the given decimals, or null when it is not finite (not measured
// or not set).
void json_number(float v, int decimals, char out[16]) {
  if (isfinite(v)) {
    snprintf(out, 16, "%.*f", decimals, static_cast<double>(v));
  } else {
    strcpy(out, "null");
  }
}

bool valid_trap_id(const char* s, size_t n) {
  if (n == 0 || n > 15) return false;
  for (size_t i = 0; i < n; ++i) {
    const char ch = s[i];
    const bool ok = (ch >= 'A' && ch <= 'Z') || (ch >= 'a' && ch <= 'z') ||
                    (ch >= '0' && ch <= '9') || ch == '_' || ch == '-';
    if (!ok) return false;
  }
  return true;
}

bool parse_long(const char* s, long lo, long hi, long* out) {
  char* end;
  const long v = strtol(s, &end, 10);
  if (end == s || *end != '\0' || v < lo || v > hi) return false;
  *out = v;
  return true;
}

// A finite decimal number from lo to hi.
bool parse_float(const char* s, float lo, float hi, float* out) {
  char* end;
  const float v = strtof(s, &end);
  if (end == s || *end != '\0' || !isfinite(v) || v < lo || v > hi) return false;
  *out = v;
  return true;
}

// The shortest text of v that strtof reads back to exactly v.
void float_text(float v, char out[24]) {
  for (int precision = 6; precision <= 9; ++precision) {
    snprintf(out, 24, "%.*g", precision, static_cast<double>(v));
    if (strtof(out, nullptr) == v) return;
  }
}

// Side A in words: up to 31 bytes, without control characters, quotes, backslashes or '|',
// which separates the tags of the Camtrap DP export.
bool valid_side_a(const char* s, size_t n) {
  if (n > 31) return false;
  for (size_t i = 0; i < n; ++i) {
    const unsigned char ch = static_cast<unsigned char>(s[i]);
    if (ch < 0x20 || ch == 0x7f || ch == '"' || ch == '\\' || ch == '|') return false;
  }
  return true;
}

// Applies one key and value to cfg; false for an unknown key or a bad value.
bool apply_setting(const char* key, const char* value, TrapConfig* cfg) {
  long n;
  if (strcmp(key, "trap_id") == 0) {
    const size_t len = strlen(value);
    if (!valid_trap_id(value, len)) return false;
    memcpy(cfg->trap_id, value, len + 1);
  } else if (strcmp(key, "utc_offset_min") == 0) {
    if (!parse_long(value, -720, 840, &n)) return false;
    cfg->utc_offset_min = static_cast<int16_t>(n);
  } else if (strcmp(key, "pilot_mode") == 0) {
    if (strcmp(value, "1") == 0 || strcmp(value, "true") == 0) {
      cfg->pilot_mode = true;
    } else if (strcmp(value, "0") == 0 || strcmp(value, "false") == 0) {
      cfg->pilot_mode = false;
    } else {
      return false;
    }
  } else if (strcmp(key, "empty_view_hour") == 0) {
    if (!parse_long(value, 0, 23, &n)) return false;
    cfg->empty_view_hour = static_cast<uint8_t>(n);
  } else if (strcmp(key, "drop_threshold") == 0) {
    if (!parse_float(value, 0.0f, 1.0f, &cfg->drop_threshold)) return false;
  } else if (strcmp(key, "latitude") == 0) {
    if (!parse_float(value, -90.0f, 90.0f, &cfg->latitude)) return false;
  } else if (strcmp(key, "longitude") == 0) {
    if (!parse_float(value, -180.0f, 180.0f, &cfg->longitude)) return false;
  } else if (strcmp(key, "placement") == 0) {
    if (strcmp(value, "line") == 0) {
      cfg->placement = Placement::Line;
    } else if (strcmp(value, "end") == 0) {
      cfg->placement = Placement::End;
    } else {
      return false;
    }
  } else if (strcmp(key, "side_a") == 0) {
    const size_t len = strlen(value);
    if (!valid_side_a(value, len)) return false;
    memcpy(cfg->side_a, value, len + 1);
  } else if (strcmp(key, "send_every_h") == 0) {
    if (!parse_long(value, 1, 168, &n)) return false;
    cfg->send_every_h = static_cast<uint8_t>(n);
  } else if (strcmp(key, "link_timeout_s") == 0) {
    if (!parse_long(value, 30, 600, &n)) return false;
    cfg->link_timeout_s = static_cast<uint16_t>(n);
  } else if (strcmp(key, "config_version") == 0) {
    if (!parse_long(value, 0, 65535, &n)) return false;
    cfg->config_version = static_cast<uint16_t>(n);
  } else {
    return false;
  }
  return true;
}

// Copies s[0..n) without surrounding spaces and tabs into out, which holds size bytes.
bool trimmed(const char* s, size_t n, char* out, size_t size) {
  while (n > 0 && (*s == ' ' || *s == '\t')) ++s, --n;
  while (n > 0 && (s[n - 1] == ' ' || s[n - 1] == '\t' || s[n - 1] == '\r')) --n;
  if (n >= size) return false;
  memcpy(out, s, n);
  out[n] = '\0';
  return true;
}

}  // namespace

bool parse_config(const char* text, TrapConfig* out) {
  TrapConfig cfg = *out;
  const char* line = text;
  while (*line) {
    const char* end = strchr(line, '\n');
    const size_t len = end ? static_cast<size_t>(end - line) : strlen(line);
    char content[80];
    if (!trimmed(line, len, content, sizeof content)) return false;
    if (content[0] != '\0' && content[0] != '#') {
      char* eq = strchr(content, '=');
      if (!eq) return false;
      char key[32], value[48];
      if (!trimmed(content, static_cast<size_t>(eq - content), key, sizeof key)) return false;
      if (!trimmed(eq + 1, strlen(eq + 1), value, sizeof value)) return false;
      if (!apply_setting(key, value, &cfg)) return false;
    }
    if (!end) break;
    line = end + 1;
  }
  *out = cfg;
  return true;
}

size_t config_text(const TrapConfig& c, char* out, size_t size) {
  Text t(out, size);
  char number[24];
  t.add("trap_id=%s\nutc_offset_min=%d\npilot_mode=%s\nempty_view_hour=%u\n", c.trap_id,
        c.utc_offset_min, c.pilot_mode ? "true" : "false", c.empty_view_hour);
  float_text(c.drop_threshold, number);
  t.add("drop_threshold=%s\n", number);
  if (isfinite(c.latitude)) {
    float_text(c.latitude, number);
    t.add("latitude=%s\n", number);
  }
  if (isfinite(c.longitude)) {
    float_text(c.longitude, number);
    t.add("longitude=%s\n", number);
  }
  t.add("placement=%s\nside_a=%s\nsend_every_h=%u\nlink_timeout_s=%u\nconfig_version=%u\n",
        c.placement == Placement::End ? "end" : "line", c.side_a, c.send_every_h,
        c.link_timeout_s, c.config_version);
  return t.done();
}

void survey_day(uint32_t utc_s, int16_t utc_offset_min, char out[11]) {
  const int64_t local = static_cast<int64_t>(utc_s) + static_cast<int64_t>(utc_offset_min) * 60;
  int64_t days = local >= 0 ? local / 86400 : (local - 86399) / 86400;
  // Before local noon the time belongs to the survey day that began the day before.
  if (local - days * 86400 < 12 * 3600) --days;
  format_date(days, out);
}

const char* pass_csv_header() {
  return "pass_id,start_utc,end_utc,direction,heights_a,heights_b,noticed_by,pictures,"
         "dropped_empty,judged_empty,pilot,model_type,model_confidence,model_version\n";
}

size_t pass_csv_line(const PassRecord& r, char* out, size_t size) {
  char start[21], end[21], heights_a[20], heights_b[20];
  format_utc(r.start_utc_s, start);
  format_utc(r.end_utc_s, end);
  heights_text(r.pass.heights_a, heights_a);
  heights_text(r.pass.heights_b, heights_b);
  Text t(out, size);
  t.add("%s,%s,%s,%s,%s,%s,%s,%s,%u,%s,%s,", r.pass_id, start, end,
        direction_text(r.pass.direction), heights_a, heights_b, noticed_by_text(r.pass),
        r.pictures ? r.pictures : "", static_cast<unsigned>(r.dropped_empty),
        r.judged_empty ? r.judged_empty : "", r.pilot ? "true" : "false");
  if (r.model.type != ModelType::None) {
    t.add("%s,%.2f,", model_type_name(r.model.type), static_cast<double>(r.model.confidence));
    t.add_csv_field(r.model_version);
  } else {
    t.add(",,");
  }
  t.add_char('\n');
  return t.done();
}

bool parse_pass_csv_line(const char* line, PassRecord* out, char* text, size_t text_size) {
  const int kFields = 14;
  const char* f[kFields];
  if (split_csv(line, text, text_size, f, kFields) != kFields) return false;

  PassRecord r{};
  const size_t id_len = strlen(f[0]);
  if (id_len == 0 || id_len >= sizeof r.pass_id) return false;
  memcpy(r.pass_id, f[0], id_len + 1);
  if (!parse_utc(f[1], &r.start_utc_s) || !parse_utc(f[2], &r.end_utc_s)) return false;
  if (!parse_direction(f[3], &r.pass.direction)) return false;
  if (!parse_heights(f[4], &r.pass.heights_a) || !parse_heights(f[5], &r.pass.heights_b))
    return false;
  if (strcmp(f[6], "lasers") == 0) {
    r.pass.by_lasers = true;
  } else if (strcmp(f[6], "pir") == 0) {
    r.pass.by_pir = true;
  } else if (strcmp(f[6], "both") == 0) {
    r.pass.by_lasers = r.pass.by_pir = true;
  } else {
    return false;
  }
  r.pictures = f[7];
  long dropped;
  if (!parse_long(f[8], 0, 255, &dropped)) return false;
  r.dropped_empty = static_cast<uint8_t>(dropped);
  r.judged_empty = f[9];
  if (strcmp(f[10], "true") == 0) {
    r.pilot = true;
  } else if (strcmp(f[10], "false") != 0) {
    return false;
  }
  if (!parse_model_type(f[11], &r.model.type)) return false;
  if (r.model.type == ModelType::None) {
    if (f[12][0] || f[13][0]) return false;
  } else if (!parse_float(f[12], 0.0f, 1.0f, &r.model.confidence)) {
    return false;
  }
  r.model_version = f[13];
  *out = r;
  return true;
}

size_t fault_csv_line(uint32_t utc_s, FaultKind kind, const char* detail, char* out,
                      size_t size) {
  char time[21];
  format_utc(utc_s, time);
  Text t(out, size);
  t.add("%s,%s,", time, fault_text(kind));
  t.add_csv_field(detail);
  t.add_char('\n');
  return t.done();
}

size_t summary_json(const StateSummary& s, const TrapConfig& c, char* out, size_t size) {
  char time[21], battery[16], temperature[16], latitude[16], longitude[16];
  format_utc(s.utc_s, time);
  json_number(s.battery_v, 2, battery);
  json_number(s.temperature_c, 2, temperature);
  // Five decimals are about a metre, as close as a float holds a longitude.
  json_number(c.latitude, 5, latitude);
  json_number(c.longitude, 5, longitude);
  // Core fields in the order of the FieldMesh readings table, then the trap's own fields.
  // qualityFlags bit 0: the daily picture did not show a clear view.
  Text t(out, size);
  t.add("{\"datetime\":\"%s\",\"nodeId\":\"%s\",\"seqNum\":%" PRIu32
        ",\"sensorPresent\":0,\"qualityFlags\":%d,\"configVersion\":%u,\"batVoltage\":%s,"
        "\"airTemp\":%s,\"latitude\":%s,\"longitude\":%s,\"trapKind\":\"state\","
        "\"trapPasses\":%" PRIu32 ",\"trapFreeMB\":%" PRIu32 ",\"trapViewClear\":%s}\n",
        time, c.trap_id, s.seq, s.view_clear ? 0 : 1, c.config_version, battery, temperature,
        latitude, longitude, s.passes, s.free_mb, s.view_clear ? "true" : "false");
  return t.done();
}

size_t pass_reading_json(const PassRecord& r, const TrapConfig& c, uint32_t seq, char* out,
                         size_t size) {
  char time[21];
  format_utc(r.start_utc_s, time);
  unsigned pictures = 0;
  if (r.pictures && r.pictures[0]) {
    pictures = 1;
    for (const char* p = r.pictures; *p; ++p) pictures += *p == ';';
  }
  // The core fields up to batVoltage, which a pass does not measure, then the trap's own keys;
  // FieldMesh refuses lists, so the beam heights go as their bits.
  Text t(out, size);
  t.add("{\"datetime\":\"%s\",\"nodeId\":\"%s\",\"seqNum\":%" PRIu32
        ",\"sensorPresent\":0,\"qualityFlags\":0,\"configVersion\":%u,\"batVoltage\":null,"
        "\"trapKind\":\"pass\",\"trapPassId\":\"%s\",\"trapDirection\":\"%s\","
        "\"trapHeightsA\":%u,\"trapHeightsB\":%u,\"trapNoticedBy\":\"%s\",\"trapPilot\":%s,",
        time, c.trap_id, seq, c.config_version, r.pass_id, direction_text(r.pass.direction),
        r.pass.heights_a, r.pass.heights_b, noticed_by_text(r.pass), r.pilot ? "true" : "false");
  if (r.model.type != ModelType::None) {
    t.add("\"trapModelType\":\"%s\",\"trapModelConf\":%.2f,\"trapModelVersion\":",
          model_type_name(r.model.type), static_cast<double>(r.model.confidence));
    t.add_json_string(r.model_version);
  } else {
    t.add("\"trapModelType\":null,\"trapModelConf\":null,\"trapModelVersion\":null");
  }
  t.add(",\"trapPictures\":%u}\n", pictures);
  return t.done();
}
