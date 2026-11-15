import os
os.environ.setdefault('MPLCONFIGDIR','/tmp/ipx896hv-matplotlib')
import json, math, struct, itertools
from pathlib import Path
import numpy as np
import cadquery as cq
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'output'
parts={p.stem.removeprefix('assembly_'):cq.Shape.importBrep(str(p)) for p in (OUT/'brep').glob('assembly_*.brep')}
P=json.loads((ROOT/'parameters.json').read_text())

def render(parts,filename,azimuth=45):
    fig=plt.figure(figsize=(12,9),facecolor='#f4f6f8');ax=fig.add_subplot()
    ax.set_facecolor('#f4f6f8')
    light=np.array([-.2,.4,1]);light/=np.linalg.norm(light)
    az=math.radians(azimuth);el=math.radians(25)
    view=np.array([math.cos(az)*math.cos(el),math.sin(az)*math.cos(el),math.sin(el)])
    all_v=[];all_tri=[];all_colors=[]
    for name,s in parts.items():
        vv,ff=s.tessellate(.18,.22);v=np.array([x.toTuple() for x in vv]);f=np.array(ff);tri=v[f];all_v.append(v)
        normals=np.cross(tri[:,1]-tri[:,0],tri[:,2]-tri[:,0]);normals/=np.maximum(np.linalg.norm(normals,axis=1)[:,None],1e-12)
        shade=.45+.55*np.maximum(normals@light,0)
        color=np.array([.56,.62,.68])
        if name in ['base','base_wall','waist']:color=np.array([.28,.37,.46])
        if name in ['drive_gear','yaw_coupler','bridge']:color=np.array([.98,.59,.16])
        if name=='palm':color=np.array([.13,.58,.68])
        if 'claw' in name:color=np.array([.25,.66,.44])
        if name.startswith('REF_'):color=np.array([.24,.26,.29])
        if 'metal_horn' in name:color=np.array([.74,.76,.80])
        all_tri.append(tri);all_colors.append(np.clip(shade[:,None]*color,0,1))
    # A pixel depth buffer avoids painter-order artifacts from long CAD triangles.
    tri=np.concatenate(all_tri);colors=np.concatenate(all_colors)
    right=np.array([-math.sin(az),math.cos(az),0]);up=np.cross(view,right)
    projected=tri@np.stack([right,up,view],axis=1)
    flat=projected.reshape(-1,3);mn=flat.min(0);mx=flat.max(0)
    width,height=1300,1050
    scale=min((width-50)/(mx[0]-mn[0]),(height-50)/(mx[1]-mn[1]))
    projected[:,:,0]=(projected[:,:,0]-(mn[0]+mx[0])/2)*scale+width/2
    projected[:,:,1]=height/2-(projected[:,:,1]-(mn[1]+mx[1])/2)*scale
    pixels=np.full((height,width,3),np.array([244,246,248])/255.)
    depth=np.full((height,width),-np.inf)
    for t,color in zip(projected,colors):
        x0=max(0,int(np.floor(t[:,0].min())));x1=min(width-1,int(np.ceil(t[:,0].max())))
        y0=max(0,int(np.floor(t[:,1].min())));y1=min(height-1,int(np.ceil(t[:,1].max())))
        a,b,c=t;den=(b[1]-c[1])*(a[0]-c[0])+(c[0]-b[0])*(a[1]-c[1])
        if abs(den)<1e-9 or x0>x1 or y0>y1:continue
        yy,xx=np.mgrid[y0:y1+1,x0:x1+1];xx=xx+.5;yy=yy+.5
        w0=((b[1]-c[1])*(xx-c[0])+(c[0]-b[0])*(yy-c[1]))/den
        w1=((c[1]-a[1])*(xx-c[0])+(a[0]-c[0])*(yy-c[1]))/den
        w2=1-w0-w1;z=w0*a[2]+w1*b[2]+w2*c[2]
        zbuf=depth[y0:y1+1,x0:x1+1]
        mask=(w0>=-1e-8)&(w1>=-1e-8)&(w2>=-1e-8)&(z>zbuf)
        zbuf[mask]=z[mask];pixels[y0:y1+1,x0:x1+1][mask]=color
    ax.imshow(pixels);ax.set_axis_off()
    fig.suptitle('IPX896HV | open / close + yaw',x=.07,y=.95,ha='left',fontsize=23,fontweight='bold',color='#183347')
    fig.text(.07,.90,'R1 fit-check prototype  |  original gripper linkage retained',fontsize=13,color='#536777')
    fig.text(.07,.06,'Blue: adapted original parts    Orange: drive interfaces / bridge    Green: original jaws',fontsize=11,color='#536777')
    fig.text(.07,.035,'Servo and horn envelopes shown. Screws / washers omitted. Dimensions and load require physical verification.',fontsize=10,color='#536777')
    fig.subplots_adjust(left=0,right=1,bottom=.07,top=.88)
    fig.savefig(OUT/'preview'/filename,dpi=170);plt.close(fig)

def bbox_overlap(a,b):
    a=a.BoundingBox();b=b.BoundingBox()
    return all(min(hi1,hi2)-max(lo1,lo2)>1e-5 for lo1,hi1,lo2,hi2 in [(a.xmin,a.xmax,b.xmin,b.xmax),(a.ymin,a.ymax,b.ymin,b.ymax),(a.zmin,a.zmax,b.zmin,b.zmax)])

def pair_volumes(parts):
    overlaps=[]
    for (na,a),(nb,b) in itertools.combinations(parts.items(),2):
        if not bbox_overlap(a,b):continue
        v=a.intersect(b).Volume()
        if v>.01:
            entry={'a':na,'b':nb,'intersection_mm3':round(v,5)};overlaps.append(entry);print(entry,flush=True)
    return overlaps

def stl_check(path):
    data=path.read_bytes();n=struct.unpack_from('<I',data,80)[0]
    assert len(data)==84+n*50,path.name
    d=np.frombuffer(data,dtype=np.dtype([('n','<f4',(3,)),('v','<f4',(3,3)),('a','<u2')]),offset=84,count=n)
    tri=d['v'].astype(float)
    verts,inv=np.unique(np.round(tri.reshape(-1,3),5),axis=0,return_inverse=True);f=inv.reshape(-1,3)
    edges=np.sort(np.concatenate([f[:,[0,1]],f[:,[1,2]],f[:,[2,0]]]),axis=1)
    _,counts=np.unique(edges,axis=0,return_counts=True)
    volume=np.einsum('ij,ij->i',tri[:,0],np.cross(tri[:,1],tri[:,2])).sum()/6
    return {'triangles':n,'finite':bool(np.isfinite(tri).all()),'boundary_edges':int((counts==1).sum()),'nonmanifold_edges':int((counts>2).sum()),'signed_volume_mm3':round(float(volume),3),'z_min_mm':round(float(tri[:,:,2].min()),5)}

if __name__=='__main__':
    report={'static_intersections':pair_volumes(parts),'stl':{}}
    for path in list((OUT/'stl').glob('*.stl'))+list((OUT/'fit_checks').glob('*.stl')):
        report['stl'][path.name]=stl_check(path)
    (OUT/'validation/static_and_mesh.json').write_text(json.dumps(report,indent=2))
    render(parts,'assembly_front.png',45)
    render(parts,'assembly_rear.png',225)
    print('DONE',flush=True)
