#include "updates.h"

#include <ArduinoJson.h>
#include <Ed25519.h>
#include <string.h>

namespace {

bool hex_to_bytes(const char* hex, uint8_t* out, size_t n) {
  if (strlen(hex) != 2 * n) return false;
  for (size_t i = 0; i < 2 * n; ++i) {
    const char ch = hex[i];
    uint8_t v;
    if (ch >= '0' && ch <= '9') {
      v = ch - '0';
    } else if (ch >= 'a' && ch <= 'f') {
      v = ch - 'a' + 10;
    } else if (ch >= 'A' && ch <= 'F') {
      v = ch - 'A' + 10;
    } else {
      return false;
    }
    out[i / 2] = i % 2 ? (out[i / 2] | v) : static_cast<uint8_t>(v << 4);
  }
  return true;
}

// A version safe to write into the pass file and into readings as it is.
bool valid_version(const char* s) {
  const size_t n = strlen(s);
  if (n == 0 || n >= sizeof(Manifest::version)) return false;
  return strspn(s, "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789.-_+") == n;
}

}  // namespace

bool verify_manifest(const uint8_t* json, size_t n, const uint8_t signature[64],
                     const uint8_t release_key[32], Manifest* out) {
  // Trust nothing in the manifest before its signature holds.
  if (!json || !Ed25519::verify(signature, release_key, json, n)) return false;
  JsonDocument doc;
  if (deserializeJson(doc, reinterpret_cast<const char*>(json), n)) return false;
  for (JsonObjectConst a : doc["artifacts"].as<JsonArrayConst>()) {
    const char* role = a["role"] | "";
    if (strcmp(role, "trap") != 0 && strcmp(role, "trap-model") != 0) continue;
    Manifest m{};
    memcpy(m.role, role, strlen(role) + 1);
    const char* version = a["version"] | "";
    if (!valid_version(version)) return false;
    memcpy(m.version, version, strlen(version) + 1);
    m.size = a["size"] | 0u;
    if (m.size == 0 || !hex_to_bytes(a["sha256"] | "", m.sha256, sizeof m.sha256)) return false;
    *out = m;
    return true;
  }
  return false;
}

FileCheck::FileCheck(const Manifest& m) : m_(m) {}

void FileCheck::update(const uint8_t* data, size_t n) {
  hash_.update(data, n);
  size_ += static_cast<uint32_t>(n);
}

bool FileCheck::matches() {
  uint8_t digest[32];
  hash_.finalize(digest, sizeof digest);
  return size_ == m_.size && memcmp(digest, m_.sha256, sizeof digest) == 0;
}
