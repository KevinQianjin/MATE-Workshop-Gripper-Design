"""Sampled rigid-body interference/closure checks. Not a load or physical gear test."""
import json, itertools
from pathlib import Path
import cadquery as cq
from motion import posed
from check_and_render import bbox_overlap

ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'output'
P=json.loads((ROOT/'parameters.json').read_text());G=P['gripper'];Y=P['yaw']
gr=cq.importers.importStep(str(ROOT/'upstream/cad/step/assembled-gripper.step')).solids().vals()
palm=cq.Shape.importBrep(str(OUT/'brep/M01_palm_IPX896HV.brep'))
drive=cq.Shape.importBrep(str(OUT/'brep/M02_drive_gear_horn_adapter.brep'))
gear_report=json.loads((OUT/'validation/gear_engagement.json').read_text())
assert gear_report.get('revision')==P['revision'],'Run the current gear analysis first'
rows=[]
def check_pose(angle,gear_angles=None):
    moving,error=posed(gr,drive,P,angle,gear_angles=gear_angles)
    parts={'palm':palm,**moving};collisions=[]
    for (na,a),(nb,b) in itertools.combinations(parts.items(),2):
        if not bbox_overlap(a,b):continue
        v=a.intersect(b).Volume()
        if v>.02:collisions.append({'a':na,'b':nb,'intersection_mm3':round(v,5)})
    gap=moving['claw_left'].distance(moving['claw_right'])
    row={'opening_rotation_deg':angle,'linkage_closure_error_mm':error,'minimum_jaw_to_jaw_distance_mm':gap,'intersections':collisions}
    return row
for angle in range(0,37,3):
    row=check_pose(angle);rows.append(row);print(json.dumps(row),flush=True)

# Check the entire linkage with the driven gears on both actual contact limits,
# rather than moving all gears only at ideal ratios inside their free play.
contact_rows=[]
for sample in gear_report['chain_samples']:
    a=sample['input_opening_deg']
    if abs(a/4-round(a/4))>1e-9 and a!=36:continue
    for contact in sample['contact_poses']:
        g=contact['gear_angles_2d']
        row=check_pose(a,{'drive':g['17'],'left':g['7'],'right':g['11'],'output':g['16']})
        row['contact_direction']=contact['direction'];contact_rows.append(row)
        print('CONTACT',json.dumps(row),flush=True)

# The complete upper assembly yaws about the servo axis; check three yaw positions
# against the fixed base and wall. Geometric hardware envelopes are checked statically.
fixed={n:cq.Shape.importBrep(str(OUT/'brep'/f'assembly_{n}.brep')) for n in ['base','base_wall']}
upper={p.stem.removeprefix('assembly_'):cq.Shape.importBrep(str(p)) for p in (OUT/'brep').glob('assembly_*.brep') if p.stem.removeprefix('assembly_') not in ['base','base_wall','REF_yaw_servo']}
yaw_checks=[]
for yaw in [-45,0,45]:
    hits=[]
    for name,shape in upper.items():
        rotated=shape.rotate((0,Y['axis_offset_y'],0),(0,Y['axis_offset_y'],1),yaw)
        for other,b in fixed.items():
            if not bbox_overlap(rotated,b):continue
            v=rotated.intersect(b).Volume()
            if v>.02:hits.append({'a':name,'b':other,'intersection_mm3':v})
    yaw_checks.append({'yaw_degrees':yaw,'intersections':hits})
report={'scope':'Rigid CAD; exact BRep intersections at ideal-ratio poses and both driven contact limits. Fastener threads, cable swept volume, elastic deflection and force are not simulated.','opening_samples':rows,'contact_limit_samples':contact_rows,'yaw_samples':yaw_checks}
(OUT/'validation/motion.json').write_text(json.dumps(report,indent=2))
assert all(not x['intersections'] for x in rows+contact_rows+yaw_checks),'Resolve motion intersections before delivery'
print('MOTION_REPORT_WRITTEN',flush=True)
