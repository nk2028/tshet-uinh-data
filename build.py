import csv
import dataclasses
from dataclasses import dataclass
import re


@dataclass
class 小韻Row:
    小韻號: str
    首字: str
    反切: str
    音韻地位: str


def load_小韻表() -> dict[str, 小韻Row]:
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
    return 小韻_data


def load_小韻細分(
    小韻_data: dict[str, 小韻Row],
) -> tuple[dict[str, list[str]], dict[str, list[str]]]:
    has_細分: dict[str, list[str]] = {}
    小韻細分_data: dict[str, list[str]] = {}
    with open('src/split.csv') as fin:
        next(fin)
        for row in csv.reader(fin):
            小韻號 = row[0]
            assert 小韻號[-1].isalpha()
            反切 = row[1]
            assert 小韻_data[小韻號].反切 == 反切, (
                f'反切 mismatch in 小韻 #{小韻號}, 小韻_data: {小韻_data[小韻號][2]}, 小韻細分_data: {反切}'
            )
            has_細分.setdefault(小韻號[:-1], []).append(小韻號[-1])
            小韻細分_data[小韻號] = row
    return has_細分, 小韻細分_data


@dataclass
class 字序Row:
    原書小韻號: str
    小韻字號: str
    字: str
    poem_小韻內字序: str
    poem_字: str
    sbgy_id: str
    sbgy_字: str
    ytenx_小韻內字序: str
    ytenx_流水序: str
    ytenx_字: str


def load_字序表() -> dict[tuple[str, str], 字序Row]:
    字序_data: dict[tuple[str, str], 字序Row] = {}
    with open('src/字序表.csv') as fin:
        rows = csv.reader(fin)
        header = next(rows)
        assert header == [x.name for x in dataclasses.fields(字序Row)]
        for row in rows:
            key = (row[0], row[1])
            字序_data[key] = 字序Row(*row)
    return 字序_data


@dataclass
class Patch:
    原書小韻號: str
    小韻字號: str
    原字頭: str
    校正字頭: str
    原釋義: str
    校正釋義: str
    原釋義參照: str
    校正釋義參照: str
    當刪說明: str
    備注: str


def load_patches() -> dict[tuple[str, str], Patch]:
    patches: dict[tuple[str, str], Patch] = {}
    with open('src/patches.csv') as fin:
        rows = csv.reader(fin)
        header = next(rows)
        assert header == [x.name for x in dataclasses.fields(Patch)]
        for row in rows:
            key = (row[0], row[1])
            patches[key] = Patch(*row)
    return patches


@dataclass
class 廣韻Row:
    小韻號: str
    小韻字號: str
    韻目原貌: str
    音韻地位: str
    反切: str
    字頭: str
    字頭當刪: str
    釋義: str
    釋義參照: str


def main():
    小韻_data = load_小韻表()
    has_細分, 小韻細分_data = load_小韻細分(小韻_data)
    字序_data = load_字序表()
    patches = load_patches()

    小韻細分_coverage: dict[str, set[str]] = {}
    patch_coverage = set()

    poem_data: dict[tuple[str, str], dict[str, str]] = {}
    with open('src/廣韻(20170209).csv') as fin:
        for row in csv.DictReader(fin):
            key = (row['小韻序'], row['小韻內字序'])
            poem_data[key] = row

    廣韻_data: dict[tuple[str, str], list[str] | None] = {k: None for k in 字序_data}
    for 字序_key in 廣韻_data:
        原書小韻號, 小韻字號 = 字序_key
        poem_小韻內字序 = 字序_data[字序_key].poem_小韻內字序
        if not poem_小韻內字序:
            poem_反切 = poem_data[(原書小韻號, '1')]['廣韻反切(覈校後)']
            字頭 = ''
            釋義 = ''
            釋義參照 = ''
        else:
            poem_row = poem_data[(原書小韻號, poem_小韻內字序)]
            # Formerly used fields (field number is 1-based, same as awk & MS Excel):
            # '字頭-補',  # 19
            # '廣韻反切原貌(覈校前)',  # 20
            # '廣韻頁序',  # 57
            # '小韻序',  # 59
            # '小韻內字序',  # 60
            (
                字頭覈校說明,
                poem_反切,
                字頭原貌,
                字頭,
                釋義,
                釋義補充,
                韻目原貌,
            ) = (
                poem_row[key]
                for key in (
                    '字頭-覈校說明',  # 18
                    '廣韻反切(覈校後)',  # 21
                    '廣韻字頭原貌(覈校前)',  # 24
                    '廣韻字頭(覈校後)',  # 25
                    '廣韻釋義',  # 26
                    '釋義補充',  # 27
                    '廣韻韻部原貌(調整前)',  # 40
                )
            )
            if 字頭覈校說明 == '校':
                字頭 = f'[{字頭原貌}/{字頭}]'
            if not 釋義:
                釋義參照 = '下'
            elif 釋義補充:
                釋義參照 = '上'
            else:
                釋義參照 = ''

        # 修正
        字頭當刪 = ''
        if (patch := patches.get(字序_key)) is not None:
            assert patch.原字頭 == 字頭, (
                f'patching 小韻 #{原書小韻號}/{小韻字號} 字 "{patch.原字頭}", but the actual 字 is "{字頭}"'
            )
            patch_coverage.add(字序_key)
            assert patch.校正字頭, (
                f'patching 小韻 #{原書小韻號}/{小韻字號} 字 "{patch.原字頭}", but 校正字頭 is missing'
            )
            if patch.校正字頭.startswith('['):
                assert re.fullmatch(r'\[.+/.+\]', patch.校正字頭), (
                    f'invalid 校正字頭: "{patch.校正字頭}"'
                )
            if '～' in patch.校正字頭:
                assert not 字頭.startswith('['), (
                    f'cannot use "～" in 校正字頭 when 字頭 contains correction: "{字頭}"'
                )
            字頭 = patch.校正字頭.replace('～', 字頭)
            if 字頭.endswith('/-]'):
                字頭當刪 = patch.當刪說明 or '當刪'
            else:
                assert not patch.當刪說明, (
                    f'patching 當刪說明 on 小韻 #{原書小韻號}/{小韻字號} 字 "{patch.原字頭}", but 校正字頭 is not marked for removal'
                )
            if patch.校正釋義 or patch.原釋義:
                assert patch.原釋義 == 釋義, (
                    f'patching 釋義 on 小韻 #{原書小韻號}/{小韻字號} 字 "{patch.原字頭}", but the actual 釋義 is "{釋義}"'
                )
                corrected = re.sub(r'\[.+?/(?:-|(.+?))\]|[{}]', r'\1', patch.校正釋義)
                釋義 = corrected
            if patch.校正釋義參照 or patch.原釋義參照:
                assert patch.原釋義參照 == 釋義參照, (
                    f'patching 釋義參照 on 小韻 #{原書小韻號}/{小韻字號} 字 "{patch.原字頭}", but the actual 釋義參照 is "{釋義參照}"'
                )
                釋義參照 = patch.校正釋義參照
        elif 字序_data[字序_key].sbgy_字.endswith('/-]'):
            assert not 字頭.startswith('[')
            字頭 = f'[{字頭}/-]'
            字頭當刪 = '當刪'

        字_check = 字序_data[字序_key].字
        assert 字頭 == 字_check, (
            f'字頭 mismatch between 字序表 and patched data: "{字_check}" != "{字頭}" (小韻 {原書小韻號}/{小韻字號})'
        )
        if 字頭.startswith('['):
            校前, 校後 = 字頭[1:-1].split('/')
            字頭 = 校後 if 校後 != '-' else 校前

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

        # 音韻地位
        音韻地位 = 小韻_data[小韻號].音韻地位

        # 反切
        反切 = 小韻_data[小韻號].反切
        if 反切 == '-':
            反切 = ''

        # 釋義中反切
        if 小韻字號 == '1' and 反切:
            反切原貌 = re.sub(r'\[.\]|<.>|⦉.⦊|\(.\)|⦅.⦆', '', 反切)
            if 反切原貌 != poem_反切:
                assert 釋義.count(poem_反切 + '切') == 1, (
                    f'釋義 not containing {反切}切 exactly once: {釋義}'
                )
            釋義 = 釋義.replace(poem_反切 + '切', 反切原貌 + '切')

        廣韻_data[字序_key] = 廣韻Row(
            小韻號, 小韻字號, 韻目原貌, 音韻地位, 反切, 字頭, 字頭當刪, 釋義, 釋義參照
        )

    for 小韻號, cov in 小韻細分_coverage.items():
        specified = set(小韻細分_data[小韻號][2])
        diff = specified - cov
        assert not diff, (
            f'字頭 listed in 小韻細分_data but not seen: {"".join(sorted(diff))} (小韻 #{小韻號})'
        )
    assert patch_coverage == set(patches), (
        f'invalid patches: {", ".join(f"#{原書小韻號}/{小韻字號}" for 原書小韻號, 小韻字號 in set(patches) - patch_coverage)}'
    )

    with open('韻書/廣韻.csv', 'w', newline='') as fout:
        print(
            ','.join(x.name for x in dataclasses.fields(廣韻Row)),
            file=fout,
        )
        for 字序_key, row in 廣韻_data.items():
            assert row is not None, f'Missing: {字序_data[字序_key]}'
            print(','.join(dataclasses.astuple(row)), file=fout)


if __name__ == '__main__':
    main()
