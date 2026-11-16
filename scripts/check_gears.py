"""Measure exported R2 tooth profiles, axial engagement and rigid backlash.

Tooth sections are sampled from exported BReps at <=0.02 mm along each edge. This is a
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
from gears import AXIS_L,AXIS_R,IDLER_SOURCE

ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'output'
P=json.loads((ROOT/'parameters.json').read_text())
design=P['gear_design'];module=design['module_mm'];counts={17:20,7:19,11:19,16:20}
files={17:'M02_drive_gear_horn_adapter',16:'M05_right_gear_involute',7:'M06_small_gear_involute_PRINT_2',11:'M06_small_gear_involute_PRINT_2'}
shapes={i:cq.Shape.importBrep(str(OUT/'brep'/f'{name}.brep')) for i,name in files.items()}
source_centers={17:AXIS_L,16:AXIS_R,7:IDLER_SOURCE,11:IDLER_SOURCE}
centers={i:c.copy() for i,c in source_centers.items()}
coords={};bands={};tips={i:module*(n+2)/2 for i,n in counts.items()}
for i in [17,7,11,16]:
    face=cq.Face.makePlane(300,300,cq.Vector(0,19.8,0),cq.Vector(0,1,0))
    op=BRepAlgoAPI_Section(shapes[i].wrapped,face.wrapped);op.Build();samples=[]
    for edge in cq.Shape.cast(op.Shape()).Edges():
        pts,_=edge.sample(max(2,math.ceil(edge.Length()/.02)))
        points=np.array([[p.x,p.z] for p in pts])
        if edge.IsClosed():points=np.vstack([points,points[0]])
        samples.append(points)
    # Section curves can meet within OCC tolerance but differ in their last
    # floating-point digits. Snap only endpoints within 0.00002 mm, and explicitly
    # close periodic edges (CadQuery sampling omits their repeated end point).
    nodes=[];lines=[]
    for points in samples:
        for k in [0,-1]:
            match=next((q for q in nodes if np.linalg.norm(q-points[k])<2e-5),None)
            if match is None:nodes.append(points[k].copy())
            else:points[k]=match
        lines.append(LineString(points))
    poly=max(polygonize(unary_union(lines)),key=lambda p:p.area)
    assert poly.area>80,f'Incomplete tooth section: {i}'
    poly=poly.intersection(Point(centers[i]).buffer(tips[i]+.01,quad_segs=256))
    coords[i]=np.asarray(poly.exterior.coords)-centers[i]
    intervals=[]
    for f in shapes[i].Faces():
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
    report={'scope':__doc__,'revision':P['revision'],'tooth_bands_y_mm':bands,'design':design,'samples':[],'pairs':{}}
    all_rows={(17,7):[],(7,11):[],(11,16):[]}
    for t in np.arange(0,36.001,.25):
        angles=nominal(float(t));polys={i:polygon(i,a) for i,a in angles.items()}
        row={'opening_deg':float(t),'pairs':{}}
        for a,b in all_rows:
            free=free_band(polys[a],b,angles[b],False)
            item={'surface_gap_mm':polys[a].distance(polys[b]),'overlap_mm2':polys[a].intersection(polys[b]).area,'driven_free_angle_deg':free[1]-free[0]}
            row['pairs'][f'{a}-{b}']=item;all_rows[a,b].append(item)
        report['samples'].append(row)
    for (a,b),rows in all_rows.items():
        ba=bands[a].copy();bb=bands[b].copy()
        overlap=max(0,min(ba[1],bb[1])-max(ba[0],bb[0]))
        alpha=math.radians(design['pressure_angle_deg']);ra=tips[a];rb=tips[b]
        base_a=module*counts[a]/2*math.cos(alpha);base_b=module*counts[b]/2*math.cos(alpha)
        distance=float(np.linalg.norm(centers[a]-centers[b]))
        contact_ratio=(math.sqrt(ra*ra-base_a*base_a)+math.sqrt(rb*rb-base_b*base_b)-distance*math.sin(alpha))/(math.pi*module*math.cos(alpha))
        report['pairs'][f'{a}-{b}']={'center_distance_mm':float(np.linalg.norm(centers[a]-centers[b])),
            'radial_tip_circle_overlap_mm':float(tips[a]+tips[b]-np.linalg.norm(centers[a]-centers[b])),
            'axial_tooth_overlap_mm':overlap,'theoretical_transverse_contact_ratio':contact_ratio,
            'surface_gap_range_mm':[min(r['surface_gap_mm'] for r in rows),max(r['surface_gap_mm'] for r in rows)],
            'driven_free_angle_range_deg':[min(r['driven_free_angle_deg'] for r in rows),max(r['driven_free_angle_deg'] for r in rows)]}
    # Serial rigid contact limits: lower/upper on successive external meshes.
    chain=[]
    for t in np.arange(0,36.001,.5):
        nom=nominal(float(t));ends=[];contact_poses=[]
        for side in [-1,1]:
            angles={17:nom[17]}
            for n,(a,b) in enumerate([(17,7),(7,11),(11,16)]):
                lower,upper=free_band(polygon(a,angles[a]),b,nom[b])
                angles[b]=lower if side*(-1)**n<0 else upper
            ends.append(angles[16])
            contact_poses.append({'direction':'opening' if side<0 else 'closing','gear_angles_2d':angles})
        chain.append({'input_opening_deg':float(t),'right_gear_contact_angle_limits_deg':ends,'right_gear_free_angle_deg':abs(ends[1]-ends[0]),'contact_poses':contact_poses})
    report['chain_samples']=chain
    report['chain_free_angle_range_deg']=[min(x['right_gear_free_angle_deg'] for x in chain),max(x['right_gear_free_angle_deg'] for x in chain)]
    baseline=json.loads((ROOT/'reference/R1_gear_engagement.json').read_text())
    report['baseline_R1_chain_free_angle_range_deg']=baseline['chain_free_angle_range_deg']
    report['target_passed']=bool(report['chain_free_angle_range_deg'][1]<=design['output_backlash_target_deg'])
    assert report['target_passed'],report['chain_free_angle_range_deg']
    assert all(v['axial_tooth_overlap_mm']>=design['minimum_axial_overlap_mm']-1e-5 for v in report['pairs'].values())
    assert all(v['theoretical_transverse_contact_ratio']>1.2 for v in report['pairs'].values())
    assert all(v['overlap_mm2']<1e-7 for row in report['samples'] for v in row['pairs'].values())
    (OUT/'validation').mkdir(parents=True,exist_ok=True)
    (OUT/'validation/gear_engagement.json').write_text(json.dumps(report,indent=2))
    (OUT/'validation/tooth_profiles.json').write_text(json.dumps({str(i):v.tolist() for i,v in coords.items()}))
    print(json.dumps({'pairs':report['pairs'],'chain_free_angle_range_deg':report['chain_free_angle_range_deg']},indent=2),flush=True)

if __name__=='__main__':main()
