// Unit tests of the records library: pass records, survey days, configuration, faults and the
// daily state summary.
#include <ctype.h>
#include <math.h>
#include <stdlib.h>
#include <string.h>
#include <unity.h>

#include <algorithm>
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
  r.pilot = false;
  r.model = ModelResult{ModelType::Lizard, 0.87f};
  r.model_version = "m1.0.0";

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
  TEST_ASSERT_EQUAL_STRING("pilot", header[10].c_str());
  TEST_ASSERT_EQUAL_STRING("false", f[10].c_str());
  TEST_ASSERT_EQUAL_STRING("model_type", header[11].c_str());
  TEST_ASSERT_EQUAL_STRING("lizard", f[11].c_str());
  TEST_ASSERT_EQUAL_STRING("model_confidence", header[12].c_str());
  TEST_ASSERT_EQUAL_STRING("0.87", f[12].c_str());
  TEST_ASSERT_EQUAL_STRING("model_version", header[13].c_str());
  TEST_ASSERT_EQUAL_STRING("m1.0.0", f[13].c_str());
}

// spec: b83ecc08
static void test_a_trap_without_a_model() {
  PassRecord r{};
  strcpy(r.pass_id, "ECT_0A1B2C-2026-05-14-7");
  r.start_utc_s = 1778792709;
  r.end_utc_s = 1778792711;
  r.pass = Pass{0, 0, Direction::AtoB, HEIGHT_LOWEST, HEIGHT_LOWEST, true, false};
  r.pictures = "ECT_0A1B2C-2026-05-14-7_1.jpg";
  r.judged_empty = "";
  r.pilot = true;

  char line[256];
  TEST_ASSERT_TRUE(pass_csv_line(r, line, sizeof line) > 0);
  TEST_ASSERT_EQUAL_STRING(
      "ECT_0A1B2C-2026-05-14-7,2026-05-14T21:05:09Z,2026-05-14T21:05:11Z,AtoB,lowest,lowest,"
      "lasers,ECT_0A1B2C-2026-05-14-7_1.jpg,0,,true,,,\n",
      line);

  // A model version without a type, as when the model did not run, is not written either.
  r.model_version = "m1.0.0";
  TEST_ASSERT_TRUE(pass_csv_line(r, line, sizeof line) > 0);
  TEST_ASSERT_NOT_NULL(strstr(line, ",true,,,\n"));
}

static void test_a_model_version_with_a_comma_is_quoted() {
  PassRecord r{};
  strcpy(r.pass_id, "T-2026-05-14-1");
  r.model = ModelResult{ModelType::Empty, 0.9f};
  r.model_version = "m1,0";
  char line[256];
  TEST_ASSERT_TRUE(pass_csv_line(r, line, sizeof line) > 0);
  TEST_ASSERT_NOT_NULL(strstr(line, ",empty,0.90,\"m1,0\"\n"));
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
  TEST_ASSERT_TRUE(isnan(c.latitude));
  TEST_ASSERT_TRUE(isnan(c.longitude));
}

static void test_config_reads_every_key() {
  TrapConfig c;
  TEST_ASSERT_TRUE(parse_config(
      "trap_id = ECT_0A1B2C\r\nutc_offset_min=-300\r\npilot_mode=0\r\n"
      "empty_view_hour=10\r\ndrop_threshold=0.05\r\nlatitude=49.4521\r\nlongitude=-7.7541\r\n"
      "placement=end\r\nside_a = pond side \r\nsend_every_h=6\r\nlink_timeout_s=240\r\n"
      "config_version=3",
      &c));
  TEST_ASSERT_EQUAL_STRING("ECT_0A1B2C", c.trap_id);
  TEST_ASSERT_EQUAL(-300, c.utc_offset_min);
  TEST_ASSERT_FALSE(c.pilot_mode);
  TEST_ASSERT_EQUAL(10, c.empty_view_hour);
  TEST_ASSERT_EQUAL_FLOAT(0.05f, c.drop_threshold);
  TEST_ASSERT_EQUAL_FLOAT(49.4521f, c.latitude);
  TEST_ASSERT_EQUAL_FLOAT(-7.7541f, c.longitude);
  TEST_ASSERT_EQUAL(Placement::End, c.placement);
  TEST_ASSERT_EQUAL_STRING("pond side", c.side_a);
  TEST_ASSERT_EQUAL(6, c.send_every_h);
  TEST_ASSERT_EQUAL(240, c.link_timeout_s);
  TEST_ASSERT_EQUAL(3, c.config_version);
}

static void test_config_defaults_for_the_link_and_placement() {
  const TrapConfig c;
  TEST_ASSERT_EQUAL(Placement::Line, c.placement);
  TEST_ASSERT_EQUAL_STRING("", c.side_a);
  TEST_ASSERT_EQUAL(24, c.send_every_h);
  TEST_ASSERT_EQUAL(180, c.link_timeout_s);
  TEST_ASSERT_EQUAL(1, c.config_version);
}

static void assert_same_config(const TrapConfig& a, const TrapConfig& b) {
  TEST_ASSERT_EQUAL_STRING(a.trap_id, b.trap_id);
  TEST_ASSERT_EQUAL(a.utc_offset_min, b.utc_offset_min);
  TEST_ASSERT_EQUAL(a.pilot_mode, b.pilot_mode);
  TEST_ASSERT_EQUAL(a.empty_view_hour, b.empty_view_hour);
  TEST_ASSERT_TRUE(a.drop_threshold == b.drop_threshold);
  TEST_ASSERT_TRUE(a.latitude == b.latitude || (isnan(a.latitude) && isnan(b.latitude)));
  TEST_ASSERT_TRUE(a.longitude == b.longitude || (isnan(a.longitude) && isnan(b.longitude)));
  TEST_ASSERT_EQUAL(a.placement, b.placement);
  TEST_ASSERT_EQUAL_STRING(a.side_a, b.side_a);
  TEST_ASSERT_EQUAL(a.send_every_h, b.send_every_h);
  TEST_ASSERT_EQUAL(a.link_timeout_s, b.link_timeout_s);
  TEST_ASSERT_EQUAL(a.config_version, b.config_version);
}

static void test_config_text_reads_back_to_the_same_settings() {
  // Every setting away from its default.
  TrapConfig c;
  strcpy(c.trap_id, "ECT_0A1B2C");
  c.utc_offset_min = -570;
  c.pilot_mode = false;
  c.empty_view_hour = 9;
  c.drop_threshold = 0.0417f;
  c.latitude = -33.86882f;
  c.longitude = 151.20929f;
  c.placement = Placement::End;
  strcpy(c.side_a, "Teichseite, Nord");
  c.send_every_h = 168;
  c.link_timeout_s = 30;
  c.config_version = 65535;

  char text[512];
  TEST_ASSERT_TRUE(config_text(c, text, sizeof text) > 0);
  TrapConfig back;
  TEST_ASSERT_TRUE_MESSAGE(parse_config(text, &back), text);
  assert_same_config(c, back);
  TEST_ASSERT_NOT_NULL(strstr(text, "drop_threshold=0.0417\n"));
  TEST_ASSERT_NOT_NULL(strstr(text, "placement=end\n"));

  // The defaults, with coordinates not set, which are left out.
  const TrapConfig defaults;
  TEST_ASSERT_TRUE(config_text(defaults, text, sizeof text) > 0);
  TEST_ASSERT_NULL(strstr(text, "latitude"));
  TEST_ASSERT_NULL(strstr(text, "longitude"));
  TrapConfig back_defaults;
  strcpy(back_defaults.trap_id, "ECT_OTHER");
  TEST_ASSERT_TRUE_MESSAGE(parse_config(text, &back_defaults), text);
  assert_same_config(defaults, back_defaults);

  // Text that does not fit gives 0 and an empty buffer.
  TEST_ASSERT_EQUAL(0, config_text(c, text, 40));
  TEST_ASSERT_EQUAL_STRING("", text);
}

static void test_config_takes_coordinates_at_their_limits() {
  TrapConfig c;
  TEST_ASSERT_TRUE(parse_config("latitude=-90\nlongitude=180\n", &c));
  TEST_ASSERT_EQUAL_FLOAT(-90.0f, c.latitude);
  TEST_ASSERT_EQUAL_FLOAT(180.0f, c.longitude);
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
      "latitude=91\n",                      // beyond a pole
      "longitude=-180.5\n",
      "latitude=nan\n",
      "longitude=inf\n",
      "latitude=\n",
      "latitude=49.45 N\n",
      "placement=middle\n",
      "side_a=a side with more than thirty-one letters\n",
      "side_a=pond|wood\n",
      "side_a=the \"pond\" side\n",
      "send_every_h=0\n",
      "send_every_h=169\n",
      "link_timeout_s=29\n",
      "link_timeout_s=601\n",
      "config_version=65536\n",
  };
  for (const char* text : bad) {
    TrapConfig c;
    TEST_ASSERT_FALSE_MESSAGE(parse_config(text, &c), text);
    TEST_ASSERT_EQUAL_STRING("ECT_UNSET", c.trap_id);
    TEST_ASSERT_TRUE(c.pilot_mode);
    TEST_ASSERT_TRUE(isnan(c.latitude));
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
// are finite numbers or null; latitude and longitude are decimal degrees or null; the core keys
// come first, in the table's order, and a reading may stop before its later columns, which are
// then absent; keys the backend does not model are stored, so they only need to be scalar
// values.

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
  const size_t required = 6;  // up to configVersion; the measurements after it may be absent
  size_t next = 0;
  bool past_core = false;
  for (const auto& [key, v] : kv) {
    const auto at = std::find(core.begin(), core.end(), key);
    if (at == core.end()) {
      past_core = true;
      continue;
    }
    if (past_core || static_cast<size_t>(at - core.begin()) != next)
      return "core key out of order: " + key;
    ++next;
  }
  if (next < required) return "core key missing: " + core[next];
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
    if (key == "latitude" || key == "longitude") {
      if (v.kind == JsonValue::Null) continue;
      const double limit = key == "latitude" ? 90 : 180;
      if (v.kind != JsonValue::Number || fabs(strtod(v.text.c_str(), nullptr)) > limit)
        return key + " must be decimal degrees or null";
    }
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
  char line[512];
  StateSummary s{1778752800, 12, 3.98f, 17.5f, 143, 98112, true};  // 2026-05-14T10:00:00Z
  TrapConfig c = trap();
  TEST_ASSERT_TRUE(parse_config("latitude=49.4521\nlongitude=7.7541\n", &c));
  TEST_ASSERT_TRUE(summary_json(s, c, line, sizeof line) > 0);
  TEST_ASSERT_EQUAL_STRING("", contract_problem(line).c_str());
  TEST_ASSERT_EQUAL_STRING(
      "{\"datetime\":\"2026-05-14T10:00:00Z\",\"nodeId\":\"ECT_0A1B2C\",\"seqNum\":12,"
      "\"sensorPresent\":0,\"qualityFlags\":0,\"configVersion\":1,\"batVoltage\":3.98,"
      "\"airTemp\":17.50,\"latitude\":49.45210,\"longitude\":7.75410,\"trapKind\":\"state\","
      "\"trapPasses\":143,\"trapFreeMB\":98112,\"trapViewClear\":true}\n",
      line);

  // Readings carry the version of the settings they were taken under.
  c.config_version = 3;
  TEST_ASSERT_TRUE(summary_json(s, c, line, sizeof line) > 0);
  TEST_ASSERT_NOT_NULL(strstr(line, "\"configVersion\":3,"));

  // A trap set up without coordinates gives null for them, which the contract allows.
  TEST_ASSERT_TRUE(summary_json(s, trap(), line, sizeof line) > 0);
  TEST_ASSERT_EQUAL_STRING("", contract_problem(line).c_str());
  TEST_ASSERT_NOT_NULL(strstr(line, "\"latitude\":null,\"longitude\":null,"));

  // A trap far south and west, at the limits of both.
  TEST_ASSERT_TRUE(parse_config("latitude=-90\nlongitude=-180\n", &c));
  TEST_ASSERT_TRUE(summary_json(s, c, line, sizeof line) > 0);
  TEST_ASSERT_EQUAL_STRING("", contract_problem(line).c_str());
  TEST_ASSERT_NOT_NULL(strstr(line, "\"latitude\":-90.00000,\"longitude\":-180.00000,"));

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

static PassRecord lizard_pass() {
  PassRecord r{};
  strcpy(r.pass_id, "ECT_0A1B2C-2026-05-14-17");
  r.start_utc_s = 1778793185;  // 2026-05-14T21:13:05Z
  r.end_utc_s = 1778793187;
  r.pass = Pass{0, 0, Direction::AtoB, HEIGHT_LOWEST, HEIGHT_LOWEST, true, false};
  r.pictures = "a_1.jpg;a_2.jpg;a_3.jpg";
  r.judged_empty = "";
  r.pilot = false;
  r.model = ModelResult{ModelType::Lizard, 0.87f};
  r.model_version = "m1.0.0";
  return r;
}

// spec: 08ab3418
static void test_fieldmesh_accepts_a_pass_record() {
  TrapConfig c = trap();
  c.config_version = 3;
  char line[512];
  TEST_ASSERT_TRUE(pass_reading_json(lizard_pass(), c, 1043, line, sizeof line) > 0);
  TEST_ASSERT_EQUAL_STRING("", contract_problem(line).c_str());
  TEST_ASSERT_EQUAL_STRING(
      "{\"datetime\":\"2026-05-14T21:13:05Z\",\"nodeId\":\"ECT_0A1B2C\",\"seqNum\":1043,"
      "\"sensorPresent\":0,\"qualityFlags\":0,\"configVersion\":3,\"batVoltage\":null,"
      "\"trapKind\":\"pass\",\"trapPassId\":\"ECT_0A1B2C-2026-05-14-17\",\"trapDirection\":\"AtoB\","
      "\"trapHeightsA\":1,\"trapHeightsB\":1,\"trapNoticedBy\":\"lasers\",\"trapPilot\":false,"
      "\"trapModelType\":\"lizard\",\"trapModelConf\":0.87,\"trapModelVersion\":\"m1.0.0\","
      "\"trapPictures\":3}\n",
      line);

  // Without a model, in pilot mode, noticed by the PIR sensor alone, with no pictures kept.
  PassRecord r = lizard_pass();
  r.model = ModelResult{};
  r.model_version = "";
  r.pilot = true;
  r.pass = Pass{0, 0, Direction::Unknown, 0, 0, false, true};
  r.pictures = "";
  TEST_ASSERT_TRUE(pass_reading_json(r, c, 1044, line, sizeof line) > 0);
  TEST_ASSERT_EQUAL_STRING("", contract_problem(line).c_str());
  TEST_ASSERT_NOT_NULL(strstr(
      line, "\"trapModelType\":null,\"trapModelConf\":null,\"trapModelVersion\":null,"));
  TEST_ASSERT_NOT_NULL(strstr(line, "\"trapDirection\":\"unknown\","));
  TEST_ASSERT_NOT_NULL(strstr(line, "\"trapNoticedBy\":\"pir\",\"trapPilot\":true,"));
  TEST_ASSERT_NOT_NULL(strstr(line, "\"trapPictures\":0}"));

  // A reading that does not fit gives 0.
  TEST_ASSERT_EQUAL(0, pass_reading_json(lizard_pass(), c, 1, line, 100));
  TEST_ASSERT_EQUAL_STRING("", line);
}

static void test_contract_check_catches_bad_readings() {
  TEST_ASSERT_TRUE(contract_problem("{\"nodeId\":\"X\"}\n") != "");
  TEST_ASSERT_TRUE(contract_problem(
      "{\"datetime\":\"2026-05-14 10:00\",\"nodeId\":\"X\",\"seqNum\":1,\"sensorPresent\":0,"
      "\"qualityFlags\":0,\"configVersion\":1,\"batVoltage\":null,\"airTemp\":null}") != "");
  TEST_ASSERT_TRUE(contract_problem(
      "{\"datetime\":\"2026-05-14T10:00:00Z\",\"nodeId\":\"X\",\"seqNum\":1,\"sensorPresent\":0,"
      "\"qualityFlags\":0,\"configVersion\":1,\"batVoltage\":nan,\"airTemp\":null}") != "");
  TEST_ASSERT_TRUE(contract_problem(
      "{\"datetime\":\"2026-05-14T10:00:00Z\",\"nodeId\":\"X\",\"seqNum\":1,\"sensorPresent\":0,"
      "\"qualityFlags\":0,\"configVersion\":1,\"batVoltage\":null,\"airTemp\":null,"
      "\"latitude\":91.0,\"longitude\":null}") != "");
  // A core key after the trap's own keys, and a reading that stops before configVersion.
  TEST_ASSERT_TRUE(contract_problem(
      "{\"datetime\":\"2026-05-14T10:00:00Z\",\"nodeId\":\"X\",\"seqNum\":1,\"sensorPresent\":0,"
      "\"qualityFlags\":0,\"configVersion\":1,\"trapKind\":\"pass\",\"batVoltage\":null}") != "");
  TEST_ASSERT_TRUE(contract_problem(
      "{\"datetime\":\"2026-05-14T10:00:00Z\",\"nodeId\":\"X\",\"seqNum\":1}") != "");
}

// spec: 45e3bf6c
static void test_a_day_without_passes() {
  char line[512];
  const StateSummary s{1778752800, 13, 3.95f, 12.0f, 0, 98000, true};
  TEST_ASSERT_TRUE(summary_json(s, trap(), line, sizeof line) > 0);
  TEST_ASSERT_NOT_NULL(strstr(line, "\"trapPasses\":0,"));
  TEST_ASSERT_EQUAL_STRING("", contract_problem(line).c_str());
}

int main() {
  UNITY_BEGIN();
  RUN_TEST(test_a_pass_leaves_its_record);
  RUN_TEST(test_a_trap_without_a_model);
  RUN_TEST(test_a_model_version_with_a_comma_is_quoted);
  RUN_TEST(test_pass_record_texts);
  RUN_TEST(test_line_that_does_not_fit_gives_zero);
  RUN_TEST(test_survey_day_runs_noon_to_noon);
  RUN_TEST(test_config_keeps_defaults_for_missing_keys);
  RUN_TEST(test_config_reads_every_key);
  RUN_TEST(test_config_takes_coordinates_at_their_limits);
  RUN_TEST(test_config_defaults_for_the_link_and_placement);
  RUN_TEST(test_config_text_reads_back_to_the_same_settings);
  RUN_TEST(test_malformed_config_changes_nothing);
  RUN_TEST(test_fault_line);
  RUN_TEST(test_fieldmesh_accepts_the_summary);
  RUN_TEST(test_fieldmesh_accepts_a_pass_record);
  RUN_TEST(test_contract_check_catches_bad_readings);
  RUN_TEST(test_a_day_without_passes);
  return UNITY_END();
}
