exec(open('inspect_bodies.py').read().split('for i,a')[0])
for i,a in enumerate(e):
 if a[66]!=1:continue
 ch=walk(U(a,76));di=next((j for j in ch if en(e[j])=='Data'),None)
 if di is None:continue
 x=n['streams'][di]
 if len(x)<4:continue
 p=4+U(x);count=0
 try:
  while p<len(x):
   t=x[p];p+=1
   for j in range(6 if t==2 else 2 if t==5 else 1):
    z=U(x,p);v=x[p+4:p+4+z];p+=4+z
    if t==12:
     count+=1
     if en(a)=='HDR_1x04_P2.54_THT':print('PREFIX',list(enumerate(v[:30])),'TEXTSTART',v.index(b'V7_LAYER'),'VERTICES',struct.unpack('<8d',v[-64:]))
  print(en(a),count)
 except:pass

