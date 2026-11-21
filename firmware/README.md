# Arduino Uno R4 WiFi gripper control

[Project home](../README.md) · [Assembly instructions](../docs/assembly.md) · [Open the sketch](GripperControl/GripperControl.ino)

The sketch controls two GDW IPX896HV servos through the Arduino Serial Monitor:

- **D9: horizontal rotation (yaw).**
- **D10: gripper opening and closing.**

It uses the Uno R4 core's hardware PWM at approximately **333 Hz** (3003 microseconds per frame), matching the supplied servo sheet. No additional Arduino library is needed. WiFi is not used. This sketch targets the Uno R4; it will not compile for the classic Uno R3 or Nano.

## Wiring

Disconnect power while wiring. Use USB to power the Arduino and a separate regulated **4.8–8.4 V** supply for the servos.

| Connection | Destination |
|---|---|
| Yaw servo orange signal | Arduino **D9** |
| Gripper servo orange signal | Arduino **D10** |
| Both servo red wires | External servo supply positive |
| Both servo brown wires | External servo supply negative |
| Arduino GND | External servo supply negative, sharing ground with both servos |

Do not power either servo through the Arduino 5V/3.3V pins or USB. Keep servo supply positive separate from the Arduino power pins. At 7.4 V, the sheet specifies 5.4 A stall current per servo, or approximately 10.8 A combined; size the supply, connectors, and wiring for the expected load and transients. Do not connect a 12.6 V battery directly to these servos.

## Upload and first use

1. Install **Arduino UNO R4 Boards** in Arduino IDE's Boards Manager. Select **Arduino UNO R4 WiFi** and its USB port. Version **1.6.0** of the board package was used for the compile check.
2. Open [GripperControl/GripperControl.ino](GripperControl/GripperControl.ino) and upload it. Leave the servo horns disconnected from the mechanism for the first centering test.
3. Open Serial Monitor at **115200 baud** with **Newline** or **Both NL & CR** selected. The controller starts with no command pulses; it does not sweep automatically.
4. Power the servos and send `ARM`. Both receive their configured start pulse, initially **1500 us**. The first movement can be immediate because the Arduino cannot read the actual shaft positions.
5. Remove servo power before fitting the centered horns. Follow the [assembly procedure](../docs/assembly.md#assembly-order), then calibrate the unloaded mechanism as described below.

Once centered and checked, send one command per line:

```text
ARM
Y -50
CENTER
OPEN
CLOSE
STOP
OFF
```

Wait for each movement to finish before sending the next command. These example commands use only the configured trial travel until you calibrate the endpoints.

## Commands

Commands are case-insensitive. `Y` and `G` use **normalized travel percentages**, not physical angles or millimetres.

| Command | Action |
|---|---|
| `ARM` | Enable outputs at yaw center and gripper start pulse; repeating it while armed leaves the position unchanged |
| `Y -100` / `Y 0` / `Y 100` | Move yaw to configured left / center / right; intermediate integers are accepted |
| `G 0` through `G 100` | Move from configured closed to configured open |
| `OPEN` / `CLOSE` | Same as `G 100` / `G 0` |
| `CENTER` | Center yaw only |
| `STOP` | Cancel both pending moves and keep sending the last commanded positions |
| `OFF` | Disable command pulses on both pins; a subsequent `ARM` starts at the configured start positions |
| `STATUS` | Show mode and commanded/target pulse widths; these are not measured positions |
| `CAL` | Cancel pending moves and enable pulse calibration commands |
| `P9 1490` / `P10 1510` | In CAL mode, request that pin's pulse width in microseconds, within its configured limits |
| `RUN` | Leave CAL mode without changing the target positions |
| `HELP` | Print the command list |

After arming, both axes can move concurrently. Pulse commands change by at most 2 us every 10 ms, so a 100 us move takes about 0.5 seconds. `STOP` holds the last command; the shaft may still be catching up. `OFF` does **not** disconnect servo power, and the servo's response to signal loss has not been verified. For electrical shutdown, turn off the external supply. Losing the Serial Monitor connection does not automatically stop a pending move.

Invalid commands and out-of-range values are rejected without replacing the current target. A PWM initialization or update failure disables both outputs and requires a board reset.

## Calibrate the endpoints

The six constants at the top of the sketch define startup positions and usable travel:

| Constant | Default (us) | Meaning after calibration |
|---|---:|---|
| `YAW_LEFT_US` | 1400 | Usable left endpoint |
| `YAW_CENTER_US` | 1500 | Center and startup yaw position |
| `YAW_RIGHT_US` | 1600 | Usable right endpoint |
| `GRIP_CLOSED_US` | 1500 | Closed endpoint without forcing the linkage |
| `GRIP_OPEN_US` | 1600 | Usable open endpoint |
| `GRIP_START_US` | 1500 | Gripper position commanded by `ARM` |

**These defaults are small trial ranges, not measured mechanical endpoints.** The default `OPEN` command does not represent the full CAD opening stroke. Even a small range needs checking against your horn alignment and gear phase.

1. Center the bare servos at 1500 us before fitting horns. With power removed, align yaw to the intended center and the gripper to a freely moving position clear of its stops.
2. On the unloaded assembly, send `ARM`, then `CAL`. Try small steps such as `P9 1490`, `P9 1500`, `P10 1510`, and `P10 1520`, watching the actual motion. Use `STATUS` to record commands.
3. Keep each endpoint inside the freely moving range, allowing clearance from contact, cable strain, and linkage stops. If more travel is needed, adjust the endpoint constants by a small amount and upload again. `P9` and `P10` intentionally cannot bypass those limits.
4. Save the measured left, center, right, closed, open, and start values in the sketch. The start value must remain between the gripper endpoints. If a direction is reversed, exchange that axis's endpoint values; descending pulse ranges are supported.
5. Re-upload and verify `Y -100`, `CENTER`, `Y 100`, `CLOSE`, and `OPEN` individually without a payload before normal use. Calibration is stored in the source constants, not EEPROM.

The servo's electrical range is **500–2500 us**. It is not permission to sweep the assembled mechanism over that range. The CAD opening stroke and yaw poses are relative geometry; they do not establish absolute servo pulse endpoints. This controller has no position, force, or current feedback, so it cannot detect a jam or regulate gripping force.

## Development checks

From the repository root, with Arduino CLI installed:

```sh
arduino-cli core update-index
arduino-cli core install arduino:renesas_uno@1.6.0
arduino-cli compile --fqbn arduino:renesas_uno:unor4wifi --warnings all firmware/GripperControl
```

Host behavior tests compile the actual sketch against simulated Serial and PWM interfaces:

```sh
mkdir -p work/arduino
g++ -std=c++17 -Wall -Wextra -Werror -Ifirmware/tests/stubs firmware/tests/controller_test.cpp -o work/arduino/controller_test
work/arduino/controller_test
```

The 61 checks cover startup with no pulses, pin mapping, command parsing, concurrent ramps, limits, stop/off behavior, calibration, timer rollover, and PWM failures. Compilation and simulated checks do not verify physical PWM timing, servo compatibility, printed clearances, or load performance. Those still require the actual board and mechanism.

Hardware PWM API: [ArduinoCore-renesas pwm.h](https://github.com/arduino/ArduinoCore-renesas/blob/1.6.0/cores/arduino/pwm.h).
