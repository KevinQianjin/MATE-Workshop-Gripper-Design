"""Check final exchange files, mesh orientation, and retained upstream geometry."""
import json, hashlib, struct
from pathlib import Path
import numpy as np
import cadquery as cq

ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'output'
report={'upstream_files':{},'step_roundtrip':{},'stl_orientation':{},'retained_geometry':{}}
manifest=json.loads((ROOT/'source_manifest.json').read_text())
by_path={e['path']:e for e in manifest['tree'] if e['type']=='blob'}
for p in sorted((ROOT/'upstream').rglob('*')):
    if not p.is_file():continue
    rel=p.relative_to(ROOT/'upstream').as_posix();data=p.read_bytes()
    actual=hashlib.sha1(f'blob {len(data)}\0'.encode()+data).hexdigest()
    assert actual==by_path[rel]['sha'],rel
    report['upstream_files'][rel]={'git_blob_sha':actual,'matched':True}
inventory=json.loads((OUT/'validation/build_inventory.json').read_text())
for p in sorted((OUT/'step').glob('*.step'))+sorted((OUT/'fit_checks').glob('*.step'))+[OUT/'IPX896HV_2DOF_assembly.step']:
    solids=cq.importers.importStep(str(p)).solids().vals()
    expected=18 if 'assembly' in p.stem else 1
    assert len(solids)==expected and all(s.isValid() for s in solids),p.name
    volume=sum(s.Volume() for s in solids)
    if p.stem in inventory:assert abs(volume-inventory[p.stem]['volume_mm3'])<.001,p.name
    report['step_roundtrip'][p.name]={'valid_solids':len(solids),'volume_mm3':volume}
def read_stl(path):
    data=path.read_bytes();n=struct.unpack_from('<I',data,80)[0]
    d=np.frombuffer(data,dtype=np.dtype([('n','<f4',(3,)),('v','<f4',(3,3)),('a','<u2')]),offset=84,count=n)
    return d['v'].astype(float)
for p in sorted((OUT/'stl').glob('*.stl'))+sorted((OUT/'fit_checks').glob('*.stl')):
    v=read_stl(p)
    area=np.linalg.norm(np.cross(v[:,1]-v[:,0],v[:,2]-v[:,0]),axis=1)/2
    assert np.isfinite(v).all() and area.min()>1e-10,p.name
    _,inv=np.unique(np.round(v.reshape(-1,3),5),axis=0,return_inverse=True);f=inv.reshape(-1,3)
    directed=np.concatenate([f[:,[0,1]],f[:,[1,2]],f[:,[2,0]]])
    _,edge_id,counts=np.unique(np.sort(directed,axis=1),axis=0,return_inverse=True,return_counts=True)
    signs=np.where(directed[:,0]<directed[:,1],1,-1)
    winding=np.bincount(edge_id,weights=signs)
    assert np.all(counts==2) and np.all(winding==0),p.name
    report['stl_orientation'][p.name]={'closed_oriented_manifold':True,'minimum_triangle_area_mm2':float(area.min())}
    if p.stem.startswith('U'):
        original=read_stl(ROOT/'upstream/cad/STL'/inventory[p.stem]['source'])
        a=np.linalg.norm(v-np.roll(v,1,axis=1),axis=2)
        b=np.linalg.norm(original-np.roll(original,1,axis=1),axis=2)
        delta=float(np.abs(a-b).max())
        assert original.shape==v.shape and delta<.0001,p.name
        report['retained_geometry'][p.name]={'triangles_unchanged':len(v),'max_edge_length_difference_mm':delta}
(OUT/'validation/delivery.json').write_text(json.dumps(report,indent=2))
print(json.dumps({'upstream_matches':len(report['upstream_files']),'step_roundtrips':len(report['step_roundtrip']),'oriented_stls':len(report['stl_orientation']),'retained_meshes':len(report['retained_geometry'])}))
