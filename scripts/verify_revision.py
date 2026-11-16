"""Verify the intended R2 change scope against retained R1 and upstream CAD."""
import json,hashlib
from pathlib import Path
import cadquery as cq
from gears import AXIS_L,AXIS_R,IDLER_SOURCE
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'output';REF=ROOT/'reference/R1_parts'
manifest=json.loads((REF/'manifest.json').read_text())
def load(path):return cq.Shape.importBrep(str(path))
def difference(a,b):return max(0,a.cut(b).Volume())+max(0,b.cut(a).Volume())
def cylinder(center,r,y,h):return cq.Solid.makeCylinder(r,h,cq.Vector(center[0],y,center[1]),cq.Vector(0,1,0))
rows={}
for name,digest in manifest['sha256'].items():
    path=REF/f'{name}.brep';assert hashlib.sha256(path.read_bytes()).hexdigest()==digest
    if name.startswith('M02'):continue
    v=difference(load(path),load(OUT/'brep'/path.name));assert v<.001,(name,v);rows[name]=v
gr=cq.importers.importStep(str(ROOT/'upstream/cad/step/assembled-gripper.step')).solids().vals()
checks=[('M02_drive_gear_horn_adapter',load(REF/'M02_drive_gear_horn_adapter.brep'),AXIS_L,8.4,2),
        ('M05_right_gear_involute',gr[16],AXIS_R,8.4,2),
        ('M06_small_gear_involute_PRINT_2',gr[7],IDLER_SOURCE,8.1,3)]
gears={}
for name,old,center,r,h in checks:
    new=load(OUT/'brep'/f'{name}.brep')
    envelope=cylinder(center,r,18.516945,h+.02)
    core=cylinder(center,4.0,-1,30)
    outer=difference(old.cut(envelope),new.cut(envelope))
    inner=difference(old.intersect(core),new.intersect(core))
    assert outer<.01 and inner<.01,(name,outer,inner)
    gears[name]={'outside_tooth_band_difference_mm3':outer,'central_interface_difference_mm3':inner}
inventory=json.loads((OUT/'validation/build_inventory.json').read_text())
quantity=sum(v['quantity'] for v in inventory.values());assert quantity==14
report={'baseline_commit':manifest['source_commit'],'unchanged_R1_parts_difference_mm3':rows,
        'preserved_gear_interfaces':gears,'main_part_types':len(inventory),'main_piece_count':quantity,
        'replacement_types_from_R1':['M01','M02','M05 (replaces U05)','M06 x2 (replaces U04 x2)'],'replacement_piece_count':5,
        'note':'Comparison excludes the intended tooth band with a 0.01 mm axial comparison margin. Hardware dimensions still need physical confirmation.'}
(OUT/'validation/revision_scope.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
