import requests
from pyquery import PyQuery as pq
from selenium import webdriver
import time

categories = {
	"热门": "0",
	"头条": "1760",
	"新鲜事": "novelty",
	"搞笑": "10011",
	"社会": "7",
	"时尚": "12",
	"军事": "4",
	"美女": "10007",
}

class Model(object):
	def __repr__(self):
		cls_name = self.__class__.__name__
		props = ["{}: ({})".format(k, v) for k, v in self.__dict__.items()]
		return cls_name + "\n" + "\n".join(props)


class Blog(Model):
	def __init__(self):
		self.title = ""
		self.forward = 0
		self.comment = 0
		self.vote = 0
		self.link = ""


def url_from_category(category):
	url = "https://weibo.com/?category={}".format(category)
	return url


def get_items(url, iter_per_category):
	# headers = {
	# 	"User-Agent": "User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36 Edge/16.16299",
	# 	"Referer": "https://weibo.com/",
	# }
	# page = requests.get(url, headers)
	# e = pq(page.content.decode("utf-8", errors="replace"))

	driver = webdriver.Chrome()
	driver.get(url)
	for i in range(iter_per_category):
		time.sleep(5)
		driver.get_screenshot_as_file("{}.png".format(i))
		driver.execute_script("window.scrollTo(0, document.body.scrollHeight)")
	e = pq(driver.page_source)
	driver.close()
	items = e("[class^='UG_list']")
	return (parsed_item(it) for it in items)


def parsed_item(item):
	b = Blog()
	e = pq(item)
	b.link = e.attr("href")
	b.title = e("[class^='list_title']").text()
	b.vote = e("em").eq(-1).text()
	b.comment = e("em").eq(-3).text()
	b.forward = e("em").eq(-5).text()
	return b


if __name__ == "__main__":
	for c in categories:
		u = url_from_category(categories[c])
		for i in get_items(u, 10):
			print(i)



