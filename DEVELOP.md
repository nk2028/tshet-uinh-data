# Develop

The data of 廣韻 is originally extracted from [廣韻字音表](https://zhuanlan.zhihu.com/p/20430939), created by poem.

Build

```sh
git restore -Ws source '廣韻(20170209).csv' 'v2音韻地位.csv'
python build.py
python check.py
```
