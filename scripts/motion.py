"""Reassemble the original four-bar parts with coincident pivot centers.
Only rigid transforms are applied here. Coordinates are the pinned source STEP's XZ plane.
"""
import math
import numpy as np

AXIS_L=np.array([-18.5960823864,-12.8816877857])
AXIS_R=np.array([11.4856,-13.7218])
IDLER_L=np.array([-10.808355,-1.9993])
IDLER_R=np.array([2.9457,-1.9993])

def rot2(v,degrees):
    t=math.radians(degrees);return np.array([[math.cos(t),-math.sin(t)],[math.sin(t),math.cos(t)]])@v
def turn(s,center,degrees_2d):
    return s.rotate((center[0],0,center[1]),(center[0],1,center[1]),-degrees_2d)
def angle(v):return math.degrees(math.atan2(v[1],v[0]))

def solve_side(gr,side,drive_degrees_2d):
    if side=='left':
        axis=AXIS_L;tip=np.array([-17.1922,-50.4052]);base=np.array([-7.9505,-37.0630]);far=np.array([-7.9505,-79.0630]);jaw_far=np.array([-7.8556,-78.2298]);link_id=8;jaw_id=14;y_shift=.3
    else:
        axis=AXIS_R;tip=np.array([11.0595,-51.2696]);base=np.array([2.0495,-37.0630]);far=np.array([1.8648,-79.0626]);jaw_far=np.array([1.3638,-78.9711]);link_id=3;jaw_id=2;y_shift=1.8
    A=axis+rot2(tip-axis,drive_degrees_2d)
    link_len=np.linalg.norm(far-base);jaw_len=np.linalg.norm(jaw_far-tip)
    d=np.linalg.norm(base-A);u=(base-A)/d
    a=(jaw_len**2-link_len**2+d*d)/(2*d);h2=jaw_len**2-a*a
    if h2<0:raise ValueError(f'{side} linkage cannot close at {drive_degrees_2d}')
    n=np.array([-u[1],u[0]])
    B=min([A+a*u+math.sqrt(h2)*n,A+a*u-math.sqrt(h2)*n],key=lambda v:v[1])
    link_angle=angle(B-base)-angle(far-base)
    jaw_angle=angle(B-A)-angle(jaw_far-tip)
    link=turn(gr[link_id],base,link_angle).translate((0,y_shift,0))
    jaw=turn(gr[jaw_id],tip,jaw_angle).translate((A[0]-tip[0],0,A[1]-tip[1]))
    err=abs(np.linalg.norm(B-base)-link_len)+abs(np.linalg.norm(B-A)-jaw_len)
    return link,jaw,float(err)

def posed(gr,drive,p,opening_degrees=0):
    fit=p['gear_alignment'];ph=fit['phase_degrees_2d']
    Lnew=np.array(fit['idler_left_xz']);Rnew=np.array(fit['idler_right_xz'])
    smallL=turn(gr[7],IDLER_L,ph['idler_left']+opening_degrees*20/19).translate((Lnew[0]-IDLER_L[0],0,Lnew[1]-IDLER_L[1]))
    smallR=turn(gr[11],IDLER_R,ph['idler_right']-opening_degrees*20/19).translate((Rnew[0]-IDLER_R[0],0,Rnew[1]-IDLER_R[1]))
    linkL,jawL,eL=solve_side(gr,'left',-opening_degrees)
    right_angle=ph['right_gear']+opening_degrees
    linkR,jawR,eR=solve_side(gr,'right',right_angle)
    jawL=jawL.translate((0,p['gripper'].get('left_jaw_axial_shift',0),0))
    jawR=jawR.translate((0,p['gripper'].get('right_jaw_axial_shift',0),0))
    return {'drive_gear':turn(drive,AXIS_L,-opening_degrees),'right_gear':turn(gr[16],AXIS_R,right_angle),'idler_left':smallL,'idler_right':smallR,'link_left':linkL,'link_right':linkR,'claw_left':jawL,'claw_right':jawR},max(eL,eR)
