# IPX896HV two-axis gripper — R2 matched-gear prototype

[Project home](../README.md) · [Models and print list](../output/README.md) · [Build instructions](build.md)

Paths shown as code are relative to the repository root. All dimensions are in millimetres unless stated otherwise.

The mechanism provides gripper opening/closing and left/right base yaw. It retains the upstream jaws, links, gear hubs, and base layout. R2 uses matched involute working rims and the R1 servo interfaces.

**Print the parts in `output/fit_checks/` first. These files have passed CAD checks; physical servo fit and load performance have not been verified.**

## R2 changes and validation scope

All four working rims use module 0.75 and a 20° pressure angle, retaining the 20/19/19/20 tooth arrangement. The working flanks are involutes; radial relief and 0.10 root fillets connect the flanks below the base circle. The big gears retain their linkage-arm junctions. Validation is limited to this gripper's 0–36° relative opening stroke.

Center distances are 14.625/14.250/14.625. Each idler pivot moves approximately 0.257 from R1. R1 axial alignment is retained, giving the full 2.0 big-gear tooth width in engagement with each idler. Original hubs, central interfaces, link lengths, and distal connection holes are retained.

**Rigid gear-chain reversal free play measured from exported CAD is 2.751–2.752°, meeting the provisional target of at most 3°.** The comparable R1 estimate is 8.2–11.6°. These are geometric estimates, excluding printing error, pivot clearance, elastic deflection, friction, and servo backlash. Confirm actual results with the trial parts.

Nominal tangential backlash is 0.12 per mesh, created by thinning each gear's pitch-circle tooth thickness by 0.06. The nearest surface gap at the nominal centered pose is approximately 0.056. Surface gap, tangential backlash, and output free angle are different quantities. Theoretical transverse contact ratio is approximately 1.54–1.55; this does not establish load capacity or contact stress.

The R1 upgrade replaces M01, M02, M05 (formerly U05), and M06 ×2 (formerly U04 ×2): four types and five pieces. The complete mechanism still uses 14 printed pieces. Use the R2 palm and gears as a set. See the [gear review](../output/preview/gear_review_R2.pdf), [gear analysis](../output/validation/gear_engagement.json), and [revision comparison](../output/validation/revision_scope.json).

## Which files to open

- `output/IPX896HV_2DOF_assembly.step`: complete assembly, including two servo and two metal-horn reference envelopes. Fusion or SolidWorks can inspect the separate parts. `REF_` objects are not printable parts.
- `output/stl/`: individual print files, positioned at Z=0 with initial orientations. Print `PRINT_2` files twice.
- `output/step/`: eight modified/new part solid models.
- `output/fit_checks/`: four interface coupons, the four-gear trial plate, and three gear-clearance sets.
- `output/preview/`: assembly previews and positioning drawings.
- `output/assembly_and_print_guide.pdf`: illustrated assembly and trial-print guide.
- `output/validation/`: geometry, mesh, and sampled-motion results.
- `parameters.json` and `scripts/build.py`: dimensions and reproducible CadQuery generation. STEP files do not contain native Fusion/SolidWorks feature history.
- `upstream/`: preserved original project files.

## Retained and modified parts

| ID | Part | Print quantity | Treatment |
|---|---|---:|---|
| U01 | Left jaw | 1 | Original STL; rigid rotation/translation for printing only |
| U02 | Right jaw | 1 | Same |
| U03 | Passive link | 2 | Same |
| U06 | Removable base wall | 1 | Same |
| M01 | Palm / servo carrier | 1 | Retain outline, jaw pivots, and rear interface; add IPX896HV carrier and shaft hole; correct both idler pivots |
| M02 | Left driving gear link | 1 | Matched rim; retain hub, linkage arm, and R1 metal-horn interface |
| M03 | Fixed base | 1 | Retain outline; widen servo opening locally, replace ear holes, and add platform mounting holes |
| M04 | Rotating waist | 1 | Retain hollow body and four side holes; adapt lower horn interface |
| M05 | Right gear link | 1 | Replace U05; change rim and retain hub/linkage arm |
| M06 | Idler gear | 2 | Replace U04; change rim and retain central interface |
| N01 | Yaw horn coupler | 1 | New adapter between metal horn and original waist |
| N02 | Gripper-to-waist bridge | 1 | New adapter between four waist holes and the palm's rear cross slots |

There are 12 main part types and 14 pieces, excluding coupons. Original links are realigned without changing their lengths. Both jaws and linkage stacks are aligned; follow the updated assembly and spacer dimensions.

## Interfaces requiring measurement

The design provisionally uses two IPX896HV servos. The case is 40.5 × 21 × 38.9 from the supplied sheet; total height provisionally follows the other drawing's 44.6. Ear upper/lower heights are provisionally 30.75/27.95; mounting-hole pitch is 48.5 along the length and 10 across the width. The output axis is 10.5 from the short edge. These dimensions may describe different variants and **have not all been confirmed on the actual hardware**.

The case opening allows 0.3 per side. Ear holes are 5.0 × 3.4 slots. Slots offer limited adjustment; they cannot compensate for incorrect case height or output-axis position.

Required metal-horn fit:

- A 25T spline that actually fits the GDW IPX896HV; tooth count alone does not establish compatibility.
- Disc outside diameter no greater than 24. The reference disc is 2 thick and 7 high overall; a 24-diameter disc is recommended.
- At least two opposed M3 tapped holes at radius 9, aligned with the adapter's cross slots. Up to four holes may be used. Although the printed slots span radii 6–9, screw-head insertion beside the gripper shaft requires radius 9. Smaller hole circles are not automatically compatible.
- If the horn uses different hole diameters, positions, or height, update the parameters/interfaces and regenerate the files. Do not force the fit or enlarge holes indiscriminately.
- Use the servo's correct supplied center-screw thread. The design provides a 6.5 tool-access passage and does not specify that screw's thread.

## Interface fit checks

1. Print F01. Confirm the servo case passes through, the ears sit flat, and all four screws enter together. Do not use screws to pull an incompatible case into place.
2. Print F02, including the extension shaft, and fit the actual metal horn. Check hole positions, M3 head recesses, and center-tool access. Use DIN 7380-type low button-head screws with head height at most 1.7 and diameter at most 5.7. Standard tall socket heads are not direct substitutes. Check insertion past the shaft; nominal minimum side clearance is only 0.15.
3. Print F03 and F04 to check the 12.0 shaft / 12.8 hole running fit. Remove elephant foot and burrs; the parts should rotate freely by hand.
4. After checking the horn interface, confirm screw ends clear the servo case. Check horn thickness and screw length together.
5. After the interface checks pass, print M01/M02 for an opening-module dry fit, then proceed to the complete set.

## Gear trial and clearance selection

1. Print `F05_four_gear_trial_plate`. Start with B12: print `F_mesh_20T_B12_PRINT_2` and `F_mesh_19T_B12_PRINT_2` twice each. Fit the 20T gears to the outer axes, approximately 30.09 apart; fit the 19T gears to the closer axes, 14.25 apart.
2. Use four M3 screws or suitable 3 mm smooth shafts with washers. Check each bore and axial endplay. The gears must rotate freely; tightening the nuts must not clamp them. The plate is for manual testing.
3. Rotate the input both ways and check the full tooth circumference for tight spots. Hold the input and measure output free angle with a pointer or protractor. Pivot looseness contributes to the measured value.
4. B08/B12/B16 denote 0.08/0.12/0.16 nominal tangential backlash per mesh. Use one code throughout the set. Choose a set that rotates smoothly both ways with low free play. Correct elephant foot, burrs, and shaft-fit issues before judging tooth clearance. Do not force a jammed train with the servo.
5. The supplied main parts use B12. To use B08 or B16, set `gear_design.tooth_thickness_reduction_mm` to 0.04 or 0.08, update the nominal backlash parameter accordingly, regenerate M02/M05/M06, and rerun validation. Greater clearance can exceed the 3° CAD target; record the new result.
6. After the gear trial passes, dry-assemble the opening module with its original links and jaws, then attach the servo and calibrate unloaded endpoints. The trial plate does not replace complete-mechanism testing.

## Hardware and materials

`BOM.csv` is a procurement starting point. Confirm lengths against actual washers and nuts. Keep M3 lengths 12/16/20 available. Prefer suitable smooth shafts or shoulder screws at moving joints, or arrange for the smooth shank rather than threads to bear the rotating contact.

Servo ears use M3 screws, washers, and nuts. Original pivot bores are approximately 2.8–3.05 and may print undersize. Ream each moving bore to its actual smooth shaft, seeking free rotation without obvious lateral play. A diametral clearance of approximately 0.05–0.10 is an initial trial value. Do not enlarge every original bore equally or increase locating-shaft diameters.

M02 and N01 horn screws require low button heads fully recessed into their slots; N01 must also sit against M04. Insert M02 screws sideways between the gear and adapter flange, slide them into position, and tighten with the short end of a hex key. Assemble the horn before passing M02 through the palm. N02 has M5 head counterbores; tighten these screws before installing the palm.

## Printing recommendations

- Use PLA for initial fit checks. Dry PETG is an option for load-bearing parts; repeat the coupons when changing material.
- Start with a 0.4 nozzle, 0.2 layers, and 4–6 perimeters. Use approximately 40% infill for brackets and locally solid material at M02's extension shaft, horn flange, and gear roots. Gears may use 0.15 layers.
- `output/stl/` parts are placed on the bed, but inspect every layer in the slicer. M01/M02 overhangs and original jaw slots may require local support. Keep support contact off tooth flanks and fit bores.
- The original base is approximately 160 × 96 and the waist is 74.5 high. These dimensions are retained to limit changes.
- No G-code is provided because the printer, nozzle, and material profile have not been specified.

## Assembly order

1. **Calibrate servo centers.** Set the centers before attaching the mechanism, then remove power before fitting horns. Do not begin with a full-range sweep.
2. **Base servo.** Insert it through M03's side, seat the ears against the upper mounting face, and fasten them. Route wires through the removable-wall side and confirm U06 does not pinch them.
3. **Base drive.** Fasten N01 to the metal horn with low-head M3 screws and install the center retaining screw through the tool passage. Attach M04 to N01 with four M3 ×12 screws, thin washers, and standard nuts. Screw ends must clear the fixed base.
4. **Bridge.** Pass four M5 screws through N02's counterbores and the original waist side holes, with nuts inside. Use the hex key before installing the palm.
5. **Opening servo.** Fit it to M01's external carrier and secure all four ears. Attach the metal horn to M02's rear flange before passing the extension shaft through the palm. The central passage provides access to the horn retaining screw.
6. **Gears, links, and jaws.** Position M06 ×2, M05, U03 ×2, and U01/U02 according to the R2 assembly STEP and drawings. Preserve axial endplay with washers and locking nuts; do not clamp moving joints.
7. **Linkage stack.** Both jaws are aligned. Allow approximately 0.3 between fixed pivots and passive links; approximately 1.9 of spacer height between each passive link and jaw; and approximately 0.3 between each gear link and jaw. These are CAD stack values: confirm real endplay and parallelism.
8. **Palm mounting.** Use four M2.5 screws and washers wide enough to span the original rear cross slots. Lower screw ends must clear the waist wall.
9. **Manual check.** Check links, gears, horns, screw ends, and wires individually. Set gear phase from the drawings and STEP. Locate any interference before applying servo torque.
10. **Powered test.** Begin with small unloaded movements. Establish usable opening and yaw endpoints, then pass the software limits to the controls team. Secure the assembly to the platform through the base mounting holes.

## Controls and test limits

Two PWM channels control opening and yaw. The supplied servo sheet specifies 4.8–8.4 V, 500–2500 microsecond pulses, a 1500 microsecond center, and 333 Hz operation. The [Uno R4 WiFi sketch and wiring guide](../firmware/README.md) use D9 for yaw and D10 for opening/closing at approximately 333 Hz. Calibrate the sketch's trial endpoints on the actual assembly; the full electrical pulse range is not the mechanism's permitted travel.

Do not connect the upstream project's 12.6 V battery directly to IPX896HV servos. At 7.4 V the specified stall current is 5.4 A per servo, so two servos may demand approximately 10.8 A peak. Select the supply and wiring accordingly and share ground with the controller.

The design retains the original base load path without an added turntable bearing. **No verified payload rating is provided.** Start unloaded and with light objects; do not size the gear train or thin links around the new servo's stall torque. CAD interference checks do not establish strength, fatigue life, thermal stability, or physical meshing performance.

Delivery checks cover eight modified/new solids; 18 solids in the complete STEP, including four purchased-part reference envelopes; closure and orientation of 23 print/trial STLs; and preserved geometry for four retained STL types. Results are in `output/validation/`.

Tooth sections are sampled every 0.25° and gear-chain contact limits every 0.5°. Motion checks include 13 ideal-ratio opening positions, 20 bidirectional contact-limit poses, and yaw at −45°/0°/+45°. Intersection report thresholds are 0.01 mm³ for static assembly and 0.02 mm³ for motion. Minimum jaw-to-jaw distance over the nominal opening samples is approximately 3.4–47.2 without pads; this is not a general object-size gripping range. Sampling does not establish clearance over every continuous position, and cable sweep or load deformation is not simulated.

## Rebuilding and attribution

Environment setup, script order, PDF generation, and packaging commands are in [Build and delivery](build.md). See the [validation index](validation.md) for report details.

Source: <https://github.com/vshreyas121-code/6-dof-robotic-arm>

Pinned revision: `258d1893ba1b8b49e87baa79da462680fd53681b`.

The upstream MIT license is retained in `upstream/LICENSE`. Original files are checked against Git blob hashes recorded in `source_manifest.json`. Modified and new files are also MIT licensed; see `LICENSE` and `NOTICE.txt`.
