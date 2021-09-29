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
    products = [                    \
        "Nvidia RTX 3060-Ti",       \
        "Nvidia RTX 3070",          \
        "Nvidia RTX 3080",          \
        "Nvidia GTX 1660S (Super)", \
        "Nvidia RTX 2070S (Super)", \
        "Nvidia GTX 1650S (Super)", \
        "Nvidia RTX 2060",          \
        "Nvidia RTX 2060S (Super)", \
        "AMD RX 5600-XT",           \
        "Nvidia GTX 1060-6GB",      \
        "Nvidia GTX 1660-Ti",       \
        "Nvidia GTX 1650",          \
        "Nvidia GTX 1050-Ti",       \
        "AMD RX 5700",              \
        "Nvidia GTX 1070",          \
        "Nvidia RTX 3060",          \
        "AMD RX 590",               \
        "AMD RX 5700-XT",           \
        "AMD RX 580",               \
        "Nvidia GTX 1660",          \
    ]

    urls = {}
    for product in products:
        purl = getHoneyProductsUrl(product)
        asins = getHoneyAsinUrls(purl)
        urls[product] = {} 

        for (asin, title) in asins:
            dataSetUrl = toHoneyUrl(asin)
            urls[product][title] = dataSetUrl
    
    txt = json.dumps(urls, indent=4)
    print(txt)

if __name__ == "__main__":
    main()
