## 用户改线后重新铺铜（2026-10-16）

当前 PCB 使用用户确认保存的主文件（2026-10-16 18:33:46），已由 KiCad 10.0.6 重新填充正、背面 GND 区。

635 个走线/过孔对象、66 个封装的位置及所有铜几何参数在铺铜前后一致；只重新计算铜区填充。H1–H4 另补充“仅 PCB 机械元素”属性，解决机械孔不属于原理图符号的提示，孔位和尺寸未变。DRC、未连接、原理图一致性问题均为 0，225 个电气引脚核对通过。详见 `output/pcb/copper_fill_audit.json`。

本次上传工程请使用 **KiCad 10.0.6 或更新兼容版本**。下文关于 KiCad 9 的描述是原始生成过程记录。正反面预览和 Gerber/钻孔文件已随当前板图重新导出；标准器件模型取自本机 KiCad 库，未提供模型的器件（含 XIAO）只显示焊盘。

# IRIS 智能相框载板 · Rev C

2026-10-16。三节一次性碱性 AA、XIAO ESP32-C5、用户已有 IRIS TCON 与39针排线，指定 FH26W-39S-0.3SHW(60) 连接器。RevC按用户确认改用 TPS61023，取消 PG 检测，保留 NFC 唤醒、电源保持和自动关机。RevB 工程保留在相邻目录。

## 本版改变

- U1 换为 **TPS61023DRLR / C919459**，六脚 SOT-563，同步升压、EN控制、真正关断。
- U3 换为 **NT3H2111W0FHKH / C710403**，XQFN8、1.6×1.6mm，中心金属区域不焊接。八个功能脚编号与原版本相同。
- 删除 PG 拉高电阻 R3、总线门控晶体管 Q6、PG 电平转换 Q8/R17。XIAO 的 D2/GPIO25 留空。
- U2.ON直接接 EN_LATCH；R15保持总线默认断开，Q7只由固件 BUS_EN 控制。没有追加电压检测芯片。
- R1=787kΩ/0.1%，R2=100kΩ/0.1%；L1改为顺络MWSA0518S-1R0MT（1µH，C408343）。PWM标称输出5.278V，PFM标称约5.33V，因此图中写“约5.3V”。电源网络名仍使用 `5V_BOOST`/`5V_SYS`，不是精确5.000V标称。

三张 A4 原理图按电源、NFC锁存、主控/FPC分组，组内直接连线、跨组网络标签。62个实体元件，较RevB减少4件。RevC属于电路修订，不能把其网表称为与RevB完全一致。

## 文件入口

- `IRIS_C5_RevC.kicad_pro`：保存的板图需 KiCad 10.0.6 或更新兼容版本，打开已有原理图无需运行生成脚本。
- `output/IRIS_C5_RevC_schematic.pdf`：三页原理图。
- `output/BOM.csv`：元件参数和封装；`PROCUREMENT.md`：采购证据及尚未锁定的物料。
- `output/native_netlist.xml`、`output/pin_connections.csv`：实际网表及逐引脚连接。
- `output/validation.json`、`output/ERC.json`：原生网表与设计清单核对、ERC结果。
- `output/revision_comparison.json`：与RevB相比的预期变更审计。
- `output/preview/`：原理图逐页渲染。
- `IRIS_C5_RevC.kicad_pcb`：已完成布线的双层 PCB，80×60mm；四个3.2mm非金属化安装孔。
- `output/pcb/board_top.png` / `board_bottom.png`：PCB 预览；不含未提供的器件三维模型。
- `output/pcb/top_copper.png` / `bottom_copper.png`：正、背面铜层与丝印，背面按翻板视角显示。
- `output/pcb/DRC.json` / `netlist_parity.json`：最终PCB检查与原理图逐引脚一致性报告。
- `output/gerbers/`：双层制板、钢网和PTH/NPTH钻孔文件，供首版样机使用。

## PCB 与装配

XIAO在左上，USB朝上板边；39针FPC在右边，排线插入方向朝板外。电池正负端在左侧，NFC外置线圈端子和手动唤醒按钮在下侧。升压功率环路先手工布线，信号布线完成后补齐双面接地过孔。主电源干线0.6–1.0mm，常规信号0.2mm，细间距焊盘局部0.15mm，最小铜间距0.15mm，常规过孔0.6/0.3mm。

板材可按双层FR-4、1.6mm厚、1oz铜起步。J3为0.3mm间距连接器，钢网按Hirose原厂0.10mm厚的开口尺寸制作；其铜和阻焊尺寸未改。XIAO底部GPIO5等焊盘也有接线，装配时需要焊接底部焊盘，不能仅焊两侧邮票孔。C10为DNP不装。外置NFC线圈需按实际结构调谐。

XIAO越过板边的USB外形和与焊盘冲突的模块外形线移至F.Fab，已同步本地封装库；模块铜焊盘、外形尺寸和电气连接保持不变。安装孔属于PCB机械元素，不增加电路BOM。最终DRC为0错误、0警告、0未连接；62个电气元件、225个引脚与原理图一致。

## 电源与工作过程

`3×AA → J1 → F1/Q1 → TPS61023 → TPS22975 → 5V_SYS → TCON 与 XIAO`

电池盒只接 J1 的 BAT+、BAT-。AA不能接XIAO的锂电BAT焊盘。XIAO 5V输入经过D1/JP1，D1阻止USB倒灌至公共电源；模块内置稳压器产生3.3V。TPS22975切换公共供电，Q2/R4用于关机放电，主控和TCON共用该供电。按TI手册§11，ON先于VIN有效不会损伤器件，但此时输出上升斜率不受CT保证；本版EN_LATCH同时开启升压与开关，保留C6作为样机调整位置，不能仅凭C6标称值认定满足TCON上升沿。

NFC射频场通过U3采能输出触发Q3/Q4锁存；后续由电池保持，不需要手机一直贴着。手机移开后，XIAO继续接收图片、刷新屏幕，完成后用PWR_OFF清除锁存。SW1为手动唤醒按钮。J2连接外置13.56MHz天线，C10默认不装，为实物调谐预留。

实际操作为：碰NFC唤醒 → 等设备启动 → 在iPhone选择照片并发送 → 刷新后关机。NFC不承担图片传输，也不自动替用户在iOS中选择照片。

## 主控引脚

| XIAO 焊盘 | 用途 |
|---|---|
| D0 / GPIO1 | PWR_OFF，高电平清除锁存 |
| D1 / GPIO0 | SPI_CS_N，经U5与33Ω串阻至J3.37 |
| D2 / GPIO25 | 不接，本版不读取PG |
| D3 / GPIO7 | BUS_EN，高电平接通SPI隔离开关 |
| D4 / GPIO23 | NFC SDA |
| D5 / GPIO24 | NFC SCL |
| D6 / GPIO11 | 不接，避免启动UART输出影响外设 |
| D7 / GPIO12 | TCON_INT，经U5接J3.24 |
| D8 / GPIO8 | SPI SCLK，经U5与33Ω至J3.34 |
| D9 / GPIO9 | SPI MISO，经U5接J3.36 |
| D10 / GPIO10 | SPI MOSI，经U5与33Ω至J3.35 |
| 底部焊盘16 / GPIO5 | BAT_ADC，测量锁存输出的分压，需校准压降 |

J3.1–6供电，7/10/13/16/19/22/25接地，31脚AGINGEN下拉；SPI模式不用的LVDS及指定NC脚留空。R21/R22在TCON侧提供CS默认高电平。FPC方向和排线两端映射以实物逐针核对。

## 固件配合

1. 启动先保持PWR_OFF=0、BUS_EN=0、SPI_CS_N=1。取消原PG_N检查；等待公共电源启动完成后再开启总线。首版可从100ms供电等待开始调试，最终以实测稳定时间确定，这不是PG检测的等效反馈。
2. 按IRIS应用说明完成TCON初始化、复位/唤醒和状态查询。原文复位后等待300ms、唤醒后5ms；10英寸刷新超时至少留15s。
3. ESP32Drop收图，转换为1024×768 BGR888，再按IRIS协议发送和刷新。完整像素帧2.25MiB；接收、解码和Wi-Fi仍需额外内存。2026-10-21 已完成 C5 AirDrop 到实屏的样机验证，详见固件仓库的 docs/iris-tcon.md。
4. 等TCON真实完成，再置BUS_EN=0。经NFC I²C读取RF_FIELD_PRESENT，确认手机场已消失至少500ms，再置PWR_OFF=1。U3.FD不用。
5. 添加接收超时、错误退出、看门狗和电池ADC判断。没有PG或新增硬件欠压锁定，因此软件不能假设电源在所有负载下都已经稳定。

USB调试时拔JP1。仅USB供XIAO、TCON未供电时必须保持BUS_EN=0；需要TCON工作时另外用电池/限流电源并按SW1开启。取消PG后，这项隔离由固件和调试操作负责，不能宣称有硬件自动联锁。

## 验证范围

225个实体引脚：188个连接、37个明确NC。原生KiCad网表与RevC冻结清单逐引脚比较；预期修订审计要求只有U1/U2/U3/U4/Q7/L1/R1修改、R3/R17/Q6/Q8删除，其余55件保持不变。最终原生ERC为0错误、0警告；原理图PDF均逐页查看。

2026-10-21 实板已完成色条和 iPhone 照片刷新；以下供电边界仍需进一步测量。TPS61023的3.7A为典型谷值开关限流，不是5V输出3.7A；整机实际启动/刷新电流和三AA压降需要样机验证，不承诺能覆盖屏幕资料中的3A浪涌。TCON要求5.0–5.5V、0.5–10ms电源边沿、断电间隔至少50ms；C6、放电R4、保险丝F1为首版值。

`validation/nfc_latch/`保留RevB锁存的ngspice验证，该部分电路未改。它只验证等效RF触发/清除等情形，不是实物NFC、TPS61023或TCON带载验证。`validation/before_layout/`是沿用的RevB历史资料，RevC当前结果以output目录为准。

## 复现

Windows下本次通过WSL Ubuntu的KiCad9.0.8生成。封装及符号随工程提供。`design_manifest.json`定义元件和连接；`layout_functional.py`控制原理图布局；`generate_schematic.py`生成原理图和BOM，已存在的.kicad_pro不覆盖。

直接打开已保存的KiCad工程即可查看和修改成品布线。工作目录内的`build_pcb.py`是初始放置/预布线脚本，运行会重建PCB，不能当作最终PCB的刷新命令；交付压缩包以已布线的原生PCB为准，只包含核对与原理图生成脚本。板图检查可运行`python3 validate_pcb.py`和`kicad-cli pcb drc --format json --output output/pcb/DRC.json IRIS_C5_RevC.kicad_pcb`。

```sh
python3 generate_schematic.py
kicad-cli sch export netlist --format kicadxml --output output/native_netlist.xml IRIS_C5_RevC.kicad_sch
kicad-cli sch erc --format json --output output/ERC.json IRIS_C5_RevC.kicad_sch
python3 validate_netlist.py
python3 compare_revision.py
kicad-cli sch export pdf --output output/IRIS_C5_RevC_schematic.pdf IRIS_C5_RevC.kicad_sch
```

依据：[TI TPS61023](https://www.ti.com/lit/ds/symlink/tps61023.pdf)、[TPS22975](https://www.ti.com/lit/ds/symlink/tps22975.pdf)、[NXP NT3H2111](https://www.nxp.com/docs/en/data-sheet/NT3H2111_2211.pdf)、[NXP采能说明](https://www.nxp.com/docs/en/application-note/AN11578.pdf)、[SN74CB3Q3245](https://www.ti.com/lit/ds/symlink/sn74cb3q3245.pdf)、Seeed官方C5电路与封装、Hirose图纸及用户提供的IRIS规格/应用说明。
