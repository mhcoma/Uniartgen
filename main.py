from PySide2.QtWidgets import *

import PIL
import PIL
import PIL.Image
import PIL.ImageDraw
import PIL.ImageFont
import PIL.ImageStat
import PIL.ImageOps

import bisect
import json
import os
import sys

class MainWindow(QMainWindow):
	def __init__(self, parent = None):
		QMainWindow.__init__(self, parent)
		self.resize(720, 480)
		self.setWindowTitle('Uniartgen')


		exit_action = QAction('&Exit', self)
		exit_action.setShortcut('Ctrl+Q')
		exit_action.setStatusTip('Exit Application')
		exit_action.triggered.connect(QApplication.exit)

		layout_1 = QHBoxLayout()

		menubar = self.menuBar()
		menubar.setNativeMenuBar(False)
		filemenu = menubar.addMenu('&File')

		filemenu.addAction(exit_action)

		

class FontDataSettings:
	def __init__(self, file_name = 'fontdata_settings.json'):
		self.file_name:str = file_name
		self.ranges:list[range] = [range(32, 127)]
		self.font_file_name:str = os.path.join("fonts", "d2coding.ttf")
		self.font_size:int = 8
		self.normalize:bool = True
		self.load()

	def save(self):
		ranges_temp:list[list[int]] = []
		for i in self.ranges:
			ranges_temp.append([i.start, i.stop - 1])

		json_data = {
			'ranges' : ranges_temp,
			'font_file_name' : self.font_file_name,
			'font_size' : self.font_size,
			'normalize' : self.normalize
		}

		json_file = open(self.file_name, 'w', encoding = 'utf-8')
		json.dump(json_data, json_file, indent = '\t')
		json_file.close()
	
	def load(self):
		if os.path.isfile(self.file_name):
			json_file = open(self.file_name, 'r', encoding = 'utf-8')
			try:
				json_data = json.load(json_file)
			except:
				json_data = self.new()
			json_file.close()

			if 'ranges' in json_data:
				self.ranges = []
				temp:list[range] = []
				for r in json_data['ranges']:
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
					temp.append(range(begin, end + 1))
				
				result:bool = True
				while True:
					x = temp[0]
					count = 0
					for i in range(1, len(temp)):
						xs = set(x)
						y = temp[i - count]
						ip = xs.intersection(y)
						if len(ip) > 0:
							begin = min(x.start, y.start)
							end = max(x.stop, y.stop)
							x = range(begin, end)
							temp.pop(i - count)
							count += 1
							result = False
					self.ranges.append(x)
					temp.pop(0)
					if result and len(temp) == 0:
						break
			
			if 'font_file_name' in json_data:
				temp = json_data['font_file_name']
				if type(temp) == str:
					self.font_file_name = temp
			
			if 'font_size' in json_data:
				temp = json_data['font_size']
				if type(temp) == int:
					self.font_size = temp
			
			if 'normalize' in json_data:
				temp = json_data['normalize']
				if type(temp) == bool:
					self.normalize = temp
		
		self.save()

class FontData:
	def __init__(self, settings:FontDataSettings):
		self.ranges:list[range] = settings.ranges
		self.font_file_name:str = settings.font_file_name
		self.font_size:int = settings.font_size
		self.normalize:bool = settings.normalize
		self.list_data:list[dict] = []
		self.load_list()
		if not self.load():
			self.generate()
	
	def load_list(self, list_file_name = 'fontdata_list.json'):
		self.list_file_name = list_file_name
		if os.path.isfile(list_file_name):
			list_file = open(list_file_name, 'r')
			self.list_data = json.load(list_file)
			list_file.close()
			return True
		else:

			list_file = open(list_file_name, 'w')
			json.dump(self.list_data, list_file, indent = '\t')
			list_file.close()

	def load(self):
		ranges_temp:list[list[int]] = []
		for i in self.ranges:
			ranges_temp.append([i.start, i.stop])

		for i in self.list_data:
			if 'ranges' in i:
				if i['ranges'] != ranges_temp:
					continue
			else:
				continue
			
			if 'font_file_name' in i:
				if i['font_file_name'] != self.font_file_name:
					continue
			else:
				continue

			if 'font_size' in i:
				if i['font_size'] != self.font_size:
					continue
			else:
				continue

			if 'normalize' in i:
				if i['normalize'] != self.normalize:
					continue
			else:
				continue

			if 'data_file_name' in i:
				data_file_name = os.path.join('fontdata', i['data_file_name'])
				if os.path.isfile(data_file_name):
					data_file = open(data_file_name, 'r')
					try:
						self.data = json.load(data_file)
						data_file.close()
					except:
						self.generate(
							data_file_name = i['data_file_name'],
							add_list = False
						)
						return True
					return True
				else:
					self.generate(
						data_file_name = i['data_file_name'],
						add_list = False
					)
					return True
			else:
				continue
		return False

	def generate(self, data_file_name = None, add_list = True):
		font = PIL.ImageFont.truetype(self.font_file_name, self.font_size, encoding = 'utf-8')
		old_list = []

		for r in self.ranges:
			for i in r:
				img = PIL.Image.new('RGB', (font.getsize(chr(i))[0], self.font_size), color = (255, 255, 255))
				draw = PIL.ImageDraw.Draw(img)
				draw.text((0, 0), chr(i), font = font, fill = (0, 0, 0))
				stat = PIL.ImageStat.Stat(img)
				value = stat.mean[0]
				old_list.append([value, i])

		old_list.sort()
		min = old_list[0][0]
		max = old_list[-1][0]
		diff = max - min
		if diff == 0:
			diff = 1

		self.data:list[list[float, int]] = []
		before = 1.0
		for i in range(len(old_list)):
			if self.normalize:
				value = ((old_list[i][0] - min) * 255) / diff
			else:
				value = old_list[i][0]
			if before != value:
				self.data.append([value, old_list[i][1]])
			before = value

		if data_file_name == None:
			data_file_name = '{}.json'.format(len(self.list_data))
		
		json_file = open(os.path.join('fontdata', data_file_name), 'w')
		json.dump(self.data, json_file, indent = '\t')
		json_file.close()
		

		if add_list:
			ranges_temp:list[list[int]] = []
			for i in self.ranges:
				ranges_temp.append([i.start, i.stop])
			
			self.list_data.append(
				{
					'ranges' : ranges_temp,
					'font_file_name' : self.font_file_name,
					'font_size' : self.font_size,
					'normalize' : self.normalize,
					'data_file_name' : data_file_name
				}
			)

			list_file = open(self.list_file_name, 'w')
			json.dump(self.list_data, list_file, indent = '\t')
			list_file.close()

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
			
	def generate(self, fontdata:FontData, normalize = True, nearest = True):
		min = 256
		max = -1
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
		diff = max - min

		output_text = ''
		for i in range(self.image.size[1]):
			for j in range(self.image.size[0]):
				average = 0
				for p in self.image.getpixel((j, i)):
					average += p
				average /= 3
				if normalize:
					average = ((average - min) / diff) * 255
				

				index = bisect.bisect(fontdata.data, [average])
				if nearest:
					temp_left = abs(fontdata.data[index-1][1] - average)
					temp_right = abs(fontdata.data[index][1] - average)
					if temp_right > temp_left:
						index -= 1

				output_text += chr(fontdata.data[index][1])
			output_text += '\n'

		return TextData(output_text, fontdata, self.image_file_name)

class TextData:
	def __init__(self, output_text:str, fontdata:FontData, image_file_name:str):
		self.text = output_text
		self.image_file_name = image_file_name
		self.font_file_name = fontdata.font_file_name
		self.font_size = fontdata.font_size

	def out_text(self, output_file_name = ''):
		if output_file_name == '':
			output_file_name = '{}_text.txt'.format(self.image_file_name)
		file = open(output_file_name, 'w', encoding = 'utf-8')
		file.write(self.text)
		file.close()
	
	def out_img(self, output_file_name = ''):
		if output_file_name == '':
			output_file_name = '{}.png'.format(self.image_file_name)
		font = PIL.ImageFont.truetype(self.font_file_name, self.font_size * 2, encoding = 'utf-8')

		lines = self.text.splitlines()
		size = (font.getsize(lines[0])[0], len(lines) * self.font_size * 2)

		img = PIL.Image.new('RGB', size, color = (255, 255, 255))
		draw = PIL.ImageDraw.Draw(img)

		for i in range(len(lines)):
			draw.text((0, i * self.font_size * 2), lines[i], font = font, fill = (0, 0, 0))

		img.save(output_file_name)

fds = FontDataSettings()
fd = FontData(fds)
img = ImageData('test2.jpg')
img.resize(200)
txt = img.generate(fd, True)
txt.out_img()