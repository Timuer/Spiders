from utils import Model
from LightSpiderFrame import Spider

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


def parse_item(e):
	b = Blog()
	b.link = e.attr("href")
	b.title = e("[class^='list_title']").text()
	b.vote = e("em").eq(-1).text()
	b.comment = e("em").eq(-3).text()
	b.forward = e("em").eq(-5).text()
	return b


if __name__ == "__main__":
	spider = Spider()
	for c in categories:
		u = url_from_category(categories[c])
		spider.load_dynamic_page(u, 5)
		print(spider.page)
		spider.parsed_items("[class^='UG_list']", parse_item)
	for i in spider.items:
		print(i)



