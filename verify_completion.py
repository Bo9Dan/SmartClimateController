from pathlib import Path
s=Path('complete_resistors.py').read_text();ns={};exec(s.split('symbols={}')[0],ns)
entries=ns['entries'];data=ns['data'];records=ns['records'];fields=ns['fields'];names=[]
for e in entries:
 if e[66]!=2:continue
 rs=records(data(e))
 if rs and b'|RECORD=1|' in rs[0][1]:
  n=fields(rs[0][1])[b'LibReference'].decode();names.append(n)
  if n.startswith('R_'):
   f={fields(r).get(b'Name'):fields(r).get(b'Text') for t,r in rs if not t and b'|RECORD=41|' in r}
   for k in ('Value','Comment','Resistance','Tolerance','Power','Package'):assert f[k.encode()] not in (None,b'*',b'None'),(n,k)
assert len(names)==23
assert len(set(names))==23
print('Verified 23 unique symbols and complete resistor fields.')
# Geometry and model records compared to backup; added variants compared to original 10k.
old=Path('Resistors_Backup_2026-11-05/Schlib1.SchLib').read_bytes();p=ns['p'];current=p.read_bytes()
loader=s.split('import re,uuid,json')[0]
loader=loader.replace("b=p.read_bytes()","b=old")
a={'old':old};exec(loader,a)
oldrs={}
for e in a['entries']:
 if e[66]==2:
  rs=records(a['data'](e))
  if rs and b'|RECORD=1|' in rs[0][1]:oldrs[fields(rs[0][1])[b'LibReference'].decode()]=rs
import re
geom=lambda rs:[(t,re.sub(rb'\|UniqueID=[^|\x00]*',b'',r) if t==0 else r) for t,r in rs if t or (b'|RECORD=1|' not in r and b'|RECORD=41|' not in r)]
for e in entries:
 if e[66]==2:
  rs=records(data(e))
  if rs and b'|RECORD=1|' in rs[0][1]:
   n=fields(rs[0][1])[b'LibReference'].decode();assert geom(rs)==geom(oldrs.get(n,oldrs['R_10k_1%_1/10W_0603'])),n
print('Verified pins, geometry and footprint links.')
Path('Documentation/Resistor_Completeness_Report.md').write_text('# Resistor completion\n\nAdded 33k 1%, 82k 1%, 1k 5%, and 1k 1% (C21190). All resistor Value, Comment, Resistance, Tolerance, Power, Package and Description fields filled. Existing manufacturer parts preserved. New generic variants require manufacturer selection; C21190 identifies UNI-ROYAL 0603WAF1001T5E (1%). Other supplied LCSC codes remain unassigned pending exact part matching. 23 unique symbols verified. Pins, geometry and footprint links preserved. Backup: Resistors_Backup_2026-11-05/Schlib1.SchLib.\n',encoding='utf-8')


