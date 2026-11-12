from pathlib import Path
s=Path('complete_resistors.py').read_text();ns={};exec(s.split('symbols={}')[0],ns)
for e in ns['entries']:
 if e[66]!=2:continue
 rs=ns['records'](ns['data'](e))
 if not rs or b'|RECORD=1|' not in rs[0][1]:continue
 f=ns['fields'](rs[0][1]);print('\n'+f[b'LibReference'].decode());print('Description:',f.get(b'ComponentDescription',b'').decode('utf-8',errors='replace'))
 for t,r in rs:
  if t:continue
  f=ns['fields'](r)
  if f.get(b'RECORD')==b'41':
   k=f.get(b'Name',b'').decode(errors='replace');v=f.get(b'Text',b'').decode('utf-8',errors='replace')
   if k not in ('SnapEDA_Link','Check_prices','Price','Availability'):print(k+': '+v)
  if f.get(b'RECORD')==b'45':print('Footprint:',f.get(b'ModelName',b'').decode())
