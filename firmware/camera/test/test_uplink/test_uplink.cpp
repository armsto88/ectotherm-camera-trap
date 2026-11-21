// Unit tests of the uplink library: the confirmed position, the order of a send, upload bodies
// and FieldMesh's replies. A simulated card and a stand-in for FieldMesh run whole sends.
#include <ArduinoJson.h>
#include <string.h>
#include <unity.h>

#include <map>
#include <set>
#include <string>
#include <tuple>
#include <vector>

#include "records.h"
#include "uplink.h"

void setUp() {}
void tearDown() {}

// --- A simulated card -------------------------------------------------------------------------

struct Card {
  std::map<std::string, std::vector<std::string>> pass_files;  // survey day -> pass file lines
  std::vector<std::string> summaries;                          // state/summaries.jsonl
  SentPosition sent;                                           // state/sent.cfg

  // Records a pass as the capture writes it: a line of its survey day's pass file.
  void record_pass(const char* day, uint32_t start_utc_s, const char* pictures) {
    auto& lines = pass_files[day];
    PassRecord r{};
    snprintf(r.pass_id, sizeof r.pass_id, "ECT_0A1B2C-%s-%zu", day, lines.size() + 1);
    r.start_utc_s = start_utc_s;
    r.end_utc_s = start_utc_s + 2;
    r.pass = Pass{0, 0, Direction::AtoB, HEIGHT_LOWEST, HEIGHT_LOWEST, true, false};
    r.pictures = pictures;
    r.judged_empty = "";
    r.model = ModelResult{ModelType::Lizard, 0.8f};
    r.model_version = "m1.0.0";
    char line[256];
    TEST_ASSERT_TRUE(pass_csv_line(r, line, sizeof line) > 0);
    lines.push_back(line);
  }

  // Writes the daily summary, as the daily job does.
  void write_summary(uint32_t utc_s, uint32_t passes) {
    TrapConfig c;
    strcpy(c.trap_id, "ECT_0A1B2C");
    const StateSummary s{utc_s, static_cast<uint32_t>(summaries.size() + 1), 3.9f, 15.0f,
                         passes, 90000, true};
    char line[512];
    TEST_ASSERT_TRUE(summary_json(s, c, line, sizeof line) > 0);
    summaries.push_back(line);
  }

  // The reading at a place of a send, as the send job reads it from the card.
  std::string reading(const ReadingPlace& place) const {
    if (place.summary) return summaries.at(place.line - 1);
    const std::string& line = pass_files.at(place.day).at(place.line - 1);
    PassRecord r;
    char text[256], out[512];
    TEST_ASSERT_TRUE(parse_pass_csv_line(line.c_str(), &r, text, sizeof text));
    TrapConfig c;
    strcpy(c.trap_id, "ECT_0A1B2C");
    TEST_ASSERT_TRUE(pass_reading_json(r, c, place.seq, out, sizeof out) > 0);
    return out;
  }
};

// --- A stand-in for FieldMesh -----------------------------------------------------------------

struct FieldMesh {
  // Readings stored, by FieldMesh's duplicate key: node, time and seqNum.
  std::set<std::tuple<std::string, std::string, long>> stored;
  std::vector<std::string> kinds;  // trapKind of each new reading, in the order stored
  std::vector<std::string> bodies;
  std::set<int> lost_answers;    // posts, counted from 1, whose answer never reaches the trap
  int posts = 0;
  bool reachable = true;         // false: no network, every post fails
  uint32_t server_time = 1778760000;

  // Posts a body; returns the HTTP status, 0 for no answer, and the reply body.
  int post(const char* body, std::string* reply) {
    ++posts;
    bodies.push_back(body);
    if (!reachable) return 0;
    JsonDocument doc;
    TEST_ASSERT_FALSE(deserializeJson(doc, body));
    uint32_t received = 0;
    for (JsonObject r : doc["readings"].as<JsonArray>()) {
      ++received;
      const auto key = std::make_tuple(r["nodeId"].as<std::string>(),
                                       r["datetime"].as<std::string>(), r["seqNum"].as<long>());
      if (stored.insert(key).second) kinds.push_back(r["trapKind"].as<std::string>());
    }
    // A post that reaches FieldMesh but whose answer is lost: stored, but never confirmed.
    if (lost_answers.count(posts)) return 0;
    *reply = "{\"success\":true,\"appended\":" + std::to_string(received) +
             ",\"duplicate\":false,\"received\":" + std::to_string(received) +
             ",\"nextCursor\":0,\"serverTimeUnix\":" + std::to_string(server_time) +
             ",\"deploymentEventAcks\":[],\"controlProtocolVersion\":2,"
             "\"deploymentEventConflicts\":[],\"commands\":[]}";
    return 200;
  }
};

// One send, as the send job runs it: every unconfirmed reading in bodies of at most max_readings,
// the position confirmed after each body FieldMesh acknowledges in full. Returns the last action.
static ReplyAction send(Card* card, FieldMesh* fm, size_t max_readings = 100,
                        uint32_t* clock = nullptr) {
  SendPlan plan(card->sent);
  for (const auto& [day, lines] : card->pass_files)
    plan.add_pass_file(day.c_str(), static_cast<uint32_t>(lines.size()));
  plan.set_summaries(static_cast<uint32_t>(card->summaries.size()));

  ReplyAction action = ReplyAction::Confirm;
  bool first = true;
  for (;;) {
    UploadBody body(max_readings);
    ReadingPlace place, last{};
    while (body.count() < max_readings && plan.next(&place)) {
      TEST_ASSERT_TRUE(body.add(card->reading(place).c_str()));
      last = place;
    }
    if (body.count() == 0) return action;
    static char text[64 * 1024];
    TEST_ASSERT_TRUE(body.write("0.3.0", first ? "{\"batVoltage\":3.9}" : nullptr, text,
                                sizeof text) > 0);
    first = false;
    std::string answer;
    const int status = fm->post(text, &answer);
    Reply reply;
    const bool parsed = status == 200 && parse_reply(answer.c_str(), &reply);
    action = judge_reply(status, parsed ? reply.received : 0, body.count());
    if (action != ReplyAction::Confirm) return action;
    plan.confirm(last);
    card->sent = plan.confirmed();  // written to state/sent.cfg after each confirmed body
    if (clock && reply.server_time_unix) *clock = reply.server_time_unix;
  }
}

static const uint32_t kMay14Night = 1778792709;  // 2026-05-14T21:05:09Z
static const uint32_t kMay15Noon = 1778846400;   // 2026-05-15T12:00:00Z

// spec: 7dcfb88b
static void test_the_days_results_are_sent() {
  Card card;
  for (uint32_t i = 0; i < 3; ++i) card.record_pass("2026-05-14", kMay14Night + i * 60, "a.jpg");
  card.write_summary(kMay15Noon, 3);
  FieldMesh fm;
  TEST_ASSERT_EQUAL(ReplyAction::Confirm, send(&card, &fm));

  // The passes, then the summary, in one body; all confirmed.
  TEST_ASSERT_EQUAL(1, fm.posts);
  const std::vector<std::string> expected = {"pass", "pass", "pass", "state"};
  TEST_ASSERT_TRUE(expected == fm.kinds);
  TEST_ASSERT_EQUAL_STRING("2026-05-14", card.sent.pass_day);
  TEST_ASSERT_EQUAL(3, card.sent.pass_line);
  TEST_ASSERT_EQUAL(1, card.sent.summary_line);
  TEST_ASSERT_EQUAL(4, card.sent.next_seq);

  // The next send has nothing to send.
  TEST_ASSERT_EQUAL(ReplyAction::Confirm, send(&card, &fm));
  TEST_ASSERT_EQUAL(1, fm.posts);
}

static void test_a_long_send_puts_the_summary_last() {
  Card card;
  for (uint32_t i = 0; i < 230; ++i) card.record_pass("2026-05-14", kMay14Night + i, "a.jpg");
  card.write_summary(kMay15Noon, 230);
  FieldMesh fm;
  TEST_ASSERT_EQUAL(ReplyAction::Confirm, send(&card, &fm));
  TEST_ASSERT_EQUAL(3, fm.posts);  // 100, 100, then 30 passes and the summary
  TEST_ASSERT_EQUAL(231, fm.kinds.size());
  TEST_ASSERT_EQUAL_STRING("state", fm.kinds.back().c_str());
  TEST_ASSERT_EQUAL(231, card.sent.next_seq);
}

// spec: 09d3c9de
static void test_no_pictures_leave_the_trap() {
  Card card;
  card.record_pass("2026-05-14", kMay14Night, "ECT_0A1B2C-2026-05-14-1_1.jpg;"
                                              "ECT_0A1B2C-2026-05-14-1_2.jpg");
  card.write_summary(kMay15Noon, 1);
  FieldMesh fm;
  send(&card, &fm);
  TEST_ASSERT_EQUAL(1, fm.bodies.size());
  const std::string& body = fm.bodies[0];
  TEST_ASSERT_TRUE(body.find(".jpg") == std::string::npos);
  TEST_ASSERT_TRUE(body.find("\"trapPictures\":2") != std::string::npos);
  TEST_ASSERT_TRUE(body.size() < 1500);
}

// spec: 6da2648a
static void test_sending_more_often() {
  TrapConfig c;
  TEST_ASSERT_EQUAL(kMay15Noon + 24 * 3600, next_send(kMay15Noon, c));
  TEST_ASSERT_TRUE(parse_config("send_every_h=6\n", &c));
  TEST_ASSERT_EQUAL(kMay15Noon + 6 * 3600, next_send(kMay15Noon, c));

  // Six hours later the trap sends what came since, and only that.
  Card card;
  card.record_pass("2026-05-14", kMay14Night, "a.jpg");
  FieldMesh fm;
  send(&card, &fm);
  card.record_pass("2026-05-14", kMay14Night + 6 * 3600, "b.jpg");
  send(&card, &fm);
  TEST_ASSERT_EQUAL(2, fm.posts);
  TEST_ASSERT_TRUE(fm.bodies[1].find("ECT_0A1B2C-2026-05-14-2") != std::string::npos);
  TEST_ASSERT_TRUE(fm.bodies[1].find("ECT_0A1B2C-2026-05-14-1\"") == std::string::npos);
  TEST_ASSERT_EQUAL(2, card.sent.pass_line);
}

// spec: 8f7fa060
static void test_a_day_without_coverage() {
  Card card;
  FieldMesh fm;
  card.record_pass("2026-05-13", kMay14Night - 86400, "a.jpg");
  card.write_summary(kMay15Noon - 86400, 1);
  fm.reachable = false;
  TEST_ASSERT_EQUAL(ReplyAction::RetryLater, send(&card, &fm));
  TEST_ASSERT_EQUAL_STRING("", card.sent.pass_day);  // nothing confirmed

  card.record_pass("2026-05-14", kMay14Night, "b.jpg");
  card.record_pass("2026-05-14", kMay14Night + 60, "c.jpg");
  card.write_summary(kMay15Noon, 2);
  fm.reachable = true;
  TEST_ASSERT_EQUAL(ReplyAction::Confirm, send(&card, &fm));
  // Yesterday's and today's passes and summaries, the summaries last.
  const std::vector<std::string> expected = {"pass", "pass", "pass", "state", "state"};
  TEST_ASSERT_TRUE(expected == fm.kinds);
  TEST_ASSERT_EQUAL_STRING("2026-05-14", card.sent.pass_day);
  TEST_ASSERT_EQUAL(2, card.sent.pass_line);
  TEST_ASSERT_EQUAL(2, card.sent.summary_line);
}

// spec: 03f27597
static void test_a_send_breaks_off() {
  Card card;
  for (uint32_t i = 0; i < 150; ++i) card.record_pass("2026-05-14", kMay14Night + i, "a.jpg");
  card.write_summary(kMay15Noon, 150);
  FieldMesh fm;
  fm.lost_answers = {2};  // the second body reaches FieldMesh, but its answer is lost
  TEST_ASSERT_EQUAL(ReplyAction::RetryLater, send(&card, &fm));
  TEST_ASSERT_EQUAL(100, card.sent.pass_line);  // the first body was confirmed
  TEST_ASSERT_EQUAL(0, card.sent.summary_line);

  // The next send carries the second body again, with the same seqNums, so FieldMesh stores
  // nothing twice and confirms it.
  TEST_ASSERT_EQUAL(ReplyAction::Confirm, send(&card, &fm));
  TEST_ASSERT_EQUAL(3, fm.posts);
  TEST_ASSERT_TRUE(fm.bodies[1].substr(0, 200) == fm.bodies[2].substr(0, 200));
  TEST_ASSERT_EQUAL(151, fm.stored.size());
  TEST_ASSERT_EQUAL(150, card.sent.pass_line);
  TEST_ASSERT_EQUAL(1, card.sent.summary_line);
  TEST_ASSERT_EQUAL(151, card.sent.next_seq);
}

// spec: 81b45c6f
static void test_the_clock_has_drifted() {
  Card card;
  card.write_summary(kMay15Noon, 0);
  FieldMesh fm;
  uint32_t clock = fm.server_time - 60;  // a minute behind
  TEST_ASSERT_EQUAL(ReplyAction::Confirm, send(&card, &fm, 100, &clock));
  TEST_ASSERT_EQUAL(fm.server_time, clock);
}

static void test_a_body_refused_as_too_large_is_resent_smaller() {
  Card card;
  for (uint32_t i = 0; i < 5; ++i) card.record_pass("2026-05-14", kMay14Night + i, "a.jpg");
  SendPlan plan(card.sent);
  plan.add_pass_file("2026-05-14", 5);
  ReadingPlace place;
  UploadBody body;
  while (plan.next(&place)) body.add(card.reading(place).c_str());
  TEST_ASSERT_EQUAL(ReplyAction::ResendSmaller, judge_reply(413, 0, body.count()));
  // Back to the confirmed position: the same readings again, with the same seqNums.
  plan.restart();
  TEST_ASSERT_TRUE(plan.next(&place));
  TEST_ASSERT_EQUAL(1, place.line);
  TEST_ASSERT_EQUAL(1, place.seq);
}

static void test_reply_actions() {
  TEST_ASSERT_EQUAL(ReplyAction::Confirm, judge_reply(200, 13, 13));
  TEST_ASSERT_EQUAL(ReplyAction::RetryLater, judge_reply(200, 11, 13));  // received short
  TEST_ASSERT_EQUAL(ReplyAction::ResendSmaller, judge_reply(400, 0, 13));
  TEST_ASSERT_EQUAL(ReplyAction::ResendSmaller, judge_reply(413, 0, 13));
  TEST_ASSERT_EQUAL(ReplyAction::ResendSmaller, judge_reply(422, 0, 13));
  TEST_ASSERT_EQUAL(ReplyAction::Stop, judge_reply(401, 0, 13));
  TEST_ASSERT_EQUAL(ReplyAction::Stop, judge_reply(403, 0, 13));
  TEST_ASSERT_EQUAL(ReplyAction::RetryLater, judge_reply(408, 0, 13));
  TEST_ASSERT_EQUAL(ReplyAction::RetryLater, judge_reply(429, 0, 13));
  TEST_ASSERT_EQUAL(ReplyAction::RetryLater, judge_reply(503, 0, 13));
  TEST_ASSERT_EQUAL(ReplyAction::RetryLater, judge_reply(0, 0, 13));
  TEST_ASSERT_EQUAL(ReplyAction::RetryLater, judge_reply(-1, 0, 13));
}

static void test_a_reply_with_commands() {
  // Shaped like FieldMesh's replies in its upload contract, with a command for the trap.
  const char* json =
      "{\"success\":true,\"appended\":13,\"duplicate\":false,\"received\":13,\"nextCursor\":131,"
      "\"serverTimeUnix\":1793953179,\"deploymentEventAcks\":[],\"controlProtocolVersion\":2,"
      "\"deploymentEventConflicts\":[],\"commands\":[{\"commandId\":\"Dabcdefghijklmnopqrstuv\","
      "\"sequence\":131,\"type\":\"SET_TRAP_CONFIG\",\"target\":{\"nodeId\":\"ECT_0A1B2C\"},"
      "\"expectedStateRevision\":43,\"payload\":{\"send_every_h\":6,\"side_a\":\"pond side\"}},"
      "{\"commandId\":\"Eabc\",\"sequence\":132,\"type\":\"REQUEST_STATUS\"}]}";
  static Reply reply;
  TEST_ASSERT_TRUE(parse_reply(json, &reply));
  TEST_ASSERT_EQUAL(13, reply.received);
  TEST_ASSERT_EQUAL(1793953179u, reply.server_time_unix);
  TEST_ASSERT_EQUAL(131, reply.next_cursor);
  TEST_ASSERT_EQUAL(2, reply.n_commands);
  TEST_ASSERT_EQUAL(131, reply.commands[0].cursor);
  TEST_ASSERT_EQUAL_STRING("Dabcdefghijklmnopqrstuv", reply.commands[0].id);
  TEST_ASSERT_EQUAL_STRING("SET_TRAP_CONFIG", reply.commands[0].type);
  TEST_ASSERT_EQUAL_STRING("{\"send_every_h\":6,\"side_a\":\"pond side\"}",
                           reply.commands[0].payload);
  TEST_ASSERT_EQUAL_STRING("REQUEST_STATUS", reply.commands[1].type);
  TEST_ASSERT_EQUAL_STRING("null", reply.commands[1].payload);
}

static void test_replies_that_are_not_json_objects() {
  static Reply reply;
  TEST_ASSERT_FALSE(parse_reply("<html>Bad gateway</html>", &reply));
  TEST_ASSERT_FALSE(parse_reply("[1,2]", &reply));
  TEST_ASSERT_FALSE(parse_reply(nullptr, &reply));
  // A refusal has no count, which never confirms a body.
  TEST_ASSERT_TRUE(parse_reply("{\"success\":false,\"error\":\"reading datetime is invalid\"}",
                               &reply));
  TEST_ASSERT_EQUAL(0, reply.received);
  TEST_ASSERT_EQUAL(0, reply.n_commands);
  TEST_ASSERT_EQUAL(ReplyAction::RetryLater, judge_reply(200, reply.received, 3));
}

static void test_an_upload_body() {
  UploadBody body(2);
  TEST_ASSERT_TRUE(body.add("{\"nodeId\":\"A\"}\n"));
  TEST_ASSERT_FALSE(body.add("not a reading"));
  TEST_ASSERT_TRUE(body.add("{\"nodeId\":\"B\"}"));
  TEST_ASSERT_FALSE(body.add("{\"nodeId\":\"C\"}"));  // full
  TEST_ASSERT_EQUAL(2, body.count());
  char out[256];
  TEST_ASSERT_TRUE(body.write("0.3.0", "{\"batVoltage\":3.9}", out, sizeof out) > 0);
  TEST_ASSERT_EQUAL_STRING(
      "{\"readings\":[{\"nodeId\":\"A\"},{\"nodeId\":\"B\"}],\"meta\":{\"firmwareVersion\":"
      "\"0.3.0\"},\"status\":{\"batVoltage\":3.9}}",
      out);
  TEST_ASSERT_TRUE(body.write("0.3.0", nullptr, out, sizeof out) > 0);
  TEST_ASSERT_EQUAL_STRING(
      "{\"readings\":[{\"nodeId\":\"A\"},{\"nodeId\":\"B\"}],\"meta\":{\"firmwareVersion\":"
      "\"0.3.0\"}}",
      out);
  TEST_ASSERT_EQUAL(0, body.write("0.3.0", nullptr, out, 20));
  TEST_ASSERT_EQUAL_STRING("", out);
}

static void test_the_sent_position_reads_back() {
  SentPosition p;
  strcpy(p.pass_day, "2026-05-14");
  p.pass_line = 17;
  p.summary_line = 12;
  p.next_seq = 1044;
  char text[128];
  TEST_ASSERT_TRUE(sent_position_text(p, text, sizeof text) > 0);
  SentPosition back;
  TEST_ASSERT_TRUE(parse_sent_position(text, &back));
  TEST_ASSERT_EQUAL_STRING("2026-05-14", back.pass_day);
  TEST_ASSERT_EQUAL(17, back.pass_line);
  TEST_ASSERT_EQUAL(12, back.summary_line);
  TEST_ASSERT_EQUAL(1044, back.next_seq);

  // A new card has no sent.cfg: nothing is confirmed yet.
  const SentPosition fresh;
  TEST_ASSERT_EQUAL_STRING("", fresh.pass_day);
  TEST_ASSERT_EQUAL(1, fresh.next_seq);

  const char* bad[] = {"pass_day=14.05.2026\n", "pass_line=-1\n", "next_seq=x\n",
                       "sent=1\n", "pass_line 3\n", "summary_line=99999999999\n"};
  for (const char* t : bad) {
    SentPosition q = p;
    TEST_ASSERT_FALSE_MESSAGE(parse_sent_position(t, &q), t);
    TEST_ASSERT_EQUAL(17, q.pass_line);
  }
}

static void test_a_full_plan_keeps_the_earliest_days() {
  SendPlan plan{SentPosition{}};
  char day[11];
  // Days added latest first; the plan keeps the earliest 64.
  bool all = true;
  for (int i = 70; i >= 1; --i) {
    snprintf(day, sizeof day, "2026-%02d-%02d", 3 + (i - 1) / 28, 1 + (i - 1) % 28);
    all = plan.add_pass_file(day, 1) && all;
  }
  TEST_ASSERT_FALSE(all);
  ReadingPlace place;
  int n = 0;
  std::string first, last;
  while (plan.next(&place)) {
    if (n == 0) first = place.day;
    last = place.day;
    ++n;
  }
  TEST_ASSERT_EQUAL(64, n);
  TEST_ASSERT_EQUAL_STRING("2026-03-01", first.c_str());
  TEST_ASSERT_EQUAL_STRING("2026-05-08", last.c_str());
}

static void test_confirmed_days_are_skipped() {
  SentPosition p;
  strcpy(p.pass_day, "2026-05-14");
  p.pass_line = 2;
  p.next_seq = 10;
  SendPlan plan(p);
  plan.add_pass_file("2026-05-13", 5);  // confirmed before
  plan.add_pass_file("2026-05-14", 3);  // one new record
  plan.add_pass_file("2026-05-15", 1);
  ReadingPlace place;
  TEST_ASSERT_TRUE(plan.next(&place));
  TEST_ASSERT_EQUAL_STRING("2026-05-14", place.day);
  TEST_ASSERT_EQUAL(3, place.line);
  TEST_ASSERT_EQUAL(10, place.seq);
  TEST_ASSERT_TRUE(plan.next(&place));
  TEST_ASSERT_EQUAL_STRING("2026-05-15", place.day);
  TEST_ASSERT_EQUAL(1, place.line);
  TEST_ASSERT_EQUAL(11, place.seq);
  TEST_ASSERT_FALSE(plan.next(&place));
}

int main() {
  UNITY_BEGIN();
  RUN_TEST(test_the_days_results_are_sent);
  RUN_TEST(test_a_long_send_puts_the_summary_last);
  RUN_TEST(test_no_pictures_leave_the_trap);
  RUN_TEST(test_sending_more_often);
  RUN_TEST(test_a_day_without_coverage);
  RUN_TEST(test_a_send_breaks_off);
  RUN_TEST(test_the_clock_has_drifted);
  RUN_TEST(test_a_body_refused_as_too_large_is_resent_smaller);
  RUN_TEST(test_reply_actions);
  RUN_TEST(test_a_reply_with_commands);
  RUN_TEST(test_replies_that_are_not_json_objects);
  RUN_TEST(test_an_upload_body);
  RUN_TEST(test_the_sent_position_reads_back);
  RUN_TEST(test_a_full_plan_keeps_the_earliest_days);
  RUN_TEST(test_confirmed_days_are_skipped);
  return UNITY_END();
}
