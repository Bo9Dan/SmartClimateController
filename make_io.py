from pathlib import Path
s=Path('complete_resistors.py').read_text();header=s.split('import re,uuid,json')[0];writer=s[s.index('sectors=[];ft=[]'):s.index('backup=pathlib')]
code='''import struct,pathlib,re,uuid,json,copy
'''+header[header.index('p=pathlib'):header.index('for i,e in enumerate(entries):')]+s[s.index('def ename(e):'):s.index('import re,uuid,json')]
# Use isolated namespaces for readers and the shared, verified sector writer.
module='''import struct,pathlib,re,uuid,json,copy
F=0xffffffff;END=0xfffffffe
def load(path):
 ns={}
 exec(READER.replace("Schlib1.SchLib",str(path)),ns)
 return ns
READER='''+repr(code)+'''
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
WRITER='''+repr(writer)+'''
def add(ns,name,kind,parent):
 e=bytearray(128);nm=name.encode('utf-16le')+b'\\0\\0';assert len(nm)<=64;e[:len(nm)]=nm;struct.pack_into('<H',e,64,len(nm));e[66]=kind;e[67]=1
 for o in (68,72,76):struct.pack_into('<I',e,o,F)
 ns['entries'].append(e);i=len(ns['entries'])-1;ns.setdefault('extra_children',{}).setdefault(parent,[]).append(i);return i
def setup(path):
 ns=load(path);ns['streams']={i:ns['data'](e) for i,e in enumerate(ns['entries']) if e[66]==2};return ns
'''
Path('library_io.py').write_text(module)
