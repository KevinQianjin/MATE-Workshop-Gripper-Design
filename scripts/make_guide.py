"""Create an English PDF guide and derived assembly views."""
import json, math
from pathlib import Path
import cadquery as cq
import fitz
from motion import posed
from check_and_render import render

ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'output'
P=json.loads((ROOT/'parameters.json').read_text());G=P['gripper'];Y=P['yaw']
parts={p.stem.removeprefix('assembly_'):cq.Shape.importBrep(str(p)) for p in (OUT/'brep').glob('assembly_*.brep')}
render(parts,'assembly_front.png',45)
render(parts,'assembly_rear.png',225)
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

from gears import layout
centers,phases=layout();trial=[cq.importers.importStep(str(OUT/'fit_checks/F05_four_gear_trial_plate.step')).val()]
for n,c,phase in zip([20,19,19,20],centers,phases):
    s=cq.importers.importStep(str(OUT/f'fit_checks/F_mesh_{n}T_B12_PRINT_2.step')).val()
    trial.append(s.rotate((0,0,0),(0,1,0),-phase).translate((c[0],4.5,c[1])))
svg=cq.exporters.getSVG(cq.Compound.makeCompound(trial),opts={'width':900,'height':480,'projectionDir':(0,1,0),'showAxes':False,'showHidden':False,'strokeWidth':.7})
(OUT/'preview/gear_trial_plate.svg').write_text('\n'.join(line.rstrip() for line in svg.splitlines())+'\n')
a=fitz.open(stream=svg.encode(),filetype='svg');b=fitz.open(stream=a.convert_to_pdf(),filetype='pdf');b[0].get_pixmap().save(str(OUT/'preview/gear_trial_plate.png'))

report=json.loads((OUT/'validation/static_and_mesh.json').read_text())
motion=json.loads((OUT/'validation/motion.json').read_text())
gears=json.loads((OUT/'validation/gear_engagement.json').read_text())
assert gears['revision']==P['revision'] and gears['target_passed']
assert not report['static_intersections'],'Resolve static clashes before generating the guide'
assert all(not x['intersections'] for x in motion['opening_samples']),'Resolve sampled-motion clashes'
assert all(not x['intersections'] for x in motion['yaw_samples'])
assert len(motion['contact_limit_samples'])==20 and all(not x['intersections'] for x in motion['contact_limit_samples'])
assert all(v['boundary_edges']==0 and v['nonmanifold_edges']==0 and v['signed_volume_mm3']>0 for v in report['stl'].values())

# Built-in PDF fonts keep the English guide independent of system fonts.
f=fitz.Font(fontname='helv');fb=fitz.Font(fontname='hebo')
doc=fitz.open();blue=(.09,.21,.29);gray=(.30,.37,.42);orange=(.80,.38,.04)

def wrapped(txt,width,size,bold=False):
    font=fb if bold else f;lines=[]
    for paragraph in txt.split('\n'):
        line=''
        for word in paragraph.split():
            candidate=(line+' '+word).strip()
            if line and font.text_length(candidate,fontsize=size)>width:
                lines.append(line);line=''
            while font.text_length(word,fontsize=size)>width:
                cut=len(word)-1
                while font.text_length(word[:cut],fontsize=size)>width:cut-=1
                lines.append(word[:cut]);word=word[cut:]
            line=(line+' '+word).strip()
        lines.append(line)
    return lines

def text(p,txt,x,y,w=523,size=11,bold=False,color=blue,leading=1.45):
    for line in wrapped(txt,w,size,bold):
        assert y<785,('Body text exceeds page',len(doc),line)
        p.insert_text((x,y),line,fontname='hebo' if bold else 'helv',fontsize=size,color=color)
        y+=size*leading
    return y

def page(title,subtitle='R2 matched-gear fit-check prototype | 2026-11-16'):
    p=doc.new_page(width=595,height=842)
    p.draw_rect(fitz.Rect(0,0,595,8),color=blue,fill=blue)
    p.insert_text((36,52),title,fontname='hebo',fontsize=22,color=blue)
    p.insert_text((36,76),subtitle,fontname='helv',fontsize=10,color=gray)
    p.draw_line((36,795),(559,795),color=(.8,.83,.85),width=.5)
    p.insert_text((36,815),'IPX896HV | Adapted open-source mechanism | Print fit coupons first',fontname='helv',fontsize=9,color=gray)
    p.insert_text((536,815),str(len(doc)),fontname='helv',fontsize=9,color=gray)
    return p

def table(p,rows,widths,y,rowheight=30):
    for k,row in enumerate(rows):
        lines=[wrapped(str(value),width-14,9,k==0) for value,width in zip(row,widths)]
        h=max(rowheight,12+max(map(len,lines))*12)
        assert y+h<785,('Table exceeds page',len(doc),row)
        if k==0:p.draw_rect(fitz.Rect(36,y,559,y+h),color=blue,fill=blue)
        elif k%2==0:p.draw_rect(fitz.Rect(36,y,559,y+h),color=None,fill=(.95,.97,.98))
        x=36
        for value,width in zip(row,widths):
            text(p,str(value),x+7,y+16,width-14,size=9,bold=k==0,color=(1,1,1) if k==0 else blue,leading=1.33)
            x+=width
        p.draw_line((36,y+h),(559,y+h),color=(.84,.88,.9),width=.4);y+=h
    return y

p=page('IPX896HV two-axis gripper','Open/close + yaw | Assembly STEP, individual STLs, fit coupons, and hardware BOM')
p.insert_image(fitz.Rect(25,96,570,550),filename=str(OUT/'preview/assembly_open.png'),keep_proportion=True)
y=text(p,'Original mechanism, improved gear engagement',36,578,size=16,bold=True)
y=text(p,'Four retained part types, six locally modified types, and two adapters: 14 main printed pieces. R2 matches the involute gear rims while retaining the original hubs and linkage interfaces.',36,y+10)
y=text(p,'Fit-test prototype: physical fit and load capacity are unverified. Both servos are provisionally IPX896HV; mounting-ear and metal-horn dimensions still need measurement.',36,y+10,bold=True,color=orange)
text(p,'Start with output/IPX896HV_2DOF_assembly.step and output/fit_checks/. Full instructions: docs/assembly.md.',36,y+10,size=10)

p=page('Print list and settings')
rows=[('ID','Part','Qty','Treatment'),('U01 / U02','Left / right jaw','1 each','Original geometry'),('U03','Passive link','2','Original geometry'),('U06','Base side wall','1','Original geometry'),('M01','Palm / servo carrier','1','R2 pivots and relief'),('M02','Driving gear link','1','R2 rim; retained interface'),('M03','Fixed base','1','Retained from R1'),('M04','Rotating waist','1','Retained from R1'),('M05','Right gear link','1','R2 rim; replaces U05'),('M06','Idler gear','2','R2 rim; replaces U04'),('N01','Yaw horn coupler','1','Retained from R1'),('N02','Gripper-to-waist bridge','1','Retained from R1')]
y=table(p,rows,[76,176,48,223],105)
y=text(p,'Start with a 0.4 mm nozzle, 0.2 mm layers, and 4-6 perimeters. Use about 40% infill for brackets; make shaft extensions, horn flanges, and gear roots locally solid.',36,y+28)
y=text(p,'Use PLA for initial fit checks. Repeat the coupons after changing to dry PETG. Files have an initial bed orientation; inspect M01/M02 overhangs and original jaw slots for support needs.',36,y+10)
text(p,'The base remains approximately 160 x 96 mm. REF servo/horn envelopes are not print parts. No printer profile or G-code is supplied.',36,y+10)

p=page('Check the servo and metal horn first')
text(p,'Drawing dimensions are starting assumptions; confirm them on the actual hardware.',36,108,bold=True,color=orange)
p.insert_image(fitz.Rect(36,133,339,305),filename=str(OUT/'preview/servo_fit.png'))
p.insert_image(fitz.Rect(359,133,559,305),filename=str(OUT/'preview/horn_fit.png'))
rows=[('Interface','Nominal design (mm)','Check'),('Servo case','40.5 x 21 x 38.9','F01: case passes freely'),('Case opening','41.1 x 21.6','0.3 clearance per side'),('Ear-hole pitch','48.5 x 10, provisional','Measure pitch and height'),('Ear mounting slots','5.0 x 3.4','All four screws enter together'),('Metal horn','Matching 25T; OD <=24','F02: verify holes and height'),('Horn screw pattern','Opposed M3 holes; radius 9','Use at least two opposed holes'),('Adapter shaft / bore','12.0 / 12.8','F03 + F04 rotate freely')]
y=table(p,rows,[125,174,224],318)
y=text(p,'Use recessed low button-head screws: head diameter <=5.7 mm and height <=1.7 mm. Radius-9 holes provide insertion space beside the shaft. Smaller hole circles are not direct substitutes. Use the correct supplied center-screw thread.',36,y+26,size=10.5)
text(p,'If the horn does not fit, update the parameters and adapter before printing. Do not force incompatible parts together with screws or servo torque.',36,y+10,size=10.5)

p=page('Assembly sequence')
steps=[
('1  Base','Install the servo, fasten its ears, and route wires clear of U06. Secure the complete mechanism to the platform through the base mounting holes.'),
('2  Base drive','Attach N01 to the metal horn with fully recessed screw heads. Attach M04 to N01 using four M3 x 12 screws, washers, and standard nuts.'),
('3  Bridge','Tighten the four N02 M5 screws before installing the palm. Their heads must sit in the counterbores; tool access is limited after palm installation.'),
('4  Opening servo','Fit the servo to M01. Connect M02 to the metal horn before passing its shaft through the palm. Use the center passage to reach the horn retaining screw.'),
('5  Gears and links','Position M06 x2, M05, U03 x2, and both jaws using the R2 STEP phase and hole positions. Use the R2 palm and gears together. Keep moving joints free.'),
('6  Spacers and palm','Allow about 0.3 mm at fixed pivots, 1.9 mm between passive links and jaws, and 0.3 mm between gear links and jaws. Verify actual endplay, then attach the palm to N02.'),
('7  Dry fit, then power','Check screw ends, horns, and cables by hand. Center the servos before attaching the mechanism. Begin with small unloaded movements and set software limits from measured endpoints.')]
y=111
for title,body in steps:
    y=text(p,title,36,y,size=12,bold=True)
    y=text(p,body,36,y+3,size=10.5);y+=13
text(p,'See BOM.csv and docs/assembly.md for hardware and detailed order. Fit each moving bore to its actual smooth shaft; about 0.05-0.10 mm diametral clearance is an initial trial value.',36,y+2,size=10,color=gray)

p=page('CAD checks and physical verification')
last=motion['opening_samples'][-1];first=motion['opening_samples'][0]
rows=[('Check','Recorded result'),('Modified / new CAD parts','Eight valid single solids'),('STL meshes',f'{len(report["stl"])} closed print/trial files with positive volume'),('Nominal assembly','No reported penetration above 0.01 mm^3'),('Opening samples','0-36 degrees, every 3 degrees'),('Bidirectional contact limits','20 gripper linkage poses; no overlap above 0.02 mm^3'),('Yaw samples','-45 / 0 / +45 degrees'),('Linkage closure','Realigned; numerical closure error near zero')]
y=table(p,rows,[164,359],108,rowheight=32)
y=text(p,f'Rigid R2 gear-chain free play is about {max(gears["chain_free_angle_range_deg"]):.2f} degrees, meeting the provisional 3-degree CAD target. R1 was about 8.2-11.6 degrees. Printing error, pivot looseness, and servo backlash are excluded.',36,y+27,bold=True)
y=text(p,f'Minimum nominal jaw-to-jaw distance across the sampled stroke is about {first["minimum_jaw_to_jaw_distance_mm"]:.1f}-{last["minimum_jaw_to_jaw_distance_mm"]:.1f} mm without pads. This is not a general object-size gripping range. No verified payload rating is provided.',36,y+10)
y=text(p,'Power and control interface',36,y+17,size=14,bold=True)
y=text(p,'Supply range: 4.8-8.4 V. Do not connect the upstream 12.6 V battery directly. At 7.4 V, stall current is 5.4 A per servo; allow for about 10.8 A combined peak. Size supply and wiring accordingly and share controller ground.',36,y+5,size=10.5)
y=text(p,'Two PWM channels: the supplied sheet specifies 500-2500 microsecond pulses, 1500 at center, and 333 Hz. Confirm driver settings. The electrical pulse range is not the permitted mechanical travel.',36,y+8,size=10.5)
text(p,'Source: vshreyas121-code/6-dof-robotic-arm\nPinned revision: 258d1893ba1b8b49e87baa79da462680fd53681b\nMIT attribution, source hashes, and modification notes are retained.',36,y+13,size=9,color=gray)

p=page('Choose clearance with the gear trial plate')
p.insert_image(fitz.Rect(36,107,559,345),filename=str(OUT/'preview/gear_trial_plate.png'),keep_proportion=True)
y=text(p,'F05 plate + two 20T gears + two 19T gears',36,372,size=14,bold=True)
y=text(p,'Fit 20T gears to the outer axes, about 30.09 mm apart, and 19T gears to the closer axes, 14.25 mm apart. Screws and washers are omitted from the drawing. Preserve axial endplay; this plate is for manual tests.',36,y+10)
rows=[('File code','Nominal backlash / mesh','Use'),('B08','0.08 mm','Tighter; check for binding'),('B12','0.12 mm','Used by the main R2 parts'),('B16','0.16 mm','Looser; more free play possible')]
y=table(p,rows,[91,181,251],y+10)
y=text(p,'Use one code per set and print two of each tooth count. Check elephant foot, burrs, bores, and shafts, then rotate both ways. Hold the input and measure output free angle.',36,y+26,size=10.5)
y=text(p,'Selecting another clearance requires updating the parameters, regenerating M02/M05/M06, and repeating validation. After the plate test, dry-assemble the complete opening linkage and jaws.',36,y+9,size=10.5)
text(p,'B08/B12/B16 are CAD design values, not measured clearances. Larger backlash may exceed the current 3-degree CAD target.',36,y+9,size=10,color=gray)

doc.save(OUT/'assembly_and_print_guide.pdf',garbage=4,deflate=True)
print('GUIDE_WRITTEN',len(doc),flush=True)
