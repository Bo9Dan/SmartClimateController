# Component Field Reference

## Resistor

| Field | Pattern |
| --- | --- |
| Name | `R_<Resistance>_<Tolerance>_<Power>_<Package>` |
| Description | `<Resistance> Ohms ±<Tolerance>% <Power>W, <FractionalPower>W Chip Resistor <ImperialPackage> (<MetricPackage> Metric) <Qualification, if applicable> <Technology>` |
| Comment | `RES <Resistance> OHM <Tolerance>% <Power>W <ImperialPackage>` |

### Matching example

| Field | Example |
| --- | --- |
| Name | `R_3k4_1%_1/10W_0603` |
| Description | `3.4 kOhms ±1% 0.1W, 1/10W Chip Resistor 0603 (1608 Metric) Automotive AEC-Q200 Thick Film` |
| Comment | `RES 3.4K OHM 1% 1/10W 0603` |

### Additional name examples

```text
R_100R_10%_1/4W_0805
R_4k7_1%_1/16W_0402
```

## Other Components

| Type | Name pattern | Name example |
| --- | --- | --- |
| Capacitor | `C_<Capacitance>_<Tolerance>_<Voltage>_<Package>` | `C_10uF_5%_50V_0603` |
| Inductor | `L_<Inductance>_<Tolerance>_<Current>_<Package>` | `L_10uH_20%_0.5A_0805` |
| BJT | `Q_<Type>_<Voltage>_<Current>_<Package>` | `Q_NPN_40V_0.6A_SOT-23` |
| Switch | `SW_<Configuration>_<Current>_<Voltage>` | `SW_SP3T_0.1A_12V` |
| Diode | `D_<Type>_<Voltage>_<Current>_<Package>` | `D_Schottky_40V_3A_SMC` |
| Connector | `J_<Type>_<Rows>x<PinsPerRow>_<Pitch>_<Mounting>` | `J_Header_1x04_2.54mm_THT` |

Description and Comment patterns for these types are not yet defined.

## Additional symbol names

| Type | Name pattern | Name example |
| --- | --- | --- |
| IC / processor / integrated sensor | `U_<PartNumber>` | `U_STM32F103C8T6` |
| LED | `D_LED_<Color>_<Wavelength>_<Package>` | `D_LED_Green_568nm_0603` |
| Crystal | `Y_<Frequency>_<LoadCapacitance>_<Package>` | `Y_8MHz_12pF_3225` |
| Connector identified by part number | `J_<PartNumber>` or `J_<Type>_<PartNumber>` | `J_SM04B-SRSS-TB`, `J_USB-C_TYPE-C-31-M-12` |

For processors, keep the name concise: designator prefix and part number. Connector part numbers may be retained to distinguish mechanical variants.
