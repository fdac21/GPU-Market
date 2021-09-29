import pymongo, json

user = 'jhammer3'
client = pymongo.MongoClient (host="da1.eecs.utk.edu")
db = client ['fdac21mp2']
coll = db[user]

def insertRow(title, urlDict):
    row = {                                         \
        'owner': user,                              \
        'topic': 'Historical GPU Prices',           \
        'title': title,                             \
        'license': 'None',                          \
        'description': 'urls harvested from Honey', \
        'urls': list(urlDict.values())              \
    }   
    coll.insert_one(row)

def main():
    with open("urls.json") as f:
        data = json.load(f)

        for category in data:
            insertRow(category, data[category])

if __name__ == "__main__":
    main()
