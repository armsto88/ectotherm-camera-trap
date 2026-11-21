// Unit tests of the updates library: manifests and files of firmware and model updates, checked
// against a release key. The tests sign releases with a test key of their own, in the FieldHub's
// release manifest format.
#include <Ed25519.h>
#include <SHA256.h>
#include <stdio.h>
#include <string.h>
#include <unity.h>

#include <string>
#include <vector>

#include "records.h"
#include "updates.h"

void setUp() {}
void tearDown() {}

// A signing key for the tests only; the trap holds the public part of the real release key.
struct TestKey {
  uint8_t private_key[32];
  uint8_t public_key[32];
  explicit TestKey(uint8_t seed) {
    for (int i = 0; i < 32; ++i) private_key[i] = static_cast<uint8_t>(seed + i);
    Ed25519::derivePublicKey(public_key, private_key);
  }
  void sign(const std::string& manifest, uint8_t signature[64]) const {
    Ed25519::sign(signature, private_key, public_key, manifest.data(), manifest.size());
  }
};

static const TestKey kReleaseKey(1);
static const TestKey kOtherKey(77);

static std::vector<uint8_t> file_of(size_t n, uint8_t seed) {
  std::vector<uint8_t> f(n);
  for (size_t i = 0; i < n; ++i) f[i] = static_cast<uint8_t>(seed + i * 31);
  return f;
}

static std::string sha256_hex(const std::vector<uint8_t>& f) {
  SHA256 h;
  h.update(f.data(), f.size());
  uint8_t d[32];
  h.finalize(d, sizeof d);
  std::string hex;
  char two[3];
  for (uint8_t b : d) {
    snprintf(two, sizeof two, "%02x", b);
    hex += two;
  }
  return hex;
}

// A release as FieldMesh would offer it, with one artifact.
static std::string release(const char* role, const char* version, const std::vector<uint8_t>& f) {
  return std::string("{\"schemaVersion\":1,\"releaseId\":\"r-") + version +
         "\",\"releaseSequence\":7,\"artifacts\":[{\"role\":\"" + role + "\",\"version\":\"" +
         version + "\",\"buildId\":\"a1b2c3d\",\"hwTargets\":[\"trap-v1\"],\"size\":" +
         std::to_string(f.size()) + ",\"sha256\":\"" + sha256_hex(f) + "\"}]}";
}

static bool verify(const std::string& manifest, const uint8_t signature[64], Manifest* out) {
  return verify_manifest(reinterpret_cast<const uint8_t*>(manifest.data()), manifest.size(),
                         signature, kReleaseKey.public_key, out);
}

// Feeds a file in pieces, as it is downloaded.
static bool file_matches(const Manifest& m, const std::vector<uint8_t>& f) {
  FileCheck check(m);
  for (size_t at = 0; at < f.size(); at += 1000)
    check.update(f.data() + at, f.size() - at < 1000 ? f.size() - at : 1000);
  return check.matches();
}

static void test_a_signed_firmware_update_passes_its_check() {
  const auto image = file_of(5000, 3);
  const std::string manifest = release("trap", "0.3.1", image);
  uint8_t signature[64];
  kReleaseKey.sign(manifest, signature);
  Manifest m;
  TEST_ASSERT_TRUE(verify(manifest, signature, &m));
  TEST_ASSERT_EQUAL_STRING("trap", m.role);
  TEST_ASSERT_EQUAL_STRING("0.3.1", m.version);
  TEST_ASSERT_EQUAL(5000, m.size);
  TEST_ASSERT_TRUE(file_matches(m, image));
}

// spec: 2a4e75f4
static void test_an_unsigned_firmware_update_is_refused() {
  const auto image = file_of(5000, 3);
  const std::string manifest = release("trap", "0.3.1", image);
  Manifest m;

  // Signed with another key than the release key.
  uint8_t signature[64];
  kOtherKey.sign(manifest, signature);
  TEST_ASSERT_FALSE(verify(manifest, signature, &m));

  // Signed with the release key, but changed after signing.
  kReleaseKey.sign(manifest, signature);
  std::string changed = manifest;
  changed.replace(changed.find("0.3.1\",\"buildId"), 5, "0.9.9");
  TEST_ASSERT_FALSE(verify(changed, signature, &m));

  // A signed manifest with a firmware image that is not the one it names.
  TEST_ASSERT_TRUE(verify(manifest, signature, &m));
  auto other = image;
  other[1234] ^= 0x01;
  TEST_ASSERT_FALSE(file_matches(m, other));
  other = image;
  other.pop_back();
  TEST_ASSERT_FALSE(file_matches(m, other));

  // The trap keeps its firmware and records a failed update.
  char line[128];
  TEST_ASSERT_TRUE(fault_csv_line(1778760000, FaultKind::UpdateFailed,
                                  "firmware 0.3.1: signature", line, sizeof line) > 0);
  TEST_ASSERT_EQUAL_STRING("2026-05-14T12:00:00Z,update_failed,firmware 0.3.1: signature\n",
                           line);
}

// spec: c3876d58
static void test_a_model_that_fails_its_check_is_refused() {
  const auto model = file_of(120000, 9);
  const std::string manifest = release("trap-model", "m1.1.0", model);
  Manifest m;
  uint8_t signature[64];

  // Its signature does not match the release key.
  kOtherKey.sign(manifest, signature);
  TEST_ASSERT_FALSE(verify(manifest, signature, &m));

  // Signed, but the model file is broken.
  kReleaseKey.sign(manifest, signature);
  TEST_ASSERT_TRUE(verify(manifest, signature, &m));
  TEST_ASSERT_EQUAL_STRING("trap-model", m.role);
  TEST_ASSERT_EQUAL_STRING("m1.1.0", m.version);
  TEST_ASSERT_TRUE(file_matches(m, model));
  auto broken = model;
  broken[0] ^= 0xff;
  TEST_ASSERT_FALSE(file_matches(m, broken));

  // The trap keeps its current model, or none, and records a failed update.
  char line[128];
  TEST_ASSERT_TRUE(fault_csv_line(1778760000, FaultKind::UpdateFailed,
                                  "model m1.1.0: file", line, sizeof line) > 0);
  TEST_ASSERT_NOT_NULL(strstr(line, ",update_failed,model m1.1.0: file\n"));
}

static void test_releases_without_a_usable_artifact_are_refused() {
  const auto image = file_of(100, 5);
  const std::vector<std::string> refused = {
      release("mothership", "0.9.0", image),  // nothing for the trap
      release("trap", "0.3.1,x", image),      // a version unsafe in records
      release("trap", "0.3.1-with-a-long-name", image),
      std::string("{\"artifacts\":[{\"role\":\"trap\",\"version\":\"0.3.1\",\"size\":100,"
                  "\"sha256\":\"abc\"}]}"),  // not a SHA-256
      std::string("{\"artifacts\":[{\"role\":\"trap\",\"version\":\"0.3.1\",\"size\":0,"
                  "\"sha256\":\"") +
          sha256_hex(image) + "\"}]}",
      std::string("not json"),
  };
  for (const auto& manifest : refused) {
    uint8_t signature[64];
    kReleaseKey.sign(manifest, signature);
    Manifest m;
    TEST_ASSERT_FALSE_MESSAGE(verify(manifest, signature, &m), manifest.c_str());
  }
}

static void test_the_trap_artifact_of_a_release_with_several() {
  const auto image = file_of(300, 2);
  const std::string manifest =
      "{\"schemaVersion\":1,\"artifacts\":[{\"role\":\"mothership\",\"version\":\"0.9.0\","
      "\"size\":10,\"sha256\":\"" + sha256_hex(file_of(10, 1)) + "\"},{\"role\":\"trap\","
      "\"version\":\"0.3.2\",\"size\":300,\"sha256\":\"" + sha256_hex(image) + "\"}]}";
  uint8_t signature[64];
  kReleaseKey.sign(manifest, signature);
  Manifest m;
  TEST_ASSERT_TRUE(verify(manifest, signature, &m));
  TEST_ASSERT_EQUAL_STRING("trap", m.role);
  TEST_ASSERT_EQUAL_STRING("0.3.2", m.version);
  TEST_ASSERT_TRUE(file_matches(m, image));
}

int main() {
  UNITY_BEGIN();
  RUN_TEST(test_a_signed_firmware_update_passes_its_check);
  RUN_TEST(test_an_unsigned_firmware_update_is_refused);
  RUN_TEST(test_a_model_that_fails_its_check_is_refused);
  RUN_TEST(test_releases_without_a_usable_artifact_are_refused);
  RUN_TEST(test_the_trap_artifact_of_a_release_with_several);
  return UNITY_END();
}
