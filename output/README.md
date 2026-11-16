# R2 models and print list

[Project home](../README.md) · [Assembly instructions](../docs/assembly.md) · [Hardware BOM](../BOM.csv)

Inspect the [complete assembly STEP](IPX896HV_2DOF_assembly.step), then print the fit-check parts. The main assembly uses **12 part types and 14 printed pieces**. The STEP also contains four `REF_` servo/metal-horn envelopes; these are purchased-part references, not printable parts.

## Main printed parts

| ID | Part | Quantity | STL | Individual STEP |
|---|---|---:|---|---|
| U01 | Left jaw | 1 | [Print](stl/U01_left_claw.stl) | — |
| U02 | Right jaw | 1 | [Print](stl/U02_right_claw.stl) | — |
| U03 | Passive link | 2 | [Print](stl/U03_linkage_PRINT_2.stl) | — |
| U06 | Base side wall | 1 | [Print](stl/U06_base_wall.stl) | — |
| M01 | Palm / servo carrier | 1 | [Print](stl/M01_palm_IPX896HV.stl) | [Edit](step/M01_palm_IPX896HV.step) |
| M02 | Drive gear link and horn interface | 1 | [Print](stl/M02_drive_gear_horn_adapter.stl) | [Edit](step/M02_drive_gear_horn_adapter.step) |
| M03 | Fixed base | 1 | [Print](stl/M03_base_IPX896HV.stl) | [Edit](step/M03_base_IPX896HV.step) |
| M04 | Rotating waist | 1 | [Print](stl/M04_original_waist_horn_interface.stl) | [Edit](step/M04_original_waist_horn_interface.step) |
| M05 | Right gear link | 1 | [Print](stl/M05_right_gear_involute.stl) | [Edit](step/M05_right_gear_involute.step) |
| M06 | Idler gear | 2 | [Print](stl/M06_small_gear_involute_PRINT_2.stl) | [Edit](step/M06_small_gear_involute_PRINT_2.step) |
| N01 | Yaw horn coupler | 1 | [Print](stl/N01_yaw_horn_coupler.stl) | [Edit](step/N01_yaw_horn_coupler.step) |
| N02 | Gripper-to-waist bridge | 1 | [Print](stl/N02_gripper_to_waist_bridge.stl) | [Edit](step/N02_gripper_to_waist_bridge.step) |

Print each `PRINT_2` file twice. Retained parts have no separate delivery STEP; inspect them in the complete assembly or pinned source STEP. Use R2 M01, M02, M05, and M06 together.

## Fit-check parts

| Trial file | Purpose / quantity |
|---|---|
| [F01 servo ear coupon](fit_checks/F01_servo_ear_fit.stl) | Check the case opening, mounting ears, and four holes; 1 piece |
| [F02 horn and shaft coupon](fit_checks/F02_horn_slot_fit.stl) | Check metal-horn holes and screw insertion space; 1 piece |
| [F03 shaft ring](fit_checks/F03_shaft_clearance_ring.stl) + [F04 shaft pin](fit_checks/F04_shaft_fit_pin.stl) | Check rotating fit; 1 each |
| [F05 four-gear plate](fit_checks/F05_four_gear_trial_plate.stl) | Manual gear-fit test; 1 piece |
| B08: [20T](fit_checks/F_mesh_20T_B08_PRINT_2.stl) / [19T](fit_checks/F_mesh_19T_B08_PRINT_2.stl) | 0.08 mm nominal tangential backlash per mesh; print 2 of each |
| **B12**: [20T](fit_checks/F_mesh_20T_B12_PRINT_2.stl) / [19T](fit_checks/F_mesh_19T_B12_PRINT_2.stl) | **Used by the main parts**; 0.12 mm nominal backlash; print 2 of each |
| B16: [20T](fit_checks/F_mesh_20T_B16_PRINT_2.stl) / [19T](fit_checks/F_mesh_19T_B16_PRINT_2.stl) | 0.16 mm nominal backlash; print 2 of each |

Start with B12 and use one code for all four gears. These are CAD design values. Selecting another clearance requires rebuilding and validating the main gears. See [gear trial and clearance selection](../docs/assembly.md#gear-trial-and-clearance-selection). Trial-part STEP files are also in [fit_checks/](fit_checks/).

## Other files

| Path | Contents |
|---|---|
| [assembly_and_print_guide.pdf](assembly_and_print_guide.pdf) | Six-page illustrated English guide |
| [preview/](preview/) | Assembly views, orthographic drawings, gear review, and trial-plate illustration |
| [validation/](validation/) | CAD and delivery check JSON files; see the [report index](../docs/validation.md) |
| [brep/](brep/) | Generated exact geometry snapshots used by checks and rendering |

Prefixes: `U` retains upstream geometry, `M` modifies an upstream part, `N` is a new adapter, and `F` is a fit-check part. STLs have an initial print orientation; confirm slicing and supports using the [printing recommendations](../docs/assembly.md#printing-recommendations).
