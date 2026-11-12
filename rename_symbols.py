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
import re,json,hashlib
names={'8-1879460-3':'R_0R82_5%_1/10W_0603','AC0603FR-104K7L':'R_4k7_1%_1/10W_0603','AC0603FR-135K1L':'R_5k1_1%_1/10W_0603','RT0603FRD0710KL':'R_10k_1%_1/10W_0603','RT0603BRD0782KL':'R_82k_0.1%_1/10W_0603','C0603X103J5RECAUTO':'C_10nF_5%_50V_0603','CC0603GRNPO9BN220':'C_22pF_2%_50V_0603','C0805C106K4PACTU':'C_10uF_10%_16V_0805','CDRH6D28NP-100NC':'L_10uH_30%_1.7A_CDRH6D28','1571294-1':'SW_SPST_0.05A_24V'}
names.update({'SS34':'D_Schottky_40V_3A_SMC','TSW-104-07-G-S':'J_Header_1x04_2.54mm_THT'})
names.update({'APT1608SGC':'D_LED_Green_568nm_0603','BME280':'U_BME280','MP2307DN-LF-Z':'U_MP2307DN-LF-Z','STM32F103C8T6':'U_STM32F103C8T6','SM04B-SRSS-TB':'J_SM04B-SRSS-TB','TYPE-C-31-M-12':'J_USB-C_TYPE-C-31-M-12','ECS-80-12-33-JGN-TR3':'Y_8MHz_12pF_3225'})
def ename(e):return bytes(e[:max(0,struct.unpack_from('<H',e,64)[0]-2)]).decode('utf-16le')
def records(x):
 out=[];pos=0
 while pos<len(x):
  h=U(x,pos);n=h&0xffffff;assert pos+4+n<=len(x);out.append((h>>24,x[pos+4:pos+4+n]));pos+=4+n
 return out
def packed(rs):return b''.join(struct.pack('<I',len(x)|(t<<24))+x for t,x in rs)
streams={i:data(e) for i,e in enumerate(entries) if e[66]==2};original=streams.copy()
for i,x in list(streams.items()):
 if ename(entries[i]) not in ('Data','FileHeader'):continue
 rs=records(x); updated=[]
 for t,r in rs:
  if t==0:
   for old,new in names.items():
    r=re.sub(rb'(\|(?:LibReference|LibRef\d+)='+re.escape(old.encode())+rb')(?=[|\x00])',lambda m:m[0].split(b'=')[0]+b'='+new.encode(),r)
  updated.append((t,r))
 streams[i]=packed(updated)
# SectionKeys maps public symbol names to existing internal storage names.
stores=[ename(e) for e in entries if e[66]==1]
s=('|KeyCount='+str(len(stores))+''.join('|LibRef%d=%s|SectionKey%d=%s'%(j,names.get(n,n),j,n) for j,n in enumerate(stores))).encode()+b'\0'
e=bytearray(128); nm='SectionKeys'.encode('utf-16le')+b'\0\0';e[:len(nm)]=nm;struct.pack_into('<H',e,64,len(nm));e[66]=2;e[67]=1
idx=next((i for i,e0 in enumerate(entries) if ename(e0)=='SectionKeys'),None)
if idx is None: idx=next(i for i,e0 in enumerate(entries) if e0[66]==0);entries[idx]=e;streams[idx]=packed([(0,s)])
F=0xffffffff;END=0xfffffffe
put=lambda e,o,v:struct.pack_into('<I',e,o,v)
# Rebuild root directory tree while preserving all component child trees.
rootids=[i for i,e in enumerate(entries) if i and e[66] in (1,2) and (e[66]==1 or ename(e) in ('FileHeader','Storage','SectionKeys'))]
rootids.sort(key=lambda i:(len(ename(entries[i])),ename(entries[i]).upper()))
maxdepth=len(rootids).bit_length()-1
def tree(ids,depth=0):
 if not ids:return F
 m=len(ids)//2;i=ids[m];e=entries[i];put(e,68,tree(ids[:m],depth+1));put(e,72,tree(ids[m+1:],depth+1));e[67]=0 if depth==maxdepth and depth else 1;return i
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
backup=pathlib.Path('Naming_Backup_2026-11-05_Remaining');backup.mkdir(exist_ok=True);bp=backup/p.name
if not bp.exists():bp.write_bytes(b)
out=bytes(h)+b''.join(sectors)
# Verify every output stream through fresh parsing, and every untouched record byte for byte.
expected=streams.copy();p.write_bytes(out)
source=pathlib.Path(__file__).read_text().split('import re,json,hashlib')[0]
exec(source)
for i,x in expected.items():assert data(entries[i])==x
for i,x in original.items():
 if x!=expected[i]:
  a=records(x);z=records(expected[i]);assert len(a)==len(z)
  for (t,r),(t2,r2) in zip(a,z):
   if r!=r2:assert t==t2==0 and (b'|LibReference=' in r or b'|HEADER=' in r)
report='# Symbol renaming\n\n| Original | New name |\n|---|---|\n'+''.join('| '+a+' | '+z+' |\n' for a,z in names.items())+'\n19 symbols preserved. 19 names changed. Pins, geometry, parameters and footprint links preserved byte for byte. Backup before initial renaming: Naming_Backup_2026-11-05/Schlib1.SchLib.\n'
pathlib.Path('Documentation/Symbol_Renaming_Report.md').write_text(report,encoding='utf-8')
print('Verified all streams; renamed',len(names),'symbols')
