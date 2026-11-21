# Build and delivery

[Documentation index](README.md) · [Models and print list](../output/README.md)

Run the following commands from the repository root. To use the supplied STEP/STL files, download [output/](../output/) directly.

Arduino upload, calibration, and firmware checks are documented separately in the [controller guide](../firmware/README.md).

## Install dependencies

Create a Python virtual environment and install [requirements.txt](../requirements.txt). The CAD engine is pinned to CadQuery 2.7.0; use a Python version supported by that package.

```sh
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

In Windows PowerShell, activate the environment with `.venv\Scripts\Activate.ps1`. The English PDF uses PyMuPDF's built-in Helvetica fonts, and the gear review uses Matplotlib's bundled DejaVu Sans. No system font installation is required.

## Generate and validate the models

Keep [upstream/](../upstream/), [reference/](../reference/), the parameters, and the source manifest in place. Run these scripts in order:

```sh
python scripts/build.py
python scripts/check_and_render.py
python scripts/check_gears.py
python scripts/validate_motion.py
python scripts/verify_delivery.py
python scripts/verify_screw_access.py
python scripts/verify_revision.py
```

`validate_motion.py` consumes the current contact-limit data from `check_gears.py`, so run the gear check first. Reports are written to `output/validation/`; see the [validation index](validation.md). Physical trial-print procedures are in the [assembly instructions](assembly.md).

## Regenerate previews and the PDF

After the checks pass, run:

```sh
python scripts/plot_gear_review.py
python scripts/make_guide.py
```

These update the assembly views, gear comparison, and trial-plate illustration in `output/preview/`, plus `output/assembly_and_print_guide.pdf`.

## Package the current delivery

The committed R2 models and reports can be packaged directly. After changing the models, complete the rebuild and checks first.

```sh
python scripts/package_delivery.py
```

Generated delivery files are placed in the ignored `dist/` directory:

| File | Contents |
|---|---|
| `IPX896HV_2DOF_R2.zip` | Models, fit checks, Arduino firmware, documentation, scripts, source files, and baselines |
| `IPX896HV_2DOF_R2.step` | Complete assembly |
| `IPX896HV_R2_assembly_and_print_guide.pdf` | Illustrated English guide |
| `IPX896HV_2DOF_R2_preview.png` | Assembly preview |
| `IPX896HV_R2_gear_review.png` / `.pdf` | Gear comparison |

To choose another output directory:

```sh
python scripts/package_delivery.py --output-dir /tmp/gripper-delivery
```

Packaging updates the root `DELIVERY_SHA256SUMS.txt`, includes it in the ZIP, and checks ZIP CRCs and each file's SHA-256. Commit the manifest together with the matching delivery files. Working files, caches, and `dist/` are excluded from the archive.

From the repository root or the extracted `IPX896HV_2DOF_R2/` directory, verify the manifest with a supported system tool:

```sh
sha256sum -c DELIVERY_SHA256SUMS.txt
```

## Script index

| Script | Responsibility |
|---|---|
| [build.py](../scripts/build.py) | Generate parts, fit coupons, and the complete assembly from source CAD and parameters |
| [gears.py](../scripts/gears.py) | Shared involute gear geometry and shaft layout |
| [motion.py](../scripts/motion.py) | Shared linkage closure and assembly transforms |
| [check_and_render.py](../scripts/check_and_render.py) | Static interference, mesh checks, and assembly rendering |
| [check_gears.py](../scripts/check_gears.py) | Exported tooth profiles, axial engagement, and rigid backlash |
| [validate_motion.py](../scripts/validate_motion.py) | Sampled opening, contact-limit, and yaw interference |
| [verify_delivery.py](../scripts/verify_delivery.py) | Source hashes, STEP re-import, and STL geometry |
| [verify_screw_access.py](../scripts/verify_screw_access.py) | Horn screw insertion paths |
| [verify_revision.py](../scripts/verify_revision.py) | Geometry retained from R1 |
| [plot_gear_review.py](../scripts/plot_gear_review.py) | R1/R2 gear review figure |
| [make_guide.py](../scripts/make_guide.py) | Assembly previews and six-page English PDF |
| [package_delivery.py](../scripts/package_delivery.py) | ZIP, standalone delivery files, and SHA-256 manifest |
