#pragma once
#include <cstdint>

// Hardware boundary only: tests execute the actual sketch and serial parser.
struct PwmOut {
  int pin;
  uint32_t period = 0;
  int pulse = 0;
  bool active = false;
  bool failBegin = false;
  bool failUpdate = false;
  explicit PwmOut(int pinNumber) : pin(pinNumber) {}
  bool begin(uint32_t periodUs, uint32_t pulseUs) {
    if (failBegin) return false;
    period = periodUs;
    pulse = static_cast<int>(pulseUs);
    active = true;
    return true;
  }
  bool pulseWidth_us(int pulseUs) {
    if (!active || failUpdate) return false;
    pulse = pulseUs;
    return true;
  }
  void end() { active = false; pulse = 0; }
};
