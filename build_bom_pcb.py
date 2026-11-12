import library_io as io,struct,pathlib
n=io.setup('PcbLib1.PcbLib');U=n['U'];pack=n['packed']
def blocks(x,offset):
 assert x[offset]==2;p=offset+1;rs=[]
 for j in range(6):z=U(x,p);rs.append(x[p+4:p+4+z]);p+=4+z
 return rs
smd=blocks(n['streams'][215],4+U(n['streams'][215]));tht=blocks(n['streams'][182],4+U(n['streams'][182]))
def mil(mm):return round(mm/0.0254*10000)
def pad(num,x,y,w,h,hole=0):
 bs=list(tht if hole else smd);bs[0]=bytes([len(str(num))])+str(num).encode();c=bytearray(bs[4]);struct.pack_into('<ii',c,13,mil(x),mil(y));struct.pack_into('<6i',c,21,*([mil(w),mil(h)]*3));struct.pack_into('<i',c,45,mil(hole));c[49:52]=bytes([1 if hole and num==1 else 2]*3);bs[4]=bytes(c)
 return b'\x02'+b''.join(struct.pack('<I',len(b))+b for b in bs)
def footprint(name,pads,description):
 si=io.add(n,name,1,0)
 for key,value in [('Header',struct.pack('<I',len(pads))),('Data',struct.pack('<I',len(name)+1)+bytes([len(name)])+name.encode()+b''.join(pads)),('Parameters',pack([(0,f'|PATTERN={name}|HEIGHT=0mil|DESCRIPTION={description}|ITEMGUID=|REVISIONGUID='.encode()+b'\0')])),('WideStrings',b'\x01\x00\x00\x00\x00')]:
  i=io.add(n,key,2,si);n['streams'][i]=value
 return name
footprint('HDR_1x03_P2.54_THT',[pad(i+1,i*2.54,0,1.8,1.8,1.02) for i in range(3)],'1x3 P2.54mm; 1.02mm plated holes; 1.8mm pads')
footprint('D_SMA_DO214AC',[pad(1,-2.1,0,1.5,1.8),pad(2,2.1,0,1.5,1.8)],'SMA DO-214AC generic; pad 1 cathode; verify manufacturer land pattern')
# Update library list: native format first record followed by count and short names.
x=n['streams'][4];print('library prefix',repr(x[:120]));pathlib.Path('pcb_library_index.bin').write_bytes(x)
io.write(n,'SmartClimate_BOM.PcbLib');print('Wrote footprints')
