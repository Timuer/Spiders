import requests
from pyquery import PyQuery as pq
import os.path


class Model(object):
	def __repr__(self):
		cls_name = self.__class__.__name__
		props = ["{}: ({})".format(k, v) for k, v in self.__dict__.items()]
		return cls_name + "\n" + "\n".join(props)


class Movie(Model):
	def __init__(self):
		self.ranking = 0
		self.title = ""
		self.info = ""
		self.score = 0
		self.comments = 0
		self.quote = ""
		self.img = ""

def cached_url(url):
	folder = "doubanCached"
	filename = url.split("=")[-1] + ".html"
	file = os.path.join(folder, filename)
	if os.path.exists(file):
		with open(file, "r", encoding="utf-8") as f:
			s = f.read()
			return s
	else:
		if not os.path.exists(folder):
			os.mkdir(folder)
		with open(file, "w", encoding="utf-8") as f:
			r = requests.get(url)
			s = r.content.decode("utf-8")
			f.write(s)
			return s


def movies_from_url(url):
	html = cached_url(url)
	dom_page = pq(html)
	items = dom_page(".item")
	return [movie_from_div(it) for it in items]


def movie_from_div(div):
	d = pq(div)
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
	movies = []
	for i in range(0, 250, 25):
		url = "https://movie.douban.com/top250?start={}".format(i)
		ms = movies_from_url(url)
		movies.extend(ms)
	for m in movies:
		print(m)