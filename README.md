# NFC 智能相框硬件

基于 Seeed XIAO ESP32-C5、三节一次性碱性 AA 电池和 IRIS TCON 的智能相框载板。

- 主控：Seeed XIAO ESP32-C5。
- NFC：NT3H2111W0FHKH，外置线圈，通过采能触发整机电源锁存。
- 电源：TPS61023DRLR 升压，TPS22975DSGR 切换公共电源；取消 PG 检测。
- 屏幕接口：Hirose FH26W-39S-0.3SHW(60)，39 针 FPC，SPI 与已有 TCON 通信。
- PCB：80×60mm，双层，四个3.2mm安装孔。

## 文件入口

工程位于 `hardware/iris_xiao_c5_revC/`。请使用 **KiCad 10.0.6 或更新兼容版本**打开 `IRIS_C5_RevC.kicad_pro`。

- `IRIS_C5_RevC.kicad_pcb`：用户修改走线后重新填充 GND 铜区的板图。
- `output/IRIS_C5_RevC_schematic.pdf`：三页原理图。
- `output/BOM.csv`、`PROCUREMENT.md`：器件清单和采购记录。
- `output/pcb/`：检查报告、正反面预览和铺铜前后几何核对记录。
- `output/gerbers/`：与当前板图对应的制板/钢网/钻孔文件。

正常电池使用时短接 JP1；USB 调试时拔掉 JP1。SW1 是手动唤醒按钮。XIAO 底部焊盘也需焊接，不能仅焊两侧邮票孔。C10 默认不装。

本仓库保存样机设计，实物上电、屏幕刷新负载、NFC 天线调谐及 ESP32Drop 在 C5 上的运行仍需样机验证。详细电路、固件时序和装配说明见工程内 `README.md`。

## 本次铺铜来源与检查

采用用户确认保存的 2026-10-16 18:33:46 主板文件。铺铜保留现有走线、过孔、器件和铜区参数；DRC、未连接与原理图一致性检查均为 0 问题。

![PCB 正面](hardware/iris_xiao_c5_revC/output/pcb/board_top.png)
