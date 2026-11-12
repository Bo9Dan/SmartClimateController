"""Add mechanical NPTH symbols and footprints, preserving existing streams."""
import library_io as io, struct, pathlib, shutil, datetime, json
ROOT=pathlib.Path(__file__).resolve().parent
U=lambda a,o=0:struct.unpack_from('<I',a,o)[0]
uid=lambda:__import__('uuid').uuid4().hex[:8].upper()
def fields(a):return dict(p.split(b'=',1) for p in a.rstrip(b'\0').split(b'|') if b'=' in p)
def sf(a,k,v):
 k=k.encode();return b'|'.join(p for p in a.rstrip(b'\0').split(b'|') if not p.startswith(k+b'='))+b'|'+k+b'='+str(v).encode()+b'\0'
def rec(**kw):return (0,('|'+ '|'.join(str(k)+'='+str(v) for k,v in kw.items())+'|UniqueID='+uid()).encode()+b'\0')
def children(n,i):
 def walk(j):
  if j>=0xfffffffa:return []
  return walk(U(n['entries'][j],68))+[j]+walk(U(n['entries'][j],72))
 return walk(U(n['entries'][i],76))
def primitives(x):
 p=4+U(x)
 while p<len(x):
  t=x[p];p+=1;bs=[]
  for _ in range(6 if t==2 else 2 if t==5 else 1):
   z=U(x,p);p+=4;bs.append(x[p:p+z]);p+=z
  yield t,bs
def primitive(t,bs):return bytes([t])+b''.join(struct.pack('<I',len(b))+b for b in bs)
def unit(mm):return round(mm/.0254*10000)
variants=[('M2',2.2,4.5),('M2_5',2.7,5.5),('M3',3.2,6.5)]
backup=ROOT/'History'/('Mounting-holes-'+datetime.datetime.now().strftime('%Y%m%d-%H%M%S'));backup.mkdir()
for fn in ['SmartClimate_BOM.SchLib','SmartClimate_BOM.PcbLib']:shutil.copy2(ROOT/fn,backup/fn)
p=io.setup((ROOT/'SmartClimate_BOM.PcbLib').as_posix());s=io.setup((ROOT/'SmartClimate_BOM.SchLib').as_posix());oldp=p['streams'].copy();olds=s['streams'].copy()
source=next(i for i,e in enumerate(p['entries']) if p['ename'](e)=='HDR_1x04_P2.54_THT')
di=next(i for i in children(p,source) if p['ename'](p['entries'][i])=='Data')
pr=list(primitives(p['streams'][di]));padbase=next(bs for t,bs in pr if t==2);trackbase=next(bs[0] for t,bs in pr if t==4)
names=[]
for size,hole,clearance in variants:
 name=f'MH_{size}_D{str(hole).replace(".","_")}_NPTH';sym=f'H_MountingHole_{size}_NPTH';names.append((sym,name,size,hole,clearance))
 assert not any(p['ename'](e)==name for e in p['entries'])
 bs=padbase.copy();bs[0]=b'\0';core=bytearray(bs[4]);struct.pack_into('<ii',core,13,0,0);struct.pack_into('<6i',core,21,*([unit(hole),unit(hole)]*3));struct.pack_into('<i',core,45,unit(hole));core[49:52]=bytes([2]*3);core[60]=0
 # NPTH: no annular copper, round drill, no electrical designator.
 bs[4]=bytes(core);parts=[primitive(2,bs)]
 # Mechanical layer 15 square identifies the screw-head clearance envelope.
 r=clearance/2
 for a,b in [((-r,-r),(r,-r)),((r,-r),(r,r)),((r,r),(-r,r)),((-r,r),(-r,-r))]:
  c=bytearray(trackbase);c[0]=71;struct.pack_into('<4i',c,13,*[unit(v) for v in a+b]);struct.pack_into('<i',c,29,unit(.1));parts.append(primitive(4,[bytes(c)]))
 si=io.add(p,name,1,0)
 for key,value in [('Header',struct.pack('<I',len(parts))),('Data',struct.pack('<I',len(name)+1)+bytes([len(name)])+name.encode()+b''.join(parts)),('Parameters',p['packed']([rec(PATTERN=name,HEIGHT='0mil',DESCRIPTION=f'{size.replace("_",".")} mounting hole; drill {hole}mm NPTH; no copper annulus; {clearance}mm screw-head envelope on Mechanical 15')])),('WideStrings',b'\x01\0\0\0\0')]:
  j=io.add(p,key,2,si);p['streams'][j]=value
 si=io.add(s,'MountingHole_'+size,1,0);j=io.add(s,'Data',2,si)
 rs=[rec(RECORD=1,LibReference=sym,ComponentDescription=f'Mechanical mounting hole {size.replace("_",".")}, {hole}mm NPTH',PartCount=2,DisplayModeCount=1,OwnerPartId=-1,CurrentPartId=1,LibraryPath='*',SourceLibraryName='*',TargetFileName='*',AllPinCount=0,Color=128,AreaColor=11599871),
 rec(RECORD=8,OwnerPartId=1,**{'Location.X':0,'Location.Y':0},Radius=12,SecondaryRadius=12,LineWidth=1,Color=128),
 rec(RECORD=8,OwnerPartId=1,**{'Location.X':0,'Location.Y':0},Radius=5,SecondaryRadius=5,LineWidth=1,Color=128),
 rec(RECORD=34,OwnerPartId=-1,**{'Location.X':15,'Location.Y':10},FontID=1,Color=8388608,Text='H?',Name='Designator',ReadOnlyState=1),
 rec(RECORD=41,OwnerPartId=-1,**{'Location.X':15,'Location.Y':-10},FontID=1,Color=8388608,Text=size.replace('_','.')+' NPTH',Name='Comment'),
 rec(RECORD=41,OwnerPartId=-1,IsHidden='T',FontID=1,Name='Hole diameter',Text=str(hole)+' mm'),
 rec(RECORD=41,OwnerPartId=-1,IsHidden='T',FontID=1,Name='Screw head clearance',Text=str(clearance)+' mm; Mechanical 15 outline'),
 rec(RECORD=44),rec(RECORD=45,OwnerIndex=7,ModelName=name,ModelType='PCBLIB',DatafileCount=1,ModelDatafile0='SmartClimate_BOM.PcbLib',ModelDatafileEntity0=name,ModelDatafileKind0='PCBLib',IsCurrent='T'),rec(RECORD=46,OwnerIndex=8),rec(RECORD=48,OwnerIndex=8)]
 s['streams'][j]=s['packed'](rs)
# PCB index: first string record then count and length-prefixed names.
pi=next(i for i,e in enumerate(p['entries']) if p['ename'](e)=='Library');idx=next(i for i in children(p,pi) if p['ename'](p['entries'][i])=='Data');x=p['streams'][idx];pos=4+U(x);count=U(x,pos)
p['streams'][idx]=x[:pos]+struct.pack('<I',count+len(names))+x[pos+4:]+b''.join(struct.pack('<I',len(n)+1)+bytes([len(n)])+n.encode() for _,n,*_ in names)
# Rebuild schematic component index and section mappings from actual symbols.
symbols=[]
for i,e in enumerate(s['entries']):
 if e[66]!=1:continue
 for j in children(s,i)+s.get('extra_children',{}).get(i,[]):
  if s['ename'](s['entries'][j])!='Data':continue
  rr=s['records'](s['streams'][j]);f=fields(rr[0][1]) if rr else {}
  if b'LibReference' in f:symbols.append((f[b'LibReference'].decode(),s['ename'](e),f.get(b'ComponentDescription',b'').decode()))
hi=next(i for i,e in enumerate(s['entries']) if s['ename'](e)=='FileHeader');a=s['records'](s['streams'][hi])[0][1];a=sf(a,'CompCount',len(symbols))
for k,(name,section,desc) in enumerate(symbols):
 for key,val in [('LibRef',name),('PartCount',2),('CompDescr',desc)]:a=sf(a,key+str(k),val)
s['streams'][hi]=s['packed']([(0,a)])
ki=next((i for i,e in enumerate(s['entries']) if s['ename'](e)=='SectionKeys'),None)
if ki is None:ki=io.add(s,'SectionKeys',2,0)
a=b'|KeyCount='+str(len(symbols)).encode()+b'\0'
for k,(name,section,_) in enumerate(symbols):a=sf(sf(a,'LibRef'+str(k),name),'SectionKey'+str(k),section)
s['streams'][ki]=s['packed']([(0,a)])
for ns,old,allowed,fn in [(p,oldp,{idx},'SmartClimate_BOM.PcbLib'),(s,olds,{hi,ki},'SmartClimate_BOM.SchLib')]:
 assert all(ns['streams'][i]==v for i,v in old.items() if i not in allowed)
 tmp=ROOT/(fn+'.mounting.tmp');fresh=io.write(ns,tmp.as_posix())
 for i,v in ns['streams'].items():assert fresh['data'](fresh['entries'][i])==v
for fn in ['SmartClimate_BOM.PcbLib','SmartClimate_BOM.SchLib']:(ROOT/(fn+'.mounting.tmp')).replace(ROOT/fn)
report={'backup':str(backup),'added':[dict(symbol=a,footprint=b,screw=c,drill_mm=d,head_envelope_mm=e) for a,b,c,d,e in names],'verification':'Original component streams unchanged; added records reread successfully. NPTH plated flag false, pad diameter equals drill. Mechanical 15 outlines are visual guides, not automatic copper keepouts.','pcb_unchanged':True}
(ROOT/'Documentation'/'Mounting_Holes_Report.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print(json.dumps(report,indent=2))

