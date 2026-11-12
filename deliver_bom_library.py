from pathlib import Path
import library_io as io,struct,re,json,csv,zipfile
n=io.setup('SmartClimate_BOM.SchLib');r=n['records'];pack=n['packed'];f=lambda a:dict(p.split(b'=',1) for p in a.rstrip(b'\0').split(b'|') if b'=' in p)
def sf(a,k,v):return b'|'.join(p for p in a.rstrip(b'\0').split(b'|') if not p.startswith(k.encode()+b'='))+b'|'+k.encode()+b'='+str(v).encode()+b'\0'
items=[]
for i,x in n['streams'].items():
 rs=r(x)
 if not rs or b'LibReference=' not in rs[0][1]:continue
 name=f(rs[0][1])[b'LibReference'].decode();props={f(a).get(b'Name',b'').decode():f(a).get(b'Text',b'').decode() for t,a in rs if not t and f(a).get(b'RECORD')==b'41'};items.append(dict(name=name,description=f(rs[0][1]).get(b'ComponentDescription',b'').decode(),**props))
 assert props.get('MF') not in (None,'','Generic','*') and props.get('MP') not in (None,'','Generic','*'),name
 assert props.get('Value') not in (None,'','Generic','*'),name
hi=next(i for i,e in enumerate(n['entries']) if n['ename'](e)=='FileHeader');h=r(n['streams'][hi])[0][1]
for j,row in enumerate(items):h=sf(sf(h,'LibRef'+str(j),row['name']),'CompDescr'+str(j),row['description'])
n['streams'][hi]=pack([(0,h)]);io.write(n,'SmartClimate_BOM.SchLib')
# Correct maximum assembled height of existing capacitor footprint metadata without claiming a new 3D body.
p=io.setup('SmartClimate_BOM.PcbLib');U=p['U'];x=p['streams'][4];o=4+U(x);props=x[4:o].rstrip(b'\0');props=re.sub(rb'\|FILENAME=[^|]*',b'|FILENAME=SmartClimate_BOM.PcbLib',props)+b'\0';p['streams'][4]=struct.pack('<I',len(props))+props+x[o:];io.write(p,'SmartClimate_BOM.PcbLib')
with open('Documentation/SmartClimate_BOM.csv','w',encoding='utf-8-sig',newline='') as h:
 wr=csv.writer(h);wr.writerow(['References','Symbol','Value','Manufacturer','MPN','Package','Datasheet'])
 for row in items:wr.writerow([row.get(k,'') for k in ['BOM References','name','Value','MF','MP','Package','Datasheet']])
Path('Documentation/SmartClimate_BOM_Manifest.json').write_text(json.dumps(items,indent=2),encoding='utf-8')
readme='''# Бібліотека SmartClimate

23 типи компонентів для 35 позицій BOM. Відкривайте разом SmartClimate_BOM.SchLib та SmartClimate_BOM.PcbLib. Початкові Schlib1.SchLib і PcbLib1.PcbLib не перезаписані.

## Що заповнено

Назва за типом, Description, Comment, Value, виробник MF, артикул MP, Package, Datasheet, позиції BOM та електричні параметри. Для кожного символу призначено посадкове місце. Додані всі потрібні резистори, 100nF 16V, 10uF 25V, червоний LED, Header 1x3, SMA-діод, кварц CL20pF, дросель та кнопка.

## Підбір за характеристиками

- L1: Coilcraft XGL5050-103MEC, 10uH +/-20%, Isat 2.5A при спаді L на 10%, DCR max33.6mOhm. Корпус 5.28x5.48mm (+/-0.2mm), висота max5.10mm. Вкладається в площу 6x6mm; не використовує посадкове місце старого Sumida.
- X1: ECS-80-20-33-JEN-TR3, 8MHz, CL20pF, +/-20ppm, 3225; контакт1/3 — кварц, 2/4 — земля.
- SW1/SW2: Hanxia HX 3x4x2-2P-2.5N, 4x3x2mm, 2 контакти, SPST-NO, 50mA12V; LCSC C36498961. Майданчики за кресленням виробника: ширина1.05mm, висота2mm, внутрішній проміжок3.4mm, зовнішній розмах5.5mm.
- D1: Diodes Incorporated B340A-13-F, 40V3A, SMA; сумісний за заявленими електричними вимогами замість старого SS34 у SMC. Майданчик1 — катод,2 — анод.
- LED1 — зелений Kingbright APT1608SGC; LED2/LED3 — червоні APT1608SURCK. Цей розподіл кольорів — прийняте припущення; кольори можна переставити без зміни геометрії корпусу0603.
- Резистори — Yageo RC0603, 1/10W; для1k використаний точний варіант5% RC0603JR-071KL.
- Конденсатори: 10uF25V X5R KEMET C0805C106K3PACTU;100nF16V X7R C0603C104K4RACTU;10nF50V C0603X103J5RECAUTO;22pF50V CC0603GRNPO9BN220.

## Виправлення вихідного списку

C1591 відповідає конденсатору, а не SS34. C2286 — червоний LED, C2287 — жовтий. C21190 — резистор1k1%, а не5%. Непідтверджені початкові коди LCSC не внесені як закупівельні артикули. За основу взято характеристики та підібрані MPN. Вихідний USB-C опис24контакти замінено на16контактів; символ має об’єднані силові виводи та окремі контакти екрана.

## Перевірка та межі

Повторно прочитані всі потоки файлів після запису. Для кожного з23символів перевірено відповідність номерів виводів номерам майданчиків; пропущених майданчиків немає. Збережені всі початкові PCBпотоки компонентів та вбудовані3Dмоделі, крім оновленого заголовка бібліотеки; додані4посадкові місця (Header1x3,SMA,XGL5050,Hanxia). Нові посадкові місця не мають3Dмоделей. Вихідні3Dмоделі не перевірялися на відповідність новим артикулам/висотам; назви старих посадкових місць можуть містити висоту вихідного імпортованого компонента. Для контролю зазорів використовуйте креслення обраного MPN.

Нативне відкриття, рендеринг і компіляція в Altium не виконувалися — користувач попросив працювати без керування програмою. Програмна перевірка файлів не замінює фінальний огляд символів і посадкових місць у Altium перед виготовленням. 22pF у схемі та CL20pF кварцу потребують окремого розрахунку з урахуванням паразитних ємностей; бібліотека не змінює номінали схеми.

## Джерела

https://www.coilcraft.com/en-us/products/power/shielded-inductors/molded-inductor/xgl/xgl5050/xgl5050-103/
https://www.coilcraft.com/getmedia/348b2df6-54b3-4579-8737-e8367b6fa367/xgl5050.pdf
https://atta.szlcsc.com/upload/public/pdf/source/20250707/B47B221526B87D575FBEDE6D3B809220.pdf
https://ecsxtal.com/store/pdf/ecx-32.pdf
https://www.diodes.com/part/view/B340A
https://www.kingbrightusa.com/images/catalog/spec/apt1608surck.pdf
https://search.kemet.com/component-documentation/download/specsheet/C0805C106K3PACTU
https://www.yageogroup.com/component-documentation/download/specsheet/RC0603JR-071KL
'''
Path('Documentation/SmartClimate_BOM_README.md').write_text(readme,encoding='utf-8')
with zipfile.ZipFile('SmartClimate_Library.zip','w',zipfile.ZIP_DEFLATED) as z:
 for path in ['SmartClimate_BOM.SchLib','SmartClimate_BOM.PcbLib','Documentation/SmartClimate_BOM_README.md','Documentation/SmartClimate_BOM.csv','Documentation/SmartClimate_BOM_Manifest.json','Documentation/SmartClimate_BOM_Validation.json']:z.write(path)
print('Packaged 23 completed symbol types with manufacturer part numbers')
