from pathlib import Path
s=Path('complete_resistors.py').read_text().split('import re,uuid,json')[0].replace("p=pathlib.Path('Schlib1.SchLib')","p=pathlib.Path('PcbLib1.PcbLib')")
exec(s)
for i,e in enumerate(entries):
 if e[66]:
  print(i,ename(e),e[66],len(data(e)) if e[66]==2 else '')
  if e[66]==2 and ename(e) in ('Header','Parameters'):print(repr(data(e)[:600]))
