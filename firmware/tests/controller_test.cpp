#define ARDUINO_UNOR4_WIFI
#include "../GripperControl/GripperControl.ino"
#include <iostream>
#include <stdexcept>

int assertions = 0;
#define CHECK(condition) do { \
  ++assertions; \
  if (!(condition)) throw std::runtime_error( \
      "Line " + std::to_string(__LINE__) + ": " #condition); \
} while (false)

void resetController() {
  Serial = FakeSerial{};
  fakeMillis = lastMoveMs = 0;
  yawPwm = PwmOut(9);
  gripPwm = PwmOut(10);
  started[0] = started[1] = false;
  hardwareReady = armed = calibration = false;
  currentUs[0] = targetUs[0] = YAW_CENTER_US;
  currentUs[1] = targetUs[1] = GRIP_START_US;
  inputLength = 0;
  discardLine = bannerShown = false;
  pinModes.fill(-1);
  pinLevels.fill(-1);
}

void receive(const std::string &bytes) {
  for (unsigned char c : bytes) Serial.input.push_back(c);
  while (Serial.available()) loop();
}

void command(const std::string &line) { receive(line + "\n"); }
void tick(uint32_t elapsed = 10) { fakeMillis += elapsed; loop(); }
void settle() { for (int i = 0; i < 100; ++i) tick(); }

void testStartupAndMotion() {
  resetController();
  setup();
  CHECK(Serial.baud == 115200);
  CHECK(yawPwm.pin == 9 && gripPwm.pin == 10);
  CHECK(yawPwm.period == 3003 && gripPwm.period == 3003);
  CHECK(hardwareReady && !armed);
  CHECK(yawPwm.pulse == 0 && gripPwm.pulse == 0);
  command("OPEN");
  command("Y 100");
  settle();
  CHECK(yawPwm.pulse == 0 && gripPwm.pulse == 0);
  command("ARM");
  CHECK(armed && yawPwm.pulse == 1500 && gripPwm.pulse == 1500);
  command("Y -100");
  command("G 100");
  CHECK(targetUs[0] == 1400 && targetUs[1] == 1600);
  CHECK(yawPwm.pulse == 1500 && gripPwm.pulse == 1500);
  tick(9);
  CHECK(yawPwm.pulse == 1500 && gripPwm.pulse == 1500);
  tick(1);
  CHECK(yawPwm.pulse == 1498 && gripPwm.pulse == 1502);
  tick(1000);  // A delayed loop must not jump to the target.
  CHECK(yawPwm.pulse == 1496 && gripPwm.pulse == 1504);
  settle();
  CHECK(yawPwm.pulse == 1400 && gripPwm.pulse == 1600);
  command("ARM");
  CHECK(yawPwm.pulse == 1400 && gripPwm.pulse == 1600);
  command("CENTER");
  CHECK(targetUs[0] == 1500 && targetUs[1] == 1600);
  command("G 25");
  settle();
  CHECK(yawPwm.pulse == 1500 && gripPwm.pulse == 1525);
  command("Y 50");
  command("CLOSE");
  settle();
  CHECK(yawPwm.pulse == 1550 && gripPwm.pulse == 1500);
}

void testStopAndOff() {
  command("Y -100");
  command("OPEN");
  tick();
  const int yawAtStop = yawPwm.pulse;
  const int gripAtStop = gripPwm.pulse;
  command("STOP");
  settle();
  CHECK(armed && yawPwm.pulse == yawAtStop && gripPwm.pulse == gripAtStop);
  command("OFF");
  CHECK(!armed && yawPwm.pulse == 0 && gripPwm.pulse == 0);
  command("OPEN");
  settle();
  CHECK(yawPwm.pulse == 0 && gripPwm.pulse == 0);
  command("ARM");
  CHECK(yawPwm.pulse == 1500 && gripPwm.pulse == 1500);
  settle();
  CHECK(targetUs[0] == 1500 && targetUs[1] == 1500);
}

void testCalibrationAndInput() {
  command("P9 1450");
  CHECK(targetUs[0] == 1500);  // Raw commands require CAL.
  command("CAL");
  command("P9 1450");
  command("P10 1551");
  settle();
  CHECK(calibration && yawPwm.pulse == 1450 && gripPwm.pulse == 1551);
  for (const auto &line : {"P9 1399", "P9 1601", "P10 1499", "P10 1601",
                           "P9 500", "P10 2500", "Y 100", "OPEN"}) {
    command(line);
    CHECK(targetUs[0] == 1450 && targetUs[1] == 1551);
  }
  command("RUN");
  CHECK(!calibration && targetUs[0] == 1450 && targetUs[1] == 1551);
  for (const auto &line : {"Y 101", "Y -101", "G -1", "G 101", "Y", "G 1.5",
                           "Y 50junk", "Y 5 6", "OPEN 1", "ARM 1", "OFF 1",
                           "P9 1500", "Y 99999999999999999999999999999999999"}) {
    command(line);
    CHECK(armed && targetUs[0] == 1450 && targetUs[1] == 1551);
  }
  // A long or binary line must not execute a valid-looking suffix.
  receive(std::string(70, 'X') + "OPEN\n");
  receive(std::string(1, '\0') + "OFF\n");
  CHECK(armed && targetUs[0] == 1450 && targetUs[1] == 1551);
  receive("  y\t-25 \r\n g 75\r\n");
  CHECK(targetUs[0] == 1475 && targetUs[1] == 1575);
  command("STATUS");
  CHECK(Serial.output.find("D9 commanded/target us:") != std::string::npos);
  command("CAL");  // Entering calibration cancels pending moves.
  CHECK(targetUs[0] == currentUs[0] && targetUs[1] == currentUs[1]);
  command("OFF");
  CHECK(!calibration && !armed);
}

void testRolloverAndFaults() {
  command("ARM");
  command("Y 100");
  lastMoveMs = fakeMillis = UINT32_MAX - 7;
  tick(13);
  CHECK(yawPwm.pulse == 1502);
  gripPwm.failUpdate = true;
  command("OPEN");
  tick();
  CHECK(!hardwareReady && !armed);
  CHECK(!yawPwm.active && !gripPwm.active);
  CHECK(pinLevels[9] == LOW && pinLevels[10] == LOW);
  command("ARM");
  CHECK(!armed);  // A PWM fault is latched until reset.

  resetController();
  gripPwm.failBegin = true;
  setup();
  CHECK(!hardwareReady && !yawPwm.active && !gripPwm.active);
  CHECK(pinModes[9] == OUTPUT && pinModes[10] == OUTPUT);
  CHECK(pinLevels[9] == LOW && pinLevels[10] == LOW);

  resetController();
  setup();
  gripPwm.failUpdate = true;
  command("ARM");
  CHECK(!armed && !hardwareReady && !yawPwm.active);

  resetController();
  setup();
  command("ARM");
  yawPwm.failUpdate = true;
  command("OFF");
  CHECK(!armed && !hardwareReady && !gripPwm.active);
}

int main() {
  try {
    testStartupAndMotion();
    testStopAndOff();
    testCalibrationAndInput();
    testRolloverAndFaults();
    std::cout << "PASS: " << assertions << " controller checks\n";
    return 0;
  } catch (const std::exception &error) {
    std::cerr << "FAIL: " << error.what() << '\n';
    return 1;
  }
}
