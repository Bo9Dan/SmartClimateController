import library_io as l,struct
s=l.setup('PCB1.PcbDoc')
def f(a):return dict(p.split('=',1) for p in a.rstrip(b'\0').decode('latin1').split('|') if '=' in p)
cs=[f(a) for t,a in s['records'](s['streams'][26])]
def mm(v):return float(v.replace('mil',''))*.0254
for i,c in enumerate(cs):
 x,y=mm(c['X']),mm(c['Y'])
 if 40<x<65 and 25<y<52:print(i,c['SOURCEDESIGNATOR'],round(x,3),round(y,3),c['ROTATION'],c['SOURCELIBREFERENCE'])
x=s['streams'][59];p=0
while p<len(x):
 assert x[p]==2,(p,x[p]);p+=1;bs=[]
 for j in range(6):
  n=struct.unpack_from('<I',x,p)[0];p+=4;bs.append(x[p:p+n]);p+=n
 a=bs[4];ci=struct.unpack_from('<H',a,7)[0]
 if ci<len(cs):
  c=cs[ci];cx,cy=mm(c['X']),mm(c['Y'])
  if 40<cx<65 and 25<cy<52:
   xy=struct.unpack_from('<ii',a,13); net=struct.unpack_from('<H',a,3)[0]
   print('PAD',c['SOURCEDESIGNATOR'],bs[0],tuple(round(v*.0254/10000,3) for v in xy),'net',net)
print('NETS',[(i,f(a)) for i,(t,a) in enumerate(s['records'](s['streams'][23]))])
