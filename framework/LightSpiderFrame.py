from pyquery import PyQuery as pq
from selenium import webdriver
from pymongo import MongoClient
import requests
import time
import os
import re
import json


class Spider(object):
	def __init__(self):
		self.headers = {
			"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
						  " AppleWebKit/537.36 (KHTML, like Gecko)"
						  " Chrome/58.0.3029.110 Safari/537.36 Edge/16.16299"
		}
		self.page = ""
		self.items = []
		self.driver = None
		self.db = None

	def set_headers(self, **kwargs):
		for k, v in kwargs.items():
			self.headers[k] = v

	def get_page(self, url):
		r = requests.get(url, self.headers)
		s = r.content.decode("utf-8")
		self.page = s

	"""
		将页面缓存到本地，之后如果请求相同的url，则直接访问本地文件
	"""
	def cached_url(self, url, folder="cached", render=False):
		filename = re.sub(r"[:/?=]+", "#", url) + ".html"
		file = os.path.join(folder, filename)
		if os.path.exists(file):
			with open(file, "r", encoding="utf-8") as f:
				s = f.read()
				self.page = s
		else:
			if not os.path.exists(folder):
				os.mkdir(folder)
			if render:
				self.rendered_page(url)
			else:
				self.get_page(url)
			with open(file, "w", encoding="utf-8") as f:
				f.write(self.page)


	"""
		适用于需要通过下拉滚轮来加载条目的页面，该函数将返回加载好的页面的源码
		url：请求的网址
		iter_count：在当前请求的页面迭代的次数（滑动到页面底部的次数）
		wait_time：每次滑动到底部等待的时间
	"""
	def load_dynamic_page(self, url, iter_count=5, wait_time=5):
		self.open_driver()
		self.driver.get(url)
		for i in range(iter_count):
			# 滚动到页面底部
			self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight)")
			time.sleep(wait_time)
		self.page = self.driver.page_source

	"""
		适用于只需要渲染页面即可即可的请求
		url：请求的网址
	"""
	def rendered_page(self, url):
		if not self.driver:
			self.open_driver()
		self.driver.get(url)
		self.page = self.driver.page_source

	def open_driver(self):
		opt = webdriver.ChromeOptions()
		# 不加载图片
		prefs = {"profile.managed_default_content_settings.images": 2}
		opt.add_experimental_option("prefs", prefs)
		# 设置为无头模式
		opt.set_headless()
		self.driver = webdriver.Chrome(options=opt)
		self.driver.set_page_load_timeout(20)

	def destroy(self):
		self.items.clear()
		self.page = ""
		self.driver.close()
		self.driver = None

	"""
		适用于由多个相似条目组成的页面，将页面中每个条目解析为对象
		selector：选择所有相似条目的CSS选择器
		method：将单个条目解析为对象的算法
		kwargs: 除了解析出的每个item，其他需要加在对象上的属性
	"""
	def parsed_items(self, selector, method, **kwargs):
		if self.page:
			e = pq(self.page)
			items = e(selector)
			self.items.extend([method(pq(it), **kwargs) for it in items])

	def clear(self):
		self.items.clear()
		self.page = ""

	def init_db(self):
		self.db = MongoClient("localhost", 27017).spiders

	def save(self):
		if not self.db:
			self.init_db()
		for it in self.items:
			self.db["lianjia"].insert(it.__dict__)
