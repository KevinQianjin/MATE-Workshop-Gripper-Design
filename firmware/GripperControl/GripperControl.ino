/*
 * MATE gripper: Arduino Uno R4 WiFi, GDW IPX896HV servos.
 * D9 = horizontal yaw signal. D10 = gripper open/close signal.
 * Serial Monitor: 115200 baud, Newline (or Both NL & CR).
 * Start with ARM, then Y -100..100 or G 0..100. HELP lists commands.
 * Power servos from a separate regulated supply with a shared ground.
 */
#include <Arduino.h>
#include <pwm.h>
#include <errno.h>
#include <stdlib.h>
#include <string.h>

#if !defined(ARDUINO_UNOR4_WIFI) && !defined(ARDUINO_UNOR4_MINIMA)
#error "Select Arduino Uno R4 WiFi (or Uno R4 Minima) in the board menu."
#endif

// These are small trial ranges, NOT measured mechanical endpoints.
// Center each servo before fitting its horn. Adjust after physical checks.
constexpr int YAW_LEFT_US = 1400;
constexpr int YAW_CENTER_US = 1500;
constexpr int YAW_RIGHT_US = 1600;
constexpr int GRIP_CLOSED_US = 1500;
constexpr int GRIP_OPEN_US = 1600;
constexpr int GRIP_START_US = 1500;

constexpr uint8_t YAW_PIN = 9;
constexpr uint8_t GRIP_PIN = 10;
constexpr uint32_t PWM_PERIOD_US = 3003;  // Approximately 333 Hz.
constexpr uint32_t MOVE_INTERVAL_MS = 10;
constexpr int MOVE_STEP_US = 2;          // At most 200 us/second.
constexpr int ELECTRICAL_MIN_US = 500;
constexpr int ELECTRICAL_MAX_US = 2500;

constexpr int lowOf(int a, int b) { return a < b ? a : b; }
constexpr int highOf(int a, int b) { return a > b ? a : b; }
constexpr int LOW_US[2] = {lowOf(YAW_LEFT_US, YAW_RIGHT_US),
                           lowOf(GRIP_CLOSED_US, GRIP_OPEN_US)};
constexpr int HIGH_US[2] = {highOf(YAW_LEFT_US, YAW_RIGHT_US),
                            highOf(GRIP_CLOSED_US, GRIP_OPEN_US)};
static_assert(LOW_US[0] >= ELECTRICAL_MIN_US && LOW_US[1] >= ELECTRICAL_MIN_US,
              "Configured endpoints are below the servo pulse range.");
static_assert(HIGH_US[0] <= ELECTRICAL_MAX_US && HIGH_US[1] <= ELECTRICAL_MAX_US,
              "Configured endpoints exceed the servo pulse range.");
static_assert(LOW_US[0] < YAW_CENTER_US && YAW_CENTER_US < HIGH_US[0],
              "Yaw center must be between its endpoints.");
static_assert(LOW_US[1] < HIGH_US[1] && LOW_US[1] <= GRIP_START_US &&
              GRIP_START_US <= HIGH_US[1], "Invalid gripper endpoints/start.");
static_assert(PWM_PERIOD_US > ELECTRICAL_MAX_US, "PWM period is too short.");

PwmOut yawPwm(YAW_PIN);
PwmOut gripPwm(GRIP_PIN);
PwmOut *outputs[2] = {&yawPwm, &gripPwm};
const uint8_t PINS[2] = {YAW_PIN, GRIP_PIN};
bool started[2] = {false, false};
bool hardwareReady = false;
bool armed = false;
bool calibration = false;
int currentUs[2] = {YAW_CENTER_US, GRIP_START_US};
int targetUs[2] = {YAW_CENTER_US, GRIP_START_US};
uint32_t lastMoveMs = 0;
char inputLine[48];
uint8_t inputLength = 0;
bool discardLine = false;
bool bannerShown = false;

void hardwareFault() {
  armed = false;
  calibration = false;
  hardwareReady = false;
  for (uint8_t i = 0; i < 2; ++i) {
    targetUs[i] = currentUs[i];
    if (started[i]) outputs[i]->end();
    started[i] = false;
    pinMode(PINS[i], OUTPUT);
    digitalWrite(PINS[i], LOW);
  }
  Serial.println("ERR PWM initialization/update failed; outputs disabled. Reset board.");
}

void printStatus() {
  Serial.print(hardwareReady ? (armed ? "ARMED " : "OFF ") : "FAULT ");
  Serial.print(calibration ? "CAL " : "RUN ");
  Serial.print("D9 commanded/target us: ");
  Serial.print(currentUs[0]); Serial.print('/'); Serial.print(targetUs[0]);
  Serial.print("; D10 commanded/target us: ");
  Serial.print(currentUs[1]); Serial.print('/'); Serial.println(targetUs[1]);
}

void printHelp() {
  Serial.println("D9 yaw; D10 grip; ~333 Hz hardware PWM. Trial endpoints require calibration.");
  Serial.println("ARM | OFF | STOP | STATUS | HELP");
  Serial.println("Y -100..100: left / center(0) / right; travel percent, not degrees.");
  Serial.println("G 0..100: configured closed(0) to open(100); OPEN | CLOSE | CENTER(yaw).");
  Serial.println("CAL: enable pulse calibration; P9 <us> | P10 <us>; RUN: normal commands.");
  Serial.println("Pulse calibration stays inside the configured endpoint limits.");
}

bool parseInteger(const char *text, long &value) {
  if (!text || !*text) return false;
  char *end = nullptr;
  errno = 0;
  value = strtol(text, &end, 10);
  return errno != ERANGE && end != text && *end == '\0';
}

bool requestPulse(uint8_t axis, long pulse) {
  if (pulse < LOW_US[axis] || pulse > HIGH_US[axis]) {
    Serial.println("ERR pulse outside configured limits; no movement requested.");
    return false;
  }
  targetUs[axis] = static_cast<int>(pulse);
  Serial.print("Target D"); Serial.print(PINS[axis]);
  Serial.print(" = "); Serial.print(targetUs[axis]); Serial.println(" us");
  return true;
}

int interpolate(int fromUs, int toUs, long percent) {
  return fromUs + (toUs - fromUs) * percent / 100;
}

void turnOff() {
  armed = false;
  calibration = false;
  for (uint8_t i = 0; i < 2; ++i) {
    targetUs[i] = currentUs[i];
    // Zero duty keeps the pin low: no servo command pulses.
    if (started[i] && !outputs[i]->pulseWidth_us(0)) {
      hardwareFault();
      return;
    }
  }
  Serial.println("OFF: command pulses disabled; servo supply is still powered.");
}

void handleCommand(char *line) {
  for (char *p = line; *p; ++p) {
    if (*p >= 'a' && *p <= 'z') *p -= 'a' - 'A';
  }
  char *command = strtok(line, " \t");
  char *argument = strtok(nullptr, " \t");
  if (!command) return;
  if (strtok(nullptr, " \t")) {
    Serial.println("ERR too many arguments.");
    return;
  }
  if (!argument) {
    if (!strcmp(command, "HELP")) { printHelp(); return; }
    if (!strcmp(command, "STATUS")) { printStatus(); return; }
    if (!strcmp(command, "OFF")) { turnOff(); return; }
    if (!strcmp(command, "ARM")) {
      if (!hardwareReady) { Serial.println("ERR PWM unavailable; reset board."); return; }
      if (armed) { Serial.println("Already armed; position unchanged."); return; }
      currentUs[0] = targetUs[0] = YAW_CENTER_US;
      currentUs[1] = targetUs[1] = GRIP_START_US;
      for (uint8_t i = 0; i < 2; ++i) {
        if (!outputs[i]->pulseWidth_us(currentUs[i])) { hardwareFault(); return; }
      }
      armed = true;
      calibration = false;
      lastMoveMs = millis();
      Serial.println("ARMED at configured start pulses. Actual shaft positions are not measured.");
      return;
    }
  }
  if (!armed) { Serial.println("ERR send ARM first."); return; }
  if (!argument) {
    if (!strcmp(command, "STOP")) {
      for (uint8_t i = 0; i < 2; ++i) targetUs[i] = currentUs[i];
      Serial.println("STOP: hold the last commanded position.");
      return;
    }
    if (!strcmp(command, "CAL")) {
      calibration = true;
      for (uint8_t i = 0; i < 2; ++i) targetUs[i] = currentUs[i];
      Serial.println("CAL: use P9/P10 in small pulse steps; STATUS shows commanded us.");
      return;
    }
    if (!strcmp(command, "RUN")) { calibration = false; Serial.println("RUN"); return; }
    if (!calibration) {
      if (!strcmp(command, "OPEN")) { requestPulse(1, GRIP_OPEN_US); return; }
      if (!strcmp(command, "CLOSE")) { requestPulse(1, GRIP_CLOSED_US); return; }
      if (!strcmp(command, "CENTER")) { requestPulse(0, YAW_CENTER_US); return; }
    }
  }
  long value;
  if (parseInteger(argument, value)) {
    if (calibration && !strcmp(command, "P9")) { requestPulse(0, value); return; }
    if (calibration && !strcmp(command, "P10")) { requestPulse(1, value); return; }
    if (!calibration && !strcmp(command, "Y") && value >= -100 && value <= 100) {
      requestPulse(0, value < 0 ? interpolate(YAW_CENTER_US, YAW_LEFT_US, -value)
                              : interpolate(YAW_CENTER_US, YAW_RIGHT_US, value));
      return;
    }
    if (!calibration && !strcmp(command, "G") && value >= 0 && value <= 100) {
      requestPulse(1, interpolate(GRIP_CLOSED_US, GRIP_OPEN_US, value));
      return;
    }
  }
  Serial.println("ERR invalid command, value, or mode. Send HELP.");
}

void readSerial() {
  // Bound work per loop so incoming text cannot starve motion updates.
  for (uint8_t count = 0; count < 32 && Serial.available(); ++count) {
    const char c = static_cast<char>(Serial.read());
    if (c == '\n' || c == '\r') {
      if (discardLine) Serial.println("ERR invalid/overlong line discarded.");
      else if (inputLength) {
        inputLine[inputLength] = '\0';
        handleCommand(inputLine);
      }
      inputLength = 0;
      discardLine = false;
    } else if (!discardLine) {
      if ((c < 32 && c != '\t') || c > 126 || inputLength >= sizeof(inputLine) - 1) {
        inputLength = 0;
        discardLine = true;
      } else inputLine[inputLength++] = c;
    }
  }
}

void updateMotion() {
  const uint32_t now = millis();
  if (!armed || static_cast<uint32_t>(now - lastMoveMs) < MOVE_INTERVAL_MS) return;
  // Do not catch up with a large jump after a delayed loop iteration.
  lastMoveMs = now;
  for (uint8_t i = 0; i < 2; ++i) {
    int delta = targetUs[i] - currentUs[i];
    if (!delta) continue;
    if (delta > MOVE_STEP_US) delta = MOVE_STEP_US;
    if (delta < -MOVE_STEP_US) delta = -MOVE_STEP_US;
    const int next = currentUs[i] + delta;
    if (!outputs[i]->pulseWidth_us(next)) { hardwareFault(); return; }
    currentUs[i] = next;
  }
}

void setup() {
  Serial.begin(115200);
  for (uint8_t i = 0; i < 2; ++i) {
    pinMode(PINS[i], OUTPUT);
    digitalWrite(PINS[i], LOW);
    // Starting at zero duty avoids a default 1500 us servo command on boot.
    started[i] = outputs[i]->begin(PWM_PERIOD_US, uint32_t(0));
    if (!started[i]) { hardwareFault(); return; }
  }
  hardwareReady = true;
}

void loop() {
  if (Serial && !bannerShown) { printHelp(); printStatus(); bannerShown = true; }
  if (!Serial) bannerShown = false;
  readSerial();
  updateMotion();
}
