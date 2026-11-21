# Changelog

[Project home](README.md) · [Documentation index](docs/README.md)

## Arduino Uno R4 WiFi controller — 2026-11-20

- Add D9 horizontal yaw and D10 gripper control using approximately 333 Hz hardware PWM.
- Add Serial Monitor commands, gradual movement, explicit arming, stop/off controls, and endpoint calibration within configured limits.
- Document external servo power, shared ground, upload steps, and the provisional trial endpoints.
- Add controller behavior tests and include the firmware in delivery packages.
- Retain the R2 mechanical geometry and CAD validation data.

## Repository organization and English documentation — 2026-11-16

- Organize the homepage around model inspection, trial printing, assembly, and rebuilding.
- Consolidate detailed assembly instructions in `docs/assembly.md`.
- Add the print inventory, build guide, validation index, and R1 baseline notes.
- Standardize repository documentation, the hardware BOM, diagrams, PDF guide, and filenames in English; remove redundant language-specific entry points.
- Use bundled fonts for English guide and plot generation.
- Default delivery packages to the ignored `dist/` directory, support `--output-dir`, and include the new documentation.
- Mark generated files and upstream sources for clearer GitHub review.
- Retain R2 mechanical geometry and CAD validation data.

## R2 matched-gear fit-check prototype — 2026-11-16

Design commit: [4ba3e1d](https://github.com/KevinQianjin/MATE-Workshop-Gripper-Design/commit/4ba3e1db5ff389de7a7f8f0c2c98523cb6c0e68d)

- Replace the four working rims with matched module 0.75, 20° involute profiles, retaining 20/19/19/20 tooth counts.
- Move each idler pivot approximately 0.257 mm and retain R1 axial alignment.
- Reduce estimated geometric reversal free play from approximately 8.2–11.6° to approximately 2.75°.
- Replace four part types, five pieces: M01, M02, M05 (formerly U05), and M06 ×2 (formerly U04 ×2).
- Add the F05 four-gear trial plate, B08/B12/B16 trial gears, and bidirectional contact-limit checks.

## R1 axial engagement correction — 2026-11-15

Design commit: [a9ed9fd](https://github.com/KevinQianjin/MATE-Workshop-Gripper-Design/commit/a9ed9fded2ce59b079b9b703d5fd8c7202095e94)

- Adapt the original open-source mechanism for IPX896HV servos with open/close and yaw motion.
- Raise the driving gear by 1.5 mm, increasing tooth-width overlap with its adjacent idler from 0.5 mm to 2 mm.
- Align the jaws and spacer stack; provide complete and individual models, interface coupons, and validation scripts.
- Retain the original tooth profiles, with approximately 8.2–11.6° estimated geometric reversal free play.

All revisions are prototypes requiring physical fit checks. CAD calculations do not establish printed fit or load capacity.
