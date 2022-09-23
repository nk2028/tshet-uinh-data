from glob import glob
import re

所有母 = '幫滂並明端透定泥來知徹澄孃精清從心邪莊初崇生俟章昌常書船日見溪羣疑影曉匣云以'
所有等 = '一二三四'
所有韻 = '東冬鍾江支脂之微魚虞模齊祭泰佳皆夬灰咍廢真臻文殷元魂痕寒刪山先仙蕭宵肴豪歌麻陽唐庚耕清青蒸登尤侯幽侵覃談鹽添咸銜嚴凡'
所有聲 = '平上去入'

PATTERN_ASCII = re.compile(r'[\x00-\x7F]')
PATTERN_描述 = re.compile(f'([{所有母}])([開合])?([{所有等}])?([AB])?([{所有韻}])([{所有聲}])')


def contains_ascii(s: str):
    '''
    Check if a string contains at least one ASCII character.
    '''
    return bool(PATTERN_ASCII.match(s))


for filename in glob('韻書/*.csv'):
    is廣韻 = filename == '韻書/廣韻.csv'
    with open(filename) as f:
        next(f)  # skip header
        for line in f:
            if is廣韻:
                小韻號, 小韻內字序, 韻部原貌, 描述, 反切覈校前, 反切, 字頭覈校前, 字頭, 釋義, 釋義補充, 圖片id = line.rstrip(
                    '\n').split(',')
            else:
                小韻號, 韻部原貌, 描述, 反切覈校前, 反切, 字頭覈校前, 字頭, 釋義, 釋義補充, 圖片id = line.rstrip(
                    '\n').split(',')
            if 描述 != '':
                assert PATTERN_描述.fullmatch(描述) is not None
            assert len(反切) in (
                2, 0), 'The length of 反切 should be 2, otherwise it should be an empty string'
            assert len(字頭) == 1, 'The length of 字頭 should be 1'
            assert not contains_ascii(
                釋義), '釋義 should not contain any ASCII characters'
