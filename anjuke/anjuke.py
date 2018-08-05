from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from pyquery import PyQuery as pq
import pymongo
from config import *

client = pymongo.MongoClient(MONGO_URL)
db = client[MONGO_DATABASE]

url = "https://wuhan.anjuke.com/community/hongshana/"
# opts = webdriver.ChromeOptions()
# opts.set_headless(True)
driver = webdriver.Chrome()
wait = WebDriverWait(driver, 10)

def to_index_page(url):
	try:
		driver.get(url)
		urls = []
		return parse_index_page(urls)
	except Exception as e:
		print("获取首页错误", e)

def parse_index_page(urls, next_page=2):
	wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "#list-content .li-itemmod")))
	elements = driver.find_elements(By.CSS_SELECTOR, "#list-content .li-itemmod")
	for e in elements:
		link = e.get_attribute("link")
		urls.append(link)
		print(link)
	a = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, ".aNxt")))
	if a.get_attribute("href"):
		a.click()
		wait.until(EC.text_to_be_present_in_element((By.CSS_SELECTOR, ".curr"), str(next_page)))
		if next_page < 20:
			parse_index_page(urls, next_page + 1)
	return urls

def to_community_detail_page(url):
	driver.get(url)
	wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "#basic-infos-box")))
	html = driver.page_source
	community_info = parse_community_detail_page(html)
	# 获取小区二手房信息
	id = url.split("/")[-1]
	next_url = "https://wuhan.anjuke.com/community/props/sale/" + id
	driver.get(next_url)
	wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "ul.m-house-list a")))

	community_info["houses"] = []
	html1 = driver.page_source
	doc = pq(html1)
	elements = doc(".m-rent-house")
	for e in elements:
		elem = pq(e)
		link = elem.find(".title").find("[href]").attr("href")
		text = to_house_detail_page(link)
		community_info["houses"].append(text)
	return community_info


def to_house_detail_page(url):
	driver.get(url)
	house_info = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".houseInfo-detail")))
	text = house_info.text
	return text

def parse_community_detail_page(html):
	doc = pq(html)
	info_box = doc.find("#basic-infos-box")
	item = {}
	item['price'] = info_box.find(".price .average").text()
	infos = info_box.find(".basic-parms-mod").text().split("\n")
	try:
		item['wuye'] = infos[1]
		item['wuyefei'] = infos[3]
		item['mianji'] = infos[5]
		item['hushu'] = infos[7]
		item['naindai'] = infos[9]
		item['tingchewei'] = infos[11]
		item['rongjilv'] = infos[13]
		item['lvhualv'] = infos[15]
		item['kaifashang'] = infos[17]
		item['wuyegongsi'] = infos[19]
	except Exception as e:
		print("解析出错")
		return {}
	return item


if __name__ == "__main__":
	try:
		for u in to_index_page(url):
			community_info = to_community_detail_page(u)
			db["anjuke"].insert(community_info)
	finally:
		driver.quit()
		# print(item)