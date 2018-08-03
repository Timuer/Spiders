from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import re
from pyquery import PyQuery as pq
import pymongo
from config import *

client = pymongo.MongoClient(MONGO_URL)
db = client[MONGO_DATABASE]

url = "https://www.taobao.com"
opts = webdriver.ChromeOptions()
opts.set_headless(True)
driver = webdriver.Chrome(opts)
wait = WebDriverWait(driver, 10)

def to_index_page(url):
	try:
		driver.get(url)
		input_pane = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "#q")))
		button_pane = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, '#J_TSearchForm > div.search-button > button')))
		input_pane.send_keys("手办")
		button_pane.click()
		total_pane = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "#mainsrp-pager > div > div > div > div.total")))
		total = re.search("(\d+)", total_pane.text)
		return int(total.group(1))
	except Exception as e:
		print("获取首页错误", e)

def next_page(num):
	try:
		input_pane = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "#mainsrp-pager > div > div > div > div.form > input")))
		button_pane = wait.until(EC.element_to_be_clickable(
			(By.CSS_SELECTOR, "#mainsrp-pager > div > div > div > div.form > span.btn.J_Submit")
		))
		input_pane.clear()
		input_pane.send_keys(str(num))
		button_pane.click()
		wait.until(EC.text_to_be_present_in_element(
			(By.CSS_SELECTOR, "#mainsrp-pager > div > div > div > ul > li.item.active > span"), str(num)
		))
	except Exception as e:
		print("获取下一页错误，正在重试", e)
		next_page(num)


def parse_page():
	wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".m-itemlist .items .item")))
	html = driver.page_source
	doc = pq(html)
	items = doc.find(".m-itemlist .items .item")
	products = []
	for it in items:
		item = {}
		fragment = pq(it)
		item['img'] = "https:" + fragment.find(".pic .J_ItemPic").attr("src")
		item['price'] = fragment.find(".price.g_price").text().replace("￥\n", "")
		item['desc'] = fragment.find(".J_ClickStat").text().replace("\n", " ")
		item['shop'] = fragment.find(".shop .shopname").text()
		item['location'] = fragment.find(".location").text()
		item['pay_cnt'] = fragment.find(".deal-cnt").text()[:-3]
		print(item)
		products.append(item)
	return products

def save_to_mongo(doc):
	if db[MONGO_TABLE].insert(doc):
		print("插入Mongo成功", doc)
		return True
	else:
		return False

def main():
	try:
		total_page_num = to_index_page(url)
		for i in range(2, total_page_num + 1):
			products = parse_page()
			print("正在保存第{}页".format(i))
			save_to_mongo({'page': i, 'products': products})
			next_page(i + 1)
	except Exception as e:
		print("出现错误", e)
	finally:
		driver.quit()


if __name__ == "__main__":
	main()