# qieyun-data [![](https://github.com/nk2028/qieyun-data/workflows/Check/badge.svg)](https://github.com/nk2028/qieyun-data/actions?query=workflow%3ACheck)

A database of the Qieyun phonological system.

## Usage

### Rhyme books

The data is in [`rhyme_book.csv`](https://github.com/nk2028/qieyun-data/blob/main/rhyme_book.csv).

Included documents:

- 王一 (partial)
- 廣韻

### Rhyme tables

The data is in [`rhyme_table.csv`](https://github.com/nk2028/qieyun-data/blob/main/rhyme_table.csv).

Included documents:

- 指微韻鑑（嘉吉本）(partial)
- 韻鏡（古逸叢書本）

## Develop

The data of rhyme books is originally extracted from [廣韻字音表](https://zhuanlan.zhihu.com/p/20430939), created by poem.

Build

```sh
git checkout source -- '廣韻(20170209).csv'
python build.py
python check.py
```
