"""Measure original tooth profiles, axial engagement and rigid backlash.

Tooth sections are sampled from STEP at <=0.03 mm along each edge. This is a
nominal, rigid geometry analysis, not a force/contact-ratio or print test.
"""
import json, math
from pathlib import Path
import numpy as np
import cadquery as cq
from OCP.BRepAdaptor import BRepAdaptor_Surface
from OCP.BRepAlgoAPI import BRepAlgoAPI_Section
from shapely.geometry import LineString,Point,Polygon
from shapely.ops import polygonize,unary_union,nearest_points

ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'output'
P=json.loads((ROOT/'parameters.json').read_text())
gr=cq.importers.importStep(str(ROOT/'upstream/cad/step/assembled-gripper.step')).solids().vals()
centers={17:np.array([-18.5960823864,-12.8816877857]),16:np.array([11.4856,-13.7218]),7:np.array([-10.808355,-1.9993]),11:np.array([2.9457,-1.9993])}
coords={};bands={};tips={17:8.15,16:8.15,7:7.5,11:7.5}
for i in [17,7,11,16]:
    face=cq.Face.makePlane(300,300,cq.Vector(0,18.8,0),cq.Vector(0,1,0))
    op=BRepAlgoAPI_Section(gr[i].wrapped,face.wrapped);op.Build();lines=[]
    for edge in cq.Shape.cast(op.Shape()).Edges():
        pts,_=edge.sample(max(2,math.ceil(edge.Length()/.03)))
        lines.append(LineString(np.round([[p.x,p.z] for p in pts],7)))
    poly=max(polygonize(unary_union(lines)),key=lambda p:p.area)
    poly=poly.intersection(Point(centers[i]).buffer(tips[i]+.01,quad_segs=256))
    coords[i]=np.asarray(poly.exterior.coords)-centers[i]
    intervals=[]
    for f in gr[i].Faces():
        if f.geomType()=='CYLINDER' and abs(BRepAdaptor_Surface(f.wrapped).Cylinder().Radius()-tips[i])<1e-5:
            b=f.BoundingBox();intervals.append((b.ymin,b.ymax))
    bands[i]=[min(v[0] for v in intervals),max(v[1] for v in intervals)]

centers[7]=np.array(P['gear_alignment']['idler_left_xz']);centers[11]=np.array(P['gear_alignment']['idler_right_xz'])
ph=P['gear_alignment']['phase_degrees_2d']
def polygon(i,deg):
    t=math.radians(deg);rot=np.array([[math.cos(t),-math.sin(t)],[math.sin(t),math.cos(t)]])
    return Polygon(coords[i]@rot.T+centers[i])
def nominal(t):return {17:-t,7:ph['idler_left']+t*20/19,11:ph['idler_right']-t*20/19,16:ph['right_gear']+t}
def free_band(a,i,beta,search=True):
    pitch=360/(19 if i in [7,11] else 20)
    if a.intersects(polygon(i,beta)):
        if not search:raise ValueError('Nominal pose penetrates')
        candidates=sorted(np.linspace(beta-pitch/2,beta+pitch/2,121),key=lambda b:abs(b-beta))
        beta=next((b for b in candidates if not a.intersects(polygon(i,b))),None)
        if beta is None:raise ValueError('No free angular position')
    out=[]
    for sign in [-1,1]:
        lo=0;hi=None
        for offset in np.linspace(pitch/40,pitch,40):
            if a.intersects(polygon(i,beta+sign*offset)):hi=offset;break
            lo=offset
        if hi is None:raise ValueError('Tooth pair does not engage within a tooth pitch')
        for _ in range(19):
            mid=(lo+hi)/2
            if a.intersects(polygon(i,beta+sign*mid)):hi=mid
            else:lo=mid
        out.append(beta+sign*lo)
    return out

def main():
    report={'scope':__doc__,'tooth_bands_source_y_mm':bands,'samples':[],'pairs':{}}
    actual=cq.Shape.importBrep(str(OUT/'brep/M02_drive_gear_horn_adapter.brep'))
    tooth_faces=[f for f in actual.Faces() if f.geomType()=='CYLINDER' and abs(BRepAdaptor_Surface(f.wrapped).Cylinder().Radius()-8.15)<1e-5]
    actual_band=[min(f.BoundingBox().ymin for f in tooth_faces),max(f.BoundingBox().ymax for f in tooth_faces)]
    assert np.allclose(actual_band,np.array(bands[17])+P['gripper'].get('drive_gear_axial_shift',0),atol=1e-5)
    report['exported_drive_tooth_band_y_mm']=actual_band
    all_rows={(17,7):[],(7,11):[],(11,16):[]}
    for t in np.arange(0,36.001,.5):
        angles=nominal(float(t));polys={i:polygon(i,a) for i,a in angles.items()}
        row={'opening_deg':float(t),'pairs':{}}
        for a,b in all_rows:
            free=free_band(polys[a],b,angles[b],False)
            item={'surface_gap_mm':polys[a].distance(polys[b]),'overlap_mm2':polys[a].intersection(polys[b]).area,'driven_free_angle_deg':free[1]-free[0]}
            row['pairs'][f'{a}-{b}']=item;all_rows[a,b].append(item)
        report['samples'].append(row)
    for (a,b),rows in all_rows.items():
        ba=bands[a].copy();bb=bands[b].copy()
        original=max(0,min(ba[1],bb[1])-max(ba[0],bb[0]))
        if a==17:ba=[v+P['gripper'].get('drive_gear_axial_shift',0) for v in ba]
        overlap=max(0,min(ba[1],bb[1])-max(ba[0],bb[0]))
        report['pairs'][f'{a}-{b}']={'center_distance_mm':float(np.linalg.norm(centers[a]-centers[b])),
            'radial_tip_circle_overlap_mm':float(tips[a]+tips[b]-np.linalg.norm(centers[a]-centers[b])),
            'original_axial_tooth_overlap_mm':original,'corrected_axial_tooth_overlap_mm':overlap,
            'surface_gap_range_mm':[min(r['surface_gap_mm'] for r in rows),max(r['surface_gap_mm'] for r in rows)],
            'driven_free_angle_range_deg':[min(r['driven_free_angle_deg'] for r in rows),max(r['driven_free_angle_deg'] for r in rows)]}
    # Serial rigid contact limits: lower/upper on successive external meshes.
    chain=[]
    for t in np.arange(0,36.001,1):
        nom=nominal(float(t));ends=[]
        for side in [-1,1]:
            angles={17:nom[17]}
            for n,(a,b) in enumerate([(17,7),(7,11),(11,16)]):
                lower,upper=free_band(polygon(a,angles[a]),b,nom[b])
                angles[b]=lower if side*(-1)**n<0 else upper
            ends.append(angles[16])
        chain.append({'input_opening_deg':float(t),'right_gear_contact_angle_limits_deg':ends,'right_gear_free_angle_deg':abs(ends[1]-ends[0])})
    report['chain_samples']=chain
    report['chain_free_angle_range_deg']=[min(x['right_gear_free_angle_deg'] for x in chain),max(x['right_gear_free_angle_deg'] for x in chain)]
    (OUT/'validation').mkdir(parents=True,exist_ok=True)
    (OUT/'validation/gear_engagement.json').write_text(json.dumps(report,indent=2))
    (OUT/'validation/tooth_profiles.json').write_text(json.dumps({str(i):v.tolist() for i,v in coords.items()}))
    print(json.dumps({'pairs':report['pairs'],'chain_free_angle_range_deg':report['chain_free_angle_range_deg']},indent=2),flush=True)

if __name__=='__main__':main()
