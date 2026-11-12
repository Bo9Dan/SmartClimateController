from pathlib import Path
import zipfile
p=Path('Documentation/SmartClimate_BOM_README.md')
p.write_text('''# SmartClimate BOM library — review version

23 symbol types; matching PCB library includes original footprints and new generic Header 1x3 and SMA pad patterns. Main original libraries were not overwritten.

## Files

- SmartClimate_BOM.SchLib
- SmartClimate_BOM.PcbLib
- SmartClimate_BOM_Manifest.json: component parameters and source symbols.
- SmartClimate_BOM_Validation.json: pin counts and footprint associations.

## Completed

All requested resistor values including 33k, 82k 1%, and 1k 5%. Fixed the wrongly named 0.82-ohm source by using the 10k resistor geometry for new resistor variants. Added 100nF 16V X7R, 10uF 25V X5R, red LED, Header 1x3, SMA diode variant, and 20pF crystal specification. Filled Value, Comment, Package, Description and component-specific electrical fields. Retained original MCU, regulator and sensor pin geometry. Generic variants are explicitly identified as Generic, without false manufacturer or purchasing assignments.

## Open selections

L1: requested 10uH, >=2A saturation current, <50mOhm DCR, 6x6mm differs from existing Sumida CDRH6D28 (7x7mm, 65mOhm). The L1 symbol has no footprint assigned until a specific manufacturer part is chosen.

SW1/SW2: requested 3x4x2mm differs from the supplied C318884 code and the existing 1571294-1 model. The switch symbol has no footprint assigned until exact part selection.

Crystal: 8MHz CL20pF symbol is generic, with existing 3225 ECX32 geometry as a provisional land pattern. Verify chosen crystal manufacturer and pinout.

SMA and red LED patterns are generic; verify the selected manufacturer land pattern and polarity before production. Header 1x3 has 1.02mm plated holes and 1.8mm pads at 2.54mm pitch. Newly generated patterns contain pads only; they do not claim manufacturer 3D bodies or silkscreen/courtyard outlines.

## Catalog corrections

- C21190 is 1k 1%, rather than 5%.
- C1591 is a capacitor rather than SS34.
- C2286 is a red LED, while C2287 is yellow rather than red.
- C165948 is TYPE-C-31-M-12 with 16 contacts; source description saying 24 contacts corrected.

Sources: https://www.lcsc.com/product-detail/C1591.html ; https://jlcpcb.com/partdetail/C2286 ; https://jlcpcb.com/partdetail/C2287 ; https://jlcpcb.com/partdetail/C165948 ; https://www.lcsc.com/product-detail/C318884.html . Unverified BOM supplier codes were not assigned to unrelated manufacturer parts.

## Validation

Re-read every CFB stream after saving. Checked 23 unique symbol definitions, 2-pin resistor symbols, 3-pin Header 1x3, and existence of every assigned footprint in the PCB library index. Two unresolved model associations intentionally omitted. No native Altium open/render/compile validation performed, as requested by the user. This is a review library, not a production-approved library.

## Use

Open both new library files in Altium. Keep them together. Review unresolved selections before placing L1 or switches. Original Schlib1.SchLib and PcbLib1.PcbLib remain available.
''',encoding='utf-8')
with zipfile.ZipFile('SmartClimate_BOM_Review.zip','w',zipfile.ZIP_DEFLATED) as z:
 for f in ['SmartClimate_BOM.SchLib','SmartClimate_BOM.PcbLib','Documentation/SmartClimate_BOM_README.md','Documentation/SmartClimate_BOM_Manifest.json','Documentation/SmartClimate_BOM_Validation.json']:z.write(f)
print('Packaged review library')
