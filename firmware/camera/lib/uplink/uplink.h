// Sending: upload bodies, the confirmed position, the order of a send and FieldMesh's replies,
// following the FieldMesh upload contract and the FieldHub's upload rules. No hardware calls, so
// it is tested on the computer.
//
// The send job on the board lists the card's files for a SendPlan, reads each reading it names,
// posts UploadBodies and, by judge_reply, confirms the plan's position or restarts it.
#pragma once

#include <stddef.h>
#include <stdint.h>

#include <string>

#include "records.h"

// What FieldMesh has confirmed, kept in state/sent.cfg on the card.
struct SentPosition {
  char pass_day[11] = "";     // survey day of the last confirmed pass; "" for none
  uint32_t pass_line = 0;     // last confirmed record in that day's pass file, from 1
  uint32_t summary_line = 0;  // confirmed lines of state/summaries.jsonl
  uint32_t next_seq = 1;      // seqNum for the next pass reading
};

/// Reads state/sent.cfg, key=value lines as sent_position_text writes them; keys left out keep
/// out's values. False on malformed text, leaving out unchanged.
bool parse_sent_position(const char* text, SentPosition* out);

/// Writes p as state/sent.cfg text. Returns its length, or 0 if it does not fit in size.
size_t sent_position_text(const SentPosition& p, char* out, size_t size);

// Where one reading of a send lies on the card.
struct ReadingPlace {
  bool summary;  // a line of state/summaries.jsonl, else a pass
  char day[11];  // survey day of the pass file
  uint32_t line; // record in its file, from 1
  uint32_t seq;  // seqNum of a pass reading
};

/// The readings of one send in order: unconfirmed passes by survey day and line, then the
/// unconfirmed summaries, so that a summary is the newest reading FieldMesh gets. A pass resent
/// after a failed batch keeps its seqNum, so FieldMesh recognises it as a duplicate.
class SendPlan {
 public:
  static const size_t kMaxDays = 64;

  explicit SendPlan(const SentPosition& confirmed);

  /// Adds a survey day's pass file with its number of records, in any order of days. Days
  /// already confirmed are skipped. False when the plan is full and a later day waits for the
  /// next send.
  bool add_pass_file(const char* day, uint32_t records);

  /// Sets the number of lines in state/summaries.jsonl.
  void set_summaries(uint32_t lines);

  /// The next reading to send; false when none is left.
  bool next(ReadingPlace* out);

  /// Moves the confirmed position past every reading up to and including last, which next gave.
  void confirm(const ReadingPlace& last);

  /// Goes back to the reading after the confirmed position, to resend what was not confirmed.
  void restart();

  const SentPosition& confirmed() const { return confirmed_; }

 private:
  struct Day {
    char day[11];
    uint32_t records;
  };
  uint32_t first_line(size_t day_index) const;

  SentPosition confirmed_;
  Day days_[kMaxDays];
  size_t n_days_ = 0;
  uint32_t summaries_ = 0;
  size_t day_index_ = 0;  // the next reading: a pass of days_[day_index_] at line_ ...
  uint32_t line_ = 1;
  uint32_t seq_ = 1;
  uint32_t summary_ = 1;  // ... or, once every day is done, this summary line
};

/// One upload: readings, meta and, on a session's first body, the trap's status.
class UploadBody {
 public:
  explicit UploadBody(size_t max_readings = 100);

  /// Adds one reading, a JSON object on one line; false when the body is full or the reading
  /// is not an object.
  bool add(const char* reading_json);

  /// The JSON body: readings, meta with the firmware version, and status when status_json is not
  /// null. Returns its length, or 0 if it does not fit in size.
  size_t write(const char* firmware_version, const char* status_json, char* out,
               size_t size) const;

  size_t count() const { return count_; }

 private:
  size_t max_;
  size_t count_ = 0;
  std::string readings_;
};

enum class ReplyAction : uint8_t { Confirm, ResendSmaller, Stop, RetryLater };

/// As the FieldHub: Confirm only on 200 with received == sent; 401 or 403 stop, since the upload
/// key must be replaced; 408, 429, 5xx and no answer (0 or below) retry at the next send; 400,
/// 413 and any other 4xx resend smaller.
ReplyAction judge_reply(int http_status, uint32_t received, uint32_t sent);

struct Command {
  uint32_t cursor;      // FieldMesh's sequence
  char id[32];          // FieldMesh's commandId, named when confirming
  char type[24];
  const char* payload;  // the payload as JSON text, in the Reply's buffer
};

struct Reply {
  uint32_t received;          // readings FieldMesh received; 0 when absent
  uint32_t server_time_unix;  // 0 when absent
  uint32_t next_cursor;       // 0 when absent
  Command commands[8];
  uint8_t n_commands;
  char payload_text[2048];    // the commands' payloads
};

/// Reads FieldMesh's reply body; false when it is not a JSON object. Commands whose ID or type
/// does not fit, or beyond the eighth or the payload buffer, are left out.
bool parse_reply(const char* json, Reply* out);

/// UTC time of the next send after the last one, every send_every_h hours.
uint32_t next_send(uint32_t last_send_utc_s, const TrapConfig& c);
