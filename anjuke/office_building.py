from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from pyquery import PyQuery as pq
import pymongo
from config import *

client = pymongo.MongoClient(MONGO_URL)
db = client[MONGO_DATABASE]

url = "https://wh.xzl.anjuke.com/zu/hongshana/"
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
	print("getting page {}".format(next_page-1))
	wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "#list-content .list-item")))
	elements = driver.find_elements(By.CSS_SELECTOR, "#list-content .list-item")
	for e in elements:
		link = e.get_attribute("link")
		urls.append(link)
	if next_page <= 35:
		a = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, ".aNxt")))
		a.click()
		wait.until(EC.text_to_be_present_in_element((By.CSS_SELECTOR, ".curr"), str(next_page)))
		parse_index_page(urls, next_page + 1)
	return urls

def to_detail_page(url):
	try:
		driver.get(url)
		wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "#fy_info")))
		wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "#xzl_desc")))
		html = driver.page_source
		return parse_detail_page(html)
	except Exception as e:
		print(e)

def parse_detail_page(html):
	doc = pq(html)
	item = {}
	item['info'] = doc("#fy_info").text()
	item['desc'] = doc("#xzl_desc .desc-con").text()
	return item

if __name__ == "__main__":
	try:
		for u in to_index_page(url):
			item = to_detail_page(u)
			db["office_building"].insert(item)
	finally:
		driver.quit()

