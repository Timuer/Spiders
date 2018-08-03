from utils import Model
from LightSpiderFrame import Spider


class Movie(Model):
	def __init__(self):
		self.ranking = 0
		self.title = ""
		self.info = ""
		self.score = 0
		self.comments = 0
		self.quote = ""
		self.img = ""


def movie_from_div(d):
	m = Movie()
	m.ranking = d(".pic").find("em").text()
	m.title = d(".title").text()
	m.info = d(".bd").find("p").eq(0).text()
	m.score = float(d(".star").find(".rating_num").text())
	m.comments = int(d(".star").find("span").eq(-1).text()[:-3])
	m.quote = d(".inq").text()
	m.img = d(".pic").find("img").attr("src")
	return m

if __name__ == "__main__":
	spider = Spider()
	for i in range(0, 250, 25):
		url = "https://movie.douban.com/top250?start={}".format(i)
		spider.cached_url(url, folder="doubanCached")
		spider.parsed_items(".item", movie_from_div)
		spider.save("douban.json")