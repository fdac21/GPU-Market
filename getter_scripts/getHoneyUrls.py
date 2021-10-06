import urllib.parse
import requests 
import json

def getHoneyProductsUrl(product):
    urlHeader='https://d.joinhoney.com/v3?operationName=web_getSearchResultsData&variables='
    urlScheme='{{"productMeta":{{"categories":"Electronics,Computer,Internal%20Components,Graphics%20Cards","enableCategoryLevelSkip":true,"limit":10,"walletEnabledFilter":false}},"query":"{}"}}'
    return urlHeader + urllib.parse.quote(urlScheme.format(product))

def getHoneyAsinUrls(purl):
    r = requests.get(purl)
    if r.status_code != requests.codes.ok:
        raise Exception("bad url")
    
    json = r.json()
    products = json['data']['getSearchResultsData']['searchProduct']['products']
    
    productAsins = []
    for product in products:
        productAsins.append((product['productId'], product['title']))
    
    return productAsins

def toHoneyUrl(asin):
    timeframe = "99999"
    urlHeader = 'https://d.joinhoney.com/v3?operationName=web_getProductPriceHistory&variables='
    urlScheme = '{{"productId":"{0}","timeframe":{1}}}'
    return urlHeader + urllib.parse.quote(urlScheme.format(asin, timeframe))

def main():

    with open('../products.json') as f:
        products = json.load(f)

        urls = {}
        for product in products:
            purl = getHoneyProductsUrl(product)
            asins = getHoneyAsinUrls(purl)
            urls[product] = {} 

            for (asin, title) in asins:
                dataSetUrl = toHoneyUrl(asin)
                urls[product][title] = dataSetUrl
        
        txt = json.dumps(urls, indent=4)
        print(txt) #use file redirection to save

if __name__ == "__main__":
    main()
