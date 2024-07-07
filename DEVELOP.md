# Develop

## Sources

- 廣韻(20170209).csv: From [廣韻字音表](https://zhuanlan.zhihu.com/p/20430939), created by poem.
- rime-table-bfa9b50.tsv: From [切韻新韻圖](https://phesoca.com/rime-table/) by unt, built from git commit `bfa9b50`.
- split.csv: Maintained here, ultimately also from 切韻新韻圖.

## Build

```sh
python build.py
python check.py
```

## Remarks

- poem 表註「應補」者，給出 Unicode 字頭者均可見於原表末尾（小韻內字序號帶 .5），未給出者（以 IDS 或文字描述字頭）則仍未錄
- poem 表註「應換序」及「順序應爲」者，均未修正，且釋義補充字段亦有問題（似乎源自早先有女同車《廣韻全字表》底本差異）
