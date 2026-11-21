#pragma once
#include <array>
#include <cstdint>
#include <deque>
#include <sstream>
#include <string>

constexpr int OUTPUT = 1;
constexpr int LOW = 0;
inline uint32_t fakeMillis = 0;
inline std::array<int, 20> pinModes{};
inline std::array<int, 20> pinLevels{};
inline uint32_t millis() { return fakeMillis; }
inline void pinMode(uint8_t pin, int mode) { pinModes.at(pin) = mode; }
inline void digitalWrite(uint8_t pin, int level) { pinLevels.at(pin) = level; }

struct FakeSerial {
  std::deque<unsigned char> input;
  std::string output;
  unsigned long baud = 0;
  bool connected = true;
  void begin(unsigned long value) { baud = value; }
  explicit operator bool() const { return connected; }
  int available() const { return static_cast<int>(input.size()); }
  int read() { int value = input.front(); input.pop_front(); return value; }
  template <typename T> void print(const T &value) {
    std::ostringstream stream;
    stream << value;
    output += stream.str();
  }
  void print(uint8_t value) { print(static_cast<unsigned int>(value)); }
  template <typename T> void println(const T &value) { print(value); output += '\n'; }
};
inline FakeSerial Serial;
