from pymongo import MongoClient
import pprint
import re

client = MongoClient('mongodb://localhost:27017/')
db = client['anjuke']
collection = db['office_building']

def save_houses():
	index = 0
	for doc in collection.find():
		print("writting document {}".format(index))
		houses = doc['houses']
		with open("anjuke.csv", "a+", encoding="utf-8") as f:
			for h in houses:
				infos = h.split('\n')
				try:
					s = ','.join([infos[1], infos[3], infos[6], infos[8], infos[10], infos[12], infos[14], infos[16], infos[18], infos[20], infos[22], infos[24]])
					s += "\n"
				except Exception as e:
					print(e)
					s = ""
				f.write(s)
		index += 1
	
def save_communities():
	index = 0
	for doc in collection.find():
		print("writting document {}".format(index))
		infos = []
		for key, value in doc.items():
			if key == 'price':
				print(value)
				value = re.sub(r"\s+", "", value)
				infos.append(value)
			elif key not in ["houses", "_id"]:
				infos.append(value)
		s = ','.join(infos) + '\n'
		with open("communities.csv", "a+", encoding="utf-8") as f:
				f.write(s)
		index += 1
		
def save_office_buildings():
	index = 0
	with open("office.csv", "a+", encoding="utf-8") as f:
		for doc in collection.find():
			print("writting document {}".format(index))
			infos = doc['info'].split('\n')
			desc = re.sub(r'\s+', '  ', doc['desc'])
			s = ""
			for index, value in enumerate(infos):
				if index % 2 != 0:
					s += infos[index] + ','	
			s += desc + '\n'
			f.write(s)
			index += 1
	

		
if __name__ == "__main__":
	save_office_buildings()