"""Create a concise Traditional Chinese PDF guide and derived assembly views."""
import json, math
from pathlib import Path
import cadquery as cq
import fitz
from fontTools.ttLib import TTFont
from fontTools import subset
from motion import posed
from check_and_render import render

ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'output'
P=json.loads((ROOT/'parameters.json').read_text());G=P['gripper'];Y=P['yaw']
parts={p.stem.removeprefix('assembly_'):cq.Shape.importBrep(str(p)) for p in (OUT/'brep').glob('assembly_*.brep')}
gr=cq.importers.importStep(str(ROOT/'upstream/cad/step/assembled-gripper.step')).solids().vals()
drive=cq.Shape.importBrep(str(OUT/'brep/M02_drive_gear_horn_adapter.brep'))
def gf(s):return s.rotate((0,0,0),(1,0,0),90).translate((G['assembly_offset_x'],G['assembly_offset_y']+Y['axis_offset_y'],G['assembly_offset_z']))
moving,_=posed(gr,drive,P,30)
opened={**parts,**{n:gf(s) for n,s in moving.items()}}
render(opened,'assembly_open.png',45)
render(opened,'assembly_open_rear.png',225)

# Three vector views for inspection. These are not tolerance-controlled drawings.
for name,direction in [('top',(0,0,1)),('side',(1,0,0)),('front',(0,1,0))]:
    s=cq.Compound.makeCompound(list(opened.values()))
    svg=cq.exporters.getSVG(s,opts={'width':1000,'height':750,'projectionDir':direction,'showAxes':False,'showHidden':False,'strokeWidth':.5})
    (OUT/'preview'/f'assembly_{name}.svg').write_text(svg)
    a=fitz.open(stream=svg.encode(),filetype='svg');b=fitz.open(stream=a.convert_to_pdf(),filetype='pdf');b[0].get_pixmap().save(str(OUT/'preview'/f'assembly_{name}_drawing.png'))

for name,path,direction in [('servo_fit','fit_checks/F01_servo_ear_fit.step',(0,1,0)),('horn_fit','fit_checks/F02_horn_slot_fit.step',(0,0,1))]:
    s=cq.importers.importStep(str(OUT/path)).val()
    svg=cq.exporters.getSVG(s,opts={'width':600,'height':350,'projectionDir':direction,'showAxes':False,'showHidden':False,'strokeWidth':1})
    a=fitz.open(stream=svg.encode(),filetype='svg');b=fitz.open(stream=a.convert_to_pdf(),filetype='pdf');b[0].get_pixmap().save(str(OUT/'preview'/f'{name}.png'))

report=json.loads((OUT/'validation/static_and_mesh.json').read_text())
motion=json.loads((OUT/'validation/motion.json').read_text())
assert not report['static_intersections'],'Resolve static clashes before generating the guide'
assert all(not x['intersections'] for x in motion['opening_samples']),'Resolve sampled-motion clashes'
assert all(not x['intersections'] for x in motion['yaw_samples'])
assert all(v['boundary_edges']==0 and v['nonmanifold_edges']==0 and v['signed_volume_mm3']>0 for v in report['stl'].values())

# Extract the Traditional Chinese face from the collection before embedding.
# Passing a TTC directly can prevent PDF font subsetting in MuPDF.
fontdir=ROOT/'work/fonts';fontdir.mkdir(parents=True,exist_ok=True)
for weight in ['Regular','Bold']:
    dst=fontdir/f'NotoSansCJKtc-{weight}.otf'
    font=TTFont(f'/usr/share/fonts/opentype/noto/NotoSansCJK-{weight}.ttc',fontNumber=3)
    opts=subset.Options();opts.desubroutinize=True;opts.retain_gids=True
    sub=subset.Subsetter(options=opts)
    sub.populate(text=Path(__file__).read_text()+'0123456789.−°³')
    sub.subset(font);font.save(dst)
FONT=str(fontdir/'NotoSansCJKtc-Regular.otf')
BOLD=str(fontdir/'NotoSansCJKtc-Bold.otf')
f=fitz.Font(fontfile=FONT);fb=fitz.Font(fontfile=BOLD)
doc=fitz.open();blue=(.09,.21,.29);gray=(.30,.37,.42);orange=(.92,.52,.08)
def page(title,subtitle='R1 試裝版  ·  2026-11-15'):
    p=doc.new_page(width=595,height=842)
    p.insert_font(fontname='F',fontfile=FONT);p.insert_font(fontname='B',fontfile=BOLD)
    p.draw_rect(fitz.Rect(0,0,595,8),color=blue,fill=blue)
    p.insert_text((36,52),title,fontname='B',fontsize=22,color=blue)
    p.insert_text((36,76),subtitle,fontname='F',fontsize=10,color=gray)
    p.draw_line((36,795),(559,795),color=(.8,.83,.85),width=.5)
    p.insert_text((36,815),'IPX896HV / 原 GitHub 機構局部改裝 / 請先印試片',fontname='F',fontsize=9,color=gray)
    p.insert_text((536,815),str(len(doc)),fontname='F',fontsize=9,color=gray)
    return p
def text(p,txt,x,y,w=523,size=11,bold=False,color=blue,leading=1.6):
    font=fb if bold else f;name='B' if bold else 'F'
    for paragraph in txt.split('\n'):
        line=''
        for c in paragraph:
            if font.text_length(line+c,fontsize=size)>w and line:
                p.insert_text((x,y),line,fontname=name,fontsize=size,color=color);y+=size*leading;line=c
            else:line+=c
        p.insert_text((x,y),line,fontname=name,fontsize=size,color=color);y+=size*leading
    return y
def table(p,rows,widths,y,header=True,rowheight=31):
    x0=36
    for k,row in enumerate(rows):
        h=rowheight
        if k==0 and header:p.draw_rect(fitz.Rect(x0,y,x0+sum(widths),y+h),color=blue,fill=blue)
        elif k%2==0:p.draw_rect(fitz.Rect(x0,y,x0+sum(widths),y+h),color=None,fill=(.95,.97,.98))
        x=x0
        for col,w in zip(row,widths):
            text(p,str(col),x+7,y+20,w-14,size=10,bold=k==0,color=(1,1,1) if k==0 else blue,leading=1.3);x+=w
        p.draw_line((x0,y+h),(x0+sum(widths),y+h),color=(.84,.88,.9),width=.4);y+=h
    return y

p=page('IPX896HV 雙自由度夾爪','開合＋左右轉向  /  完整 STEP、分件 STL、試片及五金表')
p.insert_image(fitz.Rect(25,96,570,583),filename=str(OUT/'preview/assembly_open.png'),keep_proportion=True)
y=text(p,'保留原機構，修改必要接口',36,608,size=16,bold=True)
y=text(p,'6 種原件保留幾何；4 種原件局部修改；新增 2 種轉接件。主要列印件共 14 件。所用原始 CAD 與 MIT 授權已保留。',36,y+10)
y=text(p,'重要：這是可供列印試裝的 CAD 原型，沒有完成實物配合或承載驗證。兩顆舵機均暫按 IPX896HV，舵盤及固定耳尺寸仍需核對。',36,y+10,bold=True,color=orange)
text(p,'先開 output/IPX896HV_2DOF_assembly.step；先印 output/fit_checks。完整步驟見 README_繁體中文.md。',36,y+10,size=10)

p=page('列印清單與設定')
rows=[('編號','零件','數量','處理'),('U01 / U02','左右夾指','各 1','原幾何'),('U03','被動連桿','2','原幾何'),('U04','小齒輪','2','原幾何'),('U05','右齒輪連桿','1','原幾何'),('U06','底座側壁','1','原幾何'),('M01','掌板／舵機座','1','接口＋支點校正'),('M02','驅動齒輪連桿','1','只改後端接口'),('M03','固定底座','1','孔位／局部腔體'),('M04','原旋轉座','1','底部接口'),('N01','舵盤轉接盤','1','新增'),('N02','夾爪轉接支架','1','新增')]
y=table(p,rows,[92,185,55,191],103,rowheight=32)
y=text(p,'建議：0.4 噴嘴、0.2 層高、4–6 道外壁。支架約 40% 填充；延長軸、舵盤盤面和齒輪根部局部實心。',36,y+31)
y=text(p,'先用 PLA 試配合；改 PETG 後再確認孔徑。檔案已置底，但 M01/M02 的懸空部位及原夾指槽仍可能需要支撐，請檢查切片每層。',36,y+12)
text(p,'底座保留原尺寸約 160 × 96。不要列印完整裝配中的 REF 舵機／舵盤。未提供打印機設定，因此不附 G-code。',36,y+12)

p=page('先核對舵機與金屬舵盤')
text(p,'附件尺寸作起點；未提供的實測值不得視為已確認。',36,108,bold=True,color=orange)
p.insert_image(fitz.Rect(36,133,339,310),filename=str(OUT/'preview/servo_fit.png'))
p.insert_image(fitz.Rect(359,133,559,310),filename=str(OUT/'preview/horn_fit.png'))
rows=[('配合項目','本版採用','驗證方法'),('舵機外殼','40.5 × 21 × 38.9','F01 外殼自由通過'),('外殼口','41.1 × 21.6','每側暫留 0.3'),('固定耳孔距','暫按 48.5 × 10','孔距／高度實測'),('固定耳長孔','5.0 × 3.4','四螺絲可同時穿入'),('金屬舵盤','匹配 25T，外徑 ≤24','F02 試孔位及高度'),('舵盤固定孔','相對 M3 孔，半徑 9','至少兩個相對孔'),('轉接軸／孔','12.0 / 12.8','F03＋F04 自由轉動')]
y=table(p,rows,[125,174,224],323,rowheight=32)
y=text(p,'舵盤螺絲用低頭圓頭型：頭徑 ≤5.7、頭高 ≤1.7，必須沉入槽內。半徑 9 的孔位讓螺絲頭能從延長軸旁通過；較小孔距不可直接套用。中心螺絲使用舵機配套牙型。',36,y+29)
text(p,'若舵盤不符合此接口，先改參數／轉接件。不要靠高扭矩舵機或螺絲把尺寸不合的零件硬壓入位。',36,y+10)

p=page('裝配順序')
steps=[
('1  底座','裝入舵機，鎖固定耳並安排出線；確認線材沒有被 U06 側壁夾住。利用新增底座孔將整機固定在平台上。'),
('2  底座傳動','先把 N01 鎖到金屬舵盤，確認螺絲頭沉入；再以四個 M3×12 螺絲及普通螺母將 M04 接到 N01。'),
('3  轉接支架','先鎖 N02 的四個 M5 螺絲。沉孔避免上排螺絲頭頂住掌板；裝掌板後工具較難進入。'),
('4  開合舵機','將舵機裝到 M01 外置座；M02 連接金屬舵盤，延長軸穿過掌板。中心孔可供鎖舵盤固定螺絲的工具通過。'),
('5  齒輪與連桿','依 STEP 的位置與相位裝 U04×2、U05、U03×2 和兩個夾指。原零件的支點已重新對齊；活動螺絲不可夾死。'),
('6  墊片與掌板','兩側夾指已對齊。固定支點留約 0.3；被動連桿到夾指均暫需約 1.9 墊高；齒輪連桿到夾指均約留 0.3。再將掌板鎖到 N02。'),
('7  乾裝後再通電','檢查螺絲尾端、舵盤和線材，手動確認自由運動。先小角度空載測試，實測可用端點後再設定軟限位。')]
y=111
for title,body in steps:
    y=text(p,title,36,y,size=12,bold=True)
    y=text(p,body,36,y+3,size=10.5);y+=17
text(p,'詳細螺絲尺寸及順序見 BOM.csv 和 README。原轉軸孔可能需按所用 M3 螺絲鉸至約 3.1–3.2，應逐孔確認，不能全數一律擴孔。',36,y+4,size=10,color=gray)

p=page('已檢查與仍需實測')
last=motion['opening_samples'][-1]
first=motion['opening_samples'][0]
rows=[('檢查','結果'),('修改／新增 CAD 零件','六個均為有效單一實體'),('STL 網格','16 個列印／試片檔均封閉、正體積'),('名義裝配','未檢出 >0.01 mm³ 的實體穿透'),('開合抽樣','0–36°，每 3° 檢查一次'),('轉向抽樣','−45° / 0° / +45°'),('連桿閉合','重新對齊，數值誤差近零')]
y=table(p,rows,[164,359],108,rowheight=34)
y=text(p,'R1 已將驅動齒寬重疊由 0.5 改為 2.0。但原齒形的三對間隙累積，剛體模型估算輸出端約有 8.2–11.6° 回程空隙，仍需實物檢查。詳見齒輪檢查圖。',36,y+28,bold=True)
y=text(p,f'上述開合範圍內，兩夾指最小幾何距離約 {first["minimum_jaw_to_jaw_distance_mm"]:.1f}–{last["minimum_jaw_to_jaw_distance_mm"]:.1f}，未含膠墊；不代表任意形狀物品的可夾尺寸。沒有給出已驗證的載重額定值。',36,y+12)
y=text(p,'供電與軟體接口',36,y+22,size=14,bold=True)
y=text(p,'附件電壓 4.8–8.4 V；不得直接接原專案的 12.6 V 電池。7.4 V 下單顆堵轉電流 5.4 A，兩顆可能約 10.8 A 峰值，供電與線路需相應選擇並共地。',36,y+7)
y=text(p,'兩路 PWM。附件脈寬 500–2500 μs、中位 1500 μs、工作頻率 333 Hz；由軟體組確認驅動器設定。完整脈寬範圍不可直接當作機構允許行程。',36,y+10)
text(p,'GitHub 來源：vshreyas121-code/6-dof-robotic-arm\n固定版本：258d1893ba1b8b49e87baa79da462680fd53681b\n原 MIT 授權、來源雜湊與修改說明均已保留。',36,y+19,size=9,color=gray)

doc.save(OUT/'裝配與試印指南.pdf',garbage=4,deflate=True)
print('GUIDE_WRITTEN',len(doc),flush=True)
