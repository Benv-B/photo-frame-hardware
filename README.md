# AirDrop ChLCD Photo Frame — Hardware

Open-source carrier board for a **ChLCD color e-paper frame with native iPhone AirDrop**.

The design connects a **XIAO ESP32-C5** to an **IRIS AW1005S102 panel and matching TCON**. It includes an NFC wake circuit, power latching and a three-AA battery input. NFC wakes the electronics; the photo is transferred through AirDrop.

![RevC carrier board](hardware/iris_xiao_c5_revC/output/pcb/board_top.png)

- [Firmware and project introduction](https://github.com/Benv-B/ESP32Drop)
- [KiCad project and assembly notes](hardware/iris_xiao_c5_revC) — use KiCad 10.0.6 or a compatible newer version.
- [Schematic PDF](hardware/iris_xiao_c5_revC/output/IRIS_C5_RevC_schematic.pdf) · [BOM](hardware/iris_xiao_c5_revC/output/BOM.csv) · [Gerbers](hardware/iris_xiao_c5_revC/output/gerbers)

The prototype has displayed photos received through AirDrop. Battery runtime and the complete NFC wake → display → shutdown cycle still need validation. Read the assembly notes for FPC orientation and the JP1 battery/USB configuration.

Original carrier design: [CERN-OHL-P-2.0](LICENSE). Project scripts: [0BSD](LICENSES/0BSD.txt). [Third-party library credits](THIRD_PARTY_NOTICES.md). IRIS panel/TCON internals, vendor firmware and waveforms are not included. Development and documentation were assisted by AI.

## 中文

这是 **AirDrop ChLCD 彩色电子纸相框**的自制载板：XIAO ESP32-C5 主控，连接 IRIS 屏幕和配套 TCON，带 NFC 唤醒、电源锁存和三节 AA 电池输入。

**KiCad、原理图、BOM、Gerbers 和配套固件均已开放。** 样机已完成 AirDrop 照片显示；续航和完整唤醒/断电流程仍需验证。ChLCD 属于胆甾相液晶显示，与 Spectra 6 的电泳技术不同。

装配前请看[接线说明](hardware/iris_xiao_c5_revC/README.md)。本仓库开源自制载板，不包含商用屏幕/TCON 内部固件和波形。
