import PIL
import PIL
import PIL.Image
import PIL.ImageDraw
import PIL.ImageFont
import PIL.ImageStat


import json
import os

class ImageData:
	def __init__(self, image_file_name):
		self.image_file_name = os.path.splitext(image_file_name)[0]
		self.image = PIL.Image.open(image_file_name)

		self.data:list[list[float]] = []
	
	def resize(self, size, keep_width = True, keep_ratio = True):
		if keep_ratio:
			aspect_ratio = self.image.size[0] / self.image.size[1]
			if keep_width:
				size_tuple = (size, int(size * aspect_ratio))
			else:
				size_tuple = (int(size / aspect_ratio), size)
		else:
			if keep_width:
				size_tuple = (size, self.image.size[1])
			else:
				size_tuple = (self.image.size[0], size)
		self.image = self.image.resize(size_tuple)
	
	def resize_by_ratio(self, ratio, keep_width = True):
		if keep_width:
			size_tuple = (self.image.width, int(self.image.height * ratio))
		else:
			size_tuple = (int(self.image.width) * ratio, self.image.height)
		self.image = self.image.resize(size_tuple)
			


	def generate(self, fontdata, normalize = True, nearest = True, output_file_name = ''):
		if output_file_name == '':
			output_file_name = self.image_file_name + '.txt'
		file = open(output_file_name, 'w', encoding = 'utf-8')
		
		min = 256
		max = -1
		print('정규화를 위한 값 계산 중... ', end = '')
		for i in range(self.image.size[1]):
			for j in range(self.image.size[0]):
				average = 0
				for p in self.image.getpixel((j, i)):
					average += p
				average /= 3
				if average > max:
					max = average
				if average < min:
					min = average
		print('완료')
		diff = max - min


		print('파일 작성 중... ', end = '')
		for i in range(self.image.size[1]):
			for j in range(self.image.size[0]):
				average = 0
				for p in self.image.getpixel((j, i)):
					average += p
				average /= 3
				if normalize:
					average = ((average - min) / diff) * 255
				
				if nearest:
					before_value = fontdata.value_list[0]
					for k in fontdata.value_list:
						if k[1] >= average:
							diff_before = before_value[1] - average
							diff_current = k[1] - average
							if diff_current <= diff_before:
								write_value = k[0]
							else:
								write_value = before_value[0]
							file.write(chr(write_value))
							break
						before_value = k
					else:
						file.write(chr(fontdata.value_list[-1][0]))
				else:
					for k in fontdata.value_list:
						if k[1] >= average:
							file.write(chr(k[0]))
							break
					else:
						file.write(chr(fontdata.value_list[-1][0]))
			file.write('\n')
		file.close()
		print('완료')

class FontData:
	def __init__(self, settings_file_name = 'fontdata_settings.json'):
		json_file = open(settings_file_name, 'r', encoding = 'utf-8')
		json_data = json.load(json_file)
		
		self.ranges:list[range] = []
		for r in json_data['ranges']:
			self.ranges.append(range(r[0], r[1] + 1))
		for c in json_data['characters']:
			self.ranges.append(range(ord(c), ord(c) + 1))
		self.font_file_name:str = json_data['font_file_name']
		self.font_size:int = json_data['font_size']
	
	def generate(self):
		data_file_name = self.font_file_name + '_' + str(self.font_size)
		for r in self.ranges:
			data_file_name += '_' + str(r.start) + '-' + str(r.stop - 1)
		data_file_name += '.json'

		print('데이터 불러오는 중... ', end = '')
		if os.path.isfile(data_file_name):
			json_file = open(data_file_name, 'r')
			self.value_list = json.load(json_file)
			json_file.close()
			print('완료')
		else:
			print('실패')
			font = PIL.ImageFont.truetype(self.font_file_name, self.font_size, encoding = 'utf-8')
			old_list = []
			print('서체로부터 밝기 캡처 중... ', end = '')

			for r in self.ranges:
				for i in r:
					img = PIL.Image.new('RGB', (self.font_size, self.font_size), color = (255, 255, 255))
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

			json_file = open(data_file_name, 'w')
			json.dump(self.value_list, json_file)
			json_file.close()

fd = FontData()
fd.generate()

id = ImageData('hf1.jpg')
id.resize(400)
id.resize_by_ratio(2)
id.generate(fd)
