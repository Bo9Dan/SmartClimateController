import library_io as l,struct,math
s=l.setup('PCB1.PcbDoc')
def f(a):return dict(p.split('=',1) for p in a.rstrip(b'\0').decode('latin1').split('|') if '=' in p)
cs=[f(a) for t,a in s['records'](s['streams'][26])]; pads={}
x=s['streams'][59];p=0
while p<len(x):
 assert x[p]==2;p+=1;bs=[]
 for j in range(6):
  n=struct.unpack_from('<I',x,p)[0];p+=4;bs.append(x[p:p+n]);p+=n
 a=bs[4];ci=struct.unpack_from('<H',a,7)[0]
 if ci<len(cs):
  name=cs[ci]['SOURCEDESIGNATOR'];num=bs[0][1:].decode('latin1');xy=tuple(v*.0254/10000 for v in struct.unpack_from('<ii',a,13));pads[name,num]=xy
for aa,bb in [(('U1','3'),('L1','1')),(('U1','2'),('C8','1')),(('U1','1'),('C9','2')),(('U1','3'),('D2','1')),(('U2','7'),('C1','1'))]:
 print(aa,bb,round(math.dist(pads[aa],pads[bb]),2),'mm')
for name in ['J1','J3','C1','Y1','U2']:
 print(name,[(num,tuple(round(v,2) for v in xy)) for (na,num),xy in pads.items() if na==name])
