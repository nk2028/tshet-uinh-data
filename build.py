import csv


v2_dict = {}
with open('v2音韻地位.csv') as fin:
    next(fin)
    for row in csv.reader(fin):
        v2_dict[int(row[0])] = row[1:]

第一地位override = {
    3708: set('癔'),
}

use第二地位 = set()
with open('廣韻(20170209).csv') as f, open('韻書/廣韻.csv', 'w') as g:
    next(f)  # skip header

    print('小韻號,韻目原貌,最簡描述,反切覈校前,反切,字頭覈校前,字頭,釋義,釋義補充,圖片id', file=g)

    for line in f:
        xs = line.rstrip('\n').split(',')
        反切覈校前, 反切, 字頭覈校前, 字頭, 釋義, 釋義補充, 韻目原貌, 圖片id, 小韻號, 小韻內字序 = xs[19], xs[
            20], xs[23], xs[24], xs[25], xs[26], xs[39], xs[56], xs[58], xs[59]

        小韻號 = int(小韻號)

        # 異體調整
        if 韻目原貌 == '真':
            韻目原貌 = '眞'

        # 無反切的小韻
        if len(反切覈校前) != 2:
            反切覈校前 = ''
        if len(反切) != 2:
            反切 = ''

        最簡描述, v2字頭, v2反切, _ = v2_dict[小韻號]
        if 小韻內字序.strip() == '1':
            assert 字頭 in v2字頭.split('/'), f'{字頭} not in {v2字頭}'

        if 最簡描述 == '(deleted)':
            最簡描述 = ''
        elif '/' in v2字頭:
            最簡描述 = 最簡描述.split('/')
            if 字頭 in 第一地位override.get(小韻號, set()):
                最簡描述 = 最簡描述[0]
            elif 小韻號 in use第二地位:
                最簡描述 = 最簡描述[1]
            else:
                v2字頭 = v2字頭.split('/')
                if 字頭 == v2字頭[1]:
                    use第二地位.add(小韻號)
                    最簡描述 = 最簡描述[1]
                else:
                    最簡描述 = 最簡描述[0]

        if v2反切 != 反切:
            assert 反切 == 反切覈校前
            反切 = v2反切
        if 反切覈校前 == 反切:
            反切 = ''
        if 字頭覈校前 == 字頭:
            字頭 = ''

        print(小韻號, 韻目原貌, 最簡描述, 反切覈校前, 反切, 字頭覈校前,
              字頭, 釋義, 釋義補充, 圖片id, sep=',', file=g)
