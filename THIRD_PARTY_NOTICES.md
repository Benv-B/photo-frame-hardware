# Hardware licenses and attribution

## Project-owned material

Copyright (c) 2026 Benv-B. The original carrier schematic, routed board, custom design work, BOM, fabrication outputs and project documentation are covered by CERN-OHL-P-2.0 (`LICENSE`). Project-owned Python design/validation scripts are covered by `LICENSES/0BSD.txt`. This grant does not replace the licenses of included third-party library material.

This public snapshot contains the RevC carrier, saved routing changes and refill/check outputs from 16 October 2026. On 22 October 2026 the project added public build/status documentation and these licensing notices; the electrical design was not changed for publication.

## KiCad libraries

The files in `hardware/iris_xiao_c5_revC/footprints/` are from the KiCad footprint libraries. The local Hirose FH26 and Texas DSG0008A footprints also derive from KiCad library footprints; the Hirose data includes project stencil verification. Embedded standard symbols/footprints retain their source attribution.

Copyright KiCad library contributors. License: CC-BY-SA-4.0 with the KiCad library exception. Copies are included as `LICENSES/KiCad-Libraries.md` and `LICENSES/CC-BY-SA-4.0.txt`. See [KiCad's explanation](https://www.kicad.org/libraries/license/) and [upstream footprints](https://gitlab.com/kicad/libraries/kicad-footprints).

## Seeed Studio XIAO

The XIAO ESP32-C5 module footprint is sourced from Seeed Studio's XIAO KiCad resources, linked from the [official C5 documentation](https://wiki.seeedstudio.com/xiao_esp32c5_getting_started/#resource). The corresponding official C5 design carries the **CC BY-SA 4.0** notice. Copyright Seeed Studio; the source attribution and CC-BY-SA terms are retained for this library material, separately from the original carrier design. Project modifications move module outline artwork to F.Fab while preserving pad geometry and electrical mapping.

## Purchased components and vendor documents

IRIS AW1005S102 and the matching TCON are purchased components. Their internal designs, firmware, display parameters and waveforms are not provided or relicensed. Manufacturer datasheets/manuals used during development are not included as project-owned source. The schematic PDF here is the project's own carrier schematic.

The bundled libraries and this prototype are provided without warranty. Vendor names identify compatible components and do not imply endorsement.
