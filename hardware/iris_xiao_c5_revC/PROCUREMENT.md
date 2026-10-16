# RevC 国内采购记录

2026-10-16（Asia/Singapore）。延续本会话已核实的国内商品页，以下为查询时的页面信息，未下单或锁库。用户已授权采用TPS61023并取消PG检测，以及采用XQFN8版本的NT3H2111。

| 位号 / 型号 | 国内料号与链接 | 本会话查得的小量采购条件 |
|---|---|---|
| U1 TPS61023DRLR | C919459，[立创](https://item.szlcsc.com/997354.html) | 5颗起、¥1.5036/颗，页面现货39,550颗，最快4小时；4000颗为整卷数 |
| U3 NT3H2111W0FHKH | C710403，[立创](https://item.szlcsc.com/749561.html) | 1颗起¥3.79，10颗起¥3.04/颗；页面现货49,270颗；4000颗为整卷数 |
| L1 MWSA0518S-1R0MT | C408343，[立创](https://item.szlcsc.com/397745.html) | 1µH、Irms 8A、Isat 9A、DCR17mΩ；本轮页面现货3,285颗，5颗起¥0.94/颗 |
| U2 TPS22975DSGR | C524777，[立创](https://item.szlcsc.com/542832.html) | 5颗起¥1.4712/颗，国内现货16K+ |
| U5 SN74CB3Q3245PWR | C470961，[立创](https://item.szlcsc.com/477070.html) | 1颗起¥4.42，页面现货3,875颗 |
| Q2 AO3400A / AOS | C20917，[立创](https://item.szlcsc.com/21629.html) | 型号/SOT-23条目已找到，本会话未确认动态小量库存 |
| Q1 AO3401A / AOS | C15127，[立创](https://item.szlcsc.com/15801.html) | 同上 |
| BC847B,215 / Nexperia | C57668，[立创](https://item.szlcsc.com/58704.html) | 同上 |

U1从8脚TPS61033改成6脚TPS61023，不是原焊盘直接代换。没有PG；本版按用户要求移除相关检测和门控。R1/R2与L1也已重新选值。3.7A是芯片典型谷值开关限流，不能作为保证输出3.7A的采购指标。

U3为XQFN8/SOT902-3，1.6×1.6mm，型号尾部H为完整订货号的一部分。原厂明确中心金属区域不用于焊接，本地专用封装不放中心焊盘，八脚映射LA/VSS/SCL/FD/SDA/VCC/VOUT/LB保持不变。

FPC必须采购FH26W-39S-0.3SHW(60)。XIAO为整块Seeed ESP32-C5模块。无源器件仍需按BOM的阻值、电容有效容量、耐压、精度、封装和额定能力锁定完整厂家料号；R4脉冲电阻、F1保险丝、NFC天线不能仅按封装大小替代。这份记录不代表全部BOM均已确认国内现货。

复核方法：在立创国内站搜索精确C编号，确认完整型号、厂家、封装，输入所需数量后查看起订量、增量和实际交期。需要代贴片时另外核对嘉立创SMT库存及基础/扩展库；商城库存与SMT库存不可互相代替。

原RevB采购历史保存在相邻RevB工程。本版不采购已删除的R3/R17/Q6/Q8，也不再选TPS61033或TSSOP版本NT3H2111。

L1尺寸依据[顺络MWSA-S原厂图纸](https://www.sunlordinc.com/uploads/files/20230303/MWSA-S%C2%A0series%C2%A0of%C2%A0SMD%C2%A0Power%C2%A0Inductor.pdf)第2页，采用本地Sunlord_MWSA0518S封装。
