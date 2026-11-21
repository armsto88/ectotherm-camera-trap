#include "uplink.h"

#include <ArduinoJson.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

namespace {

// A survey day as "YYYY-MM-DD".
bool valid_day(const char* s) {
  if (strlen(s) != 10 || s[4] != '-' || s[7] != '-') return false;
  for (int i : {0, 1, 2, 3, 5, 6, 8, 9})
    if (s[i] < '0' || s[i] > '9') return false;
  return true;
}

bool parse_u32(const char* s, uint32_t* out) {
  if (*s < '0' || *s > '9') return false;
  char* end;
  const unsigned long long v = strtoull(s, &end, 10);
  if (*end != '\0' || v > UINT32_MAX) return false;
  *out = static_cast<uint32_t>(v);
  return true;
}

// Copies s[0..n) without surrounding spaces, tabs and a carriage return into out.
bool trimmed(const char* s, size_t n, char* out, size_t size) {
  while (n > 0 && (*s == ' ' || *s == '\t')) ++s, --n;
  while (n > 0 && (s[n - 1] == ' ' || s[n - 1] == '\t' || s[n - 1] == '\r')) --n;
  if (n >= size) return false;
  memcpy(out, s, n);
  out[n] = '\0';
  return true;
}

}  // namespace

bool parse_sent_position(const char* text, SentPosition* out) {
  SentPosition p = *out;
  const char* line = text;
  while (*line) {
    const char* end = strchr(line, '\n');
    const size_t len = end ? static_cast<size_t>(end - line) : strlen(line);
    char content[64];
    if (!trimmed(line, len, content, sizeof content)) return false;
    if (content[0] != '\0' && content[0] != '#') {
      char* eq = strchr(content, '=');
      if (!eq) return false;
      char key[24], value[24];
      if (!trimmed(content, static_cast<size_t>(eq - content), key, sizeof key)) return false;
      if (!trimmed(eq + 1, strlen(eq + 1), value, sizeof value)) return false;
      if (strcmp(key, "pass_day") == 0) {
        if (value[0] && !valid_day(value)) return false;
        memcpy(p.pass_day, value, strlen(value) + 1);
      } else if (strcmp(key, "pass_line") == 0) {
        if (!parse_u32(value, &p.pass_line)) return false;
      } else if (strcmp(key, "summary_line") == 0) {
        if (!parse_u32(value, &p.summary_line)) return false;
      } else if (strcmp(key, "next_seq") == 0) {
        if (!parse_u32(value, &p.next_seq)) return false;
      } else {
        return false;
      }
    }
    if (!end) break;
    line = end + 1;
  }
  *out = p;
  return true;
}

size_t sent_position_text(const SentPosition& p, char* out, size_t size) {
  const int n = snprintf(out, size,
                         "pass_day=%s\npass_line=%lu\nsummary_line=%lu\nnext_seq=%lu\n",
                         p.pass_day, static_cast<unsigned long>(p.pass_line),
                         static_cast<unsigned long>(p.summary_line),
                         static_cast<unsigned long>(p.next_seq));
  if (n < 0 || static_cast<size_t>(n) >= size) {
    if (size > 0) out[0] = '\0';
    return 0;
  }
  return static_cast<size_t>(n);
}

SendPlan::SendPlan(const SentPosition& confirmed) : confirmed_(confirmed) { restart(); }

bool SendPlan::add_pass_file(const char* day, uint32_t records) {
  if (!valid_day(day)) return true;
  const int against_confirmed = strcmp(day, confirmed_.pass_day);
  if (against_confirmed < 0) return true;
  if (against_confirmed == 0 && records <= confirmed_.pass_line) return true;

  // Keep the days in order, the earliest first; when full, the latest waits.
  size_t at = 0;
  while (at < n_days_ && strcmp(days_[at].day, day) < 0) ++at;
  if (at < n_days_ && strcmp(days_[at].day, day) == 0) {
    days_[at].records = records;
    restart();
    return true;
  }
  bool all_kept = true;
  if (n_days_ == kMaxDays) {
    all_kept = false;
    if (at == kMaxDays) return false;
    --n_days_;
  }
  memmove(&days_[at + 1], &days_[at], (n_days_ - at) * sizeof(Day));
  memcpy(days_[at].day, day, sizeof days_[at].day);
  days_[at].records = records;
  ++n_days_;
  restart();
  return all_kept;
}

void SendPlan::set_summaries(uint32_t lines) {
  summaries_ = lines;
  restart();
}

uint32_t SendPlan::first_line(size_t day_index) const {
  return strcmp(days_[day_index].day, confirmed_.pass_day) == 0 ? confirmed_.pass_line + 1 : 1;
}

void SendPlan::restart() {
  day_index_ = 0;
  // Days the confirmed position has reached since they were added are done.
  while (day_index_ < n_days_ && strcmp(days_[day_index_].day, confirmed_.pass_day) < 0)
    ++day_index_;
  line_ = day_index_ < n_days_ ? first_line(day_index_) : 1;
  seq_ = confirmed_.next_seq;
  summary_ = confirmed_.summary_line + 1;
}

bool SendPlan::next(ReadingPlace* out) {
  while (day_index_ < n_days_) {
    if (line_ <= days_[day_index_].records) {
      out->summary = false;
      memcpy(out->day, days_[day_index_].day, sizeof out->day);
      out->line = line_++;
      out->seq = seq_++;
      return true;
    }
    if (++day_index_ < n_days_) line_ = first_line(day_index_);
  }
  if (summary_ <= summaries_) {
    out->summary = true;
    out->day[0] = '\0';
    out->line = summary_++;
    out->seq = 0;
    return true;
  }
  return false;
}

void SendPlan::confirm(const ReadingPlace& last) {
  if (!last.summary) {
    memcpy(confirmed_.pass_day, last.day, sizeof confirmed_.pass_day);
    confirmed_.pass_line = last.line;
    confirmed_.next_seq = last.seq + 1;
    return;
  }
  // Summaries come after every pass of the plan, so those are confirmed as well.
  uint32_t passes = 0;
  for (size_t i = 0; i < n_days_; ++i) {
    if (strcmp(days_[i].day, confirmed_.pass_day) < 0) continue;
    const uint32_t first = first_line(i);
    if (days_[i].records >= first) passes += days_[i].records - first + 1;
  }
  if (passes > 0) {
    const Day& latest = days_[n_days_ - 1];
    memcpy(confirmed_.pass_day, latest.day, sizeof confirmed_.pass_day);
    confirmed_.pass_line = latest.records;
    confirmed_.next_seq += passes;
  }
  confirmed_.summary_line = last.line;
}

UploadBody::UploadBody(size_t max_readings) : max_(max_readings) {}

bool UploadBody::add(const char* reading_json) {
  if (count_ >= max_ || !reading_json) return false;
  size_t n = strlen(reading_json);
  while (n > 0 && (reading_json[n - 1] == '\n' || reading_json[n - 1] == '\r')) --n;
  if (n < 2 || reading_json[0] != '{' || reading_json[n - 1] != '}') return false;
  if (count_ > 0) readings_ += ',';
  readings_.append(reading_json, n);
  ++count_;
  return true;
}

size_t UploadBody::write(const char* firmware_version, const char* status_json, char* out,
                         size_t size) const {
  std::string body = "{\"readings\":[";
  body += readings_;
  body += "],\"meta\":{\"firmwareVersion\":";
  JsonDocument version;
  version.set(firmware_version ? firmware_version : "");
  std::string version_json;  // serializeJson replaces a string's content
  serializeJson(version, version_json);
  body += version_json;
  body += '}';
  if (status_json) {
    body += ",\"status\":";
    body += status_json;
  }
  body += '}';
  if (body.size() >= size) {
    if (size > 0) out[0] = '\0';
    return 0;
  }
  memcpy(out, body.c_str(), body.size() + 1);
  return body.size();
}

ReplyAction judge_reply(int http_status, uint32_t received, uint32_t sent) {
  if (http_status == 200) return received == sent ? ReplyAction::Confirm : ReplyAction::RetryLater;
  if (http_status == 401 || http_status == 403) return ReplyAction::Stop;
  if (http_status == 408 || http_status == 429) return ReplyAction::RetryLater;
  if (http_status >= 400 && http_status < 500) return ReplyAction::ResendSmaller;
  return ReplyAction::RetryLater;
}

bool parse_reply(const char* json, Reply* out) {
  JsonDocument doc;
  if (!json || deserializeJson(doc, json) || !doc.is<JsonObject>()) return false;
  out->received = doc["received"] | 0u;
  out->server_time_unix = doc["serverTimeUnix"] | 0u;
  out->next_cursor = doc["nextCursor"] | 0u;
  out->n_commands = 0;
  out->payload_text[0] = '\0';
  size_t used = 0;
  for (JsonObject c : doc["commands"].as<JsonArray>()) {
    if (out->n_commands == 8) break;
    Command& cmd = out->commands[out->n_commands];
    const char* id = c["commandId"] | "";
    const char* type = c["type"] | "";
    if (!id[0] || strlen(id) >= sizeof cmd.id || !type[0] || strlen(type) >= sizeof cmd.type)
      continue;
    const size_t len = measureJson(c["payload"]);
    if (used + len + 1 > sizeof out->payload_text) break;
    serializeJson(c["payload"], out->payload_text + used, sizeof out->payload_text - used);
    cmd.cursor = c["sequence"] | 0u;
    memcpy(cmd.id, id, strlen(id) + 1);
    memcpy(cmd.type, type, strlen(type) + 1);
    cmd.payload = out->payload_text + used;
    used += len + 1;
    ++out->n_commands;
  }
  return true;
}

CommandResult apply_settings(const char* payload, const TrapConfig& c, TrapConfig* out,
                             char* reason, size_t reason_size) {
  *out = c;
  auto refuse = [&](const char* format, const char* key) {
    snprintf(reason, reason_size, format, key);
    return CommandResult::Rejected;
  };
  JsonDocument doc;
  if (!payload || deserializeJson(doc, payload) || !doc.is<JsonObject>())
    return refuse("%s", "the settings are not a JSON object");

  TrapConfig next = c;
  for (JsonPair kv : doc.as<JsonObject>()) {
    const char* key = kv.key().c_str();
    if (!key[0] || strspn(key, "abcdefghijklmnopqrstuvwxyz_") != strlen(key))
      return refuse("%s is not a setting", key);
    if (strcmp(key, "trap_id") == 0 || strcmp(key, "config_version") == 0)
      return refuse("%s is not set over the link", key);

    // Each setting as a trap.cfg line, read by the same rules as the file.
    char value[64];
    const JsonVariant v = kv.value();
    if (v.is<bool>()) {
      snprintf(value, sizeof value, "%s", v.as<bool>() ? "true" : "false");
    } else if (v.is<long>()) {
      snprintf(value, sizeof value, "%ld", v.as<long>());
    } else if (v.is<double>()) {
      snprintf(value, sizeof value, "%.9g", v.as<double>());
    } else if (v.is<const char*>()) {
      const char* text = v.as<const char*>();
      if (strpbrk(text, "\r\n") || strlen(text) >= sizeof value)
        return refuse("%s has a value that cannot be a setting", key);
      snprintf(value, sizeof value, "%s", text);
    } else {
      return refuse("%s has a value that cannot be a setting", key);
    }
    char line[96];
    snprintf(line, sizeof line, "%s=%s\n", key, value);
    if (!parse_config(line, &next)) return refuse("%s is unknown or out of range", key);
  }
  next.config_version = c.config_version == UINT16_MAX ? 1 : c.config_version + 1;
  *out = next;
  if (reason_size > 0) reason[0] = '\0';
  return CommandResult::Accepted;
}

size_t control_status_json(uint32_t last_cursor, uint16_t config_version,
                           const CommandReport* reports, size_t n, char* out, size_t size) {
  JsonDocument doc;
  doc["controlProtocolVersion"] = 2;
  doc["stateRevision"] = config_version;
  doc["lastCommandCursor"] = last_cursor;
  JsonArray results = doc["results"].to<JsonArray>();
  for (size_t i = 0; i < n; ++i) {
    JsonObject r = results.add<JsonObject>();
    r["cmdId"] = reports[i].id;
    r["outcome"] = reports[i].result == CommandResult::Accepted ? "ACCEPTED" : "INVALID";
    r["revision"] = config_version;
  }
  if (measureJson(doc) >= size) {
    if (size > 0) out[0] = '\0';
    return 0;
  }
  return serializeJson(doc, out, size);
}

uint32_t next_send(uint32_t last_send_utc_s, const TrapConfig& c) {
  return last_send_utc_s + static_cast<uint32_t>(c.send_every_h) * 3600;
}
