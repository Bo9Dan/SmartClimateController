import library_io as io,struct,re,uuid,pathlib,shutil,json,zipfile
path='SmartClimate_BOM.PcbLib';backup=pathlib.Path('Models_3D_Backup_2026-11-05');backup.mkdir(exist_ok=True);dest=backup/path
if not dest.exists():shutil.copy2(path,dest)
n=io.setup(path);U=n['U'];e=n['entries'];en=n['ename'];pack=n['packed']
def walk(i):
 if i>=0xfffffffa:return []
 return walk(U(e[i],68))+[i]+walk(U(e[i],72))
def primitives(x):
 p=4+U(x);out=[]
 while p<len(x):
  start=p;t=x[p];p+=1;bs=[]
  for j in range(6 if t==2 else 2 if t==5 else 1):z=U(x,p);bs.append(x[p+4:p+4+z]);p+=4+z
  out.append((t,bs,x[start:p]))
 return out
foot={}
for i,a in enumerate(e):
 if a[66]!=1:continue
 ch=walk(U(a,76));di=next((j for j in ch if en(e[j])=='Data'),None)
 if di is not None and en(a) in ('HDR_1x04_P2.54_THT','HDR_1x03_P2.54_THT','D_SMA_DO214AC','L_XGL5050','SW_HX_3x4x2_2P'):foot[en(a)]={en(e[j]):j for j in ch if e[j][66]==2}
template=next(bs[0] for t,bs,raw in primitives(n['streams'][foot['HDR_1x04_P2.54_THT']['Data']]) if t==12)
assert template.index(b'V7_LAYER')==22
base=template[22:22+U(template,18)].rstrip(b'\0').decode()
def body(label,x,y,w,h,z0,z1,color):
 fields={p.split('=',1)[0]:p.split('=',1)[1] for p in base.split('|') if '=' in p}
 mm=lambda v:f'{v/.0254:.9f}mil'
 fields.update(NAME=' ',STANDOFFHEIGHT=mm(z0),OVERALLHEIGHT=mm(z1),BODYCOLOR3D=str(color),IDENTIFIER=','.join(str(ord(c)) for c in label),MODELID='{'+str(uuid.uuid4()).upper()+'}',**{'MODEL.CHECKSUM':str(uuid.uuid4().int&0xffffffff),'MODEL.2D.X':mm(x),'MODEL.2D.Y':mm(y),'MODEL.EXTRUDED.MINZ':mm(z0),'MODEL.EXTRUDED.MAXZ':mm(z1),'MODEL.MODELTYPE':'0'})
 text='|'.join(k+'='+v for k,v in fields.items()).encode()+b'\0';coords=[]
 for px,py in [(x-w/2,y-h/2),(x+w/2,y-h/2),(x+w/2,y+h/2),(x-w/2,y+h/2)]:coords.extend([px/.0254*10000,py/.0254*10000])
 payload=template[:18]+struct.pack('<I',len(text))+text+struct.pack('<I',4)+struct.pack('<8d',*coords)
 return b'\x0c'+struct.pack('<I',len(payload))+payload
black=0x282828;metal=0xB8B8B8;gold=0x40B8D0
models={
'HDR_1x03_P2.54_THT': [('Insulator',2.54,0,7.62,2.54,0,2.54,black)]+[(f'Pin {i+1}',i*2.54,0,.64,.64,-3.05,8.38,gold) for i in range(3)],
'D_SMA_DO214AC':[('SMA body',0,0,4.3,2.6,.15,2.29,black),('Cathode stripe',-1.65,0,.35,2.6,2.29,2.3,metal),('Cathode terminal',-2.35,0,.6,1.6,0,.25,metal),('Anode terminal',2.35,0,.6,1.6,0,.25,metal)],
'L_XGL5050':[('Composite shield',0,0,5.28,5.48,.1,5.1,0x606060),('Terminal 1',-1.655,0,1.18,4.7,0,.15,metal),('Terminal 2',1.655,0,1.18,4.7,0,.15,metal)],
'SW_HX_3x4x2_2P':[('Switch case',0,0,4,3,.12,1.5,black),('Metal cover',0,0,3.8,2.8,1.5,1.65,metal),('Actuator',0,0,1.8,1.8,1.65,2,black),('Terminal 1',-2.225,0,.45,1.3,0,.12,metal),('Terminal 2',2.225,0,.45,1.3,0,.12,metal)]}
report=[];original=n['streams'].copy()
for name,parts in models.items():
 ids=foot[name];di=ids['Data'];hi=ids['Header'];before=primitives(n['streams'][di]);assert not any(t==12 for t,bs,raw in before)
 n['streams'][di]+=b''.join(body(*part) for part in parts);n['streams'][hi]=struct.pack('<I',U(n['streams'][hi])+len(parts))
 pi=ids['Parameters'];rs=n['records'](n['streams'][pi]);t,a=rs[0];a=re.sub(rb'\|HEIGHT=[^|\x00]*',('|HEIGHT=%.8fmil'%(max(v[6] for v in parts)/.0254)).encode(),a);n['streams'][pi]=pack([(t,a)])
 report.append(dict(footprint=name,bodies=len(parts),height_mm=max(v[6] for v in parts),kind='Native Altium extruded bodies; simplified dimensional model',parts=parts))
io.write(n,path)
fresh=io.setup(path)
for name in models:
 ids=foot[name];di=ids['Data'];before=[raw for t,bs,raw in primitives(original[di]) if t!=12];after=[raw for t,bs,raw in primitives(fresh['streams'][di]) if t!=12];assert before==after,name
 assert sum(t==12 for t,bs,raw in primitives(fresh['streams'][di]))==len(models[name])
 for t,bs,raw in primitives(fresh['streams'][di]):
  if t==12:
   v=bs[0];z=U(v,18);assert len(v)==22+z+4+64;assert U(v,22+z)==4
pathlib.Path('Documentation/SmartClimate_3D_Report.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
readme=pathlib.Path('Documentation/SmartClimate_BOM_README.md');s=readme.read_text(encoding='utf-8').replace('Нові посадкові місця не мають3Dмоделей.','Для Header1x3,SMA,XGL5050 та Hanxia додано спрощені нативні об’ємні моделі Altium за габаритами.');s+='\n## Доповнення 3D\n\nДодано16об’ємних тіл у4посадкові місця. Усі майданчики, отвори, доріжки та шовкографія збережені побайтно. Моделі спрощені, без внутрішньої будови та написів виробника. Для дроселя висота5.1mm;кнопки2mm;SMA2.3mm;Header8.38mm над платою, хвости3.05mm нижче плати. Резервна копія:Models_3D_Backup_2026-11-05/SmartClimate_BOM.PcbLib. Нативний перегляд уAltium не виконувався.\n';readme.write_text(s,encoding='utf-8')
with zipfile.ZipFile('SmartClimate_Library.zip','w',zipfile.ZIP_DEFLATED) as z:
 for path in ['SmartClimate_BOM.SchLib','SmartClimate_BOM.PcbLib','Documentation/SmartClimate_BOM_README.md','Documentation/SmartClimate_BOM.csv','Documentation/SmartClimate_BOM_Manifest.json','Documentation/SmartClimate_BOM_Validation.json','Documentation/SmartClimate_3D_Report.json']:z.write(path)
print('Added',sum(len(v) for v in models.values()),'native 3D bodies to',len(models),'footprints. Verified original 2D geometry unchanged. Updated ZIP.')
