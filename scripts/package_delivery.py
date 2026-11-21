"""Package reviewed source and deliverables, excluding internal working files."""
import argparse, hashlib, json, shutil, zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--output-dir',type=Path,default=ROOT/'dist',help='Delivery directory (default: <repo>/dist)')
args=parser.parse_args()
DEST=args.output_dir.expanduser().resolve();DEST.mkdir(parents=True,exist_ok=True)
report=json.loads((ROOT/'output/validation/static_and_mesh.json').read_text())
motion=json.loads((ROOT/'output/validation/motion.json').read_text())
delivery=json.loads((ROOT/'output/validation/delivery.json').read_text())
screw=json.loads((ROOT/'output/validation/screw_access.json').read_text())
assert not report['static_intersections']
assert all(not x['intersections'] for x in motion['opening_samples']+motion['contact_limit_samples']+motion['yaw_samples'])
assert len(delivery['stl_orientation'])==23 and len(delivery['retained_geometry'])==4
assert len(screw['checks'])==4
gears=json.loads((ROOT/'output/validation/gear_engagement.json').read_text())
assert gears['revision']=='R2-matched-gears-fit-check' and gears['target_passed']
assert abs(gears['pairs']['17-7']['axial_tooth_overlap_mm']-2)<1e-5
files=[]
for name in ['README.md','CHANGELOG.md','BOM.csv','parameters.json','requirements.txt','LICENSE','NOTICE.txt','source_manifest.json','.gitignore','.gitattributes']:
    files.append(ROOT/name)
for name in ['docs','firmware','upstream','output','scripts','reference']:
    for p in sorted((ROOT/name).rglob('*')):
        if not p.is_file() or '__pycache__' in p.parts or p.name.startswith('DEBUG_') or p.name=='inspect_source.py':continue
        files.append(p)
checksums=''.join(hashlib.sha256(p.read_bytes()).hexdigest()+'  '+p.relative_to(ROOT).as_posix()+'\n' for p in files)
manifest=ROOT/'DELIVERY_SHA256SUMS.txt';manifest.write_text(checksums);files.append(manifest)
target=DEST/'IPX896HV_2DOF_R2.zip'
with zipfile.ZipFile(target,'w',zipfile.ZIP_DEFLATED,compresslevel=9) as z:
    for p in files:z.write(p,Path('IPX896HV_2DOF_R2')/p.relative_to(ROOT))
with zipfile.ZipFile(target) as z:
    assert z.testzip() is None
    for p in files:
        assert hashlib.sha256(z.read(str(Path('IPX896HV_2DOF_R2')/p.relative_to(ROOT)))).digest()==hashlib.sha256(p.read_bytes()).digest()
for rel,name in [('output/IPX896HV_2DOF_assembly.step','IPX896HV_2DOF_R2.step'),('output/assembly_and_print_guide.pdf','IPX896HV_R2_assembly_and_print_guide.pdf'),('output/preview/assembly_open.png','IPX896HV_2DOF_R2_preview.png'),('output/preview/gear_review_R2.png','IPX896HV_R2_gear_review.png'),('output/preview/gear_review_R2.pdf','IPX896HV_R2_gear_review.pdf')]:
    shutil.copy2(ROOT/rel,DEST/name)
print(json.dumps({'archive':str(target),'files':len(files),'bytes':target.stat().st_size,'sha256':hashlib.sha256(target.read_bytes()).hexdigest()},indent=2))
