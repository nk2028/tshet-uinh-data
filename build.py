import csv


nk2028_dict = {}

with open('src/小韻表.csv') as fin:
    next(fin)
    for row in csv.reader(fin):
        row[0] = int(row[0])
        nk2028_dict[(row[0], row[1])] = row[2:]


小韻細分by字頭 = {
    409: ['礥㘋', '𧥺'],
    1043: ['飍', '烋'],
    1423: ['箉', '拐'],
    3521: ['孑𨥂趌', '訐䅥揭'],
    3708: ['憶億臆肊𠶷繶醷澺薏𦺳䗷𩍖檍𣚍癔', '抑𡊁'],
}

for v in 小韻細分by字頭.values():
    v[0] = set(v[0])
    v[1] = set(v[1])


def get小韻細分(小韻號: int, 字頭: str) -> int | None:
    if 小韻號 not in 小韻細分by字頭:
        return None
    for i, chs in enumerate(小韻細分by字頭[小韻號], 1):
        if 字頭 in chs:
            return i
    return None


def to描述(母: str, 呼: str | None, 等: str, 重紐: str | None, 韻: str, 聲: str) -> str:
    return 母 + (呼 or '') + 等 + (重紐 or '') + 韻 + 聲


rows = []
with open('src/廣韻(20170209).csv') as f:
    next(f)  # skip header
    for line in f:
        xs = line.rstrip('\n').split(',')
        反切覈校前, 反切, 字頭覈校前, 字頭, 釋義, 釋義補充, 韻目原貌, 圖片id, 小韻號, 小韻內字序 = xs[19], xs[
            20], xs[23], xs[24], xs[25], xs[26], xs[39], xs[56], xs[58], xs[59]

        小韻號 = int(小韻號)

        # 無反切的小韻
        if len(反切覈校前) != 2:
            反切覈校前 = ''
        if len(反切) != 2:
            反切 = ''

        小韻細分 = get小韻細分(小韻號, 字頭)
        key = (小韻號, str(小韻細分) if 小韻細分 is not None else '')

        nk2028代表字, nk2028反切, nk2028韻目原貌, 母, 呼, 等, 重紐, 韻, 聲 = nk2028_dict[key][:9]

        # 適應 Qieyun.js 音韻地位
        # 小韻表.csv 體系較 Qieyun.js 更為超前一些，故需適配一下

        # 等調整
        # Qieyun.js 對「等」的界定方式不同，致使以下四等要標為二三等
        # XXX 考慮今後統合兩者體系
        if 母 == '來' and 韻 == '庚' and 等 == '四':
            等 = '二'
        elif 母 in ('端', '透', '定', '泥') and 等 == '四':
            if 韻 in ('佳', '庚'):
                等 = '二'
            elif 韻 in ('脂', '麻'):
                等 = '三'

        # 驗證兩表一致性
        # NOTE poem 表的小韻內字序可能有 .5，不全是整數
        if 小韻內字序.strip() == '1':
            assert 字頭 == nk2028代表字, f'代表字 mismatch for 小韻 #{小韻號}: {字頭} != {nk2028代表字}'
            assert 韻目原貌 == nk2028韻目原貌, f'韻目原貌 mismatch for 小韻 #{小韻號}: {韻目原貌} != {nk2028韻目原貌}'

        描述 = ''
        if 母:
            描述 = to描述(母, 呼 or None, 等, 重紐 or None, 韻, 聲)

        if nk2028反切 != 反切:
            assert 反切 == 反切覈校前
            反切 = nk2028反切
        if 反切覈校前 == 反切:
            反切覈校前 = ''
        if 字頭覈校前 == 字頭:
            字頭覈校前 = ''

        rows.append((小韻號, 小韻內字序, 韻目原貌, 描述, 反切覈校前,
                     反切, 字頭覈校前, 字頭, 釋義, 釋義補充, 圖片id))

rows.sort(key=lambda row: (row[0], float(row[1])))

with open('韻書/廣韻.csv', 'w') as fout:
    print('小韻號,小韻內字序,韻目原貌,描述,反切覈校前,反切,字頭覈校前,字頭,釋義,釋義補充,圖片id', file=fout)
    for row in rows:
        print(*row, sep=',', file=fout)
