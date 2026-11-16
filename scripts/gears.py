"""R2 spur-gear geometry and layout. Units mm and degrees in the source XZ plane.

Working flanks are involutes of a common base pitch. Below the base circle,
radial relief and a small root fillet connect to the dedendum circle. These are
printed gears, not a claim of a particular manufacturing accuracy grade.
"""
import math
import numpy as np
import cadquery as cq

AXIS_L=np.array([-18.5960823864,-12.8816877857])
AXIS_R=np.array([11.4856,-13.7218])
IDLER_SOURCE=np.array([-10.808355,-1.9993])

def layout(module=.75,big_teeth=20,small_teeth=19):
    delta=AXIS_R-AXIS_L;distance=np.linalg.norm(delta);u=delta/distance;n=np.array([-u[1],u[0]])
    bs=module*(big_teeth+small_teeth)/2;ss=module*small_teeth
    h=math.sqrt(bs*bs-((distance-ss)/2)**2);mid=(AXIS_L+AXIS_R)/2
    centers=[AXIS_L,mid+n*h-u*ss/2,mid+n*h+u*ss/2,AXIS_R]
    counts=[big_teeth,small_teeth,small_teeth,big_teeth];phases=[0.]
    for i in range(3):
        a=math.atan2(*(centers[i+1]-centers[i])[::-1]);za,zb=counts[i:i+2]
        phase=a+math.pi+za/zb*(a-math.radians(phases[-1]))-math.pi/zb
        pitch=2*math.pi/zb;phase=(phase+pitch/2)%pitch-pitch/2
        phases.append(math.degrees(phase))
    return centers,phases

def involute_face(teeth,module,pressure_deg,tooth_thinning,root_fillet=.10,center=(0.,0.),y=0.,phase_deg=0.):
    rp=module*teeth/2;alpha=math.radians(pressure_deg);rb=rp*math.cos(alpha)
    ra=rp+module;rf=rp-1.25*module
    half=math.pi/(2*teeth)-tooth_thinning/(2*rp)
    inv_alpha=math.tan(alpha)-alpha;base_half=half+inv_alpha
    tmax=math.sqrt((ra/rb)**2-1);pitch=2*math.pi/teeth
    assert half>0 and rf<rb and root_fillet>=0
    def v(r,a):return cq.Vector(center[0]+r*math.cos(a),y,center[1]+r*math.sin(a))
    def arc(r,a,b):return cq.Edge.makeThreePointArc(v(r,a),v(r,(a+b)/2),v(r,b))
    edges=[]
    for k in range(teeth):
        c=math.radians(phase_deg)+k*pitch
        ts=np.linspace(0,tmax,19)
        angles=base_half-(ts-np.arctan(ts));radii=rb*np.sqrt(1+ts*ts)
        left=[v(float(r),c-float(a)) for r,a in zip(radii,angles)]
        right=[v(float(r),c+float(a)) for r,a in zip(radii,angles)]
        edges.append(cq.Edge.makeLine(v(rf,c-base_half),left[0]))
        edges.append(cq.Edge.makeSpline(left))
        edges.append(arc(ra,c-float(angles[-1]),c+float(angles[-1])))
        edges.append(cq.Edge.makeSpline(list(reversed(right))))
        edges.append(cq.Edge.makeLine(right[0],v(rf,c+base_half)))
        edges.append(arc(rf,c+base_half,c+pitch-base_half))
    face=cq.Face.makeFromWires(cq.Wire.assembleEdges(edges))
    if root_fillet:
        roots=[vtx for vtx in face.Vertices() if abs(math.hypot(vtx.X-center[0],vtx.Z-center[1])-rf)<1e-6]
        face=face.fillet2D(root_fillet,roots)
    assert face.isValid()
    return face

def gear_solid(teeth,module,pressure_deg,tooth_thinning,center,y,thickness,phase_deg=0.,root_fillet=.10):
    face=involute_face(teeth,module,pressure_deg,tooth_thinning,root_fillet,center,y,phase_deg)
    shape=cq.Solid.extrudeLinear(face.outerWire(),face.innerWires(),cq.Vector(0,thickness,0))
    assert shape.isValid() and len(shape.Solids())==1
    return shape

def replace_rim(original,center,y0,thickness,old_tip_radius,teeth,settings,phase_deg=0.,arm_tip=None,tooth_thinning=None):
    """Retain original center features and the connecting arm; replace tooth band."""
    def cyl(r,y,h):return cq.Solid.makeCylinder(r,h,cq.Vector(center[0],y,center[1]),cq.Vector(0,1,0))
    # Keep the original counterbores and central interfaces inside radius 4.2.
    ring_cut=cyl(old_tip_radius+.15,y0-.0001,thickness+.0002).cut(cyl(4.2,y0-.001,thickness+.002))
    if arm_tip is not None:
        u=np.asarray(arm_tip)-np.asarray(center);u=u/np.linalg.norm(u);n=np.array([-u[1],u[0]])
        # The original 5 mm arm remains integral. This nonworking sector is
        # opposite the idler contact region throughout the gripper's stroke.
        points=[np.asarray(center)+u*t+n*w for t,w in [(0,-2.51),(65,-2.51),(65,2.51),(0,2.51)]]
        wire=cq.Wire.makePolygon([cq.Vector(p[0],y0-1,p[1]) for p in points],close=True)
        keeper=cq.Solid.extrudeLinear(wire,[],cq.Vector(0,thickness+2,0))
        ring_cut=ring_cut.cut(keeper)
    retained=original.cut(ring_cut)
    thinning=settings['tooth_thickness_reduction_mm'] if tooth_thinning is None else tooth_thinning
    teeth_shape=gear_solid(teeth,settings['module_mm'],settings['pressure_angle_deg'],thinning,center,y0,thickness,phase_deg,settings['root_fillet_mm'])
    teeth_shape=teeth_shape.cut(cyl(4.1,y0-.001,thickness+.002))
    result=retained.fuse(teeth_shape).clean()
    assert result.isValid() and len(result.Solids())==1,'Gear must remain a connected valid solid'
    return result
