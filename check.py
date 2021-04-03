import Qieyun
import re

pattern = re.compile(r'[\x00-\x7F]')

def contains_ascii(s: str):
	'''
	Check if a string contains at least one ASCII character.
	'''
	return bool(pattern.match(s))

with open('data.csv') as f:
	next(f) # skip header
	for line in f:
		資料名稱, 小韻號, 韻部原貌, 最簡描述, 反切覈校前, 反切, 字頭覈校前, 字頭, 釋義, 釋義補充, 圖片id = line.rstrip('\n').split(',')
		Qieyun.音韻地位.from描述(最簡描述) # function from描述 will perform checks on 描述
		assert len(反切) in (2, 0), 'The length of 反切 should be 2, otherwise it should be an empty string'
		assert len(字頭) == 1, 'The length of 字頭 should be 1'
		assert not contains_ascii(釋義), '釋義 should not contain any ASCII characters'
