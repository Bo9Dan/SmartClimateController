import library_io as io,struct,re,pathlib,json
n=io.setup('SmartClimate_BOM.SchLib');r=n['records'];pack=n['packed'];f=lambda a:dict(p.split(b'=',1) for p in a.rstrip(b'\0').split(b'|') if b'=' in p)
def sf(a,k,v):return b'|'.join(p for p in a.rstrip(b'\0').split(b'|') if not p.startswith(k.encode()+b'='))+b'|'+k.encode()+b'='+str(v).encode()+b'\0'
def pinno(a):o=26+a[26]+1;return a[o+1:o+1+a[o]].decode()
source=io.setup('Schlib1.SchLib');old=next(r(x) for x in source['streams'].values() if r(x) and b'LibReference=SW_' in r(x)[0][1]);pins=[]
for t,a in old:
 if not t:continue
 num=pinno(a)
 if num not in ('1','3'):continue
 if num=='3':a=a.replace(b'\x013\x013',b'\x012\x012')
 aa=bytearray(a);struct.pack_into('<h',aa,20,0);pins.append((1,bytes(aa)))
assert len(pins)==2
rename={'L_10uH_20%_2A_6x6mm':'L_10uH_20%_2.5A_XGL5050'};summ=[]
for i,x in list(n['streams'].items()):
 rs=r(x)
 if not rs or b'|RECORD=1|' not in rs[0][1]:continue
 name=f(rs[0][1])[b'LibReference'].decode()
 if name.startswith('SW_'):
  out=[]
  for t,a in rs:
   if t or f(a).get(b'RECORD') in (b'6',b'12',b'44',b'45',b'46',b'48'):continue
   out.append((t,a))
  for px in [-10,10]:out.append((0,f'|RECORD=12|OwnerPartId=1|Location.X={px}|Radius=1|LineWidth=1|StartAngle=0|EndAngle=360|Color=16711680'.encode()+b'\0'))
  out.append((0,b'|RECORD=6|OwnerPartId=1|LineWidth=1|LocationCount=2|X1=-10|Y1=0|X2=7|Y2=8|Color=16711680\0'));out+=pins
  oi=len(out);out.append((0,b'|RECORD=44\0'));mi=len(out);out.append((0,f'|RECORD=45|OwnerIndex={oi}|ModelName=SW_HX_3x4x2_2P|ModelType=PCBLIB|DatafileCount=1|ModelDatafileEntity0=SW_HX_3x4x2_2P|ModelDatafileKind0=PCBLib|ModelDatafile0=SmartClimate_BOM.PcbLib|IsCurrent=T'.encode()+b'\0'));out.extend([(0,f'|RECORD=46|OwnerIndex={mi}'.encode()+b'\0'),(0,f'|RECORD=48|OwnerIndex={mi}'.encode()+b'\0')]);rs=out
 if name in rename:rs[0]=(0,sf(rs[0][1],'LibReference',rename[name]));name=rename[name]
 # Set concise useful comment and value; selected part is already in MP.
 params={f(a).get(b'Name'):f(a).get(b'Text') for t,a in rs if not t and f(a).get(b'RECORD')==b'41'}
 for j,(t,a) in enumerate(rs):
  if not t and f(a).get(b'Name')==b'Comment':a=sf(a,'Text',name);rs[j]=(t,a)
 n['streams'][i]=pack(rs);summ.append((i,name,f(rs[0][1]).get(b'ComponentDescription',b'').decode()))
# Synchronize public library metadata and section mappings after all edits.
hi=next(i for i,e in enumerate(n['entries']) if n['ename'](e)=='FileHeader');h=r(n['streams'][hi])[0][1]
for j,(i,name,desc) in enumerate(summ):h=sf(sf(h,'LibRef'+str(j),name),'CompDescr'+str(j),desc)
n['streams'][hi]=pack([(0,h)])
ki=next(i for i,e in enumerate(n['entries']) if n['ename'](e)=='SectionKeys');a=r(n['streams'][ki])[0][1]
for j,(i,name,desc) in enumerate(summ):a=sf(a,'LibRef'+str(j),name)
n['streams'][ki]=pack([(0,a)])
io.write(n,'SmartClimate_BOM.SchLib');print('Synchronized all metadata; corrected switch pin coordinates')
