import requests
import json
import re
import os
from hashlib import md5
from urllib.parse import urlencode
import pymongo
from config import *

headers = {
	"User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36"
}


client = pymongo.MongoClient(MONGO_URL)
db = client[MONGO_DATABASE]

def get_index_page(offset, keyword):
	global headers
	base_url = "https://www.toutiao.com/search_content/?"
	query = {
		"offset": offset,
		"format": "json",
		"keyword": keyword,
		"autoload": "true",
		"count": "20",
		"cur_tab": "3",
		"from": "gallery",
	}
	url = base_url + urlencode(query)
	try:
		resp = requests.get(url, headers=headers)
		return resp.text.strip()
	except Exception as e:
		print("获取索引页失败", e)
		return None

def parse_index_page(html):
	info = json.loads(html)
	if (info and info.get("data")):
		for item in info["data"]:
			article_url = item["article_url"]
			title = item["title"]
			yield (title, article_url)

def get_detail_page(article_url):
	global headers
	try:
		resp = requests.get(article_url, headers=headers)
		return resp.text
	except Exception as e:
		print("获取详情页失败", e)
		return None

def parse_detail_page(html):
	m = re.search('gallery: JSON.parse\("(.*?)"\)', html, re.S)
	images = []
	if m:
		group = m.group(1)
		data = json.loads(group.replace("\\", ""))
		pics = data.get("sub_images")
		for p in pics:
			images.append(p["url"])
		return images

def save_to_mongo(doc):
	if db[MONGO_TABLE].insert(doc):
		print("插入Mongo成功", doc)
		return True
	else:
		return False

def download_image(url):
	try:
		resp = requests.get(url)
		print("正在下载{}".format(url))
		if resp.status_code == 200:
			save_image(resp.content)
		else:
			return None
	except Exception as e:
		print("下载{}失败".format(url))
		print(e)

def save_image(content):
	file = os.getcwd() + os.sep + md5(content).hexdigest + ".jpg"
	if not os.path.exists(file):
		with open(file, "wb") as f:
			f.write(content)
			f.close()

if __name__ == "__main__":
	for i in range(LOAD_TIMES):
		html = get_index_page(i * NUM_PER_TIME, KEY_WORD)
		if html:
			for title, article_url in parse_index_page(html):
				detail_html = get_detail_page(article_url)
				if detail_html:
					images = parse_detail_page(detail_html)
					save_to_mongo({"title": title, "images": images})

