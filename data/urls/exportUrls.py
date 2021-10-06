import pymongo, json

user = 'jhammer3'
client = pymongo.MongoClient (host="da1.eecs.utk.edu")
db = client ['fdac21mp2']
coll = db[user]

def insertRow(title, urlDict):
    row = {                                         
        'owner': user,                              
        'topic': 'Historical GPU Prices',           
        'title': title,                             
        'license': 'None',                          
        'description': 'urls harvested from Honey', 
        'urls': list(urlDict.values())              
    }   
    coll.insert_one(row)

def main():
    urls = ['covid_urls.json', 'honey_urls.json']
    for url in urls:
        with open(url) as f:
            data = json.load(f)

            for category in data:
                if not isinstance(data[category], dict):
                    data[category] = {'0': data[category]}
                insertRow(category, data[category])

if __name__ == "__main__":
    main()
