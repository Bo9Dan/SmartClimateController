from pathlib import Path
s=Path('rename_symbols.py').read_text();exec(s.split('import re,json,hashlib')[0])
import re
for i,e in enumerate(entries):
 if e[66]!=2:continue
 x=data(e)
 if b'|LibReference=R_' not in x:continue
 print('\nSYMBOL',re.search(rb'LibReference=([^|\x00]+)',x)[1].decode())
 pos=0
 while pos<len(x):
  h=U(x,pos);n=h&0xffffff;r=x[pos+4:pos+4+n];pos+=4+n
  if h>>24==0 and (b'|RECORD=1|' in r or b'|RECORD=41|' in r or b'|RECORD=45|' in r):print(r.decode('utf-8',errors='replace'))
