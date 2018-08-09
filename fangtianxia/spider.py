from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from pyquery import PyQuery as pq
import pymongo
from config import *


client = pymongo.MongoClient(MONGO_URL)
db = client[MONGO_DATABASE]

url = "http://esf.wuhan.fang.com/housing/495__1_0_0_0_1_0_0_0/"
opts = webdriver.ChromeOptions()
# opts.set_headless(True)
prefs={"profile.managed_default_content_settings.images":2}
opts.add_experimental_option("prefs",prefs)

driver = webdriver.Chrome(options=opts)
wait = WebDriverWait(driver, 10)

def to_index_page(url):
	try:
		driver.get(url)
		urls = []
		return parse_index_page(urls)
	except Exception as e:
		print("获取首页错误", e)

def parse_index_page(urls, next_page=2):
	try:
		wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".houseList .plotTit")))
		elements = driver.find_elements(By.CSS_SELECTOR, ".houseList .plotTit")
		for e in elements:
			link = e.get_attribute("href")
			urls.append(link)
			print(link)
		a = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "#PageControl1_hlk_next")))
		if a.get_attribute("href"):
			a.click()
			wait.until(EC.text_to_be_present_in_element((By.CSS_SELECTOR, ".pageNow"), str(next_page)))
			if next_page < 16:
				parse_index_page(urls, next_page + 1)
	except Exception as e:
		print(e)
		if next_page < 16:
			parse_index_page(urls, next_page + 1)
	return urls

def to_community_detail(url):
	url += 'xiangqing/'
	driver.get(url)
	wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".inforwrap")))
	info = driver.find_element(By.CSS_SELECTOR, ".inforwrap")
	return info.text

def to_rent_detail(url):
	url += 'chuzu/'
	driver.get(url)
	wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".fangList")))
	infos = driver.find_elements(By.CSS_SELECTOR, ".fangList")
	texts = []
	for i in infos:
		t = i.text
		texts.append(t)
	if len(texts) > 2:
		texts = texts[:2]
	return texts

def to_sell_detail(url):
	url += 'chushou/'
	driver.get(url)
	wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".fangTitle")))
	infos = driver.find_elements(By.CSS_SELECTOR, ".fangTitle")
	links = []
	for i in infos:
		link = i.find_element(By.CSS_SELECTOR, "[href]").get_attribute("href")
		links.append(link)
	if len(links) > 8:
		links = links[:8]
	items = []
	for l in links:
		item = {}
		driver.get(l)
		# 楼房信息
		wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".cont .text-item")))
		info = driver.find_element(By.CSS_SELECTOR, ".cont")
		item['building_info'] = info.text
		# 房屋信息
		wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".tr-line")))
		panes = driver.find_elements(By.CSS_SELECTOR, ".tr-line")
		item["price"] = panes[0].find_element(By.CSS_SELECTOR, ".price_esf").text
		text = ""
		for p in panes[2: 5]:
			text += p.text + "\n"
		item["house_info"] = text
		print(item)
		items.append(item)
	return items

def get_detail(url):
	item = {}
	print('解析小区信息')
	item['community'] = to_community_detail(url)
	print('解析租房信息')
	item['rent'] = to_rent_detail(url)
	print('解析出售信息')
	item['sell'] = to_sell_detail(url)
	return item

def save_to_mongo(info):
	db["ershoufang"].insert(info)

if __name__ == "__main__":
	try:
		for u in to_index_page(url):
			print('解析{}...'.format(u))
			try:
				dt = get_detail(u)
				save_to_mongo(dt)
			except Exception as e:
				print('解析{} 出现错误'.format(u), e)
				continue
	finally:
		driver.quit()
