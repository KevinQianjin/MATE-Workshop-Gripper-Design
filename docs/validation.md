# Validation report index

[Documentation index](README.md) · [Build instructions](build.md) · [Gear review](../output/preview/gear_review_R2.pdf)

These reports describe the committed R2 CAD. After changing parameters or geometry, rerun the relevant scripts to update them.

| Report | Contents |
|---|---|
| [build_inventory.json](../output/validation/build_inventory.json) | 12 main part types, 14 pieces, modified solids, and source STL mapping |
| [static_and_mesh.json](../output/validation/static_and_mesh.json) | Nominal assembly interference, closure, and positive volume for 23 STLs |
| [gear_engagement.json](../output/validation/gear_engagement.json) | 145 nominal profile positions, bidirectional contact limits at 73 input angles, and backlash estimates |
| [motion.json](../output/validation/motion.json) | 13 nominal opening poses, 20 gripper linkage contact-limit poses, and 3 yaw poses |
| [delivery.json](../output/validation/delivery.json) | 20 source file hashes, 20 STEP imports, 23 STL orientations, and 4 retained mesh types |
| [screw_access.json](../output/validation/screw_access.json) | Four M3 horn screw-head insertion paths |
| [revision_scope.json](../output/validation/revision_scope.json) | Geometry comparison of retained R1 parts and original gear interfaces |
| [datums.json](../output/validation/datums.json) | Servo, shaft, and assembly datum positions |
| [tooth_profiles.json](../output/validation/tooth_profiles.json) | Sections extracted from exported BRep geometry for analysis and plotting |

## Checked scope

- Relative opening motion spans 0–36°. Tooth profiles are sampled every 0.25° and gear-chain contact limits every 0.5°. The gripper linkage is also checked at 13 nominal positions and 20 bidirectional contact-limit poses.
- Yaw is sampled at −45°, 0°, and +45°.
- Reported intersection thresholds are 0.01 mm³ for the nominal assembly and 0.02 mm³ for sampled motion.
- R2 output reversal free play is approximately 2.75° in rigid CAD, meeting the provisional 3° target. Axial tooth overlap is 2 mm for each big/small gear pair and 3 mm between the idlers.
- R1 replacement parts are M01, M02, M05, and M06 ×2. Retained parts, hubs, central interfaces, and linkage comparisons are recorded in `revision_scope.json`.

## Physical checks still required

The CAD samples do not validate actual servo or horn dimensions, printing tolerances, friction, pivot looseness, cable sweep, elastic deflection, or load performance. They do not establish clearance throughout every continuous position. No verified payload rating is provided.

Follow the [trial-print and assembly procedure](assembly.md), then test unloaded operation and calibrate endpoints. Original R1 comparison data is retained in [reference/](../reference/README.md).
