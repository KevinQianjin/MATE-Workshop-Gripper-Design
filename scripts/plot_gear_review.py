"""Draw measured tooth sections and before/after axial engagement."""
import os,json,math
os.environ.setdefault('MPLCONFIGDIR','/tmp/ipx896hv-matplotlib')
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from matplotlib.font_manager import FontProperties
from shapely.geometry import Polygon
from shapely.ops import nearest_points
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'output'
F=FontProperties(fname='/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc')
plt.rcParams['axes.unicode_minus']=False
p=json.loads((ROOT/'parameters.json').read_text());r=json.loads((OUT/'validation/gear_engagement.json').read_text())
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
 text(ax,c[i][0],c[i][1],{17:'驅動',7:'A',11:'B',16:'輸出'}[i],ha='center',va='center',fontsize=10)
for a,b in [(17,7),(7,11),(11,16)]:
 ax.plot([c[a][0],c[b][0]],[c[a][1],c[b][1]],'--',color='#52616a',lw=.8)
ax.set_aspect('equal');ax.set_xlabel('mm');ax.set_ylabel('mm');label(ax,'① 齒圈截面：仍有咬入，沒有完全分離')
ax=axes[0,1];a,b=nearest_points(polys[17],polys[7]);mid=np.array([(a.x+b.x)/2,(a.y+b.y)/2])
for i in [17,7]:
 x,y=polys[i].exterior.xy;ax.fill(x,y,color=colors[i],alpha=.85);ax.plot(x,y,color='#24444f',lw=.8)
ax.plot([a.x,b.x],[a.y,b.y],color='#b83f39',lw=2)
ax.set_xlim(mid[0]-1.2,mid[0]+1.2);ax.set_ylim(mid[1]-1.1,mid[1]+1.1);ax.set_aspect('equal')
gap=a.distance(b);text(ax,mid[0]-1.05,mid[1]+.82,f'本位置最近齒面距離 {gap:.3f} mm',fontsize=10,color='#a7322d')
ax.set_xlabel('mm');label(ax,'② 間隙放大：全行程抽樣約 0.12–0.25 mm')
ax=axes[1,0]
for y,low,high,color,s in [(3,17.026945,19.026945,colors[17],'R0 驅動'),(2.25,18.526945,21.526945,colors[7],'相鄰小齒輪'),(.8,18.526945,20.526945,colors[17],'R1 驅動'),(.05,18.526945,21.526945,colors[7],'相鄰小齒輪')]:
 ax.add_patch(Rectangle((low,y),high-low,.5,color=color));text(ax,16.8,y+.25,s,ha='right',va='center',fontsize=10)
for low,high,y,s in [(18.526945,19.026945,2.0,'原重疊 0.5 mm'),(18.526945,20.526945,-.2,'修正重疊 2.0 mm')]:
 ax.annotate('',(low,y),(high,y),arrowprops={'arrowstyle':'|-|','color':'#b83f39'})
 text(ax,(low+high)/2,y-.32,s,ha='center',fontsize=10,color='#b83f39')
ax.set_xlim(16.7,22);ax.set_ylim(-.8,3.8);ax.set_yticks([]);ax.spines[['left','top','right']].set_visible(False)
ax.set_xlabel('CAD 軸向位置（mm）',fontproperties=F);label(ax,'③ 高度問題：驅動齒輪抬高 1.5 mm')
ax=axes[1,1];t=[x['input_opening_deg'] for x in r['chain_samples']];v=[x['right_gear_free_angle_deg'] for x in r['chain_samples']]
ax.plot(t,v,color='#b83f39',lw=2);ax.fill_between(t,0,v,color='#b83f39',alpha=.12);ax.set_ylim(0,14);ax.grid(alpha=.18)
ax.set_xlabel('輸入開合相對角度（°）',fontproperties=F);ax.set_ylabel('輸出端幾何空行程（°）',fontproperties=F)
label(ax,'④ 三對間隙累積：約 8.2–11.6° 回程空隙')
fig.suptitle('齒輪檢查與 R1 高度修正',fontproperties=F,fontsize=22,x=.055,ha='left',color='#173447')
fig.text(.055,.025,'截面／剛體接觸估算；未計入列印誤差、軸孔鬆動、彈性變形或負載。R1 保留原齒形，回程空隙仍需實物確認。',fontproperties=F,fontsize=11,color='#536777')
fig.subplots_adjust(left=.08,right=.97,top=.9,bottom=.1,wspace=.26,hspace=.38)
(OUT/'preview').mkdir(parents=True,exist_ok=True)
fig.savefig(OUT/'preview/gear_review_R1.png',dpi=170);fig.savefig(OUT/'preview/gear_review_R1.pdf');plt.close(fig)
print('GEAR_REVIEW_DRAWN')
