# Develop

## Sources

_poem_'s 廣韻 data:

- 廣韻(20170209).csv: From [廣韻字音表](https://zhuanlan.zhihu.com/p/20430939), created by _poem_

Maintained by NK2028:

- 小韻表.csv: 音韻地位 and 反切
- split.csv: Details of 小韻s with multiple 音韻地位s
- 字序表: Correct order of 廣韻's entries
  - `poem_*` fields refer to _poem_'s 廣韻字音表
  - `sbgy_*` fields refer to [宋本廣韻データ](https://kanji-database.sourceforge.net/dict/sbgy/index.html)
  - `ytenx_*` fields refer to [韻典網](https://ytenx.org/)
    - Data is taken from commit `d95d247` (2023-12-21), which differs from the current (as of Jan. 2025) deployed version (commit `3666370` 2020-03-23) by two 字頭s (小韻 1326 茅→芧, 小韻 2882 匕→𠤎)
- patches.csv: Corrections to _poem_'s data

## Build

```sh
python build.py
python check.py
```
