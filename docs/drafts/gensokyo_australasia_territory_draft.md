# 幻想乡迁往澳大拉西亚：第一版领土分配
本阶段只调整初始领土与首都州；人物、人口、建筑及州区重做留待版图确认后处理。西澳大利亚完全保留原状。
分配直接读取原版 `13_australasia.txt` 的 `provinces` 表，再以原版城市、港口、农场、矿场、林场的省份作为空间锚点切分。所有纳入州的色码只出现一次。
| 州区 | 国家及省份数 | 合计 |
|---|---:|---:|
| STATE_NEW_SOUTH_WALES | MFSR 44、HITO 48、MYRN 56、HAKR 37、YSSK 11 | 196 |
| STATE_VICTORIA | MYRN 20、KZNH 29、EITR 13 | 62 |
| STATE_TASMANIA | MTOU 21 | 21 |
| STATE_QUEENSLAND | MRYA 195、YKYM 100、MIST 50、RDMK 22 | 367 |
| STATE_SOUTH_AUSTRALIA | CHRD 136、KZNH 34、HIGN 35 | 205 |
| STATE_NORTHERN_TERRITORY | CHRD 210、MKAI 13、YKYM 69 | 292 |
| STATE_NORTH_ISLAND | BYKR 28、HIGN 5、YKMF 2 | 35 |
| STATE_SOUTH_ISLAND | YKMF 25、BYKR 16、TENG 6 | 47 |

核验：八个州区共 `1225` 个原版省份；分配后 `1225` 个，重复 `0`，遗漏 `0`。
