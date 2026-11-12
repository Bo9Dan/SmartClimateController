from pathlib import Path
p=Path('rename_symbols.py');s=p.read_text();s=s.replace("def ename(e):", "names.update({'SS34':'D_Schottky_40V_3A_SMC','TSW-104-07-G-S':'J_Header_1x04_2.54mm_THT'})\ndef ename(e):")
s=s.replace("idx=next(i for i,e0 in enumerate(entries) if e0[66]==0)","idx=next((i for i,e0 in enumerate(entries) if ename(e0)=='SectionKeys'),None)\nif idx is None: idx=next(i for i,e0 in enumerate(entries) if e0[66]==0)")
s=s.replace("Naming_Backup_2026-11-05'","Naming_Backup_2026-11-05_Diode_Connector'")
s=s.replace('19 symbols preserved. 10 names changed.','19 symbols preserved. 12 names changed.').replace('Backup: Naming_Backup_2026-11-05/','Backup before initial renaming: Naming_Backup_2026-11-05/').replace("p.write_bytes(out)","p.write_bytes(out)")
p.write_text(s)
p=Path('Documentation/Component_Naming_Convention.md');s=p.read_text(encoding='utf-8');s=s.replace('Description and Comment patterns', '| Diode | `D_<Type>_<Voltage>_<Current>_<Package>` | `D_Schottky_40V_3A_SMC` |\n| Connector | `J_<Type>_<Rows>x<PinsPerRow>_<Pitch>_<Mounting>` | `J_Header_1x04_2.54mm_THT` |\n\nDescription and Comment patterns');s=s.replace('|\n\n| Diode','|\n| Diode');p.write_text(s,encoding='utf-8')
