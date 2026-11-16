# R1 comparison baselines

[Project home](../README.md) · [Changelog](../CHANGELOG.md) · [Validation reports](../docs/validation.md)

This directory preserves R1 data for R2 validation and comparison plots. The baseline commit is [`a9ed9fded2ce59b079b9b703d5fd8c7202095e94`](https://github.com/KevinQianjin/MATE-Workshop-Gripper-Design/commit/a9ed9fded2ce59b079b9b703d5fd8c7202095e94).

| File | Purpose |
|---|---|
| [R1_parameters.json](R1_parameters.json) | R1 dimensions and gear assembly parameters |
| [R1_gear_engagement.json](R1_gear_engagement.json) | Original-profile backlash estimates for the R1/R2 comparison |
| [R1_parts/](R1_parts/) | R1 BRep snapshots of M02, M03, M04, N01, and N02 |
| [R1_parts/manifest.json](R1_parts/manifest.json) | Snapshot source commit and SHA-256 hashes |

`scripts/verify_revision.py` verifies snapshot hashes before comparing the retained parts and gear interfaces with R2. Preserve these baselines when editing the current design. Current trial-print files are in [output/](../output/README.md).
