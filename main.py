import PIL
import PIL
import PIL.Image
import PIL.ImageDraw
import PIL.ImageFont
import PIL.ImageStat

import os


class ImageData:
	def __init__(self, image_file_name, size):
		self.image = PIL.Image.open(image_file_name)
		if self.image.size[1] != size:
			self.image.thumbnail((size, size), PIL.Image.ANTIALIAS)

	def generate(self, output_file_name, fontdata):

		print('파일 작성 중... ', end = '')
		file = open(output_file_name, 'w', encoding = 'utf-8')
		for i in range(self.image.size[1]):
			for j in range(self.image.size[0]):
				average = 0
				for p in self.image.getpixel((j, i)):
					average += p
				average /= 3
				
				for k in fontdata.value_list:
					if k[1] >= average:
						file.write(chr(k[0]))
						break
			file.write('\n')
		file.close()
		print('완료')

class FontData:
	def __init__(self, font_file_name, size):
		font = PIL.ImageFont.truetype(font_file_name, size, encoding = 'utf-8')
		old_list = []
		print('서체로부터 밝기 캡처 중... ', end = '')

		ranges = [range(44032, 55204)]

		for r in ranges:
			for i in r:
				img = PIL.Image.new('RGB', (size, size), color = (255, 255, 255))
				draw = PIL.ImageDraw.Draw(img)
				draw.text((0, 0), chr(i), font = font, fill = (0, 0, 0))
				stat = PIL.ImageStat.Stat(img)
				value = stat.mean[0]
				old_list.append([value, i])
		print('완료')

		old_list.sort()
		min = old_list[0][0]
		max = old_list[-1][0]
		diff = max - min

		self.value_list = []
		before = 1.0
		print('정규화 및 중복 값 제거 중... ', end = '')
		for i in range(len(old_list)):
			value = ((old_list[i][0] - min) * 255) / diff
			if before != value:
				self.value_list.append([old_list[i][1], value])
			before = value
		print('완료')

'''
fontname = os.path.join('windows', 'fonts', 'batang.ttc')
fontdata = FontData(fontname, 8)

imagedata = ImageData('ranma.jpg', 800)
imagedata.generate('test.txt', fontdata)
'''