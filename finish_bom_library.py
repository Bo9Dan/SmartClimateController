from pathlib import Path
import library_io as io,struct,re,json,uuid
s=Path('build_bom_pcb.py').read_text().split("footprint('HDR_1x03")[0].replace("n=io.setup('PcbLib1.PcbLib')","n=io.setup('SmartClimate_BOM.PcbLib')")
exec(s)
footprint('L_XGL5050',[pad(1,-1.655,0,1.18,4.7),pad(2,1.655,0,1.18,4.7)],'Coilcraft XGL5050 recommended land pattern; 3.31mm pad centers, 1.18x4.7mm pads')
footprint('SW_HX_3x4x2_2P',[pad(1,-2.225,0,1.05,2),pad(2,2.225,0,1.05,2)],'Hanxia HX 3x4x2-2P; pad outer span5.5 inner gap3.4 height2mm')
# Add silk outline and mechanical outline to new footprints.
t=bytearray.fromhex('210c00fffffffffffffffffffff396f7fff396f7fff396f7ffaf31fbffafe6000000000000000000000600030100000000')
def track(x1,y1,x2,y2,layer=33):
 b=bytearray(t);b[0]=layer;struct.pack_into('<5i',b,13,mil(x1),mil(y1),mil(x2),mil(y2),mil(.15));return b'\x04'+struct.pack('<I',len(b))+b
def children(i):
 def walk(j):
  if j>=io.F-5:return []
  e=n['entries'][j];return walk(U(e,68))+[j]+walk(U(e,72))
 return walk(U(n['entries'][i],76))+n.get('extra_children',{}).get(i,[])
newinfo={'L_XGL5050':(2.9,3.0),'SW_HX_3x4x2_2P':(1.8,1.7),'D_SMA_DO214AC':(1.8,1.55)}
for i,e in enumerate(n['entries']):
 name=n['ename'](e)
 if e[66]!=1 or name not in newinfo:continue
 ch=children(i);di=next(j for j in ch if n['ename'](n['entries'][j])=='Data');hi=next(j for j in ch if n['ename'](n['entries'][j])=='Header');a,b=newinfo[name]
 lines=[track(-a,b,a,b),track(-a,-b,a,-b)]
 if name=='L_XGL5050':lines.extend([track(-a,-b,-a,b),track(a,-b,a,b)])
 n['streams'][di]+=b''.join(lines);n['streams'][hi]=struct.pack('<I',U(n['streams'][hi])+len(lines))
x=n['streams'][4];o=4+U(x);count=U(x,o);p=o+4;fps=[]
for j in range(count):z=U(x,p);fps.append(x[p+5:p+4+z].decode());p+=4+z
for name in ['L_XGL5050','SW_HX_3x4x2_2P']:
 if name not in fps:fps.append(name)
n['streams'][4]=x[:o]+struct.pack('<I',len(fps))+b''.join(struct.pack('<I',len(v)+1)+bytes([len(v)])+v.encode() for v in fps)
io.write(n,'SmartClimate_BOM.PcbLib')
# Fill selected manufacturer parts; maintain short processor names.
n=io.setup('SmartClimate_BOM.SchLib');r=n['records'];pack=n['packed'];fld=lambda a:dict(p.split(b'=',1) for p in a.rstrip(b'\0').split(b'|') if b'=' in p)
def sf(a,k,v):return b'|'.join(p for p in a.rstrip(b'\0').split(b'|') if not p.startswith(k.encode()+b'='))+b'|'+k.encode()+b'='+str(v).encode()+b'\0'
selected={'Y_8MHz_20pF_3225':dict(MF='ECS Inc.',MP='ECS-80-20-33-JEN-TR3',Datasheet='https://ecsxtal.com/store/pdf/ecx-32.pdf',**{'Load Capacitance':'20pF','Frequency Tolerance':'+/-20ppm','Frequency Stability':'+/-50ppm'}),'L_10uH_20%_2A_6x6mm':dict(MF='Coilcraft',MP='XGL5050-103MEC',Package='5.28x5.48x5.10mm max height',**{'Saturation Current':'2.5A at 10% drop; 3.7A at 20% drop','DC Resistance':'33.6mOhm max','Rated Current':'4.6A at 20C rise','Datasheet':'https://www.coilcraft.com/getmedia/348b2df6-54b3-4579-8737-e8367b6fa367/xgl5050.pdf'}),'SW_SPST_3x4x2mm':dict(MF='Hanxia',MP='HX 3x4x2-2P-2.5N',LCSC='C36498961',Voltage='12V',Current='50mA',**{'Operating Force':'2.5N','Datasheet':'https://atta.szlcsc.com/upload/public/pdf/source/20250707/B47B221526B87D575FBEDE6D3B809220.pdf'}),'D_Schottky_40V_3A_SMA':dict(MF='Diodes Incorporated',MP='B340A-13-F',Datasheet='https://www.diodes.com/part/view/B340A'),'D_LED_Green_0603':dict(MF='Kingbright',MP='APT1608SGC',Datasheet='https://www.kingbrightusa.com/images/catalog/spec/APT1608SGC.pdf'),'D_LED_Red_0603':dict(MF='Kingbright',MP='APT1608SURCK',Datasheet='https://www.kingbrightusa.com/images/catalog/spec/apt1608surck.pdf'),'C_10uF_10%_25V_0805':dict(MF='KEMET',MP='C0805C106K3PACTU',Datasheet='https://search.kemet.com/component-documentation/download/specsheet/C0805C106K3PACTU'),'C_10nF_5%_50V_0603':dict(MF='KEMET',MP='C0603X103J5RECAUTO'),'C_100nF_10%_16V_0603':dict(MF='KEMET',MP='C0603C104K4RACTU'),'C_22pF_2%_50V_0603':dict(MF='Yageo',MP='CC0603GRNPO9BN220')}
for val,tol,mpval in [('5k1','1','5K1'),('4k7','1','4K7'),('82k','1','82K'),('33k','1','33K'),('1k','5','1K'),('10k','1','10K')]:selected[f'R_{val}_{tol}%_1/10W_0603']=dict(MF='Yageo',MP=f'RC0603{"J" if tol=="5" else "F"}R-07{mpval}L',Datasheet='https://www.yageo.com/upload/media/product/productsearch/datasheet/rchip/PYu-RC_Group_51_RoHS_L_12.pdf')
models={'L_10uH_20%_2A_6x6mm':'L_XGL5050','SW_SPST_3x4x2mm':'SW_HX_3x4x2_2P'}
for i,x in list(n['streams'].items()):
 rs=r(x)
 if not rs or b'|RECORD=1|' not in rs[0][1]:continue
 name=fld(rs[0][1])[b'LibReference'].decode();props=selected.get(name,{});out=[];seen=set()
 for typ,a in rs:
  f=fld(a) if not typ else {};pn=f.get(b'Name',b'').decode(errors='replace')
  if pn=='Selection Status':continue
  if pn in props:a=sf(a,'Text',props[pn]);seen.add(pn)
  if not typ and f.get(b'RECORD')==b'1' and name in models:a=sf(a,'ComponentDescription',('10uH +/-20% shielded inductor, Isat 2.5A at 10% drop, DCR 33.6mOhm max, Coilcraft XGL5050' if name.startswith('L_') else 'Hanxia HX 3x4x2-2P-2.5N tactile switch, SPST-NO, 50mA 12V, 4x3x2mm'));a=sf(a,'AllPinCount','2')
  if name.startswith('Y_') and not typ and f.get(b'RECORD')==b'1':a=sf(a,'ComponentDescription','ECS-80-20-33-JEN-TR3 8MHz quartz crystal, CL20pF, +/-20ppm, 3225 4-pad')
  if name.startswith('SW_') and typ:
   if b'\x011\x011' in a:aa=bytearray(a);struct.pack_into('<h',aa,19,0);a=bytes(aa)
   elif b'\x013\x013' in a:aa=bytearray(a.replace(b'\x013\x013',b'\x012\x012'));struct.pack_into('<h',aa,19,0);a=bytes(aa)
   else:continue
  out.append((typ,a))
 for k,v in props.items():
  if k not in seen:out.append((0,f'|RECORD=41|OwnerPartId=-1|IsHidden=T|FontID=1|Name={k}|Text={v}|UniqueID={uuid.uuid4().hex[:8].upper()}'.encode()+b'\0'))
 if name in models:
  oi=len(out);out.append((0,b'|RECORD=44\0'));mi=len(out);fp=models[name]
  out.append((0,f'|RECORD=45|OwnerIndex={oi}|ModelName={fp}|ModelType=PCBLIB|DatafileCount=1|ModelDatafileEntity0={fp}|ModelDatafileKind0=PCBLib|ModelDatafile0=SmartClimate_BOM.PcbLib|IsCurrent=T|UniqueID={uuid.uuid4().hex[:8].upper()}'.encode()+b'\0'))
  out.extend([(0,f'|RECORD=46|OwnerIndex={mi}'.encode()+b'\0'),(0,f'|RECORD=48|OwnerIndex={mi}'.encode()+b'\0')])
 n['streams'][i]=pack(out)
io.write(n,'SmartClimate_BOM.SchLib');Path('Documentation/SmartClimate_Selected_Parts.json').write_text(json.dumps(selected,indent=2),encoding='utf-8');print('Selected manufacturer parts and completed L1/SW footprint associations')
