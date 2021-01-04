from PySide2.QtWidgets import *

import PIL
import PIL
import PIL.Image
import PIL.ImageDraw
import PIL.ImageFont
import PIL.ImageStat
import PIL.ImageOps

import json
import os
import sys

class Widget(QWidget):
	def __init__(self):
		QWidget.__init__(self)
		self.resize(720, 480)
		self.setWindowTitle('Uniartgen')

		self.font_combo_box = QFontComboBox(self)

		

class TextData:
	def __init__(self, out:tuple):
		self.text = out[0]
		self.font_size = out[1]

	def output_text(self, output_file_name = ''):
		if output_file_name == '':
			output_file_name = 'output.txt'
		file = open(output_file_name, 'w', encoding = 'utf-8')
		file.write(self.text)
		file.close()


class ImageData:
	def __init__(self, image_file_name):
		self.image_file_name = os.path.splitext(image_file_name)[0]
		self.image = PIL.Image.open(image_file_name)
	
	def invert(self):
		self.image = PIL.ImageOps.invert(self.image)

	def resize(self, size, keep_width = True, keep_ratio = True):
		if keep_ratio:
			aspect_ratio = self.image.size[0] / self.image.size[1]
			if keep_width:
				size_tuple = (size, int(size / aspect_ratio))
			else:
				size_tuple = (int(size * aspect_ratio), size)
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
			size_tuple = (int(self.image.width / ratio), self.image.height)
		self.image = self.image.resize(size_tuple)
			


	def generate(self, fontdata, normalize = True, nearest = True):
		
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


		print('문자열 작성 중... ', end = '')

		output_text = ''
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
							diff_before = abs(before_value[1] - average)
							diff_current = abs(k[1] - average)
							if diff_current <= diff_before:
								write_value = k[0]
							else:
								write_value = before_value[0]
							output_text += chr(write_value)
							break
						before_value = k
					else:
						output_text += chr(fontdata.value_list[-1][0])
				else:
					for k in fontdata.value_list:
						if k[1] >= average:
							output_text += chr(k[0])
							break
					else:
						output_text += chr(fontdata.value_list[-1][0])
			output_text += '\n'
		print('완료')

		return output_text, fontdata.font_size

class FontDataSettings:
	def __init__(self, file_name = 'fontdata_settings.json'):
		self.file_name = file_name
	
	def load(self):
		json_file = open(self.file_name, 'r', encoding = 'utf-8')
		json_data = json.load(json_file)
		json_file.close()

		self.ranges:list[range] = [range(32, 127)]
		self.font_file_name:str = "d2coding.ttf"
		self.font_size:int = 8

		if 'characters' in json_data:
			self.ranges = []
			for r in json_data['characters']:
				begin:int
				end:int

				if type(r) == list:
					if len(r) == 2:
						rb:any = r[0]
						re:any = r[1]
						
						if type(rb) == str:
							begin = ord(rb)
						elif type(rb) == int:
							begin = rb
						else:
							continue

						if type(re) == str:
							end = ord(re)
						elif type(re) == int:
							end = re
						else:
							continue
					else:
						continue
				elif type(r) == str:
					begin = ord(r[0])
					end = ord(r[0])
				elif type(r) == int:
					begin = r
					end = r
				else:
					continue
				self.ranges.append(range(begin, end + 1))

		if 'font_file_name' in json_data:
			temp = json_data['font_file_name']
			if type(temp) == str:
				self.font_file_name = temp
		
		if 'font_size' in json_data:
			temp = json_data['font_size']
			if type(temp) == int:
				self.font_size = temp
		
		print(self.ranges)

class FontData:
	def __init__(self, settings:FontDataSettings):
		self.ranges = settings.ranges
		self.font_file_name = settings.font_file_name
		self.font_size = settings.font_size
	
	def generate(self, normalize = True):
		data_file_name = self.font_file_name + '_' + str(self.font_size)
		for r in self.ranges:
			data_file_name += '_' + str(r.start) + '-' + str(r.stop - 1)
		data_file_name += '-' + str(normalize)
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
			if diff == 0:
				diff = 1

			self.value_list = []
			before = 1.0
			print('정규화 및 중복 값 제거 중... ', end = '')
			for i in range(len(old_list)):
				if normalize:
					value = ((old_list[i][0] - min) * 255) / diff
				else:
					value = old_list[i][0]
				if before != value:
					self.value_list.append([old_list[i][1], value])
				before = value
			print('완료')

			json_file = open(data_file_name, 'w')
			json.dump(self.value_list, json_file)
			json_file.close()

fd = FontDataSettings()
fd.load()