import library_io as io,pathlib,struct,re,json,csv,zipfile
n=io.setup('SmartClimate_BOM.SchLib');r=n['records'];pack=n['packed'];f=lambda a:dict(p.split(b'=',1) for p in a.rstrip(b'\0').split(b'|') if b'=' in p)
def sf(a,k,v):return b'|'.join(p for p in a.rstrip(b'\0').split(b'|') if not p.startswith(k.encode()+b'='))+b'|'+k.encode()+b'='+str(v).encode()+b'\0'
for i,x in list(n['streams'].items()):
 rs=r(x)
 if not rs or b'LibReference=D_Schottky' not in rs[0][1]:continue
 out=[]
 for t,a in rs:
  if t:
   o=27+a[26];num=a[o+1:o+1+a[o]];assert num in (b'A',b'C');a=a[:o+1]+(b'2' if num==b'A' else b'1')+a[o+2:]
  elif f(a).get(b'RECORD')==b'1':a=sf(a,'ComponentDescription','B340A-13-F Schottky rectifier, 40V 3A, SMA DO-214AC; cathode pin1, anode pin2')
  out.append((t,a))
 n['streams'][i]=pack(out)
io.write(n,'SmartClimate_BOM.SchLib')
