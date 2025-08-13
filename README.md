# qieyun-data [![](https://github.com/nk2028/qieyun-data/workflows/Check/badge.svg)](https://github.com/nk2028/qieyun-data/actions?query=workflow%3ACheck)

A database of the Qieyun phonological system.

- 韻書
  - 王一：`王一.csv` (not completed)
  - 王三：`王三.csv` (小韻內部待校)
  - 廣韻 (澤存堂本, with corrections from 廣韻校本, 廣韻形聲考 etc.)：`廣韻.csv`
- 韻圖
  - 韻鏡（嘉吉本）：`韻鏡（嘉吉本）.csv` (not completed)
  - 韻鏡（古逸叢書本）：`韻鏡（古逸叢書本）.csv`
- 反切音韻地位
  - 王三：`王三反切音韻地位表.csv` (rev. Ayaka & unt)
  - 廣韻：`廣韻反切音韻地位表.csv` (beta)

## About fields in 韻書/廣韻.csv

- 小韻號: May contain suffix `a`/`b`/`c` if a 小韻 has multiple 音韻地位s
- 小韻字號: May contain suffix `a1`, `a2` etc for entries not present in 澤存堂本 but added back according to other versions of 廣韻 (chiefly according to 廣韻校本)
- 反切: May contain annotations:
  - 脫字：［徒］候【小韻 #3067 豆】
  - 訛字：士〈七〉演【小韻 #1625 淺】
  - 異體字正則化：袪狶（豨）【小韻 #1313 豈】
  - 改用其他來源的音韻地位（雙六角括號）: 姊宜〘規〙【小韻 #133 厜】
  - 替換成近似等價字，反切結果改變: 符咸〖䒦〗【小韻 #1155 凡】
  - 替換成音近字，反切結果改變: 式之〖脂〗【小韻 #157 尸】
  - 替換成同音字，反切結果不變: 甫｟府｠妄【小韻 #2918 放】
  - 替換成等價字，反切結果不變: 呼東｟紅｠【小韻 #32 烘】
  - 複合使用: 以沼｟小｠〈水〉【小韻 #1692a 鷕】
- 字頭: May contain annotations:
  - 應補字：［嬹］【小韻 #961】
  - 應刪字：｛𪈥｝【小韻 #318】
  - 校訛字：汦〈泜〉【小韻 #144】
- 字頭原貌 & 字頭: The character for the entry
  - A non-empty 字頭原貌 indicates a correction of the character
  - Additionally, an empty 字頭 indicates this entry in 澤存堂本 is erroneous and should be removed
- 字頭說明: contains notes about some of the corrections or removals
- 釋義參照:
  - `上` if 釋義 refers to the entry above ("同上", "俗", "古文" etc.)
  - `下` if it shares 釋義 with the entry below ("並上同", "並古文" etc.)
