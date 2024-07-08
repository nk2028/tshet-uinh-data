import re

所有母 = '幫滂並明端透定泥來知徹澄孃精清從心邪莊初崇生俟章昌常書船日見溪羣疑影曉匣云以'
所有等 = '一二三四'
所有韻 = '東冬鍾江支脂之微魚虞模齊祭泰佳皆夬灰咍廢真臻文殷元魂痕寒刪山仙先蕭宵肴豪歌麻陽唐庚耕清青蒸登尤侯幽侵覃談鹽添咸銜嚴凡'
所有聲 = '平上去入'

PATTERN_ASCII = re.compile(r'[\x00-\x7F]')
PATTERN_描述 = re.compile(
    f'([{所有母}])([開合])?([{所有等}])([ABC])?([{所有韻}])([{所有聲}])'
)


def contains_ascii(s: str):
    """
    Check if a string contains at least one ASCII character.
    """
    return bool(PATTERN_ASCII.match(s))


if __name__ == '__main__':
    with open('韻書/廣韻.csv') as f:
        assert (
            next(f).rstrip('\n')
            == '小韻號,小韻內字序,韻目原貌,音韻地位,反切,字頭,字頭又作,釋義,釋義補充'
        )
        for line in f:
            (
                小韻號,
                小韻內字序,
                韻目原貌,
                音韻地位描述,
                反切,
                字頭,
                字頭又作,
                釋義,
                釋義補充,
            ) = line.rstrip('\n').split(',')
            if 音韻地位描述 != '':
                assert (
                    PATTERN_描述.fullmatch(音韻地位描述) is not None
                ), f'invalid 音韻地位: {音韻地位描述}'
            assert len(反切) in (
                2,
                0,
            ), 'The length of 反切 should be 2, otherwise it should be an empty string'
            assert len(字頭) == 1, 'The length of 字頭 should be 1'
            assert not contains_ascii(
                釋義
            ), '釋義 should not contain any ASCII characters'
