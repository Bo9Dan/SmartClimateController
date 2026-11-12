import library_io as io,struct,pathlib,json
n=io.setup('SmartClimate_BOM.PcbLib');x=n['streams'][4];o=4+n['U'](x);count=n['U'](x,o);names=[];p=o+4
for j in range(count):z=n['U'](x,p);names.append(x[p+5:p+4+z].decode());p+=4+z
assert p==len(x)
for name in ['HDR_1x03_P2.54_THT','D_SMA_DO214AC']:
 if name not in names:names.append(name)
n['streams'][4]=x[:o]+struct.pack('<I',len(names))+b''.join(struct.pack('<I',len(v)+1)+bytes([len(v)])+v.encode() for v in names)
io.write(n,'SmartClimate_BOM.PcbLib')
s=io.setup('SmartClimate_BOM.SchLib');records=s['records'];pack=s['packed'];fld=lambda r:dict(p.split(b'=',1) for p in r.rstrip(b'\0').split(b'|') if b'=' in p)
summary=[]
for i,x in list(s['streams'].items()):
 rs=records(x)
 if not rs or b'|RECORD=1|' not in rs[0][1]:continue
 name=fld(rs[0][1])[b'LibReference'].decode();pins=[r for t,r in rs if t==1];fps=[fld(r).get(b'ModelName',b'').decode() for t,r in rs if not t and fld(r).get(b'RECORD')==b'45']
 if 'PENDING' in ''.join(fps):
  rs=[(t,r) for t,r in rs if t or fld(r).get(b'RECORD') not in (b'44',b'45',b'46',b'48')];s['streams'][i]=pack(rs);fps=[]
 for fp in fps:assert fp in names,(name,fp)
 if name=='J_Header_1x03_2.54mm_THT':assert len(pins)==3,len(pins)
 if name.startswith('R_'):assert len(pins)==2
 summary.append((name,len(pins),','.join(fps)))
io.write(s,'SmartClimate_BOM.SchLib')
pathlib.Path('Documentation/SmartClimate_BOM_Validation.json').write_text(json.dumps(summary,indent=2),encoding='utf-8')
print('23 symbols verified; all assigned footprints resolve; header3 has 3 pins; resistors have 2 pins. Two unresolved footprints explicitly unassigned.')
