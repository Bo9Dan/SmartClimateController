from pathlib import Path
import library_io as io,struct,re,uuid,json,shutil
src=io.setup('Schlib1.SchLib');rec=src['records'];pack=src['packed'];fld=lambda r:dict(p.split(b'=',1) for p in r.rstrip(b'\0').split(b'|') if b'=' in p)
def sf(r,k,v):
 parts=[p for p in r.rstrip(b'\0').split(b'|') if not p.startswith(k.encode()+b'=')];return b'|'.join(parts)+b'|'+k.encode()+b'='+str(v).encode()+b'\0'
syms={fld(rec(x)[0][1])[b'LibReference'].decode():rec(x) for x in src['streams'].values() if rec(x) and b'|RECORD=1|' in rec(x)[0][1]}
# independent file retains compatible source symbols and creates explicit generic variants.
rows=[]
def item(source,name,refs,desc,package,fp=None,**props):rows.append(dict(source=source,name=name,refs=refs,desc=desc,package=package,fp=fp,props=props))
item('U_STM32F103C8T6','U_STM32F103C8T6','U1','STM32F103C8T6 32-bit Cortex-M3 MCU, 64KB Flash, 72MHz, LQFP-48 7x7mm','LQFP-48 (7x7mm)',MP='STM32F103C8T6',MF='STMicroelectronics',Flash='64KB',Frequency='72MHz')
item('U_MP2307DN-LF-Z','U_MP2307DN-LF-Z','U2','MP2307DN-LF-Z 3A, 23V, 340kHz step-down DC-DC regulator, SOIC-8-EP','SOIC-8-EP',MP='MP2307DN-LF-Z',MF='Monolithic Power Systems',Current='3A',Voltage='23V',Frequency='340kHz')
item('U_BME280','U_BME280','U3','BME280 temperature, humidity and pressure sensor, LGA-8 2.5x2.5mm','LGA-8 (2.5x2.5mm)',MP='BME280',MF='Bosch')
item('J_USB-C_TYPE-C-31-M-12','J_USB-C_TYPE-C-31-M-12','J1','TYPE-C-31-M-12 USB Type-C USB2.0 receptacle, 16 contacts','SMD top mount',MP='TYPE-C-31-M-12',MF='Korean Hroparts Elec',LCSC='C165948',Datasheet='https://datasheet.lcsc.com/lcsc/1903211732_Korean-Hroparts-Elec-TYPE-C-31-M-12_C165948.pdf')
item('J_SM04B-SRSS-TB','J_SM04B-SRSS-TB','J2','JST SH 4-position 1.0mm right-angle side-entry SMT connector','JST SH 1x4 1.0mm SMT',MP='SM04B-SRSS-TB',MF='JST',Pitch='1.0mm')
for n,ref in [(4,'J3'),(3,'J4')]:item('J_Header_1x04_2.54mm_THT',f'J_Header_1x{n:02}_2.54mm_THT',ref,f'Pin header 1x{n}, 2.54mm pitch, vertical through hole',f'1x{n} P2.54 THT',f'HDR_1x0{n}_P2.54_THT',Pitch='2.54mm',MP='Generic',MF='Generic',**{'Number of Pins':str(n)})
item('Y_8MHz_12pF_3225','Y_8MHz_20pF_3225','X1','8MHz passive quartz crystal, +/-20ppm, CL=20pF, 3225 4-pad; manufacturer selection pending','3225 4-pad',Frequency='8MHz',**{'Load Capacitance':'20pF','Frequency Tolerance':'+/-20ppm','MP':'Generic','MF':'Generic','Selection Status':'Manufacturer and land pattern require verification'})
item('L_10uH_30%_1.7A_CDRH6D28','L_10uH_20%_2A_6x6mm','L1','10uH shielded power inductor; required Isat >=2A, DCR <50mOhm, 6x6mm; manufacturer selection pending','6x6mm shielded', 'L_10uH_6x6_PENDING',Inductance='10uH',Tolerance='20%',**{'Saturation Current Requirement':'>=2A','DC Resistance Requirement':'<50mOhm','MP':'Generic','MF':'Generic','Selection Status':'Do not place: exact manufacturer footprint required'})
item('D_Schottky_40V_3A_SMC','D_Schottky_40V_3A_SMA','D1','SS34 Schottky rectifier, 40V, 3A, SMA DO-214AC','SMA DO-214AC','D_SMA_DO214AC',MP='SS34',MF='Generic',Voltage='40V',Current='3A')
for color in ['Green','Red']:item('D_LED_Green_568nm_0603',f'D_LED_{color}_0603','LED1-LED3',f'{color} LED, 0603 (1608 metric)','0603 (1608 Metric)',MP='Generic',MF='Generic',Color=color,**{'Selection Status':'Generic LED; verify polarity and land pattern for selected part'})
item('SW_SPST_0.05A_24V','SW_SPST_3x4x2mm','SW1,SW2','Normally-open momentary tactile switch, 3x4x2mm; exact manufacturer selection pending','3x4x2mm','SW_3x4_PENDING',MP='Generic',MF='Generic',Configuration='SPST-NO',**{'Selection Status':'Do not place: exact manufacturer footprint required'})
for val,tol,volt,pkg,diel,source,refs in [('10uF','10','25','0805','X5R','C_10uF_10%_16V_0805','C1,C2'),('10nF','5','50','0603','X7R','C_10nF_5%_50V_0603','C3'),('100nF','10','16','0603','X7R','C_10nF_5%_50V_0603','C4-C8'),('22pF','2','50','0603','C0G','C_22pF_2%_50V_0603','C9,C10')]:
 item(source,f'C_{val}_{tol}%_{volt}V_{pkg}',refs,f'{val} +/-{tol}% {volt}V {diel} ceramic capacitor {pkg}',pkg,Capacitance=val,Tolerance=tol+'%',Voltage=volt+'V',Dielectric=diel,MP='Generic',MF='Generic')
for val,tol,refs in [('5k1','1','R1,R2'),('4k7','1','R3,R4'),('82k','1','R5'),('33k','1','R6'),('1k','5','R7-R9'),('10k','1','R10')]:
 item('R_10k_1%_1/10W_0603',f'R_{val}_{tol}%_1/10W_0603',refs,f'{val} Ohms +/-{tol}% 0.1W, 1/10W Chip Resistor 0603 (1608 Metric) Thick Film','0603 (1608 Metric)',Resistance=val,Tolerance=tol+'%',Power='0.1W',Technology='Thick Film',MP='Generic',MF='Generic')
# New clean SchLib built from known Altium records; no stale source purchasing parameters.
ns=io.setup('Schlib1.SchLib');ns['entries']=[bytearray(e) for e in ns['entries'][:2]];ns['streams']={1:ns['streams'][1]};struct.pack_into('<I',ns['entries'][0],76,io.F);struct.pack_into('<II',ns['entries'][1],68,io.F,io.F);ns['extra_children']={0:[1]}
for idx,row in enumerate(rows):
 si=io.add(ns,'Component%02d'%idx,1,0);di=io.add(ns,'Data',2,si);rs=syms[row['source']];out=[];mapping={};fp=row['fp']
 for oldidx,(t,r) in enumerate(rs):
  f=fld(r) if not t else {}
  if f.get(b'RECORD')==b'41':continue
  if row['refs']=='J4' and t==1 and b'\x014\x014' in r:continue
  mapping[oldidx]=len(out)
  if not t:
   if b'UniqueID=' in r:r=sf(r,'UniqueID',uuid.uuid4().hex[:8].upper())
   if f.get(b'RECORD')==b'1':
    r=re.sub(rb'\|%UTF8%ComponentDescription=[^|]*',b'',r);r=sf(sf(r,'LibReference',row['name']),'ComponentDescription',row['desc'])
    if row['refs']=='J4':r=sf(r,'AllPinCount','3')
   if f.get(b'RECORD')==b'45':
    if fp:r=sf(sf(r,'ModelName',fp),'ModelDatafileEntity0',fp)
    r=sf(r,'ModelDatafile0','SmartClimate_BOM.PcbLib')
   if f.get(b'RECORD')==b'34':r=sf(r,'Text',row['name'].split('_')[0]+'?')
  out.append((t,r))
 # OwnerIndex refers to records; preserve references after removing supplier parameters.
 for j,(t,r) in enumerate(out):
  f=fld(r) if not t else {}
  if b'OwnerIndex' in f:
   oi=int(f[b'OwnerIndex']);r=sf(r,'OwnerIndex',mapping.get(oi,oi));out[j]=(t,r)
 props={'Value':row['props'].get('Resistance',row['props'].get('Capacitance',row['props'].get('MP',row['name']))),'Comment':row['name'],'Package':row['package'],'BOM References':row['refs'],**row['props']}
 for k,v in props.items():out.append((0,f'|RECORD=41|OwnerPartId=-1|IsHidden=T|FontID=1|Color=8388608|Name={k}|Text={v}|UniqueID={uuid.uuid4().hex[:8].upper()}'.encode()+b'\0'))
 ns['streams'][di]=pack(out)
header=rec(ns['streams'][1])[0][1];header=re.sub(rb'\|(?:LibRef|PartCount|CompDescr)\d+=[^|\x00]*',b'',header);header=re.sub(rb'\|%UTF8%CompDescr\d+=[^|]*',b'',header);header=sf(header,'CompCount',str(len(rows)))
for i,row in enumerate(rows):header=sf(sf(sf(header,'LibRef'+str(i),row['name']),'PartCount'+str(i),'2'),'CompDescr'+str(i),row['desc'])
ns['streams'][1]=pack([(0,header)]);ki=io.add(ns,'SectionKeys',2,0);ns['streams'][ki]=pack([(0,('|KeyCount='+str(len(rows))+''.join(f'|LibRef{i}={r["name"]}|SectionKey{i}=Component{i:02}' for i,r in enumerate(rows))).encode()+b'\0')])
io.write(ns,'SmartClimate_BOM.SchLib');Path('Documentation/SmartClimate_BOM_Manifest.json').write_text(json.dumps(rows,indent=2),encoding='utf-8');print('Built',len(rows),'symbols')
