import urllib.parse
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
import requests 
import json
import time
import sys

class CardScraper:
    def __init__(self, cardName, cardID):
        self.cardName = cardName
        self.cardID = cardID

        baseurl = 'https://www.techpowerup.com/gpu-specs/0.{}'
        url = baseurl.format(cardID)
        ua = UserAgent()
        headers = {
            'User-Agent': ua.random
        }
        res = requests.get(url, headers=headers)
        if res.status_code != requests.codes.ok:
            print('REQUEST ERROR! status code: ' + str(res.status_code), file=sys.stderr)
            #print(res.text, file=sys.stderr)
            exit()
        self.soup = BeautifulSoup(res.text, features="lxml")

    def getTag(self, text, tag='dt'):
        tag = self.soup.find(tag, text=text)
        if not tag:
            raise Exception('soup could not find tag ' + str(tag) + ' with text ' + text)
        else:
            return tag

    def getTagData(self, text):
        try:
            tag = self.getTag(text)
            nextTag = tag.find_next('dd')
            return ' '.join(nextTag.text.split()) #remove all whitespace
        except Exception as e:
            print(text + ': ' + str(e), file=sys.stderr)
            return None

    def getCardData(self):
        scrapeFields = [
            'Architecture',
            'Foundry',
            'Process Size',
            'Transistors',
            'Die Size',
            'Base Clock',
            'Boost Clock',
            'Memory Clock',
            'TDP',
            'Suggested PSU',
            'Outputs',
            'Release Date',
            'Availability',
            'Generation',
            'Production',
            'Launch Price',
            'Bus Interface',
            'Memory Size',
            'Memory Type',
            'Memory Bus',
            'Bandwidth',
            'DirectX',
            'OpenGL',
            'OpenCL',
            'Vulkan',
            'CUDA',
            'Shader Model',
            'Shading Units',
            'TMUs',
            'ROPs',
            'Compute Units',
            'L2 Cache',
            'Pixel Rate',
            'Texture Rate',
            'FP16 (half) performance',
            'FP32 (float) performance',
            'FP64 (double) performance',
        ]
        data = {}
        for field in scrapeFields:
            tagData = self.getTagData(field)
            data[field] = tagData if tagData is not None else 'NA'
        return data

def main():

    with open('../products.json') as f:
        data = json.load(f)

        cardData = {}
        for (cardName, cardID) in zip(data['cards'], data['techpowerupIDs']):
            print('processing ' + cardName, file=sys.stderr)
            
            cs = CardScraper(cardName, cardID)
            cardData[cardName] = cs.getCardData()
            #print(cardData[cardName], file=sys.stderr)

            time.sleep(60.0)

        txt = json.dumps(cardData, indent=4)
        print(txt) #use file redirection to save

if __name__ == "__main__":
    main()
