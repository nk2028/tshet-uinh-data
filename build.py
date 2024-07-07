import csv


幫組 = tuple('幫滂並明')
幫見影組 = tuple('幫滂並明見溪羣疑影曉匣云')


def process_音韻地位(row: list[str]) -> str:
    母, 呼, 等類, 韻, 聲 = row[10:15]
    if not 母:
        return ''
    if (pos := 韻.find('→')) != -1:
        韻 = 韻[pos + 1 :]
    if 等類 == '四(?)':
        等類 = '三' if 韻 in ('脂', '麻') else '二'
    等類 = 等類.replace('(', '')
    等類 = 等類.replace(')', '')
    if 母 in 幫見影組 and 等類 == '三':
        if 韻 == '麻' or (韻 == '幽' and 母 not in 幫組):
            等類 += 'A'
        elif 韻 == '幽' or (韻 == '蒸' and (呼 == '合' or 母 in 幫組)):
            等類 += 'B'
        else:
            等類 += 'C'
    return 母 + 呼 + 等類 + 韻 + 聲


def main():
    小韻_data: dict[str, list[str]] = {}
    with open('src/rime-table-bfa9b50.tsv') as fin:
        next(fin)
        for line in fin:
            row = line.rstrip('\n').split('\t')
            小韻號 = row[0]
            小韻_data[小韻號] = row

    音韻地位_data: dict[str, str] = {
        key: process_音韻地位(row) for key, row in 小韻_data.items()
    }

    has_細分: dict[str, list[str]] = {}
    小韻細分_data: dict[str, list[str]] = {}
    with open('src/split.csv') as fin:
        next(fin)
        for row in csv.reader(fin):
            小韻號 = row[0]
            assert 小韻號[-1].isalpha()
            反切 = row[1]
            assert (
                小韻_data[小韻號][2] == 反切
            ), f'反切 mismatch in 小韻 #{小韻號}, 小韻_data: {小韻_data[小韻號][2]}, 小韻細分_data: {反切}'
            has_細分.setdefault(小韻號[:-1], []).append(小韻號[-1])
            小韻細分_data[小韻號] = row

    小韻細分_coverage: dict[str, set[str]] = {}
    廣韻_data: list[tuple[tuple[int, float], list[str]]] = []
    with open('src/廣韻(20170209).csv') as fin:
        rows = csv.reader(fin)

        header = next(rows)
        success = True
        for [idx, field] in (
            (18, '字頭-補'),
            (19, '廣韻反切原貌(覈校前)'),
            (20, '廣韻反切(覈校後)'),
            (23, '廣韻字頭原貌(覈校前)'),
            (24, '廣韻字頭(覈校後)'),
            (25, '廣韻釋義'),
            (26, '釋義補充'),
            (39, '廣韻韻部原貌(調整前)'),
            (56, '廣韻頁序'),
            (58, '小韻序'),
            (59, '小韻內字序'),
        ):
            if header[idx] != field:
                success = False
                print(
                    f'[Error] header mismatch: expected {repr(field)}, got header[{idx}] = {repr(header[idx])}'
                )
        if not success:
            print()
            print(list(enumerate(header)))
            exit(2)

        for row in rows:
            (
                增刪說明,
                字頭,
                釋義,
                釋義補充,
                韻目原貌,
                小韻號原貌,
                小韻內字序,
            ) = (
                row[18],
                row[24],
                row[25],
                row[26],
                row[39],
                row[58],
                row[59],
            )

            if 增刪說明 == '應刪':
                continue

            order_key = (int(小韻號原貌), float(小韻內字序))

            # 小韻號
            if 小韻號原貌 in has_細分:
                for 細分 in has_細分[小韻號原貌]:
                    小韻號 = 小韻號原貌 + 細分
                    if 字頭 in 小韻細分_data[小韻號][2]:
                        小韻細分_coverage.setdefault(小韻號, set()).add(字頭)
                        break
                else:
                    raise ValueError(
                        f'cannot determine 小韻細分 for {字頭} (小韻 #{小韻號原貌})'
                    )
            else:
                小韻號 = 小韻號原貌

            音韻地位 = 音韻地位_data[小韻號]
            反切 = 小韻_data[小韻號][2]
            if 反切 == '無':
                反切 = ''

            字頭又作 = {
                '𩏑': '韓',
                '𧖴': '脈',
            }.get(字頭, '')

            廣韻_data.append(
                (
                    order_key,
                    [
                        小韻號,
                        小韻內字序,
                        韻目原貌,
                        音韻地位,
                        反切,
                        字頭,
                        字頭又作,
                        釋義,
                        釋義補充,
                    ],
                )
            )

    for 小韻號, cov in 小韻細分_coverage.items():
        specified = set(小韻細分_data[小韻號][2])
        diff = specified - cov
        assert not diff, f'字頭 listed in 小韻細分_data but not seen: {"".join(sorted(diff))} (小韻 #{小韻號})'

    廣韻_data.sort(key=lambda x: x[0])

    last_原小韻號 = 0
    小韻內字序 = 0
    with open('韻書/廣韻.csv', 'w') as fout:
        print(
            '小韻號,小韻內字序,韻目原貌,音韻地位,反切,字頭,字頭又作,釋義,釋義補充',
            file=fout,
        )
        for (原小韻號, _), row in 廣韻_data:
            if 原小韻號 != last_原小韻號:
                last_原小韻號 = 原小韻號
                小韻內字序 = 0
            小韻內字序 += 1
            row[1] = 小韻內字序
            print(*row, sep=',', file=fout)


if __name__ == '__main__':
    main()
