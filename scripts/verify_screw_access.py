"""Check the specified M3 button screw's sampled entry path into the drive flange.

The drive and metal horn are assembled before fitting the palm. This checks the
printed drive only; real horn threads, tool ergonomics and tolerances need a trial.
"""
import json, math
from pathlib import Path
import cadquery as cq
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'output'
P=json.loads((ROOT/'parameters.json').read_text());H=P['metal_horn_interface']
D=json.loads((OUT/'validation/datums.json').read_text());sx,sz=D['gripper_drive_axis_xz']
drive=cq.Shape.importBrep(str(OUT/'brep/M02_drive_gear_horn_adapter.brep'))
def cylinder(radius,height,x,y,z):
    return cq.Solid.makeCylinder(radius,height,cq.Vector(x,y,z),cq.Vector(0,1,0))
checks=[]
for angle in H['bolt_directions_degrees']:
    a=math.radians(angle);r=H['required_bolt_hole_radius']
    # Insert radially from the side with the screw tip above the flange.
    path=[(rad,11) for rad in [18,16,14,12,10,r]]
    # Then lower into the slot, past the central shaft.
    path += [(r,11-i*.5) for i in range(1,20)]
    max_v=0
    for rad,y in path:
        x=sx+rad*math.cos(a);z=sz+rad*math.sin(a)
        head=cylinder(H['bolt_head_max_diameter']/2,H['bolt_head_max_height'],x,y,z)
        shank=cylinder(1.5,6,x,y-6,z)
        v=drive.intersect(head.fuse(shank)).Volume();max_v=max(max_v,v)
    # Short leg of a 2 mm AF hex key; long leg approaches from outside.
    tool=cylinder(1.16,7,sx+r*math.cos(a),2,sz+r*math.sin(a))
    tool_v=drive.intersect(tool).Volume()
    assert max_v<.001 and tool_v<.001,(angle,max_v,tool_v)
    checks.append({'angle_deg':angle,'sampled_positions':len(path),'max_intersection_mm3':max_v,'short_tool_leg_intersection_mm3':tool_v})
report={'scope':'Specified M3x6 screw, head OD<=5.7 and height<=1.7, radial hole R9. Sampled side-entry path before installing palm. Threads and physical handling not simulated.',
        'nominal_head_to_shaft_radial_clearance_mm':H['required_bolt_hole_radius']-H['bolt_head_max_diameter']/2-P['gripper']['shaft_extension_diameter']/2,
        'checks':checks}
(OUT/'validation/screw_access.json').write_text(json.dumps(report,indent=2))
print('SCREW_ACCESS_PASS',len(checks))
