import re

所有母 = '幫滂並明端透定泥來知徹澄孃精清從心邪莊初崇生俟章昌常書船日見溪羣疑影曉匣云以'
所有等 = '一二三四'
所有韻 = '東冬鍾江支脂之微魚虞模齊祭泰佳皆夬灰咍廢真臻文殷元魂痕寒刪山仙先蕭宵肴豪歌麻陽唐庚耕清青蒸登尤侯幽侵覃談鹽添咸銜嚴凡'
所有聲 = '平上去入'

PATTERN_ASCII = re.compile(r'[\x00-\x7F]')
PATTERN_描述 = re.compile(
    f'([{所有母}])([開合])?([{所有等}])([ABC])?([{所有韻}])([{所有聲}])'
)
PATTERN_反切 = re.compile(
    r"""(?x)(
        \[.\] |  # 脫字
        . ( <.> | ⦉.⦊ | \(.\) | ⦅.⦆ )*  # 原貌及校正
    ){2}"""
)
PATTERN_IDC = re.compile(r'[\u2ff0-\u2fff\u303e\u31ef]')


def contains_ascii(s: str):
    """
    Check if a string contains at least one ASCII character.
    """
    return bool(PATTERN_ASCII.match(s))


if __name__ == '__main__':
    with open('韻書/廣韻.csv') as f:
        assert (
            next(f).rstrip('\n')
            == '小韻號,小韻字號,韻目原貌,音韻地位,反切,字頭原貌,字頭,字頭說明,釋義,釋義參照'
        )
        for line in f:
            (
                小韻號,
                小韻字號,
                韻目原貌,
                音韻地位描述,
                反切,
                字頭原貌,
                字頭,
                字頭說明,
                釋義,
                釋義參照,
            ) = line.rstrip('\n').split(',')

            assert re.fullmatch(r'\d+[abc]?', 小韻號), f'invalid 小韻號: {小韻號}'
            assert re.fullmatch(r'\d+(a\d+)?', 小韻字號), (
                f'invalid 小韻字號: {小韻字號}'
            )
            assert len(韻目原貌) == 1, f'invalid 韻目原𩩕: {韻目原貌}'
            assert 字頭原貌 != 字頭, f'字頭原貌 same as 字頭: {字頭}'
            for field, 字 in (('字頭原貌', 字頭原貌), ('字頭', 字頭)):
                if not 字:
                    continue
                assert 字 != '-' and (len(字) == 1 or PATTERN_IDC.match(字)), (
                    f'invalid {field}: {字}'
                )

            assert PATTERN_描述.fullmatch(音韻地位描述) is not None, (
                f'invalid 音韻地位: {音韻地位描述}'
            )

            if 反切:
                assert PATTERN_反切.fullmatch(反切) is not None, f'invalid 反切: {反切}'

            assert 釋義 or 釋義參照, '釋義 and 釋義參照 should not be both empty'
            assert not contains_ascii(釋義), (
                '釋義 should not contain any ASCII characters'
            )
            assert 釋義參照 in ('', '上', '下'), '釋義參照 should be "上" or "下"'
