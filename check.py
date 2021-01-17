from QieyunEncoder import from描述

with open('data.csv') as f:
	next(f) # skip header
	for line in f:
		描述, 反切, 字頭, 解釋 = line.rstrip('\n').split(',')
		from描述(描述)
