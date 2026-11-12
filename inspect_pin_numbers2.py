import library_io as l,struct
s=l.setup('SmartClimate_BOM.SchLib');p=l.setup('SmartClimate_BOM.PcbLib');r=s['records'];f=lambda a:dict(x.split(b'=',1) for x in a.rstrip(b'\0').split(b'|') if b'=' in x)
for x in s['streams'].values():
 rr=r(x)
 if not rr or b'LibReference=' not in rr[0][1]:continue
 name=f(rr[0][1])[b'LibReference'].decode();pn=[]
 for t,a in rr:
  if t:
   off=25;ln=a[off];off+=1+ln
   try:pn.append(a[26:26+a[25]].decode())
   except:pn.append('?')
 print(name,pn)

