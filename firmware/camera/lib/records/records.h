// Records, summary and configuration: the text of everything the trap writes to its card.
// No hardware calls, so it is tested on the computer.
#pragma once

#include <stddef.h>
#include <stdint.h>

#include "passes.h"

// The trap's settings from trap.cfg. A default-constructed TrapConfig holds the defaults, which
// parse_config keeps for keys the file leaves out.
struct TrapConfig {
  char trap_id[16] = "ECT_UNSET";  // also the FieldMesh nodeId, e.g. ECT_0A1B2C
  int16_t utc_offset_min = 0;      // for survey days and the daily times
  bool pilot_mode = true;          // only mark pictures judged empty; delete nothing
  uint8_t empty_view_hour = 12;    // local hour of the daily picture and summary
  float drop_threshold = 0.03f;    // filter: largest difference still "empty"
};

struct PassRecord {      // one row of a survey day's pass file
  char pass_id[40];      // <trap_id>-<survey day>-<number>
  uint32_t start_utc_s, end_utc_s;
  Pass pass;
  const char* pictures;  // ';'-separated file names
  uint8_t dropped_empty;     // pictures the filter dropped
  const char* judged_empty;  // ';'-separated names marked in pilot mode
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

/// Survey day (noon to noon, local) of a UTC time, as "YYYY-MM-DD" of its first noon.
void survey_day(uint32_t utc_s, int16_t utc_offset_min, char out[11]);

/// CSV header of a survey day's pass file, ending in a newline.
const char* pass_csv_header();

/// One pass record as a CSV line ending in a newline; pictures and judged-empty marks as
/// ';'-separated names. Returns its length, or 0 if it does not fit in size.
size_t pass_csv_line(const PassRecord& r, char* out, size_t size);

/// One fault as a CSV line for faults.csv, ending in a newline. Returns its length, or 0 if it
/// does not fit in size.
size_t fault_csv_line(uint32_t utc_s, FaultKind kind, const char* detail, char* out, size_t size);

/// The day's state summary as one FieldMesh reading, JSON on one line ending in a newline.
/// Returns its length, or 0 if it does not fit in size.
size_t summary_json(const StateSummary& s, const TrapConfig& c, char* out, size_t size);
