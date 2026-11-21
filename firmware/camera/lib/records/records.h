// Records, summary and configuration: the text of everything the trap writes to its card.
// No hardware calls, so it is tested on the computer.
#pragma once

#include <math.h>
#include <stddef.h>
#include <stdint.h>

#include "passes.h"
#include "typing.h"

enum class Placement : uint8_t { Line, End };  // in the fence line, or at a fence end

// The trap's settings from trap.cfg. A default-constructed TrapConfig holds the defaults, which
// parse_config keeps for keys the file leaves out.
struct TrapConfig {
  char trap_id[16] = "ECT_UNSET";  // also the FieldMesh nodeId, e.g. ECT_0A1B2C
  int16_t utc_offset_min = 0;      // for survey days and the daily times
  bool pilot_mode = true;          // only mark pictures judged empty; delete nothing
  uint8_t empty_view_hour = 12;    // local hour of the daily picture and summary
  float drop_threshold = 0.03f;    // filter: largest difference still "empty"
  float latitude = NAN;            // decimal degrees from setup, -90 to 90; NaN when not set
  float longitude = NAN;           // decimal degrees from setup, -180 to 180; NaN when not set
  Placement placement = Placement::Line;
  char side_a[32] = "";            // side A in words, e.g. "pond side"; may be empty
  uint8_t send_every_h = 24;       // hours between sends, 1 to 168
  uint16_t link_timeout_s = 180;   // longest try per send, 30 to 600
  uint16_t config_version = 1;     // raised by each settings command taken; FieldMesh's
                                   // configVersion of every reading
};

struct PassRecord {      // one row of a survey day's pass file
  char pass_id[40];      // <trap_id>-<survey day>-<number>
  uint32_t start_utc_s, end_utc_s;
  Pass pass;
  const char* pictures;  // ';'-separated file names
  uint8_t dropped_empty;      // pictures the filter dropped
  const char* judged_empty;   // ';'-separated names marked in pilot mode
  bool pilot;                 // the trap was in pilot mode
  ModelResult model;          // type None when the trap has no model
  const char* model_version;  // "" or null when the trap has no model
};

enum class FaultKind : uint8_t { BeamBlocked, BeamClear, BatteryLow, StorageLow, CameraFailed };

struct StateSummary {  // the values of one daily summary
  uint32_t utc_s, seq;
  float battery_v, temperature_c;  // NaN when not measured
  uint32_t passes, free_mb;        // passes since the last summary
  bool view_clear;                 // from the daily empty-view picture
};

/// Reads trap.cfg text into out, keeping defaults for missing keys; false on a malformed line.
/// The text holds key=value lines, blank lines and lines starting with '#'. An unknown key or a
/// value out of range is malformed. On false, out is left unchanged.
bool parse_config(const char* text, TrapConfig* out);

/// Writes c as trap.cfg text, which parse_config reads back to the same values; coordinates that
/// are not set are left out. Returns its length, or 0 if it does not fit in size.
size_t config_text(const TrapConfig& c, char* out, size_t size);

/// Survey day (noon to noon, local) of a UTC time, as "YYYY-MM-DD" of its first noon.
void survey_day(uint32_t utc_s, int16_t utc_offset_min, char out[11]);

/// CSV header of a survey day's pass file, ending in a newline.
const char* pass_csv_header();

/// One pass record as a CSV line ending in a newline; pictures and judged-empty marks as
/// ';'-separated names, and the model's columns empty when its type is None. Returns its length,
/// or 0 if it does not fit in size.
size_t pass_csv_line(const PassRecord& r, char* out, size_t size);

/// Reads a line of a pass file, as pass_csv_line writes it, back into out, so that a stored pass
/// is sent as pass_reading_json. Its texts (pictures, judged-empty marks, model version) point
/// into text, which holds text_size bytes; the watcher times are 0. False on a malformed line.
bool parse_pass_csv_line(const char* line, PassRecord* out, char* text, size_t text_size);

/// One fault as a CSV line for faults.csv, ending in a newline. Returns its length, or 0 if it
/// does not fit in size.
size_t fault_csv_line(uint32_t utc_s, FaultKind kind, const char* detail, char* out, size_t size);

/// The day's state summary as one FieldMesh reading, JSON on one line ending in a newline, with
/// the configured latitude and longitude, or null for them when not set. Returns its length, or 0
/// if it does not fit in size.
size_t summary_json(const StateSummary& s, const TrapConfig& c, char* out, size_t size);

/// One pass as a FieldMesh reading, JSON on one line ending in a newline, with flat trap keys and
/// its own seqNum; the model's keys are null when its type is None. Returns its length, or 0 if
/// it does not fit in size.
size_t pass_reading_json(const PassRecord& r, const TrapConfig& c, uint32_t seq, char* out,
                         size_t size);
