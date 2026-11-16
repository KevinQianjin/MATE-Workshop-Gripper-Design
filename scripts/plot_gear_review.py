"""Draw measured R2 tooth sections and the R1/R2 gear-chain comparison."""
import os,json,math
os.environ.setdefault('MPLCONFIGDIR','/tmp/ipx896hv-matplotlib')
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties
from shapely.geometry import Polygon
from shapely.ops import nearest_points
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'output'
F=FontProperties(family='DejaVu Sans')
plt.rcParams['pdf.fonttype']=42
plt.rcParams['axes.unicode_minus']=False
p=json.loads((ROOT/'parameters.json').read_text());r=json.loads((OUT/'validation/gear_engagement.json').read_text())
baseline=json.loads((ROOT/'reference/R1_gear_engagement.json').read_text())
c={17:np.array([-18.5960823864,-12.8816877857]),16:np.array([11.4856,-13.7218]),7:np.array(p['gear_alignment']['idler_left_xz']),11:np.array(p['gear_alignment']['idler_right_xz'])}
ph=p['gear_alignment']['phase_degrees_2d'];angles={17:0,7:ph['idler_left'],11:ph['idler_right'],16:ph['right_gear']}
raw=json.loads((OUT/'validation/tooth_profiles.json').read_text());polys={}
for i,a in angles.items():
 t=math.radians(a);rot=np.array([[math.cos(t),-math.sin(t)],[math.sin(t),math.cos(t)]])
 polys[i]=Polygon(np.asarray(raw[str(i)])@rot.T+c[i])
colors={17:'#e99424',7:'#3099aa',11:'#3099aa',16:'#8394a3'}
fig,axes=plt.subplots(2,2,figsize=(14,10),facecolor='#f6f8fa')
def label(ax,text):ax.set_title(text,fontproperties=F,fontsize=14,pad=12,loc='left',color='#173447')
def text(ax,x,y,s,**kw):ax.text(x,y,s,fontproperties=F,**kw)
for ax in axes.flat:
 ax.set_facecolor('white');ax.spines[['top','right']].set_visible(False)
ax=axes[0,0]
for i in [17,7,11,16]:
 x,y=polys[i].exterior.xy;ax.fill(x,y,color=colors[i],alpha=.85);ax.plot(x,y,color='#24444f',lw=.6)
 ax.plot(*c[i],'+',color='black',ms=6)
 text(ax,c[i][0],c[i][1]+1.3,{17:'Drive',7:'A',11:'B',16:'Output'}[i],ha='center',va='center',fontsize=10)
for a,b in [(17,7),(7,11),(11,16)]:
 ax.plot([c[a][0],c[b][0]],[c[a][1],c[b][1]],'--',color='#52616a',lw=.8)
ax.set_aspect('equal');ax.set_xlabel('mm');ax.set_ylabel('mm');label(ax,'1  Matched rims; original hubs and links retained')
ax=axes[0,1];a,b=nearest_points(polys[17],polys[7]);mid=np.array([(a.x+b.x)/2,(a.y+b.y)/2])
for i in [17,7]:
 x,y=polys[i].exterior.xy;ax.fill(x,y,color=colors[i],alpha=.85);ax.plot(x,y,color='#24444f',lw=.8)
ax.plot([a.x,b.x],[a.y,b.y],color='#b83f39',lw=2)
ax.set_xlim(mid[0]-1.2,mid[0]+1.2);ax.set_ylim(mid[1]-1.1,mid[1]+1.1);ax.set_aspect('equal')
gap=a.distance(b);text(ax,mid[0]-1.05,mid[1]+.82,f'Nearest flank gap here: {gap:.3f} mm',fontsize=10,color='#a7322d')
ax.set_xlabel('mm');label(ax,'2  Flank gap at the nominal centered pose')
ax=axes[1,0]
ax.set_axis_off();label(ax,'3  Design and replacement scope')
items=[('Module / pressure angle','0.75 mm / 20°'),('Tooth counts','20 / 19 / 19 / 20'),('Center distances','14.625 / 14.250 / 14.625 mm'),('Nominal backlash / mesh','0.12 mm (B12)'),('Axial tooth overlap','2.0 / 3.0 / 2.0 mm'),('Main replacement parts','M01, M02, M05, M06 x2'),('Main printed pieces','14; same count as R1'),('Trial clearance sets','B08 / B12 / B16')]
for j,(key,value) in enumerate(items):
 y=.92-j*.105;text(ax,.02,y,key,transform=ax.transAxes,fontsize=11,color='#536777');text(ax,.48,y,value,transform=ax.transAxes,fontsize=11,color='#173447')
ax=axes[1,1];t=[x['input_opening_deg'] for x in r['chain_samples']];v=[x['right_gear_free_angle_deg'] for x in r['chain_samples']]
tb=[x['input_opening_deg'] for x in baseline['chain_samples']];vb=[x['right_gear_free_angle_deg'] for x in baseline['chain_samples']]
ax.plot(tb,vb,color='#b83f39',lw=2,label='R1');ax.plot(t,v,color='#258a68',lw=2.5,label='R2')
ax.axhline(3,color='#536777',ls='--',lw=1);text(ax,24,3.5,'CAD target: 3°',fontsize=10,color='#536777')
ax.fill_between(t,0,v,color='#258a68',alpha=.12);ax.set_ylim(0,14);ax.grid(alpha=.18);ax.legend(loc='upper right')
ax.set_xlabel('Relative input opening angle (°)',fontproperties=F);ax.set_ylabel('Output reversal free play (°)',fontproperties=F)
label(ax,f'4  Backlash: R2 {max(v):.2f}°; R1 8.2–11.6°')
fig.suptitle('R2 matched gears and backlash review',fontproperties=F,fontsize=22,x=.055,ha='left',color='#173447')
fig.text(.055,.025,'Rigid CAD estimates exclude print error, pivot clearance, servo backlash, deflection, and load. Verify with trial prints.',fontproperties=F,fontsize=11,color='#536777')
fig.subplots_adjust(left=.08,right=.97,top=.9,bottom=.1,wspace=.26,hspace=.38)
(OUT/'preview').mkdir(parents=True,exist_ok=True)
fig.savefig(OUT/'preview/gear_review_R2.png',dpi=170);fig.savefig(OUT/'preview/gear_review_R2.pdf');plt.close(fig)
print('GEAR_REVIEW_DRAWN')
