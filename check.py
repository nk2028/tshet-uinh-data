from QieyunEncoder import validate, encode, decode

seen = set()

with open('小韻表.csv') as f:
	next(f) # skip header
	for line in f:
		音韻編碼, 反切 = line.rstrip('\n').split(',')
		母, 呼, 等, 重紐, 韻, 聲 = decode(音韻編碼)
		assert 反切 == '' or len(反切) == 2
		assert (母, 呼, 等, 重紐, 韻, 聲) not in seen
		validate(母, 呼, 等, 重紐, 韻, 聲)
		seen.add((母, 呼, 等, 重紐, 韻, 聲))

with open('字頭表.csv') as f:
	next(f) # skip header
	for line in f:
		音韻編碼, 字頭, 釋義 = line.rstrip('\n').split(',')
		母, 呼, 等, 重紐, 韻, 聲 = decode(音韻編碼)
		assert (母, 呼, 等, 重紐, 韻, 聲) in seen
