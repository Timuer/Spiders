import requests
from urllib.parse import urlencode

headers = {
	"User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64)"
				  " AppleWebKit/537.36 (KHTML, like Gecko)"
				  " Chrome/67.0.3396.99 Safari/537.36",
	"Referer": "https://www.zhihu.com/"
}

def make_request(url):
	resp = requests.get(url, headers=headers)
	return resp.text

if __name__ == "__main__":
	make_request()