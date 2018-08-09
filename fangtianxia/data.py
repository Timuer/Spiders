import pymongo
import pprint
import re

MONGO_URL = "mongodb://127.0.0.1:27017"
MONGO_DATABASE = "fangtianxia"

client = pymongo.MongoClient(MONGO_URL)
db = client[MONGO_DATABASE]
tab = db["ershoufang"]

log = pprint.pprint

def parse_community():
	with open('community.csv', 'a+', encoding='utf-8') as f:
		doc = tab.find_one()
		lines = doc['community'].split('\n')
		result = ','.join([l.split('：')[0].strip() for l in lines])
		f.write(result + '\n')
		i = 0
		for doc in tab.find():
			print('parsing {}'.format(i))
			lines = doc['community'].split('\n')
			result = ','.join([l.split('：')[1].strip() for l in lines])
			f.write(result + '\n')
			i += 1
			
def parse_rent():
	with open('rent.csv', 'a+', encoding='utf-8') as f:
		i = 0
		for doc in tab.find():
			print('parsing {}'.format(i))
			for d in doc['rent']:
				lines = d.split('\n')
				result = ','.join(lines)
				f.write(result + '\n')
				i += 1
				
def parse_sell():
	with open('sell.csv', 'a+', encoding='utf-8') as f:
		doc = tab.find_one()
		head = parse_sell_head(doc)
		f.write(head + '\n')
		
		for doc in tab.find():
			for d in doc['sell']:
				line = parse_sell_body(d)
				f.write(line + '\n')
		
def parse_sell_head(doc):
	d = doc['sell'][0]
	building_info = d['building_info'].split('\n')
	price = re.sub('\s+', '', d['price'])
	house_info = d['house_info'].split('\n')
	headings = []
	for index, value in enumerate(building_info):
		if index % 2 == 0:
			headings.append(value)
	headings.append('价格')
	headings.extend(['朝向', '楼层', '区域'])
	head = ','.join(headings)
	return head

def parse_sell_body(d):
	building_info = d['building_info'].split('\n')
	price = re.sub('\s+', '', d['price'])
	house_info = d['house_info'].split('\n')
	infos = []
	for index, value in enumerate(building_info):
		if index % 2 == 1:
			infos.append(value)
	infos.append(price)
	infos.append(house_info[0])
	infos.append(house_info[2] + ' ' + house_info[3])
	infos.append(house_info[5])
	return ','.join(infos)
	

	
if __name__ == "__main__":
	parse_sell()