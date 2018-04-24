from pyquery import PyQuery as qp
from LightSpiderFrame import Spider
from utils import Model
from utils import reconnect
import json
import os

base_url = "https://wh.lianjia.com"
classes = ["ershoufang"]
positions = [
	"jiangan",
	"jianghan",
	"qiaokou",
	"dongxihu",
	"wuchang",
	"qingshan",
	"hongshan",
	"hanyang",
	"donghugaoxin",
	"jiangxia",
]


class House(Model):
	def __init__(self):
		self.title = ""
		self.address = ""
		self.date = ""
		self.follow = ""
		self.price = ""


spider = Spider()

def make_url(base, cls, position, page):
	return "/".join([base, cls, position, "pg{}".format(page)])


@reconnect
def get_page_limit(base, cls, pos):
	url = "/".join([base, cls, pos])
	spider.cached_url(url, folder="lianjiaCached", render=True)
	e = qp(spider.page)
	attr = e(".house-lst-page-box").attr("page-data")
	try:
		d = json.loads(attr, encoding="utf-8")
		return int(d['totalPage'])
	except Exception as ex:
		print(ex)
		return 0


def parse_item(item, **kwargs):
	h = House()
	h.title = item.find(".title").text()
	h.address = item.find(".address").text()
	h.date = item.find(".flood").text()
	h.follow = item.find(".followInfo").text()
	h.price = item.find(".priceInfo").text()
	for k, v in kwargs.items():
		setattr(h, k, v)
	return h


@reconnect
def parse_from_pages():
	for cls in classes:
		for pos in positions:
			limit = get_page_limit(base_url, cls, pos)
			for pg in range(1, limit + 1):
				url = make_url(base_url, cls, pos, pg)
				print("caching {}".format(url))
				spider.cached_url(url, "lianjiaCached", render=True)
				spider.parsed_items(".clear.info", parse_item, cls=cls, position=pos)
			spider.save("db{}{}.json".format(os.sep, pos))
			spider.clear()
	spider.destroy()


if __name__ == "__main__":
	parse_from_pages()




