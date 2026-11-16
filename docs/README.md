# Documentation index

[Project home](../README.md)

| Document | Purpose |
|---|---|
| [Assembly and trial printing](assembly.md) | Servo and horn interfaces, fit checks, print settings, hardware, and assembly order |
| [Models and print list](../output/README.md) | STL quantities, modified-part STEP files, trial parts, and naming conventions |
| [Build and delivery](build.md) | Dependencies, script order, ZIP generation, and checksums |
| [Validation reports](validation.md) | What each JSON report checks and what still requires physical testing |
| [PDF assembly guide](../output/assembly_and_print_guide.pdf) | Six-page illustrated assembly and trial-print guide |
| [Hardware BOM](../BOM.csv) | Servos, metal horns, screws, nuts, and washers |
| [Changelog](../CHANGELOG.md) | R1, R2, and repository maintenance history |
| [R1 baseline notes](../reference/README.md) | Evidence used for geometry-preservation and backlash comparisons |

## Directory responsibilities

- `output/` contains the current R2 delivery models and matching check results. Use STL for slicing and STEP for CAD inspection.
- `scripts/` and `parameters.json` support rebuilding. After changing the design, rerun the relevant checks.
- `upstream/` preserves the original project files pinned by `source_manifest.json`.
- `reference/` stores the R1 data used by `verify_revision.py` and the gear comparison plot.
- `dist/` and `work/` contain local generated files and are excluded from version control.

Detailed assembly instructions are maintained in [assembly.md](assembly.md).
