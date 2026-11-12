import struct,pathlib,re,uuid,json,copy
F=0xffffffff;END=0xfffffffe
def load(path):
 ns={}
 exec(READER.replace("Schlib1.SchLib",str(path)),ns)
 return ns
READER="import struct,pathlib,re,uuid,json,copy\np=pathlib.Path('Schlib1.SchLib'); b=p.read_bytes(); U=lambda x,o=0:struct.unpack_from('<I',x,o)[0]; ss=1<<struct.unpack_from('<H',b,30)[0]; sec=lambda n:b[(n+1)*ss:(n+2)*ss]\nfat=[]\nfor n in struct.unpack_from('<109I',b,76):\n if n<0xfffffffa: fat+=list(struct.unpack('<%dI'%(ss//4),sec(n)))\ndef chain(n,tab=fat):\n r=[]\n while n<0xfffffffa:\n  r.append(n); n=tab[n]\n return r\ndef read(n):return b''.join(sec(i) for i in chain(n))\nd=read(U(b,48)); entries=[bytearray(d[i:i+128]) for i in range(0,len(d),128)]\nmini=read(U(entries[0],116)); mf=read(U(b,60)); mf=list(struct.unpack('<%dI'%(len(mf)//4),mf))\ndef data(e):\n n=U(e,116); z=U(e,120)\n return (b''.join(mini[i*64:(i+1)*64] for i in chain(n,mf)) if z<4096 else read(n))[:z]\ndef ename(e):return bytes(e[:max(0,struct.unpack_from('<H',e,64)[0]-2)]).decode('utf-16le')\ndef records(x):\n out=[];pos=0\n while pos<len(x):\n  h=U(x,pos);n=h&0xffffff;assert pos+4+n<=len(x);out.append((h>>24,x[pos+4:pos+4+n]));pos+=4+n\n return out\ndef packed(rs):return b''.join(struct.pack('<I',len(x)|(t<<24))+x for t,x in rs)\n\n"
def write(ns,path):
 ns=ns.copy();ns['streams']=ns['streams'].copy();ns['entries']=[bytearray(e) for e in ns['entries']];ns['put']=lambda e,o,v:struct.pack_into('<I',e,o,v);ns['END']=END;ns['F']=F
 # Rebuild every sibling tree from membership in original child trees.
 entries=ns['entries'];U=ns['U'];ename=ns['ename']
 def members(n):
  if n>=0xfffffffa:return []
  return members(U(entries[n],68))+[n]+members(U(entries[n],72))
 groups={i:members(U(e,76)) for i,e in enumerate(entries) if e[66] in (1,5)}
 for i,ids in ns.get('extra_children',{}).items():groups.setdefault(i,[]).extend(ids)
 def rebuild(ids):
  ids=sorted(set(ids),key=lambda i:(len(ename(entries[i])),ename(entries[i]).upper()));depth=len(ids).bit_length()-1
  def go(a,d=0):
   if not a:return F
   m=len(a)//2;i=a[m];e=entries[i];struct.pack_into('<I',e,68,go(a[:m],d+1));struct.pack_into('<I',e,72,go(a[m+1:],d+1));e[67]=0 if d==depth and d else 1;return i
  return go(ids)
 for i,ids in groups.items():struct.pack_into('<I',entries[i],76,rebuild(ids))
 ns['entries']=entries
 exec(WRITER,ns)
 out=bytes(ns['h'])+b''.join(ns['sectors']);pathlib.Path(path).write_bytes(out)
 fresh=load(path)
 for i,x in ns['streams'].items():assert fresh['data'](fresh['entries'][i])==x,(path,i)
 return fresh
WRITER="sectors=[];ft=[]\ndef alloc(x):\n if not x:return END\n start=len(sectors);n=(len(x)+511)//512;x=x.ljust(n*512,b'\\0')\n for j in range(n):sectors.append(x[j*512:(j+1)*512]);ft.append(start+j+1 if j<n-1 else END)\n return start\nmb=bytearray();mft=[]\nfor i,x in streams.items():\n e=entries[i];struct.pack_into('<Q',e,120,len(x))\n if len(x)<4096:\n  n=(len(x)+63)//64;start=len(mft);put(e,116,start if n else END);mb.extend(x.ljust(n*64,b'\\0'));mft.extend(start+j+1 if j<n-1 else END for j in range(n))\n else:put(e,116,alloc(x))\nput(entries[0],116,alloc(mb));struct.pack_into('<Q',entries[0],120,len(mb))\nmfstart=alloc(struct.pack('<%dI'%len(mft),*mft));mfcount=(len(mft)*4+511)//512\ndirid=alloc(b''.join(entries));nf=1\nwhile nf*128<len(sectors)+nf:nf+=1\nfatids=list(range(len(sectors),len(sectors)+nf));ft.extend([0xfffffffd]*nf);ft.extend([F]*(nf*128-len(ft)))\nfor j in range(nf):sectors.append(struct.pack('<128I',*ft[j*128:(j+1)*128]))\nh=bytearray(b[:512]);put(h,44,nf);put(h,48,dirid);put(h,60,mfstart);put(h,64,mfcount);put(h,68,END);put(h,72,0);struct.pack_into('<109I',h,76,*(fatids+[F]*(109-nf)))\n"
def add(ns,name,kind,parent):
 e=bytearray(128);nm=name.encode('utf-16le')+b'\0\0';assert len(nm)<=64;e[:len(nm)]=nm;struct.pack_into('<H',e,64,len(nm));e[66]=kind;e[67]=1
 for o in (68,72,76):struct.pack_into('<I',e,o,F)
 ns['entries'].append(e);i=len(ns['entries'])-1;ns.setdefault('extra_children',{}).setdefault(parent,[]).append(i);return i
def setup(path):
 ns=load(path);ns['streams']={i:ns['data'](e) for i,e in enumerate(ns['entries']) if e[66]==2};return ns
