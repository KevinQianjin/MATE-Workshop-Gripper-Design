# MATE Workshop Gripper Design

A 3D-printable, two-degree-of-freedom gripper: **open/close + left/right yaw**. The current design is the **R2 matched-gear fit-check prototype**, provisionally using two GDW IPX896HV servos.

[Models and print list](output/README.md) · [Assembly instructions](docs/assembly.md) · [Arduino control](firmware/README.md) · [PDF guide](output/assembly_and_print_guide.pdf) · [Hardware BOM](BOM.csv)

![R2 two-axis gripper assembly](output/preview/assembly_open.png)

## Start here

| What you need | File or guide |
|---|---|
| Inspect the complete mechanism in Fusion or SolidWorks | [Assembly STEP](output/IPX896HV_2DOF_assembly.step) |
| Check servo, horn, and gear fit | [Fit-check parts](output/fit_checks/) and [trial procedure](docs/assembly.md#interface-fit-checks) |
| Print the mechanism | [12 part types, 14 printed pieces](output/README.md#main-printed-parts) |
| Control it with an Arduino Uno R4 WiFi | [Sketch, wiring, and calibration](firmware/README.md): D9 yaw, D10 open/close |
| Modify the design | [8 modified/new part STEP files](output/step/) and [parameters](parameters.json) |
| Review the gear improvement and checks | [Gear comparison](output/preview/gear_review_R2.pdf) and [validation index](docs/validation.md) |
| Rebuild or package the project | [Build and delivery guide](docs/build.md) |

1. Download the repository using GitHub **Code → Download ZIP** or `git clone`, then read the [assembly instructions](docs/assembly.md). Using the supplied STEP/STL files does not require Python.
2. Print the F01–F04 interface coupons, followed by the F05 trial plate and two each of the B12 20T and 19T gears. Check their fit before printing the full mechanism.
3. Use the [print list](output/README.md) and [BOM](BOM.csv) to prepare the complete assembly, then calibrate its usable endpoints without a payload.

## Current design

| Item | R2 specification |
|---|---|
| Degrees of freedom | Open/close + left/right yaw, 2 axes |
| Main printed parts | 12 types, 14 pieces; print `PRINT_2` files twice |
| Gear configuration | Module 0.75, 20° pressure angle, 20/19/19/20 teeth |
| Replacement scope from R1 | M01, M02, M05, M06 ×2: 4 types, 5 pieces |
| Estimated output reversal free play | Approximately 2.75°; R1 approximately 8.2–11.6° |
| CAD checks | 23 STLs, 20 STEPs, 145 nominal gear-profile positions, and 20 bidirectional contact-limit poses |

**This is a CAD-checked fit-test prototype.** Servo mounting ears, the metal horn, printed fit, and load capacity still need physical verification. Backlash values come from rigid geometry and exclude printing error and servo backlash. Use the R2 palm and gears together. See the [assembly instructions](docs/assembly.md) and [validation scope](docs/validation.md).

## Repository layout

```text
docs/                   Assembly, build, and validation documentation
firmware/               Uno R4 WiFi sketch, wiring guide, and controller tests
output/                 R2 models, fit coupons, PDFs, and validation results
scripts/                CAD generation, checking, rendering, and packaging
reference/              R1 comparison baselines
upstream/               Original GitHub project files and license
BOM.csv                 Hardware procurement list
parameters.json         Design dimensions and unverified assumptions
CHANGELOG.md            Revision history
source_manifest.json    Pinned upstream revision and file hashes
DELIVERY_SHA256SUMS.txt  Delivery file checksums
```

`dist/` contains generated delivery packages. `work/` contains local working files. Both are excluded from Git. See the [documentation index](docs/README.md) for more detail.

## Source and license

Based on [vshreyas121-code/6-dof-robotic-arm](https://github.com/vshreyas121-code/6-dof-robotic-arm), pinned to `258d1893ba1b8b49e87baa79da462680fd53681b`. The original jaws, linkage interfaces, gear hubs, and base layout are retained where possible; R2 replaces the working gear rims.

MIT licensed. See [LICENSE](LICENSE), [NOTICE.txt](NOTICE.txt), and the [upstream license](upstream/LICENSE). Revision details are in the [changelog](CHANGELOG.md).
