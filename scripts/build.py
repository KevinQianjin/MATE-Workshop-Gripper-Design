"""Minimal-interface IPX896HV adaptation of pinned upstream CAD. Units: mm.

CadQuery 2.x. Run: python scripts/build.py
R1 is a fit-check prototype, not a physically validated production assembly.
"""
import json, math, shutil, struct, hashlib
from pathlib import Path
import cadquery as cq
import numpy as np
from OCP.BRepAdaptor import BRepAdaptor_Surface

ROOT=Path(__file__).resolve().parents[1]
P=json.loads((ROOT/'parameters.json').read_text())
S=P['servo']; H=P['metal_horn_interface']; G=P['gripper']; Y=P['yaw']
OUT=ROOT/'output'
for folder in ['step','stl','fit_checks','preview','validation','brep']:
    (OUT/folder).mkdir(parents=True,exist_ok=True)

def box(x0,x1,y0,y1,z0,z1):
    assert x1>x0 and y1>y0 and z1>z0
    return cq.Solid.makeBox(x1-x0,y1-y0,z1-z0,cq.Vector(x0,y0,z0))
def cyl(r,h,point,direction=(0,0,1)):
    return cq.Solid.makeCylinder(r,h,cq.Vector(*point),cq.Vector(*direction))
def capsule_y(x0,x1,z,r,y0,y1):
    return box(x0,x1,y0,y1,z-r,z+r).fuse(cyl(r,y1-y0,(x0,y0,z),(0,1,0)),cyl(r,y1-y0,(x1,y0,z),(0,1,0)))
def capsule_z(x0,x1,y,r,z0,z1):
    return box(x0,x1,y-r,y+r,z0,z1).fuse(cyl(r,z1-z0,(x0,y,z0)),cyl(r,z1-z0,(x1,y,z0)))
def cylinder_origin(shape,radius):
    for f in shape.Faces():
        if f.geomType()=='CYLINDER':
            c=BRepAdaptor_Surface(f.wrapped).Cylinder()
            if abs(c.Radius()-radius)<1e-5:
                a=c.Location();return np.array([a.X(),a.Y(),a.Z()])
    raise ValueError(radius)
def angular_horn_slots_y(shape,sx,sz,y0,y1,width=None):
    r0=H['bolt_slot_inner_radius'];r1=H['bolt_slot_outer_radius'];w=(width or H['bolt_slot_width'])/2
    basic=capsule_y(sx+r0,sx+r1,sz,w,y0,y1)
    for ang in H['bolt_directions_degrees']:
        shape=shape.cut(basic.rotate((sx,0,sz),(sx,1,sz),ang))
    return shape
def angular_horn_slots_z(shape,z0,z1,cy=0,width=None):
    r0=H['bolt_slot_inner_radius'];r1=H['bolt_slot_outer_radius'];w=(width or H['bolt_slot_width'])/2
    basic=capsule_z(r0,r1,cy,w,z0,z1)
    for ang in H['bolt_directions_degrees']:
        shape=shape.cut(basic.rotate((0,cy,0),(0,cy,1),ang))
    return shape
def mesh_to_bed(source,dest,flip=False):
    """Rigidly orient an upstream binary STL. Connectivity and triangles unchanged."""
    raw=bytearray(source.read_bytes());n=struct.unpack_from('<I',raw,80)[0]
    arr=np.frombuffer(raw,dtype=np.dtype([('n','<f4',(3,)),('v','<f4',(3,3)),('a','<u2')]),offset=84,count=n)
    a=-math.pi/2 if flip else math.pi/2
    rot=np.array([[1,0,0],[0,math.cos(a),-math.sin(a)],[0,math.sin(a),math.cos(a)]])
    v=arr['v'].astype(float)@rot.T
    mn=v.reshape(-1,3).min(0);mx=v.reshape(-1,3).max(0)
    v-=np.array([(mn[0]+mx[0])/2,(mn[1]+mx[1])/2,mn[2]])
    arr['v']=v;arr['n']=arr['n'].astype(float)@rot.T
    dest.write_bytes(raw)
    return {'triangles':n,'rigid_transform_only':True,'original_sha256':hashlib.sha256(source.read_bytes()).hexdigest()}
def bed(shape,axis='z',flip=False):
    if axis=='y':shape=shape.rotate((0,0,0),(1,0,0),-90 if flip else 90)
    elif axis=='z' and flip:shape=shape.rotate((0,0,0),(1,0,0),180)
    b=shape.BoundingBox()
    return shape.translate((-(b.xmin+b.xmax)/2,-(b.ymin+b.ymax)/2,-b.zmin))

gr=cq.importers.importStep(str(ROOT/'upstream/cad/step/assembled-gripper.step')).solids().vals()
arm=cq.importers.importStep(str(ROOT/'upstream/cad/step/6-dof-robotic-arm.step')).solids().vals()
assert len(gr)==19 and len(arm)==43,'Unexpected upstream assembly'
assert abs(gr[6].Volume()-29090.485)<.1
assert abs(arm[16].Volume()-184756.116)<.1
sx,_,sz=cylinder_origin(gr[17],7.0)
base_axis=cylinder_origin(arm[12],32.5)
base_bottom=arm[16].BoundingBox().ymin
def base_frame(s):
    return s.translate((-base_axis[0],-base_bottom,-base_axis[2])).rotate((0,0,0),(1,0,0),90)
original_base=base_frame(arm[16]);basewall=base_frame(arm[18])
original_rotor=base_frame(arm[12]).rotate((0,0,0),(0,0,1),180)
original_rotor_bottom=original_rotor.BoundingBox().zmin

# 01: Keep the original palm, pivot bosses, rear mount and all linkage datums.
# Fill only the old micro-servo opening; an external carrier holds the larger servo.
palm=gr[6].fuse(box(-30,3,6.527,16.027,sz-7.62,sz+7.62))
palm=palm.cut(cyl(G['shaft_running_clearance_diameter']/2,80,(sx,-30,sz),(0,1,0)))
palm=palm.cut(cyl(7.3,2.2,(sx,14.3,sz),(0,1,0)))
# Relocate only the two idler bosses. The upstream gear shapes are untouched.
for source_i,key in [(7,'idler_left_xz'),(11,'idler_right_xz')]:
    old=cylinder_origin(gr[source_i],7.5)
    nx,nz=P['gear_alignment'][key]
    palm=palm.cut(cyl(2.8,5,(old[0],16.0269,old[2]),(0,1,0)))
    palm=palm.fuse(cyl(3.55,9.5,(old[0],6.527,old[2]),(0,1,0)))
    palm=palm.fuse(cyl(2.75,3.5,(nx,16.027,nz),(0,1,0)))
    palm=palm.cut(cyl(1.525,15,(nx,6,nz),(0,1,0)))
    palm=palm.cut(cyl(3.5,1.65,(nx,6.477,nz),(0,1,0)))
    # The relocated teeth approach the original rear mounting flange.
    # Relieve its front edge, preserving the center boss and the rear screw seats.
    relief=cyl(7.85,7,(nx,16.2,nz),(0,1,0)).cut(cyl(6.0,7.2,(nx,16.1,nz),(0,1,0)))
    palm=palm.cut(relief)
body_front=G['servo_case_top_y'];body_back=body_front-S['body_height']
ear_front=body_back+S['ear_top_height'];carrier_front=ear_front+G['carrier_thickness']
cx=sx+S['body_length']/2-S['axis_from_short_end']
carrier=box(sx-21.5,sx+42,ear_front,carrier_front,sz-16,sz+16)
clear=S['body_clearance_per_side']
body_opening=box(cx-S['body_length']/2-clear,cx+S['body_length']/2+clear,ear_front-1,carrier_front+1,sz-S['body_width']/2-clear,sz+S['body_width']/2+clear)
carrier=carrier.cut(body_opening)
slot_half=(S['mount_slot_length']-S['mount_slot_width'])/2
for x in [cx-S['ear_hole_pitch_length']/2,cx+S['ear_hole_pitch_length']/2]:
    for z in [sz-S['ear_hole_pitch_width']/2,sz+S['ear_hole_pitch_width']/2]:
        carrier=carrier.cut(capsule_y(x-slot_half,x+slot_half,z,S['mount_slot_width']/2,ear_front-1,carrier_front+1))
for x0,x1 in [(-35.95,-29.95),(15.5,21.5)]:
    for z0,z1 in [(sz-16,sz-10),(sz+10,sz+16)]:
        carrier=carrier.fuse(box(x0,x1,carrier_front-.1,7.0,z0,z1))
palm=palm.fuse(carrier).clean()

# 02: Original driving gear tooth profile and connecting arm are retained.
# Replace only its horn recess with a through-tool-access shaft and slotted flange.
lift=G['drive_gear_axial_shift']
drive=gr[17].translate((0,lift,0))
drive=drive.fuse(cyl(4.08,4.5,(sx,14.6+lift,sz),(0,1,0)))
drive=drive.fuse(cyl(G['shaft_extension_diameter']/2,15.0+lift,(sx,0,sz),(0,1,0)))
drive=drive.fuse(cyl(G['coupler_flange_diameter']/2,G['coupler_flange_thickness'],(sx,0,sz),(0,1,0)))
drive=drive.cut(cyl(H['central_tool_access_diameter']/2,25,(sx,-1,sz),(0,1,0)))
drive=angular_horn_slots_y(drive,sx,sz,-1,5).clean()
drive=angular_horn_slots_y(drive,sx,sz,1.5,4.0,width=6.4).clean()

# 03: Original base plate and housing, with a slightly widened upper servo slot.
# Move the servo axis 0.5 mm toward the open side to reuse the removable wall.
cy=Y['axis_offset_y'];yaw_cx=-(S['body_length']/2-S['axis_from_short_end'])
base=original_base
# Close the four original MG995 mounting bores before making the new slots;
# otherwise the two overlapping patterns leave unsupported slivers.
for f in arm[16].Faces():
    if f.geomType()=='CYLINDER':
        c=BRepAdaptor_Surface(f.wrapped).Cylinder()
        if abs(c.Radius()-1.575)<1e-5:
            q=c.Location()
            base=base.fuse(cyl(1.60,8.5,(q.X()-base_axis[0],-(q.Z()-base_axis[2]),39)))
base=base.cut(box(yaw_cx-S['body_length']/2-clear,yaw_cx+S['body_length']/2+clear,cy-S['body_width']/2-clear,cy+S['body_width']/2+clear,38.99,60))
for x in [yaw_cx-S['ear_hole_pitch_length']/2,yaw_cx+S['ear_hole_pitch_length']/2]:
    for y in [cy-S['ear_hole_pitch_width']/2,cy+S['ear_hole_pitch_width']/2]:
        base=base.cut(capsule_z(x-slot_half,x+slot_half,y,S['mount_slot_width']/2,38.9,50))
# Four table-fixing holes in the existing plate; no change to its footprint.
for x in [-65,45]:
    for y in [-35,35]:base=base.cut(cyl(2.7,9,(x,y,-1)))
base=base.clean()
yaw_bottom=Y['ear_top_z']-S['ear_top_height']
yaw_shaft_top=yaw_bottom+S['overall_height']
yaw_horn_face=yaw_shaft_top+Y['horn_face_above_shaft_top']
rotor_bottom=yaw_horn_face+Y['coupler_thickness']
rotor_lift=rotor_bottom-original_rotor_bottom
# 04: Original hollow waist. Replace only its underside horn interface.
rotor=original_rotor.fuse(cyl(21,4.5,(0,0,original_rotor_bottom)))
rotor=rotor.cut(cyl(H['central_tool_access_diameter']/2,6,(0,0,original_rotor_bottom-1)))
for x in [-Y['rotor_bolt_x'],Y['rotor_bolt_x']]:
    for y in [-Y['rotor_bolt_y'],Y['rotor_bolt_y']]:
        rotor=rotor.cut(cyl(1.7,6,(x,y,original_rotor_bottom-1)))
rotor=rotor.translate((0,cy,rotor_lift)).clean()
# 05: Flat coupling plate between the metal horn and retained waist.
yaw_adapter=cyl(Y['coupler_diameter']/2,Y['coupler_thickness'],(0,cy,yaw_horn_face))
yaw_adapter=angular_horn_slots_z(yaw_adapter,yaw_horn_face-1,rotor_bottom+1,cy)
yaw_adapter=angular_horn_slots_z(yaw_adapter,yaw_horn_face+1.5,rotor_bottom,cy,width=6.4)
yaw_adapter=yaw_adapter.cut(cyl(H['central_tool_access_diameter']/2,6,(0,cy,yaw_horn_face-1)))
for x in [-Y['rotor_bolt_x'],Y['rotor_bolt_x']]:
    for y in [-Y['rotor_bolt_y'],Y['rotor_bolt_y']]:
        yaw_adapter=yaw_adapter.cut(cyl(1.7,6,(x,y+cy,yaw_horn_face-1)))
yaw_adapter=yaw_adapter.clean()

def gripper_frame(s):
    return s.rotate((0,0,0),(1,0,0),90).translate((G['assembly_offset_x'],G['assembly_offset_y']+cy,G['assembly_offset_z']))
gripper_rear_y=G['assembly_offset_y']+cy-gr[6].BoundingBox().zmax
# 06: A single bridge uses the four existing waist mounting holes and palm cross slots.
bridge=box(-25,25,26+cy,gripper_rear_y,65,149)
waist_holes=[]
for f in arm[12].Faces():
    if f.geomType()!='CYLINDER':continue
    c=BRepAdaptor_Surface(f.wrapped).Cylinder()
    if abs(c.Radius()-3)>1e-5:continue
    a=c.Location();d=c.Axis().Direction()
    # Original -> canonical base -> 180-degree waist turn -> installed offset.
    p=np.array([-(a.X()-base_axis[0]),a.Z()-base_axis[2]+cy,a.Y()-base_bottom+rotor_lift])
    v=np.array([-d.X(),d.Z(),d.Y()]);v=v/np.linalg.norm(v)
    x=p[0]+v[0]*(26+cy-p[1])/v[1]
    bridge=bridge.fuse(cyl(6,8,(x,20+cy,p[2]),(0,1,0)))
    waist_holes.append((p,v))
bridge=bridge.cut(rotor)
for p,v in waist_holes:
    bridge=bridge.cut(cyl(2.8,45,tuple(p-v*10),tuple(v)))
    x=p[0]+v[0]*(gripper_rear_y-p[1])/v[1]
    # Recess M5 socket heads, otherwise the upper two heads hit the palm rear wall.
    bridge=bridge.cut(cyl(4.7,5.5,(x,gripper_rear_y-5.4,p[2]),(0,1,0)))
palm_bolts=[(-12,136.527),(12,136.527),(0,130),(0,143)]
for x,z in palm_bolts:bridge=bridge.cut(cyl(1.5,20,(x,20+cy,z),(0,1,0)))
bridge=bridge.clean()

# Purchased-part envelopes; display/reference only, never export as printable parts.
def servo_y(sx,sz,case_top,positive_x=True):
    cx=sx+(1 if positive_x else -1)*(S['body_length']/2-S['axis_from_short_end'])
    back=case_top-S['body_height']
    body=box(cx-S['body_length']/2,cx+S['body_length']/2,back,case_top,sz-S['body_width']/2,sz+S['body_width']/2)
    ear=box(cx-S['ear_total_length']/2,cx+S['ear_total_length']/2,back+S['ear_bottom_height'],back+S['ear_top_height'],sz-S['body_width']/2,sz+S['body_width']/2)
    spindle=cyl(2.98,S['overall_height']-S['body_height'],(sx,case_top,sz),(0,1,0))
    return body.fuse(ear,spindle)
gr_servo=servo_y(sx,sz,body_front)
yaw_servo=servo_y(0,0,yaw_bottom+S['body_height'],positive_x=False).rotate((0,0,0),(1,0,0),90).translate((0,cy,0))
def horn_y(x,z,face_y):
    disk=cyl(H['max_disc_diameter']/2,H['reference_disc_thickness'],(x,face_y-H['reference_disc_thickness'],z),(0,1,0))
    hub=cyl(6,H['reference_total_height']-H['reference_disc_thickness'],(x,face_y-H['reference_total_height'],z),(0,1,0))
    return disk.fuse(hub).cut(cyl(3,10,(x,face_y-8,z),(0,1,0)))
gr_horn=horn_y(sx,sz,0)
yaw_horn=horn_y(0,0,yaw_horn_face).rotate((0,0,0),(1,0,0),90).translate((0,cy,0))

parts={
 'M01_palm_IPX896HV':(palm,'y',True),
 'M02_drive_gear_horn_adapter':(drive,'y',True),
 'M03_base_IPX896HV':(base,'z',False),
 'M04_original_waist_horn_interface':(rotor,'z',False),
 'N01_yaw_horn_coupler':(yaw_adapter,'z',False),
 'N02_gripper_to_waist_bridge':(bridge,'y',True),
}
result={}
for name,(s,axis,flip) in parts.items():
    assert s.isValid(),f'Invalid solid: {name}'
    if len(s.Solids())!=1:
        s.exportBrep(str(OUT/'brep'/f'DEBUG_{name}.brep'))
        print('SPLIT',name,[(a.Volume(),a.Center().toTuple()) for a in s.Solids()],flush=True)
    assert len(s.Solids())==1,f'Disconnected part: {name}: {len(s.Solids())}'
    cq.exporters.export(s,str(OUT/'step'/f'{name}.step'))
    cq.exporters.export(bed(s,axis,flip),str(OUT/'stl'/f'{name}.stl'),tolerance=.04,angularTolerance=.1)
    s.exportBrep(str(OUT/'brep'/f'{name}.brep'))
    b=s.BoundingBox();result[name]={'valid':True,'solids':1,'volume_mm3':s.Volume(),'bounds_mm':[b.xlen,b.ylen,b.zlen]}

reuse={
 'U01_left_claw':('gripper/claw/left-claw.stl',1,False),
 'U02_right_claw':('gripper/claw/right-claw.stl',1,False),
 'U03_linkage_PRINT_2':('gripper/2x-linkage.stl',2,False),
 'U04_small_gear_PRINT_2':('gripper/gears/2x-small-gear.stl',2,True),
 'U05_big_gear_right':('gripper/gears/big-gear-right.stl',1,True),
 'U06_base_wall':('base/base-wall.stl',1,False)
}
for name,(path,qty,flip) in reuse.items():
    r=mesh_to_bed(ROOT/'upstream/cad/STL'/path,OUT/'stl'/f'{name}.stl',flip)
    r.update({'quantity':qty,'source':path});result[name]=r

# Low-cost fit checks before printing the main parts.
carrier_test=carrier.intersect(box(-100,100,ear_front-.1,carrier_front+.01,-100,100))
horn_test=cyl(G['coupler_flange_diameter']/2,4,(0,0,0)).fuse(cyl(G['shaft_extension_diameter']/2,15+lift,(0,0,0)))
horn_test=angular_horn_slots_z(horn_test,-1,5)
horn_test=angular_horn_slots_z(horn_test,1.5,4,width=6.4)
horn_test=horn_test.cut(cyl(H['central_tool_access_diameter']/2,17+lift,(0,0,-1)))
ring_test=cyl(10,4,(0,0,0)).cut(cyl(G['shaft_running_clearance_diameter']/2,6,(0,0,-1)))
shaft_test=cyl(6,10,(0,0,0)).fuse(cyl(9,2,(0,0,0)))
for name,s,axis in [('F01_servo_ear_fit',carrier_test,'y'),('F02_horn_slot_fit',horn_test,'z'),('F03_shaft_clearance_ring',ring_test,'z'),('F04_shaft_fit_pin',shaft_test,'z')]:
    assert s.isValid() and len(s.Solids())==1,name
    cq.exporters.export(bed(s,axis),str(OUT/'fit_checks'/f'{name}.stl'),tolerance=.04,angularTolerance=.1)
    cq.exporters.export(s,str(OUT/'fit_checks'/f'{name}.step'))

assembled={
 'base':base,'base_wall':basewall,'yaw_coupler':yaw_adapter,'waist':rotor,'bridge':bridge,
 'palm':gripper_frame(palm),'drive_gear':gripper_frame(drive),
 'REF_yaw_servo':yaw_servo,'REF_gripper_servo':gripper_frame(gr_servo),
 'REF_yaw_metal_horn':yaw_horn,'REF_gripper_metal_horn':gripper_frame(gr_horn)
}
from motion import posed
moving,_=posed(gr,drive,P,0)
assembled.update({name:gripper_frame(s) for name,s in moving.items()})
colors={'base':(.30,.38,.46),'base_wall':(.30,.38,.46),'waist':(.30,.38,.46),'yaw_coupler':(.95,.60,.10),'bridge':(.95,.60,.10),'palm':(.15,.55,.65),'drive_gear':(.95,.60,.10)}
assembly=cq.Assembly(name='IPX896HV_2DOF_R1_FIT_CHECK')
for name,s in assembled.items():
    color=colors.get(name,(.63,.68,.72) if not name.startswith('REF_') else (.16,.18,.20))
    if 'claw' in name:color=(.30,.65,.48)
    assembly.add(s,name=name,color=cq.Color(*color))
    s.exportBrep(str(OUT/'brep'/f'assembly_{name}.brep'))
assembly.save(str(OUT/'IPX896HV_2DOF_assembly.step'))
(OUT/'validation/build_inventory.json').write_text(json.dumps(result,indent=2))
datums={'gripper_drive_axis_xz':[sx,sz],'yaw_ear_top_z':Y['ear_top_z'],'yaw_servo_bottom':yaw_bottom,'yaw_horn_face_z':yaw_horn_face,'rotor_bottom_z':rotor_bottom,'rotor_lift':rotor_lift,'gripper_ear_front_y':ear_front,'gripper_carrier_front_y':carrier_front,'gripper_rear_assembly_y':gripper_rear_y}
(OUT/'validation/datums.json').write_text(json.dumps(datums,indent=2))
print(json.dumps({'modified_and_new_parts':result,'datums':datums},indent=2))
