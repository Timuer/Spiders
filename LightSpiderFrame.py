from pyquery import PyQuery as pq
from selenium import webdriver
import requests
import time
import os
import re


class Spider(object):
	def __init__(self):
		self.headers = {
			"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
						  " AppleWebKit/537.36 (KHTML, like Gecko)"
						  " Chrome/58.0.3029.110 Safari/537.36 Edge/16.16299"
		}
		self.page = ""
		self.items = []

	def set_headers(self, **kwargs):
		for k, v in kwargs.items():
			self.headers[k] = v

	def get_page(self, url):
		r = requests.get(url, self.headers)
		s = r.content.decode("utf-8")
		self.page = s

	def cached_url(self, url, folder="cached"):
		filename = re.sub(r"[:/?=]+", "#", url) + ".html"
		file = os.path.join(folder, filename)
		if os.path.exists(file):
			with open(file, "r", encoding="utf-8") as f:
				s = f.read()
				self.page = s
		else:
			if not os.path.exists(folder):
				os.mkdir(folder)
			with open(file, "w", encoding="utf-8") as f:
				r = requests.get(url, self.headers)
				s = r.content.decode("utf-8")
				f.write(s)
				self.page = s

	"""
		适用于需要通过下拉滚轮来加载条目的页面，该函数将返回加载好的页面的源码
		url：请求的网址
		iter_count：在当前请求的页面迭代的次数（滑动到页面底部的次数）
		wait_time：每次滑动到底部等待的时间
	"""
	def load_dynamic_page(self, url, iter_count=5, wait_time=5):
		# 创建Chrome参数对象
		opt = webdriver.ChromeOptions()
		# 把Chrome设置为无界面模式
		opt.set_headless()
		# 创建无界面Chrome对象
		driver = webdriver.Chrome(options=opt)
		driver.get(url)
		for i in range(iter_count):
			time.sleep(wait_time)
			# 滚动到页面底部
			driver.execute_script("window.scrollTo(0, document.body.scrollHeight)")
		self.page = driver.page_source

	"""
		适用于由多个相似条目组成的页面，将页面中每个条目解析为对象
		selector：选择所有相似条目的CSS选择器
		method：将单个条目解析为对象的算法
	"""
	def parsed_items(self, selector, method):
		e = pq(self.page)
		items = e(selector)
		self.items.extend([method(pq(it)) for it in items])