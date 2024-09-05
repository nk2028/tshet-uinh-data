import csv


# 「通俗地位」
音韻地位_patches = {
    '892': ('幫二庚平', '幫二耕平'),
    '1016': ('明一侯平', '明三C尤平'),
    '3059': ('明一侯去', '明三C尤去'),
}
# 補全缺失釋義補充
釋義補充_patch_from = {
    ('949', '蔆'): None,
}
釋義補充_patch_to = {
    ('949', '菱'): ('949', '蔆', 0),
    ('949', '䔖'): ('949', '蔆', 0),
}


def process_音韻地位(row: list[str]) -> str:
    母, 呼, 等類, 韻, 聲 = row[10:15]
    if not 母:
        return ''
    if (pos := 韻.find('→')) != -1:
        韻 = 韻[pos + 1 :]
    # NOTE 原資料莊組真殷韻依原貌。由於資料中已列「韻目原貌」，故地位不需再分
    if 韻 in ('真', '殷') and 呼 == '開' and 母 in tuple('莊初崇生俟'):
        韻 = '臻'
    return 母 + 呼 + 等類 + 韻 + 聲


def fix_pua(s: str) -> str:
    fixed = s.replace('\uee42', '𧞬').replace('\uece0', '勳')
    for ch in fixed:
        assert not (
            0xE000 <= ord(ch) <= 0xF8FF
        ), f'PUA character U+{ord(ch):04x} in {repr(s)}'
    return fixed


def main():
    小韻_data: dict[str, list[str]] = {}
    with open('src/rime-table-0b69606.tsv') as fin:
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
        for row in csv.DictReader(fin):
            # Formerly used fields (field number is 1-based, same as awk & MS Excel):
            # '廣韻反切(覈校後)',  # 21
            # '廣韻字頭原貌(覈校前)',  # 24
            # '廣韻頁序',  # 57
            (
                增刪說明,
                反切原貌,
                字頭,
                釋義,
                釋義補充,
                韻目原貌,
                小韻號原貌,
                小韻內字序,
            ) = (
                row[key]
                for key in (
                    '字頭-補',  # 19
                    '廣韻反切原貌(覈校前)',  # 20
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
            patch = 音韻地位_patches.get(小韻號)
            if patch is not None:
                assert (
                    音韻地位 == patch[0]
                ), f'invalid patch: expect {patch[0]} -> {patch[1]}, got {音韻地位}'
                音韻地位 = patch[1]

            反切 = 小韻_data[小韻號][2]
            if 反切 == '無':
                反切 = ''

            if len(反切原貌) != 2 or 反切原貌 == 反切:
                反切原貌 = ''

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
                        反切原貌,
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
        key = 條目[1][0], 條目[1][6]
        if (patch := 釋義補充_patch_to.get(key)) is not None:
            assert not 條目[1][8], f'條目 already containing 釋義補充: {條目[1]}'
            條目[1][8] = 釋義補充_patch_from[(patch[0], patch[1])][patch[2]]

    廣韻_data.sort(key=lambda x: x[0])

    last_原小韻號 = 0
    小韻內字序 = 0
    with open('韻書/廣韻.csv', 'w', newline='') as fout:
        print(
            '小韻號,小韻內字序,韻目原貌,音韻地位,反切,反切原貌,字頭,釋義,釋義補充',
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
