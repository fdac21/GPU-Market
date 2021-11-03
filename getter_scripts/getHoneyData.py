import os
import requests 
import json
import time

def downloadURLData(url):
    r = requests.get(url)
    if r.status_code != requests.codes.ok:
        raise Exception(r.status_code, r)
    return r.json()

def toCardFileName(venderName):
    return ("_".join(venderName.replace('/', '-').replace(',', '').split()) + '.json')

def main():
    with open('../data/urls/honey_urls.json') as f:
        cards = json.load(f)
        saveDir = '../data/raw/cardPriceHistory'
        os.makedirs(saveDir, exist_ok=True)
        for i, cardName in enumerate(cards):
            card = cards[cardName]
            cardDir = saveDir + '/' + toCardFileName(cardName)
            os.makedirs(cardDir, exist_ok=True)
            for j, venderCardName in enumerate(card):
                cfn = toCardFileName(venderCardName)
                url = card[venderCardName]
                data = downloadURLData(url)
                data = data['data']['getProductPriceHistory']['history']
                with open(cardDir + '/' + cfn, 'w') as ofile:
                    json.dump(data, ofile)
                time.sleep(10)

if __name__ == "__main__":
    main()
