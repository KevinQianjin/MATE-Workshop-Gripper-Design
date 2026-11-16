"""Draw measured R2 tooth sections and the R1/R2 gear-chain comparison."""
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
 text(ax,c[i][0],c[i][1]+1.3,{17:'驅動',7:'A',11:'B',16:'輸出'}[i],ha='center',va='center',fontsize=10)
for a,b in [(17,7),(7,11),(11,16)]:
 ax.plot([c[a][0],c[b][0]],[c[a][1],c[b][1]],'--',color='#52616a',lw=.8)
ax.set_aspect('equal');ax.set_xlabel('mm');ax.set_ylabel('mm');label(ax,'① R2 匹配漸開線齒圈：原輪轂與連桿保留')
ax=axes[0,1];a,b=nearest_points(polys[17],polys[7]);mid=np.array([(a.x+b.x)/2,(a.y+b.y)/2])
for i in [17,7]:
 x,y=polys[i].exterior.xy;ax.fill(x,y,color=colors[i],alpha=.85);ax.plot(x,y,color='#24444f',lw=.8)
ax.plot([a.x,b.x],[a.y,b.y],color='#b83f39',lw=2)
ax.set_xlim(mid[0]-1.2,mid[0]+1.2);ax.set_ylim(mid[1]-1.1,mid[1]+1.1);ax.set_aspect('equal')
gap=a.distance(b);text(ax,mid[0]-1.05,mid[1]+.82,f'本位置最近齒面距離 {gap:.3f} mm',fontsize=10,color='#a7322d')
ax.set_xlabel('mm');label(ax,'② 名義中位的最近齒面距離：約 0.056 mm')
ax=axes[1,0]
ax.set_axis_off();label(ax,'③ 設計與更換範圍')
items=[('模數 / 壓力角','0.75 mm / 20°'),('齒數','20 / 19 / 19 / 20'),('中心距','14.625 / 14.250 / 14.625 mm'),('每對名義切向齒隙','0.12 mm（B12）'),('工作齒寬重疊','2.0 / 3.0 / 2.0 mm'),('主要更換件','M01、M02、M05、M06 ×2'),('主要列印件總數','14 件，維持 R1 配置'),('齒隙試裝版本','B08 / B12 / B16')]
for j,(key,value) in enumerate(items):
 y=.92-j*.105;text(ax,.02,y,key,transform=ax.transAxes,fontsize=12,color='#536777');text(ax,.40,y,value,transform=ax.transAxes,fontsize=12,color='#173447')
ax=axes[1,1];t=[x['input_opening_deg'] for x in r['chain_samples']];v=[x['right_gear_free_angle_deg'] for x in r['chain_samples']]
tb=[x['input_opening_deg'] for x in baseline['chain_samples']];vb=[x['right_gear_free_angle_deg'] for x in baseline['chain_samples']]
ax.plot(tb,vb,color='#b83f39',lw=2,label='R1');ax.plot(t,v,color='#258a68',lw=2.5,label='R2')
ax.axhline(3,color='#536777',ls='--',lw=1);text(ax,24,3.5,'模型目標 3°',fontsize=10,color='#536777')
ax.fill_between(t,0,v,color='#258a68',alpha=.12);ax.set_ylim(0,14);ax.grid(alpha=.18);ax.legend(loc='upper right')
ax.set_xlabel('輸入開合相對角度（°）',fontproperties=F);ax.set_ylabel('輸出端幾何空行程（°）',fontproperties=F)
label(ax,f'④ 齒輪鏈回程：R2 約 {max(v):.2f}°，R1 約 8.2–11.6°')
fig.suptitle('R2 匹配齒輪與回程檢查',fontproperties=F,fontsize=22,x=.055,ha='left',color='#173447')
fig.text(.055,.025,'數值為匯出 CAD 的剛體估算；未計入列印誤差、軸孔鬆動、舵機回程、彈性變形或負載。實際效果需先試印驗證。',fontproperties=F,fontsize=11,color='#536777')
fig.subplots_adjust(left=.08,right=.97,top=.9,bottom=.1,wspace=.26,hspace=.38)
(OUT/'preview').mkdir(parents=True,exist_ok=True)
fig.savefig(OUT/'preview/gear_review_R2.png',dpi=170);fig.savefig(OUT/'preview/gear_review_R2.pdf');plt.close(fig)
print('GEAR_REVIEW_DRAWN')
