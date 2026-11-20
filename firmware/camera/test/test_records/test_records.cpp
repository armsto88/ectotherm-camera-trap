// Unit tests of the records library: pass records, survey days, configuration, faults and the
// daily state summary.
#include <ctype.h>
#include <math.h>
#include <stdlib.h>
#include <string.h>
#include <unity.h>

#include <string>
#include <vector>

#include "passes.h"
#include "records.h"

void setUp() {}
void tearDown() {}

// Splits a CSV line without quoting into its fields, dropping the newline at its end.
static std::vector<std::string> fields(const char* line) {
  std::string s(line);
  if (!s.empty() && s.back() == '\n') s.pop_back();
  std::vector<std::string> out;
  size_t start = 0;
  for (;;) {
    const size_t comma = s.find(',', start);
    out.push_back(s.substr(start, comma == std::string::npos ? std::string::npos : comma - start));
    if (comma == std::string::npos) return out;
    start = comma + 1;
  }
}

// spec: c2ab65dd
static void test_a_pass_leaves_its_record() {
  // An animal passes from side A to side B, interrupting the lowest beam at both points.
  PassBuilder b(5000, 0, 0);
  b.add(Crossing{1000, 0, HEIGHT_LOWEST, 1});
  b.add(Crossing{1300, 0, HEIGHT_LOWEST, 0});
  b.add(Crossing{3000, 1, HEIGHT_LOWEST, 1});
  TEST_ASSERT_TRUE(b.add(Crossing{3300, 1, HEIGHT_LOWEST, 0}));

  PassRecord r{};
  strcpy(r.pass_id, "ECT_0A1B2C-2026-05-14-7");
  r.start_utc_s = 1778792709;  // 2026-05-14T21:05:09Z
  r.end_utc_s = 1778792711;
  r.pass = b.pass();
  r.pictures = "ECT_0A1B2C-2026-05-14-7_1.jpg;ECT_0A1B2C-2026-05-14-7_2.jpg";
  r.dropped_empty = 0;
  r.judged_empty = "";

  char line[256];
  TEST_ASSERT_TRUE(pass_csv_line(r, line, sizeof line) > 0);
  const auto f = fields(line);
  const auto header = fields(pass_csv_header());
  TEST_ASSERT_EQUAL(header.size(), f.size());
  TEST_ASSERT_EQUAL_STRING("pass_id", header[0].c_str());
  TEST_ASSERT_EQUAL_STRING("ECT_0A1B2C-2026-05-14-7", f[0].c_str());
  TEST_ASSERT_EQUAL_STRING("2026-05-14T21:05:09Z", f[1].c_str());
  TEST_ASSERT_EQUAL_STRING("2026-05-14T21:05:11Z", f[2].c_str());
  TEST_ASSERT_EQUAL_STRING("AtoB", f[3].c_str());
  TEST_ASSERT_EQUAL_STRING("lowest", f[4].c_str());
  TEST_ASSERT_EQUAL_STRING("lowest", f[5].c_str());
  TEST_ASSERT_EQUAL_STRING("lasers", f[6].c_str());
  TEST_ASSERT_EQUAL_STRING("ECT_0A1B2C-2026-05-14-7_1.jpg;ECT_0A1B2C-2026-05-14-7_2.jpg",
                           f[7].c_str());
  TEST_ASSERT_EQUAL_STRING("0", f[8].c_str());
  TEST_ASSERT_EQUAL_STRING("", f[9].c_str());
}

static void test_pass_record_texts() {
  PassRecord r{};
  strcpy(r.pass_id, "T-2026-05-14-1");
  r.pass = Pass{0, 0, Direction::BackB, 0, HEIGHT_LOWEST | HEIGHT_TOP, true, true};
  char line[256];
  pass_csv_line(r, line, sizeof line);
  auto f = fields(line);
  TEST_ASSERT_EQUAL_STRING("backB", f[3].c_str());
  TEST_ASSERT_EQUAL_STRING("", f[4].c_str());
  TEST_ASSERT_EQUAL_STRING("lowest;top", f[5].c_str());
  TEST_ASSERT_EQUAL_STRING("both", f[6].c_str());

  r.pass = Pass{0, 0, Direction::Unknown, 0, 0, false, true};
  pass_csv_line(r, line, sizeof line);
  f = fields(line);
  TEST_ASSERT_EQUAL_STRING("unknown", f[3].c_str());
  TEST_ASSERT_EQUAL_STRING("pir", f[6].c_str());
}

static void test_line_that_does_not_fit_gives_zero() {
  PassRecord r{};
  strcpy(r.pass_id, "T-2026-05-14-1");
  char line[20];
  TEST_ASSERT_EQUAL(0, pass_csv_line(r, line, sizeof line));
  TEST_ASSERT_EQUAL_STRING("", line);
}

static void test_survey_day_runs_noon_to_noon() {
  char day[11];
  // One hour ahead of UTC: 23:00 and 01:00 local time fall into the same survey day.
  survey_day(1778796000, 60, day);  // 2026-05-14T22:00:00Z
  TEST_ASSERT_EQUAL_STRING("2026-05-14", day);
  survey_day(1778803200, 60, day);  // 2026-05-15T00:00:00Z
  TEST_ASSERT_EQUAL_STRING("2026-05-14", day);
  // The day changes at local noon.
  survey_day(1778756340, 60, day);  // 11:59 local
  TEST_ASSERT_EQUAL_STRING("2026-05-13", day);
  survey_day(1778756400, 60, day);  // 12:00 local
  TEST_ASSERT_EQUAL_STRING("2026-05-14", day);
  // Five hours behind UTC: 02:30 UTC is 21:30 the evening before.
  survey_day(1778812200, -300, day);
  TEST_ASSERT_EQUAL_STRING("2026-05-14", day);
  // Leap day.
  survey_day(1709251199, 0, day);  // 2024-02-29T23:59:59Z
  TEST_ASSERT_EQUAL_STRING("2024-02-29", day);
}

static void test_config_keeps_defaults_for_missing_keys() {
  TrapConfig c;
  TEST_ASSERT_TRUE(parse_config("# trap at the north fence\ntrap_id=ECT_0A1B2C\n\n", &c));
  TEST_ASSERT_EQUAL_STRING("ECT_0A1B2C", c.trap_id);
  const TrapConfig defaults;
  TEST_ASSERT_EQUAL(defaults.utc_offset_min, c.utc_offset_min);
  TEST_ASSERT_EQUAL(defaults.pilot_mode, c.pilot_mode);
  TEST_ASSERT_EQUAL(defaults.empty_view_hour, c.empty_view_hour);
  TEST_ASSERT_EQUAL_FLOAT(defaults.drop_threshold, c.drop_threshold);
}

static void test_config_reads_every_key() {
  TrapConfig c;
  TEST_ASSERT_TRUE(parse_config(
      "trap_id = ECT_0A1B2C\r\nutc_offset_min=-300\r\npilot_mode=0\r\n"
      "empty_view_hour=10\r\ndrop_threshold=0.05",
      &c));
  TEST_ASSERT_EQUAL_STRING("ECT_0A1B2C", c.trap_id);
  TEST_ASSERT_EQUAL(-300, c.utc_offset_min);
  TEST_ASSERT_FALSE(c.pilot_mode);
  TEST_ASSERT_EQUAL(10, c.empty_view_hour);
  TEST_ASSERT_EQUAL_FLOAT(0.05f, c.drop_threshold);
}

static void test_malformed_config_changes_nothing() {
  const char* bad[] = {
      "trap_id=ECT_0A1B2C\npilotmode=0\n",  // unknown key, such as a typo
      "trap_id ECT_0A1B2C\n",               // no '='
      "empty_view_hour=24\n",               // out of range
      "trap_id=ECT 0A1B2C\n",               // not allowed in a FieldMesh nodeId
      "trap_id=ECT_0123456789ABC\n",        // longer than 15 characters
      "pilot_mode=yes\n",
      "drop_threshold=0.05x\n",
  };
  for (const char* text : bad) {
    TrapConfig c;
    TEST_ASSERT_FALSE_MESSAGE(parse_config(text, &c), text);
    TEST_ASSERT_EQUAL_STRING("ECT_UNSET", c.trap_id);
    TEST_ASSERT_TRUE(c.pilot_mode);
  }
}

static void test_fault_line() {
  char line[128];
  TEST_ASSERT_TRUE(fault_csv_line(1778792709, FaultKind::BatteryLow, "3.41 V", line, sizeof line));
  TEST_ASSERT_EQUAL_STRING("2026-05-14T21:05:09Z,battery_low,3.41 V\n", line);
  fault_csv_line(1778792709, FaultKind::BeamBlocked, "point A, lowest", line, sizeof line);
  TEST_ASSERT_EQUAL_STRING("2026-05-14T21:05:09Z,beam_blocked,\"point A, lowest\"\n", line);
  fault_csv_line(1778792709, FaultKind::CameraFailed, "said \"no\"", line, sizeof line);
  TEST_ASSERT_EQUAL_STRING("2026-05-14T21:05:09Z,camera_failed,\"said \"\"no\"\"\"\n", line);
  TEST_ASSERT_EQUAL(0, fault_csv_line(1778792709, FaultKind::StorageLow, "x", line, 30));
}

// --- Checking a reading against the FieldMesh upload contract --------------------------------
// The rules of the readings table of the FieldMesh upload contract, version 1 of 2026-11-16:
// datetime is ISO 8601 UTC with Z; nodeId has letters, digits, '_' and '-' only, up to 15
// characters; seqNum, sensorPresent, qualityFlags and configVersion are integers; measurements
// are finite numbers or null; the core keys come in the table's order; keys the backend does not
// model are stored, so they only need to be scalar values.

struct JsonValue {
  enum Kind { String, Number, Bool, Null } kind;
  std::string text;
};

// Parses a flat JSON object of scalar values; false if it is not one.
static bool parse_flat_json(const std::string& s, std::vector<std::pair<std::string, JsonValue>>* out) {
  size_t i = 0;
  auto skip = [&] { while (i < s.size() && (s[i] == ' ' || s[i] == '\n')) ++i; };
  auto read_string = [&](std::string* str) {
    if (s[i] != '"') return false;
    const size_t end = s.find('"', i + 1);
    if (end == std::string::npos) return false;
    *str = s.substr(i + 1, end - i - 1);
    i = end + 1;
    return true;
  };
  skip();
  if (i >= s.size() || s[i++] != '{') return false;
  for (;;) {
    skip();
    std::string key;
    if (!read_string(&key)) return false;
    if (s[i++] != ':') return false;
    JsonValue v{JsonValue::Null, ""};
    if (s[i] == '"') {
      v.kind = JsonValue::String;
      if (!read_string(&v.text)) return false;
    } else {
      const size_t end = s.find_first_of(",}", i);
      if (end == std::string::npos) return false;
      v.text = s.substr(i, end - i);
      i = end;
      if (v.text == "true" || v.text == "false") {
        v.kind = JsonValue::Bool;
      } else if (v.text == "null") {
        v.kind = JsonValue::Null;
      } else {
        char* e;
        strtod(v.text.c_str(), &e);
        if (*e != '\0' || v.text.empty() || v.text == "nan" || v.text == "inf") return false;
        v.kind = JsonValue::Number;
      }
    }
    out->push_back({key, v});
    if (s[i] == ',') { ++i; continue; }
    if (s[i] == '}') { ++i; skip(); return i == s.size(); }
    return false;
  }
}

static bool is_integer(const JsonValue& v) {
  return v.kind == JsonValue::Number && v.text.find_first_of(".eE") == std::string::npos;
}

static bool is_iso_utc(const std::string& t) {
  if (t.size() != 20 || t[19] != 'Z' || t[4] != '-' || t[7] != '-' || t[10] != 'T' ||
      t[13] != ':' || t[16] != ':')
    return false;
  for (size_t i : {0, 1, 2, 3, 5, 6, 8, 9, 11, 12, 14, 15, 17, 18})
    if (t[i] < '0' || t[i] > '9') return false;
  return true;
}

// Checks one reading against the contract's rules; returns what is wrong, or "" if it is valid.
static std::string contract_problem(const char* line) {
  std::vector<std::pair<std::string, JsonValue>> kv;
  if (!parse_flat_json(line, &kv)) return "not a flat JSON object";
  const std::vector<std::string> core = {"datetime", "nodeId", "seqNum", "sensorPresent",
                                         "qualityFlags", "configVersion", "batVoltage", "airTemp"};
  for (size_t i = 0; i < core.size(); ++i) {
    if (i >= kv.size() || kv[i].first != core[i]) return "core key out of order: " + core[i];
  }
  for (const auto& [key, v] : kv) {
    if (key == "datetime" && (v.kind != JsonValue::String || !is_iso_utc(v.text)))
      return "datetime is invalid";
    if (key == "nodeId") {
      if (v.kind != JsonValue::String || v.text.empty() || v.text.size() > 15) return "nodeId";
      for (char ch : v.text)
        if (!isalnum(static_cast<unsigned char>(ch)) && ch != '_' && ch != '-') return "nodeId";
    }
    if ((key == "seqNum" || key == "sensorPresent" || key == "qualityFlags" ||
         key == "configVersion") && !is_integer(v))
      return key + " must be an integer";
    if ((key == "batVoltage" || key == "airTemp") && v.kind != JsonValue::Number &&
        v.kind != JsonValue::Null)
      return key + " must be a finite number or null";
  }
  return "";
}

static TrapConfig trap() {
  TrapConfig c;
  strcpy(c.trap_id, "ECT_0A1B2C");
  return c;
}

// spec: 94733795
static void test_fieldmesh_accepts_the_summary() {
  char line[256];
  StateSummary s{1778752800, 12, 3.98f, 17.5f, 143, 98112, true};  // 2026-05-14T10:00:00Z
  TEST_ASSERT_TRUE(summary_json(s, trap(), line, sizeof line) > 0);
  TEST_ASSERT_EQUAL_STRING("", contract_problem(line).c_str());
  TEST_ASSERT_EQUAL_STRING(
      "{\"datetime\":\"2026-05-14T10:00:00Z\",\"nodeId\":\"ECT_0A1B2C\",\"seqNum\":12,"
      "\"sensorPresent\":0,\"qualityFlags\":0,\"configVersion\":1,\"batVoltage\":3.98,"
      "\"airTemp\":17.50,\"trapPasses\":143,\"trapFreeMB\":98112,\"trapViewClear\":true}\n",
      line);

  // Values the trap could not measure become null, which the contract allows.
  s.battery_v = NAN;
  s.temperature_c = NAN;
  s.view_clear = false;
  summary_json(s, trap(), line, sizeof line);
  TEST_ASSERT_EQUAL_STRING("", contract_problem(line).c_str());
  TEST_ASSERT_NOT_NULL(strstr(line, "\"batVoltage\":null,\"airTemp\":null"));
  TEST_ASSERT_NOT_NULL(strstr(line, "\"qualityFlags\":1"));
  TEST_ASSERT_NOT_NULL(strstr(line, "\"trapViewClear\":false"));
}

static void test_contract_check_catches_bad_readings() {
  TEST_ASSERT_TRUE(contract_problem("{\"nodeId\":\"X\"}\n") != "");
  TEST_ASSERT_TRUE(contract_problem(
      "{\"datetime\":\"2026-05-14 10:00\",\"nodeId\":\"X\",\"seqNum\":1,\"sensorPresent\":0,"
      "\"qualityFlags\":0,\"configVersion\":1,\"batVoltage\":null,\"airTemp\":null}") != "");
  TEST_ASSERT_TRUE(contract_problem(
      "{\"datetime\":\"2026-05-14T10:00:00Z\",\"nodeId\":\"X\",\"seqNum\":1,\"sensorPresent\":0,"
      "\"qualityFlags\":0,\"configVersion\":1,\"batVoltage\":nan,\"airTemp\":null}") != "");
}

// spec: 45e3bf6c
static void test_a_day_without_passes() {
  char line[256];
  const StateSummary s{1778752800, 13, 3.95f, 12.0f, 0, 98000, true};
  TEST_ASSERT_TRUE(summary_json(s, trap(), line, sizeof line) > 0);
  TEST_ASSERT_NOT_NULL(strstr(line, "\"trapPasses\":0,"));
  TEST_ASSERT_EQUAL_STRING("", contract_problem(line).c_str());
}

int main() {
  UNITY_BEGIN();
  RUN_TEST(test_a_pass_leaves_its_record);
  RUN_TEST(test_pass_record_texts);
  RUN_TEST(test_line_that_does_not_fit_gives_zero);
  RUN_TEST(test_survey_day_runs_noon_to_noon);
  RUN_TEST(test_config_keeps_defaults_for_missing_keys);
  RUN_TEST(test_config_reads_every_key);
  RUN_TEST(test_malformed_config_changes_nothing);
  RUN_TEST(test_fault_line);
  RUN_TEST(test_fieldmesh_accepts_the_summary);
  RUN_TEST(test_contract_check_catches_bad_readings);
  RUN_TEST(test_a_day_without_passes);
  return UNITY_END();
}
