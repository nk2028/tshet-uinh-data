# qieyun-data [![](https://github.com/nk2028/qieyun-data/workflows/Check/badge.svg)](https://github.com/nk2028/qieyun-data/actions?query=workflow%3ACheck)

A database of the phonological position of the Qieyun phonological system of Chinese characters, based on Guangyun.

The data is in [`data.csv`](https://github.com/nk2028/qieyun-data/blob/main/data.csv).

The data is originally extracted from [廣韻字音表](https://zhuanlan.zhihu.com/p/20430939), created by poem.

Build

```sh
git checkout source -- '廣韻(20170209).csv'
python build.py
python check.py
```
