seen = set()

with open('小韻表.csv') as f:
	next(f) # skip header

	for line in f:
		小韻號, 母, 呼, 等, 重紐, 韻, 聲, 反切 = line.rstrip('\n').split(',')

		assert len(母) == 1 and 母 in '幫滂並明端透定泥來知徹澄孃精清從心邪莊初崇生俟章昌常書船日見溪羣疑影曉匣云以'
		assert len(等) == 1 and 等 in '一二三四'
		assert len(韻) == 1 and 韻 in '東冬鍾江支脂之微魚虞模齊祭泰佳皆夬灰咍廢眞臻文欣元魂痕寒刪山仙先蕭宵肴豪歌麻陽唐庚耕清青蒸登尤侯幽侵覃談鹽添咸銜嚴凡'
		assert len(聲) == 1 and 聲 in '平上去入'

		if 母 in '幫滂並明' or 韻 == '模':
			assert 呼 == ''
		else:
			assert len(呼) == 1 and 呼 in '開合'

		if 韻 in '支脂祭眞仙宵侵鹽清' and 母 in '幫滂並明見溪羣疑影曉匣云以':
			assert len(重紐) == 1 and 重紐 in 'AB'
		else:
			assert 重紐 == ''

		assert 反切 == '' or len(反切) == 2

		assert (母, 呼, 等, 重紐, 韻, 聲) not in seen
		seen.add((母, 呼, 等, 重紐, 韻, 聲))
