// Signed updates: checks the manifests and files of firmware and model updates against the
// release key. Follows the FieldHub's release manifest: a JSON release with a list of artifacts,
// signed with Ed25519 over its exact bytes in a separate signature, each artifact with its role,
// version, size and SHA-256. No hardware calls, so it is tested on the computer.
#pragma once

#include <SHA256.h>
#include <stddef.h>
#include <stdint.h>

// The artifact of a release meant for the trap.
struct Manifest {
  char role[16];       // "trap" for firmware, "trap-model" for models
  char version[16];    // letters, digits, '.', '-', '_' and '+' only
  uint32_t size;       // bytes of the file
  uint8_t sha256[32];  // of the file
};

/// Checks the Ed25519 signature over the exact bytes of manifest.json against the release key,
/// then reads the first artifact with the role "trap" or "trap-model" into out. False on a bad
/// signature, a malformed manifest or a release with nothing for the trap.
bool verify_manifest(const uint8_t* json, size_t n, const uint8_t signature[64],
                     const uint8_t release_key[32], Manifest* out);

/// Feeds a downloaded file in pieces and compares its size and SHA-256 with the manifest.
class FileCheck {
 public:
  explicit FileCheck(const Manifest& m);

  void update(const uint8_t* data, size_t n);

  /// True when the file had the manifest's size and SHA-256; call once, after the last piece.
  bool matches();

 private:
  Manifest m_;
  uint32_t size_ = 0;
  SHA256 hash_;
};
