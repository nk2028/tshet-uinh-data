from collections.abc import Iterable
import csv
import dataclasses
from dataclasses import dataclass
import re


@dataclass
class 小韻Row:
    小韻號: str
    首字: str
    音韻地位: str
    反切: str
    直音: str


def load_小韻表() -> tuple[
    dict[str, 小韻Row], dict[str, list[str]], dict[str, list[str]]
]:
    小韻_data = dict[str, 小韻Row]()
    細分號_by_原書小韻 = dict[str, list[str]]()
    細分轄字_by_小韻 = dict[str, list[str]]()
    with open('src/小韻表.csv') as fin:
        rows = csv.reader(fin)
        header = next(rows)
        assert header == [
            '小韻號',
            '首字',
            '音韻地位',
            '反切',
            '直音',
            '細分轄字',
        ], repr(header)
        for row in rows:
            小韻號, 首字, 音韻地位, 反切, 直音, 細分轄字 = row
            小韻_data[小韻號] = 小韻Row(小韻號, 首字, 音韻地位, 反切, 直音)
            if 小韻號[-1].isalpha():
                原書小韻號 = 小韻號[:-1]
                細分號_by_原書小韻.setdefault(原書小韻號, []).append(小韻號[-1])
                細分轄字_by_小韻[小韻號] = list(細分轄字)
    for 原書小韻號, 各細分號 in 細分號_by_原書小韻.items():
        assert 各細分號 == [chr(ord('a') + i) for i in range(len(各細分號))], (
            f'細分號 for 小韻 #{原書小韻號} out of order: {各細分號}'
        )
    return 小韻_data, 細分號_by_原書小韻, 細分轄字_by_小韻


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
    字頭說明: str
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


def split_head_with_ids(s: str) -> tuple[str, str]:
    if not s:
        raise ValueError('empty string')
    if s[0] in (
        '⿰',
        '⿱',
        '⿴',
        '⿵',
        '⿶',
        '⿷',
        '⿸',
        '⿹',
        '⿺',
        '⿻',
        '⿼',
        '⿽',
        '㇯',
    ):
        num_parts = 2
    elif s[0] in ('⿲', '⿳'):
        num_parts = 3
    elif s[0] in ('⿾', '⿿', '〾'):
        num_parts = 1
    else:
        return s[0], s[1:]
    idc = s[0]
    parts = []
    rest = s[1:]
    for i in range(num_parts):
        # if not rest:
        #     break
        part, rest = split_head_with_ids(rest)
        parts.append(part)
    return idc + ''.join(parts), rest


def iter_chars_with_ids(s: str) -> Iterable[str]:
    while s:
        head, s = split_head_with_ids(s)
        yield head


# NOTE Only handles simple annotations for now.
def remove_annotations(original: str) -> str:
    original = original.replace('`', '')
    chars = list(iter_chars_with_ids(original))
    n = len(chars)
    removable = [False] * n
    i = 0
    while i < len(chars):
        ch = chars[i]
        if ch in ('［', '］'):
            removable[i] = True
            i += 1
        elif ch == '｛':
            j = chars.index('｝', i + 1)
            removable[i : j + 1] = (True,) * (j + 1 - i)
            i = j + 1
        elif ch == '〈':
            j = chars.index('〉', i + 1)
            removable[i] = removable[j] = True
            k = j - i - 1
            assert not any(removable[i - k : i])
            removable[i - k : i] = (True,) * k
            i = j + 1
        else:
            i += 1
    return ''.join(ch for ch, rm in zip(chars, removable) if not rm)


@dataclass
class 廣韻Row:
    小韻號: str
    小韻字號: str
    韻目原貌: str
    音韻地位: str
    反切: str
    直音: str
    字頭: str
    字頭說明: str
    釋義: str
    釋義參照: str


def main():
    小韻_data, 細分號_by_原書小韻, 細分轄字_by_小韻 = load_小韻表()
    字序_data = load_字序表()
    patches = load_patches()

    小韻號_seen = set[str]()
    小韻細分_coverage = dict[str, set[str]]()
    patch_coverage = set[tuple[str, str]]()

    poem_data = dict[tuple[str, str], dict[str, str]]()
    with open('src/廣韻(20170209).csv') as fin:
        for row in csv.DictReader(fin):
            key = (row['小韻序'], row['小韻內字序'])
            poem_data[key] = row

    廣韻_data: dict[tuple[str, str], 廣韻Row | None] = {k: None for k in 字序_data}
    for 字序_key in 廣韻_data:
        原書小韻號, 小韻字號 = 字序_key
        poem_小韻內字序 = 字序_data[字序_key].poem_小韻內字序
        if not poem_小韻內字序:
            poem_反切 = poem_data[(原書小韻號, '1')]['廣韻反切(覈校後)']
            字頭 = ''
            釋義 = ''
            釋義參照 = ''
            韻目原貌 = poem_data[(原書小韻號, '1')]['廣韻韻部原貌(調整前)']
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
                字頭 = f'{字頭原貌}〈{字頭}〉'
            if not 釋義:
                釋義參照 = '下'
            elif 釋義補充:
                釋義參照 = '上'
            else:
                釋義參照 = ''

        # 修正
        字頭說明 = ''
        if (patch := patches.get(字序_key)) is not None:
            assert patch.原字頭 == 字頭, (
                f'patching 小韻 #{原書小韻號}/{小韻字號} 字 "{patch.原字頭}", but the actual 字 is "{字頭}"'
            )
            patch_coverage.add(字序_key)
            assert patch.校正字頭, (
                f'patching 小韻 #{原書小韻號}/{小韻字號} 字 "{patch.原字頭}", but 校正字頭 is missing'
            )
            # TODO Stricter format check
            assert re.fullmatch(
                r'｛.+｝|［.+］|.+〈.+〉|[^｛｝［］〈〉]+', patch.校正字頭
            ), f'invalid 校正字頭: "{patch.校正字頭}"'
            if '～' in patch.校正字頭:
                assert 字頭 and 字頭[-1] not in tuple('｝］〉'), (
                    f'cannot use "～" in 校正字頭 when 字頭 contains correction or is empty: "{字頭}"'
                )
            字頭 = patch.校正字頭.replace('～', 字頭)

            # 字頭說明 is an added field, thus it does not have an original value
            字頭說明 = patch.字頭說明

            if patch.校正釋義 or patch.原釋義:
                assert patch.原釋義 == 釋義, (
                    f'patching 釋義 on 小韻 #{原書小韻號}/{小韻字號} 字 "{patch.原字頭}", but the actual 釋義 is "{釋義}"'
                )
                釋義 = remove_annotations(patch.校正釋義)
            if patch.校正釋義參照 or patch.原釋義參照:
                assert patch.原釋義參照 == 釋義參照, (
                    f'patching 釋義參照 on 小韻 #{原書小韻號}/{小韻字號} 字 "{patch.原字頭}", but the actual 釋義參照 is "{釋義參照}"'
                )
                釋義參照 = patch.校正釋義參照

        字_check = 字序_data[字序_key].字
        assert 字頭 == 字_check, (
            f'字頭 mismatch between 字序表 and (patched) 廣韻 data: "{字_check}" != "{字頭}" (小韻 {原書小韻號}/{小韻字號})'
        )
        if 字頭[-1] in ('｝', '］'):
            字頭或原貌 = 字頭[1:-1]
        elif 字頭[-1] == '〉':
            字頭或原貌 = 字頭[字頭.index('〈') + 1 : -1]
        else:
            字頭或原貌 = 字頭

        # 小韻號
        # NOTE 字頭 & 細分轄字 in 小韻表.tsv does not contain 字頭原貌 (yet)
        if 原書小韻號 in 細分號_by_原書小韻:
            for 細分 in 細分號_by_原書小韻[原書小韻號]:
                小韻號 = 原書小韻號 + 細分
                if 字頭或原貌 in 細分轄字_by_小韻[小韻號]:
                    小韻細分_coverage.setdefault(小韻號, set()).add(字頭或原貌)
                    break
            else:
                raise ValueError(
                    f'cannot determine 小韻細分 for {字頭或原貌} (小韻 #{原書小韻號})'
                )
        else:
            小韻號 = 原書小韻號

        if 小韻號 not in 小韻號_seen:
            assert 字頭或原貌 == 小韻_data[小韻號].首字, (
                f'首字 mismatch for 小韻 #{小韻號}: {字頭或原貌} != {小韻_data[小韻號].首字}'
            )
            小韻號_seen.add(小韻號)

        # 音韻地位
        音韻地位 = 小韻_data[小韻號].音韻地位

        # 反切
        反切 = 小韻_data[小韻號].反切

        # 釋義中反切
        if 小韻字號 == '1' and 反切:
            反切原貌 = re.sub(r'［.］|〈.〉|（.）|〘.〙|〖.〗|｟.｠', '', 反切)
            if 反切原貌 != poem_反切:
                assert 釋義.count(poem_反切 + '切') == 1, (
                    f'釋義 not containing {反切}切 exactly once: {釋義}'
                )
            釋義 = 釋義.replace(poem_反切 + '切', 反切原貌 + '切')

        直音 = 小韻_data[小韻號].直音

        廣韻_data[字序_key] = 廣韻Row(
            小韻號,
            小韻字號,
            韻目原貌,
            音韻地位,
            反切,
            直音,
            字頭,
            字頭說明,
            釋義,
            釋義參照,
        )

    for 小韻號, cov in 小韻細分_coverage.items():
        specified = set(細分轄字_by_小韻[小韻號])
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
