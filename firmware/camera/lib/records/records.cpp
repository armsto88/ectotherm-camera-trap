#include "records.h"

#include <inttypes.h>
#include <math.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

namespace {

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
    default: return "camera_failed";
  }
}

// The length of what snprintf wrote, or 0 with an empty out when it did not fit.
size_t fitted(int n, char* out, size_t size) {
  if (n < 0 || static_cast<size_t>(n) >= size) {
    if (size > 0) out[0] = '\0';
    return 0;
  }
  return static_cast<size_t>(n);
}

// A measurement as a JSON number with two decimals, or null when not measured.
void json_number(float v, char out[16]) {
  if (isfinite(v)) {
    snprintf(out, 16, "%.2f", static_cast<double>(v));
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
    char* end;
    const float v = strtof(value, &end);
    if (end == value || *end != '\0' || !(v >= 0.0f && v <= 1.0f)) return false;
    cfg->drop_threshold = v;
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

void survey_day(uint32_t utc_s, int16_t utc_offset_min, char out[11]) {
  const int64_t local = static_cast<int64_t>(utc_s) + static_cast<int64_t>(utc_offset_min) * 60;
  int64_t days = local >= 0 ? local / 86400 : (local - 86399) / 86400;
  // Before local noon the time belongs to the survey day that began the day before.
  if (local - days * 86400 < 12 * 3600) --days;
  format_date(days, out);
}

const char* pass_csv_header() {
  return "pass_id,start_utc,end_utc,direction,heights_a,heights_b,noticed_by,pictures,"
         "dropped_empty,judged_empty\n";
}

size_t pass_csv_line(const PassRecord& r, char* out, size_t size) {
  char start[21], end[21], heights_a[20], heights_b[20];
  format_utc(r.start_utc_s, start);
  format_utc(r.end_utc_s, end);
  heights_text(r.pass.heights_a, heights_a);
  heights_text(r.pass.heights_b, heights_b);
  const int n = snprintf(out, size, "%s,%s,%s,%s,%s,%s,%s,%s,%u,%s\n", r.pass_id, start, end,
                         direction_text(r.pass.direction), heights_a, heights_b,
                         noticed_by_text(r.pass), r.pictures ? r.pictures : "",
                         static_cast<unsigned>(r.dropped_empty),
                         r.judged_empty ? r.judged_empty : "");
  return fitted(n, out, size);
}

size_t fault_csv_line(uint32_t utc_s, FaultKind kind, const char* detail, char* out,
                      size_t size) {
  char time[21];
  format_utc(utc_s, time);
  const int head = snprintf(out, size, "%s,%s,", time, fault_text(kind));
  if (!fitted(head, out, size)) return 0;
  size_t n = static_cast<size_t>(head);

  // A detail with a comma, quote or line break is quoted, with quotes doubled.
  const char* d = detail ? detail : "";
  const bool quote = strpbrk(d, ",\"\r\n") != nullptr;
  if (quote) {
    if (n + 1 >= size) return fitted(-1, out, size);
    out[n++] = '"';
  }
  for (; *d; ++d) {
    const size_t needed = (*d == '"') ? 2 : 1;
    if (n + needed >= size) return fitted(-1, out, size);
    if (*d == '"') out[n++] = '"';
    out[n++] = *d;
  }
  if (n + (quote ? 2 : 1) >= size) return fitted(-1, out, size);
  if (quote) out[n++] = '"';
  out[n++] = '\n';
  out[n] = '\0';
  return n;
}

size_t summary_json(const StateSummary& s, const TrapConfig& c, char* out, size_t size) {
  char time[21], battery[16], temperature[16];
  format_utc(s.utc_s, time);
  json_number(s.battery_v, battery);
  json_number(s.temperature_c, temperature);
  // Core fields in the order of the FieldMesh readings table, then the trap's own fields.
  // qualityFlags bit 0: the daily picture did not show a clear view.
  const int n = snprintf(
      out, size,
      "{\"datetime\":\"%s\",\"nodeId\":\"%s\",\"seqNum\":%" PRIu32
      ",\"sensorPresent\":0,\"qualityFlags\":%d,\"configVersion\":1,\"batVoltage\":%s,"
      "\"airTemp\":%s,\"trapPasses\":%" PRIu32 ",\"trapFreeMB\":%" PRIu32
      ",\"trapViewClear\":%s}\n",
      time, c.trap_id, s.seq, s.view_clear ? 0 : 1, battery, temperature, s.passes, s.free_mb,
      s.view_clear ? "true" : "false");
  return fitted(n, out, size);
}
