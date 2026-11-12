exec(open('inspect_updated_placement.py').read().split('for aa,bb')[0])
x=s['streams'][74];p=0
while p<len(x):
 t=x[p];n=struct.unpack_from('<I',x,p+1)[0];a=x[p+5:p+5+n];p+=5+n
 if b'ISBOARDCUTOUT=TRUE' not in a:continue
 z=struct.unpack_from('<I',a,18)[0];off=22+z;cnt=struct.unpack_from('<I',a,off)[0];off+=4
 vv=[struct.unpack_from('<dd',a,off+j*16) for j in range(cnt)]
 print('CUTOUT',[(round(xx*.0254/10000,3),round(yy*.0254/10000,3)) for xx,yy in vv])
for name in ['U3','C13','C14']:
 print(name,[(num,tuple(round(v,3) for v in xy)) for (na,num),xy in pads.items() if na==name])
for aa,bb in [(('U3','8'),('C13','1')),(('U3','6'),('C14','1')),(('L1','2'),('C10','2')),(('L1','2'),('C11','2')),(('U1','2'),('C8','1')),(('U2','7'),('C1','1'))]:
 print(aa,bb,round(math.dist(pads[aa],pads[bb]),3))
