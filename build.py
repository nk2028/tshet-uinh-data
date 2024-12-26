import csv
from dataclasses import dataclass


# 補全缺失釋義補充
釋義補充_patch_from = {
    ('949', '蔆'): None,
}
釋義補充_patch_to = {
    ('949', '菱'): ('949', '蔆', 0),
    ('949', '䔖'): ('949', '蔆', 0),
}


def fix_pua(s: str) -> str:
    fixed = s.replace('\uee42', '𧞬').replace('\uece0', '勳')
    for ch in fixed:
        assert not (
            0xE000 <= ord(ch) <= 0xF8FF
        ), f'PUA character U+{ord(ch):04x} in {repr(s)}'
    return fixed


@dataclass
class 小韻Row:
    小韻號: str
    首字: str
    反切: str
    音韻地位: str


def main():
    小韻_data: dict[str, 小韻Row] = {}
    with open('src/小韻表.tsv') as fin:
        header = next(fin)
        assert header.rstrip('\n').split('\t') == [
            '小韻號',
            '首字',
            '反切',
            '音韻地位',
        ], repr(header)
        for line in fin:
            row = line.rstrip('\n').split('\t')
            小韻_data[row[0]] = 小韻Row(*row)

    has_細分: dict[str, list[str]] = {}
    小韻細分_data: dict[str, list[str]] = {}
    with open('src/split.csv') as fin:
        next(fin)
        for row in csv.reader(fin):
            小韻號 = row[0]
            assert 小韻號[-1].isalpha()
            反切 = row[1]
            assert (
                小韻_data[小韻號].反切 == 反切
            ), f'反切 mismatch in 小韻 #{小韻號}, 小韻_data: {小韻_data[小韻號][2]}, 小韻細分_data: {反切}'
            has_細分.setdefault(小韻號[:-1], []).append(小韻號[-1])
            小韻細分_data[小韻號] = row

    小韻細分_coverage: dict[str, set[str]] = {}
    廣韻_data: list[tuple[tuple[int, float], list[str]]] = []
    with open('src/廣韻(20170209).csv') as fin:
        for row in csv.DictReader(fin):
            # Formerly used fields (field number is 1-based, same as awk & MS Excel):
            # '廣韻反切原貌(覈校前)',  # 20
            # '廣韻反切(覈校後)',  # 21
            # '廣韻字頭原貌(覈校前)',  # 24
            # '廣韻頁序',  # 57
            (
                增刪說明,
                字頭,
                釋義,
                釋義補充,
                韻目原貌,
                原書小韻號,
                小韻內字序,
            ) = (
                row[key]
                for key in (
                    '字頭-補',  # 19
                    '廣韻字頭(覈校後)',  # 25
                    '廣韻釋義',  # 26
                    '釋義補充',  # 27
                    '廣韻韻部原貌(調整前)',  # 40
                    '小韻序',  # 59
                    '小韻內字序',  # 60
                )
            )

            if 增刪說明 == '應刪':
                continue

            order_key = (int(原書小韻號), float(小韻內字序))

            # 小韻號
            if 原書小韻號 in has_細分:
                for 細分 in has_細分[原書小韻號]:
                    小韻號 = 原書小韻號 + 細分
                    if 字頭 in 小韻細分_data[小韻號][2]:
                        小韻細分_coverage.setdefault(小韻號, set()).add(字頭)
                        break
                else:
                    raise ValueError(
                        f'cannot determine 小韻細分 for {字頭} (小韻 #{原書小韻號})'
                    )
            else:
                小韻號 = 原書小韻號

            音韻地位 = 小韻_data[小韻號].音韻地位

            反切 = 小韻_data[小韻號].反切
            if 反切 == '-':
                反切 = ''

            # TODO patch 反切 in 釋義 (and in 釋義補充)

            釋義_key = (小韻號, 字頭)
            if 釋義_key in 釋義補充_patch_from:
                assert (
                    釋義補充_patch_from[釋義_key] is None
                ), f'duplicate (小韻號, 字頭): {釋義_key}'
                釋義補充_patch_from[釋義_key] = (釋義, 釋義補充)

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
                        釋義,
                        釋義補充,
                    ],
                )
            )

    for 小韻號, cov in 小韻細分_coverage.items():
        specified = set(小韻細分_data[小韻號][2])
        diff = specified - cov
        assert not diff, f'字頭 listed in 小韻細分_data but not seen: {"".join(sorted(diff))} (小韻 #{小韻號})'

    for 條目 in 廣韻_data:
        key = 條目[1][0], 條目[1][5]
        if (patch := 釋義補充_patch_to.get(key)) is not None:
            assert not 條目[1][7], f'條目 already containing 釋義補充: {條目[1]}'
            條目[1][7] = 釋義補充_patch_from[(patch[0], patch[1])][patch[2]]

    廣韻_data.sort(key=lambda x: x[0])

    last_原小韻號 = 0
    小韻內字序 = 0
    with open('韻書/廣韻.csv', 'w', newline='') as fout:
        print(
            '小韻號,小韻內字序,韻目原貌,音韻地位,反切,字頭,釋義,釋義補充',
            file=fout,
        )
        for (原小韻號, _), row in 廣韻_data:
            if 原小韻號 != last_原小韻號:
                last_原小韻號 = 原小韻號
                小韻內字序 = 0
            小韻內字序 += 1
            row[1] = str(小韻內字序)
            print(fix_pua(','.join(row)), file=fout)


if __name__ == '__main__':
    main()
