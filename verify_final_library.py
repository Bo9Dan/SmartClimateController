import library_io as io,struct,re,json,pathlib,csv
n=io.setup('SmartClimate_BOM.SchLib');r=n['records'];pack=n['packed'];f=lambda a:dict(p.split(b'=',1) for p in a.rstrip(b'\0').split(b'|') if b'=' in p)
def sf(a,k,v):return b'|'.join(p for p in a.rstrip(b'\0').split(b'|') if not p.startswith(k.encode()+b'='))+b'|'+k.encode()+b'='+str(v).encode()+b'\0'
for i,x in list(n['streams'].items()):
 rs=r(x)
 if not rs or b'LibReference=' not in rs[0][1]:continue
 name=f(rs[0][1])[b'LibReference'].decode();params={f(a).get(b'Name',b'').decode():f(a).get(b'Text',b'').decode() for t,a in rs if not t and f(a).get(b'RECORD')==b'41'};updates={}
 if name.startswith('J_Header'):updates.update(MF='Samtec',MP='TSW-10'+('3' if '1x03' in name else '4')+'-07-G-S',Datasheet='https://suddendocs.samtec.com/prints/tsw-xxx-xx-x-x-xx-xxx-footprint.pdf')
 if name.startswith('C_') and 'Datasheet' not in params:
  updates['Datasheet']=('https://search.kemet.com/component-documentation/download/specsheet/'+params['MP']) if params['MF']=='KEMET' else 'https://www.yageogroup.com/component-documentation/download/specsheet/'+params['MP']
 if name.startswith('U_'):updates['Datasheet']={'U_STM32F103C8T6':'https://www.st.com/resource/en/datasheet/stm32f103c8.pdf','U_BME280':'https://www.bosch-sensortec.com/media/boschsensortec/downloads/datasheets/bst-bme280-ds002.pdf','U_MP2307DN-LF-Z':'https://www.monolithicpower.com/en/mp2307.html'}[name]
 if name=='J_SM04B-SRSS-TB':updates['Datasheet']='https://www.jst-mfg.com/product/pdf/eng/eSH.pdf'
 if name.startswith('R_'):
  val=name.split('_')[1];human={'5k1':'5.1K','4k7':'4.7K','82k':'82K','33k':'33K','1k':'1K','10k':'10K'}[val];updates['Comment']=f'RES {human} OHM {params["Tolerance"]} 1/10W 0603';updates['Value']=human
 else:updates['Value']=params.get('Capacitance',params.get('Frequency',params.get('Inductance',updates.get('MP',params.get('MP',name)))))
 if name=='D_LED_Green_0603':updates['BOM References']='LED1'
 if name=='D_LED_Red_0603':updates['BOM References']='LED2,LED3'
 seen=set()
 for j,(t,a) in enumerate(rs):
  pn=f(a).get(b'Name',b'').decode() if not t else ''
  if pn in updates:rs[j]=(t,sf(a,'Text',updates[pn]));seen.add(pn)
 for k,v in updates.items():
  if k not in seen:rs.append((0,f'|RECORD=41|OwnerPartId=-1|IsHidden=T|FontID=1|Name={k}|Text={v}'.encode()+b'\0'))
 n['streams'][i]=pack(rs)
io.write(n,'SmartClimate_BOM.SchLib')
# Verify physical pads against schematic pin numbers for every linked symbol.
p=io.setup('SmartClimate_BOM.PcbLib');U=p['U'];entries=p['entries'];streams=p['streams']
def members(j):
 if j>=0xfffffffa:return []
 return members(U(entries[j],68))+[j]+members(U(entries[j],72))
fps={}
for i,e in enumerate(entries):
 if e[66]!=1:continue
 ch=members(U(e,76));di=next((j for j in ch if p['ename'](entries[j])=='Data'),None)
 if di is None:continue
 x=streams[di];pads={}
 for offset in range(len(x)-30):
  if x[offset]!=2:continue
  try:
   off=offset+1;bs=[]
   for q in range(6):z=U(x,off);assert z<5000;bs.append(x[off+4:off+4+z]);off+=4+z
   assert len(bs[0])>1 and bs[0][0]==len(bs[0])-1 and len(bs[4])>=110 and len(bs[1])==1 and len(bs[3])==1
   num=bs[0][1:].decode('ascii');core=bs[4];assert core[0] in (1,74)
   pads[num]=[v*.0254/10000 for v in struct.unpack_from('<6i',core,13)]
  except (AssertionError,IndexError,struct.error,UnicodeDecodeError):continue
 fps[p['ename'](e)]=pads
summary=[]
for i,x in n['streams'].items():
 rs=r(x)
 if not rs or b'LibReference=' not in rs[0][1]:continue
 name=f(rs[0][1])[b'LibReference'].decode();props={f(a).get(b'Name',b'').decode():f(a).get(b'Text',b'').decode() for t,a in rs if not t and f(a).get(b'RECORD')==b'41'}
 pinlist=[]
 for t,a in rs:
  if t:o=27+a[26];pinlist.append(a[o+1:o+1+a[o]].decode())
 fp=next(f(a)[b'ModelName'].decode() for t,a in rs if not t and f(a).get(b'RECORD')==b'45')
 missing=set(pinlist)-set(fps[fp]);print(name,'pins',pinlist,'missing',sorted(missing))
 summary.append(dict(name=name,parameters=props,footprint=fp,pins=pinlist,missingPads=sorted(missing)))
pathlib.Path('Documentation/SmartClimate_BOM_Validation.json').write_text(json.dumps(summary,indent=2),encoding='utf-8')
