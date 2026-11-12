import struct, pathlib
p=pathlib.Path('Schlib1.SchLib'); b=p.read_bytes(); U=lambda x,o=0:struct.unpack_from('<I',x,o)[0]; ss=1<<struct.unpack_from('<H',b,30)[0]; sec=lambda n:b[(n+1)*ss:(n+2)*ss]
fat=[]
for n in struct.unpack_from('<109I',b,76):
 if n<0xfffffffa: fat+=list(struct.unpack('<%dI'%(ss//4),sec(n)))
def chain(n,tab=fat):
 r=[]
 while n<0xfffffffa:
  r.append(n); n=tab[n]
 return r
def read(n):return b''.join(sec(i) for i in chain(n))
d=read(U(b,48)); entries=[bytearray(d[i:i+128]) for i in range(0,len(d),128)]
mini=read(U(entries[0],116)); mf=read(U(b,60)); mf=list(struct.unpack('<%dI'%(len(mf)//4),mf))
def data(e):
 n=U(e,116); z=U(e,120)
 return (b''.join(mini[i*64:(i+1)*64] for i in chain(n,mf)) if z<4096 else read(n))[:z]
for i,e in enumerate(entries):
 name=bytes(e[:struct.unpack_from('<H',e,64)[0]-2]).decode('utf-16le',errors='replace')
 if e[66]==2:
  x=data(e)
def ename(e):return bytes(e[:max(0,struct.unpack_from('<H',e,64)[0]-2)]).decode('utf-16le')
def records(x):
 out=[];pos=0
 while pos<len(x):
  h=U(x,pos);n=h&0xffffff;assert pos+4+n<=len(x);out.append((h>>24,x[pos+4:pos+4+n]));pos+=4+n
 return out
def packed(rs):return b''.join(struct.pack('<I',len(x)|(t<<24))+x for t,x in rs)

import re,uuid,json
from pathlib import Path
F=0xffffffff;END=0xfffffffe
put=lambda e,o,v:struct.pack_into('<I',e,o,v)
streams={i:data(e) for i,e in enumerate(entries) if e[66]==2};original=streams.copy()
def fields(r):return dict(part.split(b'=',1) for part in r.rstrip(b'\0').split(b'|') if b'=' in part)
def setf(r,k,v):
 k=k.encode();v=v.encode();parts=r.rstrip(b'\0').split(b'|');parts=[part for part in parts if not part.startswith(k+b'=')];return b'|'.join(parts)+b'|'+k+b'='+v+b'\0'
def newentry(name,kind):
 e=bytearray(128);nm=name.encode('utf-16le')+b'\0\0';assert len(nm)<=64;e[:len(nm)]=nm;struct.pack_into('<H',e,64,len(nm));e[66]=kind;e[67]=1
 for off in (68,72,76):put(e,off,F)
 entries.append(e);return len(entries)-1
symbols={}
for i,x in streams.items():
 rs=records(x)
 if rs and b'|RECORD=1|' in rs[0][1]:symbols[fields(rs[0][1])[b'LibReference'].decode()]=i
base=symbols['R_10k_1%_1/10W_0603']
added=[]
for val,tol in [('82k','1'),('33k','1'),('1k','5'),('1k','1')]:
 name=f'R_{val}_{tol}%_1/10W_0603';si=newentry('Resistor_'+val+'_'+tol,1);di=newentry('Data',2);put(entries[si],76,di)
 rs=records(streams[base]);rs=[(t,setf(r,'UniqueID',uuid.uuid4().hex[:8].upper()) if t==0 and b'UniqueID=' in r else r) for t,r in rs];rs[0]=(0,setf(rs[0][1],'LibReference',name));streams[di]=packed(rs);symbols[name]=di;added.append(name)
settings={'5k1':('5.1 k','1','Thick Film'),'4k7':('4.7 k','1','Thick Film'),'82k':('82 k','1','Thick Film'),'33k':('33 k','1','Thick Film'),'1k':('1 k','5','Thick Film'),'10k':('10 k','1','Thin Film'),'0R82':('0.82','5','Thick Film')}
for name,i in symbols.items():
 if not name.startswith('R_'):continue
 value=name.split('_')[1];res,_,tech=settings[value];tol=name.split('_')[2][:-1]
 if value=='82k' and tol=='0.1':tech='Thin Film'
 rs=records(streams[i]);isnew=name in added
 desc=f'{res}Ohms +/-{tol}% 0.1W, 1/10W Chip Resistor 0603 (1608 Metric) {tech}'
 r=rs[0][1];r=re.sub(rb'\|%UTF8%ComponentDescription=[^|]*',b'',r);rs[0]=(0,setf(r,'ComponentDescription',desc))
 values={'Value':value,'Comment':f'RES {res.replace(" ","").upper()} OHM {tol}% 1/10W 0603','Resistance':res+'Ohms','Tolerance':tol+'%','Power':'0.1W','Package':'0603 (1608 Metric)','Technology':tech}
 if value=='82k' and tol=='0.1':values.update(MF='Yageo')
 if value=='0R82':values.update(MF='TE Connectivity')
 if isnew:values.update(MF='Generic',MP='Generic resistor; select manufacturer part')
 if value=='1k' and tol=='1':values.update(MF='UNI-ROYAL',MP='0603WAF1001T5E',LCSC='C21190',Datasheet='https://www.lcsc.com/product-detail/C21190.html',Technology='Thick Film')
 seen=set();out=[]
 for t,r in rs:
  f=fields(r) if t==0 else {};pn=f.get(b'Name',b'').decode(errors='replace')
  if isnew and pn in ('SnapEDA_Link','Check_prices'):r=setf(r,'Text','')
  if pn in values:r=setf(r,'Text',values[pn]);seen.add(pn)
  out.append((t,r))
 for pn,v in values.items():
  if pn not in seen:out.append((0,f'|RECORD=41|OwnerPartId=-1|FontID=1|Color=8388608|IsHidden=T|Text={v}|Name={pn}|UniqueID={uuid.uuid4().hex[:8].upper()}'.encode()+b'\0'))
 streams[i]=packed(out)
# Refresh library index and mapping from actual symbol records.
headerid=next(i for i,e in enumerate(entries) if ename(e)=='FileHeader');r=records(streams[headerid])[0][1]
r=re.sub(rb'\|(?:LibRef|CompDescr|PartCount)\d+=[^|\x00]*',b'',r);r=re.sub(rb'\|%UTF8%CompDescr\d+=[^|]*',b'',r);r=setf(r,'CompCount',str(len(symbols)))
for j,(name,i) in enumerate(symbols.items()):
 r=setf(r,'LibRef'+str(j),name);r=setf(r,'PartCount'+str(j),'2');f=fields(records(streams[i])[0][1]);r=setf(r,'CompDescr'+str(j),f.get(b'ComponentDescription',b'').decode('latin1'))
streams[headerid]=packed([(0,r)])
# Find owning storage via its Data child, including existing mappings.
parents={U(e,76):ename(e) for e in entries if e[66]==1}
sk=next((i for i,e in enumerate(entries) if ename(e)=='SectionKeys'),None)
if sk is None: sk=newentry('SectionKeys',2)
r=('|KeyCount='+str(len(symbols))+''.join(f'|LibRef{j}={name}|SectionKey{j}={parents[i]}' for j,(name,i) in enumerate(symbols.items()))).encode()+b'\0';streams[sk]=packed([(0,r)])
rootids=[i for i,e in enumerate(entries) if i and (e[66]==1 or ename(e) in ('FileHeader','Storage','SectionKeys'))];rootids.sort(key=lambda i:(len(ename(entries[i])),ename(entries[i]).upper()));maxdepth=len(rootids).bit_length()-1
def tree(ids,dep=0):
 if not ids:return F
 m=len(ids)//2;i=ids[m];e=entries[i];put(e,68,tree(ids[:m],dep+1));put(e,72,tree(ids[m+1:],dep+1));e[67]=0 if dep==maxdepth and dep else 1;return i
put(entries[0],76,tree(rootids))
sectors=[];ft=[]
def alloc(x):
 if not x:return END
 start=len(sectors);n=(len(x)+511)//512;x=x.ljust(n*512,b'\0')
 for j in range(n):sectors.append(x[j*512:(j+1)*512]);ft.append(start+j+1 if j<n-1 else END)
 return start
mb=bytearray();mft=[]
for i,x in streams.items():
 e=entries[i];struct.pack_into('<Q',e,120,len(x))
 if len(x)<4096:
  n=(len(x)+63)//64;start=len(mft);put(e,116,start if n else END);mb.extend(x.ljust(n*64,b'\0'));mft.extend(start+j+1 if j<n-1 else END for j in range(n))
 else:put(e,116,alloc(x))
put(entries[0],116,alloc(mb));struct.pack_into('<Q',entries[0],120,len(mb))
mfstart=alloc(struct.pack('<%dI'%len(mft),*mft));mfcount=(len(mft)*4+511)//512
dirid=alloc(b''.join(entries));nf=1
while nf*128<len(sectors)+nf:nf+=1
fatids=list(range(len(sectors),len(sectors)+nf));ft.extend([0xfffffffd]*nf);ft.extend([F]*(nf*128-len(ft)))
for j in range(nf):sectors.append(struct.pack('<128I',*ft[j*128:(j+1)*128]))
h=bytearray(b[:512]);put(h,44,nf);put(h,48,dirid);put(h,60,mfstart);put(h,64,mfcount);put(h,68,END);put(h,72,0);struct.pack_into('<109I',h,76,*(fatids+[F]*(109-nf)))
backup=pathlib.Path('Resistors_Backup_2026-11-05');backup.mkdir(exist_ok=True);bp=backup/p.name
if not bp.exists():bp.write_bytes(b)
out=bytes(h)+b''.join(sectors)

p.write_bytes(out)
expected=streams.copy()
exec(Path('rename_symbols.py').read_text().split('import re,json,hashlib')[0])
for i,x in expected.items():assert data(entries[i])==x
for name,i in symbols.items():
 if name.startswith('R_'):
  before=records(original.get(i,original[base]));after=records(expected[i])
  geom=lambda rs:[(t,r) for t,r in rs if t or (b'|RECORD=1|' not in r and b'|RECORD=41|' not in r)]
  assert geom(before)==geom(after),name
assert len(symbols)==23
print('Verified 23 symbols; all resistor geometry, pins and footprint links preserved.')
Path('Documentation/Resistor_Completeness_Report.md').write_text('# Resistor completion\n\nAdded 33k 1%, 82k 1%, 1k 5%, and 1k 1% (C21190). Filled Value, Comment, Resistance, Tolerance, Power, Package and Description for all resistors. Existing manufacturer parts preserved. New generic parts require manufacturer selection, except C21190. Other supplied LCSC codes remain unassigned to avoid linking Yageo parts to unrelated supplier products. All 0603 resistor symbols have linked footprints. New variants reuse the existing 0603 resistor geometry and footprint. Backup: Resistors_Backup_2026-11-05/Schlib1.SchLib.\n',encoding='utf-8')



