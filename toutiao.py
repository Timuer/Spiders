from utils import Model
from LightSpiderFrame import Spider

categories = {
	"热点": "news_hot",
	"科技": "news_tech",
	"娱乐": "news_entertainment",
	"游戏": "news_game",
	"体育": "news_sports",
	"汽车": "news_car",
	"财经": "news_finance",
	"搞笑": "news_funny",
}


class Toutiao(Model):
	def __init__(self):
		self.title = ""
		self.time_past = ""
		self.comment = ""
		self.source = ""


def url_from_category(category):
	return "https://www.toutiao.com/ch/{}".format(category)


def parse_item(item):
	t = Toutiao()
	t.title = item.find(".title-box").text()
	t.time_past = item.find(".lbtn").eq(-1).text()
	t.comment = item.find(".lbtn.comment").text()[:-4]
	t.source = item.find(".lbtn.source").text()[:-2]
	return t


if __name__ == "__main__":
	spider = Spider()
	for c in categories:
		u = url_from_category(categories[c])
		spider.load_dynamic_page(u, 5)
		spider.parsed_items(".rbox-inner", parse_item)
	for i in spider.items:
		print(i)