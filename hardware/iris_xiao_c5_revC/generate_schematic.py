"""Generate a three-sheet, conventional-symbol KiCad 9 engineering schematic.
Run in WSL Ubuntu with kicad-symbols installed. KiCad CLI renders/checks the result.
"""
from pathlib import Path
import json, re, uuid, copy, math, csv, shutil

ROOT=Path(__file__).resolve().parent
OUT=ROOT/'output';OUT.mkdir(exist_ok=True)
LIBDIR=Path('/usr/share/kicad/symbols')
def uid(key):return str(uuid.uuid5(uuid.NAMESPACE_URL,'iris-revc/'+key))
def q(x):return json.dumps(str(x),ensure_ascii=False)
def parse(s):
    tokens=re.findall(r'"(?:[^"\\]|\\.)*"|[()]|[^\s()]+',s);stack=[];roots=[]
    for t in tokens:
        if t=='(':
            n=[];(stack[-1] if stack else roots).append(n);stack.append(n)
        elif t==')':stack.pop()
        else:stack[-1].append(json.loads(t) if t.startswith('"') else t)
    assert not stack and len(roots)==1
    return roots[0]
def atom(v):
    s=str(v)
    return s if re.fullmatch(r'[A-Za-z0-9_.+~:/#-]+',s) else q(s)
def dump(n):
    return '('+' '.join(dump(v) if isinstance(v,list) else q(v) if i>0 and n[0] in ('symbol','property','name','number','extends','lib_id','project','path','reference') else atom(v) for i,v in enumerate(n))+')'
def kids(n,k):return [x for x in n if isinstance(x,list) and x and x[0]==k]
def one(n,k):return next(x for x in n if isinstance(x,list) and x and x[0]==k)
cache={};SYMS={}
def stock(lib,name):
    if lib not in cache:
        cache[lib]={s[1]:s for s in kids(parse((LIBDIR/(lib+'.kicad_sym')).read_text()),'symbol')}
    orig=copy.deepcopy(cache[lib][name]);ex=kids(orig,'extends')
    if ex:
        base=copy.deepcopy(stock(lib,ex[0][1]));old=base[1].split(':')[-1]
        props={x[1]:x for x in kids(orig,'property')}
        base=[x for x in base if not(isinstance(x,list) and x[0]=='property' and x[1] in props)]
        base.extend(props.values())
        for s in kids(base,'symbol'):s[1]=s[1].replace(old+'_',name+'_',1)
        base[1]=lib+':'+name;return base
    orig[1]=lib+':'+name;return orig
def getstock(lib,name):
    key=lib+':'+name
    if key not in SYMS:SYMS[key]=stock(lib,name)
    return key
def effects(size=1,extra=''):return f'(effects (font (size {size} {size})) {extra})'

def chip(name,left,right,top=(),bottom=(),width=30.48):
    """Pins: number, name, electrical type; 0.1-inch grid."""
    key='IRIS_RevC:'+name;h=max(len(left),len(right),3)*2.54+5.08;w=width/2
    a=['symbol',key,['pin_names',['offset','0.762']],['in_bom','yes'],['on_board','yes'],
       ['property','Reference','U',['at','0',str(h/2+3),'0'],['effects',['font',['size','1.27','1.27']]]],
       ['property','Value',name,['at','0',str(h/2+1),'0'],['effects',['font',['size','1','1']]]],
       ['symbol',name+'_0_1',['rectangle',['start',str(-w),str(h/2)],['end',str(w),str(-h/2)],['stroke',['width','0.254'],['type','default']],['fill',['type','background']]]]]
    p=['symbol',name+'_1_1']
    for side,ls in [('L',left),('R',right),('T',top),('B',bottom)]:
        for i,(num,nm,typ) in enumerate(ls):
            if side in ['L','R']:
                x=(-w-2.54) if side=='L' else (w+2.54);y=(len(ls)-1)*1.27-i*2.54;ang=0 if side=='L' else 180
            else:
                x=(i-(len(ls)-1)/2)*5.08;y=h/2+2.54 if side=='T' else -h/2-2.54;ang=270 if side=='T' else 90
            p.append(['pin',typ,'line',['at',str(x),str(y),str(ang)],['length','2.54'],['name',nm,['effects',['font',['size','1','1']]]],['number',str(num),['effects',['font',['size','0.9','0.9']]]]])
    a.append(p);SYMS[key]=a;return key

R=getstock('Device','R');C=getstock('Device','C');L=getstock('Device','L');D=getstock('Device','D');FUSE=getstock('Device','Fuse')
NPN=getstock('Transistor_BJT','BC847');PNP=getstock('Transistor_BJT','BC857')
NMOS=getstock('Transistor_FET','2N7002');NPOWER=getstock('Transistor_FET','AO3400A');PPOWER=getstock('Transistor_FET','AO3401A')
BTN=getstock('Switch','SW_Push');JP=getstock('Jumper','Jumper_2_Open')
TERM=chip('Battery_Wires',[(1,'BAT+','passive'),(2,'BAT-','passive')],[],width=15.24)
ANT=chip('External_NFC_Antenna',[(1,'LA','passive'),(2,'LB','passive')],[],width=20.32)
BOOST=chip('TPS61023',[(3,'VIN','power_in'),(2,'EN','input'),(1,'FB','input')],[(5,'SW','power_out'),(6,'VOUT','power_out')],bottom=[(4,'GND','power_in')])
LOAD=chip('TPS22975',[(1,'VIN','power_in'),(2,'VIN','passive'),(4,'VBIAS','power_in'),(3,'ON','input')],[(7,'VOUT','power_out'),(8,'VOUT','passive'),(6,'CT','passive')],bottom=[(5,'GND','power_in'),(9,'EP','power_in')])
TAG=chip('NT3H2111',[(1,'LA','passive'),(8,'LB','passive'),(7,'VOUT_EH','power_out')],[(3,'SCL','input'),(5,'SDA','bidirectional'),(4,'FD','open_collector')],top=[(6,'VCC','power_in')],bottom=[(2,'GND','power_in')])
BUS=chip('SN74CB3Q3245',[(i+2,'A'+str(i+1),'bidirectional') for i in range(8)]+[(19,'OE_N','input')],[(18-i,'B'+str(i+1),'bidirectional') for i in range(8)]+[(1,'NC','no_connect')],top=[(20,'VCC','power_in')],bottom=[(10,'GND','power_in')],width=35.56)
GPIO=[(1,'D0_GPIO1'),(2,'D1_GPIO0'),(3,'D2_GPIO25'),(4,'D3_GPIO7'),(5,'D4_GPIO23'),(6,'D5_GPIO24'),(7,'D6_GPIO11'),(8,'D7_GPIO12'),(9,'D8_GPIO8'),(10,'D9_GPIO9'),(11,'D10_GPIO10')]
MCU=chip('XIAO_ESP32_C5_SMD',[(n,nm,'bidirectional') for n,nm in GPIO],[(14,'5V_VBUS','power_in'),(12,'3V3_OUT','power_out'),(22,'3V3_OUT','passive'),(16,'MTDO_GPIO5_ADC','input'),(15,'MTDI_GPIO3','bidirectional'),(17,'EN','input'),(19,'MTMS_GPIO2','bidirectional'),(20,'MTCK_GPIO4','bidirectional'),(21,'BOOT_GPIO28','input'),(23,'BAT_LIPO_ONLY','passive'),(25,'PAD','passive')],bottom=[(13,'GND','power_in'),(18,'GND','passive'),(24,'GND','passive')],width=50.8)
FPCnames={**{n:'VCCS' for n in range(1,7)},**{n:'GND' for n in [7,10,13,16,19,22,25]},8:'D3+',9:'D3-',11:'D2+',12:'D2-',14:'CLK+',15:'CLK-',17:'D1+',18:'D1-',20:'D0+',21:'D0-',24:'INT_DF',31:'AGINGEN',34:'SCLK',35:'MOSI',36:'MISO',37:'CE_N'}
FPC=chip('FH26W_39S',[(n,FPCnames.get(n,'NC'),'passive') for n in range(1,21)],[(n,FPCnames.get(n,'NC'),'passive') for n in range(21,40)],width=30.48)

COMPS=[];PAGES=[]
ROOTID=uid('root');PROJECT='IRIS_C5_RevC'
class Page:
    def __init__(self,name,title,num):
        self.name=name;self.title=title;self.num=num;self.id=ROOTID if num==1 else uid(name);self.path='/'+ROOTID+('/'+uid('sheet/'+name) if num!=1 else '')
        self.items=[];self.cs=[];self.n=0;self.calls=[];self.wired=set();self.positions={};PAGES.append(self)
    def uuid(self):self.n+=1;return uid(self.name+'/'+str(self.n))
    def wire(self,a,b):
        if a==b:return
        self.items.append(f'(wire (pts (xy {a[0]} {a[1]}) (xy {b[0]} {b[1]})) (stroke (width 0) (type default)) (uuid {self.uuid()}))')
    def text(self,x,y,s,size=1.5):self.items.append(f'(text {q(s)} (at {x} {y} 0) {effects(size,"(justify left)")} (uuid {self.uuid()}))')
    def label(self,pos,name,angle=0):
        just='left' if angle==0 else 'right'
        self.items.append(f'(global_label {q(name)} (shape passive) (at {pos[0]} {pos[1]} {angle}) {effects(.95,"(justify "+just+")")} (uuid {self.uuid()}))')
    def add(self,ref,key,val,x,y,nets,rot=0,fp='',note='',labeloffset=5.08):
        self.calls.append((ref,key,val,x,y,nets,rot,fp,note,labeloffset))
        pins=[p for sub in kids(SYMS[key],'symbol') for p in kids(sub,'pin')]
        nets={str(k):v for k,v in nets.items()};expected={one(p,'number')[1] for p in pins}
        assert expected==set(nets),(ref,expected,set(nets))
        inst=f'(symbol (lib_id {q(key)}) (at {x} {y} {rot}) (unit 1) (in_bom yes) (on_board yes) (dnp {"yes" if val.startswith("DNP") else "no"}) (uuid {uid(ref)})'
        ys=[float(one(p,'at')[2]) for p in pins];isic=key.startswith('IRIS_RevC:')
        bounds=[float(one(rect,'start')[2]) for sub in kids(SYMS[key],'symbol') for rect in kids(sub,'rectangle')]
        py=y-max(ys+bounds)-5.08 if isic else y-5.08
        prop_x=x-10.16 if (isic and any(float(one(pp,'at')[3])==270 for pp in pins)) or key.startswith('Transistor_') else x
        if key in (R,C,L,FUSE) and rot%180==0:
            prop_x=x+7.62;py=y-1.27
        field_angle=rot % 180
        inst+=f'(property "Reference" {q(ref)} (at {prop_x} {py} {field_angle}) {effects(1.27)}) (property "Value" {q(val)} (at {prop_x} {py+2.0} {field_angle}) {effects(1.05)}) (property "Footprint" {q(fp)} (at {x} {y} {field_angle}) {effects(1,"hide")})'
        pcs=[];pos={};a=math.radians(rot)
        for p in pins:
            n=one(p,'number')[1];name=one(p,'name')[1];at=one(p,'at');px,py=float(at[1]),float(at[2]);angle=(float(at[3])+rot)%360
            wx=round(x+px*math.cos(a)-py*math.sin(a),4);wy=round(y-(px*math.sin(a)+py*math.cos(a)),4);pos[n]=(wx,wy)
            inst+=f'(pin {q(n)} (uuid {uid(ref+"/"+n)}))'
            net=nets[n];pcs.append(dict(num=n,name=name,net=net,type=p[1],xy=[wx,wy]))
            if net is None:self.items.append(f'(no_connect (at {wx} {wy}) (uuid {self.uuid()}))');continue
            if (ref,n) in self.wired:continue
            # Short labelled wires; vertical pins jog outward to a horizontal label.
            if angle in (0,180):
                ex=wx-labeloffset if angle==0 else wx+labeloffset;end=(round(ex,4),wy);self.wire((wx,wy),end);self.label(end,net,180 if angle==0 else 0)
            else:
                ey=wy-labeloffset if angle==270 else wy+labeloffset;end=(wx,round(ey,4));self.wire((wx,wy),end);self.label(end,net,0)
        inst+=f'(instances (project {q(PROJECT)} (path {q(self.path)} (reference {q(ref)}) (unit 1)))))'
        self.items.append(inst)
        c=dict(ref=ref,key=key,value=val,footprint=fp,note=note,sheet=self.num,pins=pcs);COMPS.append(c);self.cs.append(c);self.positions[ref]=pos;return pos
    def passive(self,ref,val,a,b,x,y,kind=R,fp=None,note=''):
        if fp is None:fp='Resistor_SMD:R_0603_1608Metric' if kind==R else 'Capacitor_SMD:C_0603_1608Metric'
        return self.add(ref,kind,val,x,y,{1:a,2:b},90,fp,note)
    def normalize_wires(self):
        # KiCad stores a distinct wire segment on each side of a T junction.
        # Pre-split to avoid its loader dropping the rest of a long segment.
        wires=[];points=set();keep=[]
        for item in self.items:
            if item.startswith('(wire '):
                pts=[tuple(round(float(v),4) for v in p[1:]) for p in kids(one(parse(item),'pts'),'xy')]
                wires.append(pts);points.update(pts)
            else:
                keep.append(item)
                if item.startswith('(junction '):points.add(tuple(round(float(v),4) for v in one(parse(item),'at')[1:]))
                if item.startswith('(global_label '):points.add(tuple(round(float(v),4) for v in one(parse(item),'at')[1:3]))
        segments=set()
        for a,b in wires:
            assert a[0]==b[0] or a[1]==b[1],(a,b)
            cut=sorted(pt for pt in points if min(a[0],b[0])<=pt[0]<=max(a[0],b[0]) and min(a[1],b[1])<=pt[1]<=max(a[1],b[1]))
            for aa,bb in zip(cut,cut[1:]):segments.add((aa,bb))
        self.items=keep
        for a,b in sorted(segments):self.wire(a,b)
    def save(self):
        self.normalize_wires()
        use={c['key'] for c in self.cs}
        header=f'(kicad_sch (version 20250114) (generator "eeschema") (generator_version "9.0") (uuid {self.id}) (paper "A4") (title_block (title {q(self.title)}) (date "2026-10-16") (rev "C.0") (company "IRIS photo frame / XIAO ESP32-C5") (comment 1 "Engineering prototype: validate power transient / NFC / cable before fabrication")))'
        # Keep the root open after title_block.
        header=header[:-1]
        data=header+'\n(lib_symbols\n'+'\n'.join(dump(SYMS[k]) for k in sorted(use))+')\n'+'\n'.join(self.items)+f'\n(sheet_instances (path "/" (page "{self.num}"))))\n'
        (ROOT/(self.name+'.kicad_sch')).write_text(data,encoding='utf-8')

exec((ROOT / "layout_functional.py").read_text(encoding="utf-8"), globals())
for page in PAGES: page.save()

# Store only the symbols actually used as a project-local library.
used={cc['key'] for cc in COMPS}
libnodes=[]
for k in sorted(used):
    node=copy.deepcopy(SYMS[k]);node[1]=k.split(':')[-1];libnodes.append(dump(node))
(ROOT/'IRIS_RevC.kicad_sym').write_text('(kicad_symbol_lib (version 20231120) (generator "kicad_symbol_editor")\n'+'\n'.join(libnodes)+'\n)',encoding='utf-8')
(ROOT/'sym-lib-table').write_text('(sym_lib_table (version 7) '+''.join('(lib (name '+q(lib)+')(type "KiCad")(uri "${KIPRJMOD}/IRIS_RevC.kicad_sym")(options "")(descr "Project-bundled symbols"))' for lib in sorted({k.split(':')[0] for k in used}))+')',encoding='utf-8')
local=ROOT/'IRIS_Local.pretty';local.mkdir(exist_ok=True)
research=ROOT.parents[1]/'tmp'
for src in [research/'pcb_research/xiao/footprints/New_XIAO_Series_Footprints/XIAO-ESP32-C5-SMD.kicad_mod',research/'pcb_research/fh26/Hirose_FH26-39S-0.3SHW_2Rows-39Pins-1MP_P0.60mm_Horizontal.kicad_mod',research/'power_revB/Texas_DSG0008A_WSON-8-1EP_2x2mm_P0.5mm_EP0.9x1.6mm.kicad_mod']:
    if src.exists():shutil.copy2(src,local/src.name)
(local/'Battery_Wire_2P.kicad_mod').write_text('(footprint "Battery_Wire_2P" (version 20241229) (generator "pcbnew") (layer "F.Cu") (attr through_hole) (fp_text reference "REF**" (at 0 -3) (layer "F.SilkS") (effects (font (size 1 1) (thickness .15)))) (fp_text value "Battery_Wire_2P" (at 0 3) (layer "F.Fab") (effects (font (size 1 1) (thickness .15)))) (pad "1" thru_hole rect (at -2.54 0) (size 3.2 3.2) (drill 1.6) (layers "*.Cu" "*.Mask")) (pad "2" thru_hole circle (at 2.54 0) (size 3.2 3.2) (drill 1.6) (layers "*.Cu" "*.Mask")))')
(local/'Bourns_SRP4020CC.kicad_mod').write_text('''(footprint "Bourns_SRP4020CC" (version 20241229) (generator "pcbnew") (layer "F.Cu")
  (descr "Bourns SRP4020CC: manufacturer recommended land pattern, srp4020cc.pdf page 2") (attr smd)
  (fp_text reference "REF**" (at 0 -3) (layer "F.SilkS") (effects (font (size 1 1) (thickness .15))))
  (fp_text value "SRP4020CC-R47M" (at 0 3) (layer "F.Fab") (effects (font (size 1 1) (thickness .15))))
  (fp_rect (start -2.225 -2.03) (end 2.225 2.03) (stroke (width .1) (type solid)) (fill none) (layer "F.Fab"))
  (fp_rect (start -2.85 -2.5) (end 2.85 2.5) (stroke (width .05) (type solid)) (fill none) (layer "F.CrtYd"))
  (fp_line (start -2.2 -2.3) (end 2.2 -2.3) (stroke (width .12) (type solid)) (layer "F.SilkS"))
  (fp_line (start -2.2 2.3) (end 2.2 2.3) (stroke (width .12) (type solid)) (layer "F.SilkS"))
  (pad "1" smd roundrect (at -1.85 0) (size 1.5 2.4) (layers "F.Cu" "F.Paste" "F.Mask") (roundrect_rratio .05))
  (pad "2" smd roundrect (at 1.85 0) (size 1.5 2.4) (layers "F.Cu" "F.Paste" "F.Mask") (roundrect_rratio .05)))''')
footlibs={'IRIS_Local':'${KIPRJMOD}/IRIS_Local.pretty'}
for cc in COMPS:
    if not cc['footprint']:continue
    lib,nm=cc['footprint'].split(':',1)
    if lib=='IRIS_Local':continue
    src=Path('/usr/share/kicad/footprints')/(lib+'.pretty')/(nm+'.kicad_mod')
    if src.exists():
        dest=ROOT/'footprints'/(lib+'.pretty');dest.mkdir(parents=True,exist_ok=True);shutil.copy2(src,dest/src.name)
        footlibs[lib]='${KIPRJMOD}/footprints/'+lib+'.pretty'
    else:print('Unresolved footprint:',cc['ref'],cc['footprint'])
(ROOT/'fp-lib-table').write_text('(fp_lib_table (version 7) '+''.join('(lib (name '+q(lib)+')(type "KiCad")(uri '+q(uri)+')(options "")(descr "Bundled footprint"))' for lib,uri in sorted(footlibs.items()))+')',encoding='utf-8')
if not (ROOT/(PROJECT+'.kicad_pro')).exists():
    (ROOT/(PROJECT+'.kicad_pro')).write_text(json.dumps({'meta':{'filename':PROJECT+'.kicad_pro','version':1}},indent=2))
(OUT/'connectivity.json').write_text(json.dumps(COMPS,indent=2),encoding='utf-8')
with (OUT/'BOM.csv').open('w',encoding='utf-8-sig',newline='') as f:
    w=csv.writer(f);w.writerow(['Reference','Value','Footprint','Sheet','Notes'])
    for cc in COMPS:
        if not cc['ref'].startswith('#'):w.writerow([cc[k] for k in ['ref','value','footprint','sheet','note']])
with (OUT/'pin_connections.csv').open('w',encoding='utf-8-sig',newline='') as f:
    w=csv.writer(f);w.writerow(['Reference','Pin','Name','Net','Type'])
    for cc in COMPS:
        for pp in cc['pins']:w.writerow([cc['ref'],pp['num'],pp['name'],pp['net'] or 'NC',pp['type']])
print('Generated',len(COMPS),'symbols /',sum(len(cc['pins']) for cc in COMPS),'pins / 3 sheets')
