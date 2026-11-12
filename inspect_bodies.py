import library_io as l,struct
n=l.setup('SmartClimate_BOM.PcbLib');U=n['U'];e=n['entries'];en=n['ename']
def walk(i):
 if i>=0xfffffffa:return []
 return walk(U(e[i],68))+[i]+walk(U(e[i],72))
for i,a in enumerate(e):
 if a[66]!=1:continue
 ch=walk(U(a,76));di=next((j for j in ch if en(e[j])=='Data'),None)
 if di is None:continue
 x=n['streams'][di]
 if en(a) not in ('HDR_1x04_P2.54_THT','L_XGL5050','SW_HX_3x4x2_2P','D_SMA_DO214AC','HDR_1x03_P2.54_THT'):continue
 p=4+U(x);counts={}
 while p<len(x):
  t=x[p];p+=1;counts[t]=counts.get(t,0)+1
  for j in range(6 if t==2 else 2 if t==5 else 1):
   z=U(x,p);v=x[p+4:p+4+z];p+=4+z
   if t==12:print('BODY',en(a),len(v),repr(v[:1600]))
 print(en(a),counts)
