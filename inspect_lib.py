import struct, pathlib
p=pathlib.Path('Schlib1.SchLib'); b=p.read_bytes(); U=lambda x,o=0:struct.unpack_from('<I',x,o)[0]; ss=1<<struct.unpack_from('<H',b,30)[0]; sec=lambda n:b[(n+1)*ss:(n+2)*ss]
fat=[]
for n in struct.unpack_from('<109I',b,76):
 if n<0xfffffffa: fat+=list(struct.unpack('<%dI'%(ss//4),sec(n)))
def chain(n,tab=fat):
 r=[]
 while n<0xfffffffa:
  r.append(n); n=tab[n]
 return r
def read(n):return b''.join(sec(i) for i in chain(n))
d=read(U(b,48)); entries=[bytearray(d[i:i+128]) for i in range(0,len(d),128)]
mini=read(U(entries[0],116)); mf=read(U(b,60)); mf=list(struct.unpack('<%dI'%(len(mf)//4),mf))
def data(e):
 n=U(e,116); z=U(e,120)
 return (b''.join(mini[i*64:(i+1)*64] for i in chain(n,mf)) if z<4096 else read(n))[:z]
for i,e in enumerate(entries):
 name=bytes(e[:struct.unpack_from('<H',e,64)[0]-2]).decode('utf-16le',errors='replace')
 if e[66]==2:
  x=data(e)
  if name in ['FileHeader','Data']: print(i,name,len(x),repr(x[:2000]))

for i,e in enumerate(entries):
 print(i,bytes(e[:max(0,struct.unpack_from('<H',e,64)[0]-2)]).decode('utf-16le',errors='replace'),e[66])
 if e[66]==2 and b'LibReference=RT0603BR' in data(e): print(repr(data(e)))
