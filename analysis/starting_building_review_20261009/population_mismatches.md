# 人口历史地区归属失配

只校验人口初始化中的region_state与州主是否匹配，不把脚本size当作游戏中已成功生成的人口；未计算迁移、人口增长或人口倍率。

|州|实际州主|错误地区国家|人口size合计|来源|
|---|---|---|---:|---|
|纽约 (STATE_NEW_YORK)|NRHD|HHWO|2,221,000|common/history/pops/05_north_america.txt:57|
|肯塔基 (STATE_KENTUCKY)|SLOF|USAF|744,376|common/history/pops/05_north_america.txt:595|
|萨哈林 (STATE_SAKHALIN)|SKH,AIN,ULT,HTS|EZO|640|common/history/pops/11_east_asia.txt:1753|
