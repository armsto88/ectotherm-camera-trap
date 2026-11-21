// Stand-in for the Arduino core on the computer: just enough for the Crypto library's sources to
// build in the native environment. Nothing tested here calls these.
#pragma once

#include <stdint.h>
#include <stdlib.h>
#include <string.h>

inline unsigned long millis() { return 0; }
inline unsigned long micros() { return 0; }
