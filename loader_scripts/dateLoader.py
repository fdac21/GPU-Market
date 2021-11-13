import os
import json
import math
from datetime import date, timedelta
import pandas as pd
from scipy.stats import spearmanr

def fn2pn(fn):
    return os.path.splitext(os.path.basename(fn))[0]

def loadCSV(filePath):
    return pd.read_csv(filePath).to_dict()

def loadJSON(filePath):
    with open(filePath) as f:
        d = json.load(f)
        if isinstance(d, list):
            d = {i: data for i,data in enumerate(d)}
        return d

def loadFile(filePath):
    if 'csv' in filePath:
        return loadCSV(filePath)
    elif 'json' in filePath:
        return loadJSON(filePath)
    else:
        print('could not load ' + filePath, os.stderr)

def loadDirR(path, data):
    for fileName in os.listdir(path):
        filePath = path + '/' + fileName
        if os.path.isdir(filePath):
            data[fileName] = {}
            loadDirR(filePath, data[fileName])
        else:
            pn = fn2pn(fileName)
            data[pn] = loadFile(filePath)
    return data

def loadDir(path):
    return loadDirR(path, {})

def _transformCardPriceHistory(data):
    newData = {}
    for prop in data:
        datum = data[prop]
        year, month, day = datum['day'].split('-')
        d = date(int(year), int(month), int(day))
        newData[d] = datum['lo']
    return newData

def transformCardPriceHistory(data):
    for propName, card in data['cardPriceHistory'].items():
        for fname in card:
            card[fname] = _transformCardPriceHistory(card[fname])



def _transformCardData(data):
    month, day, year = data['Release Date'].split()
    month = ['jan', 'feb', 'mar', 'apr', 'may', 'jun', 'jul', 'aug', 'sep', 'oct', 'nov', 'dec'].index(month.lower())+1
    day = ''.join([d for d in day if d.isdigit()])
    return date(int(year), int(month), int(day))


def transformCardData(data):
    data['cardData'] = data['cardData']['cardData']
    for propName in data['cardData']:
        data['cardData'][propName] = _transformCardData(data['cardData'][propName])


def _addUpCovidData(data):
    s = 0
    for d in data.values():
        s += d
    return s

def transformCovidData(data):
    newData = {}
    data['covidData'] = data['covidData']['data']
    for propName in data['covidData']:
        if not propName[0].isdigit():
            continue
        else:
            month, day, year = propName.split('/')
            newPropName = date(int(year)+2000, int(month), int(day))
            newData[newPropName] = _addUpCovidData(data['covidData'][propName])
    data['covidData'] = newData

def transformCryptoData(data):
    for coinName in data['cryptoData']:
        coin = data['cryptoData'][coinName]
        newData = {}
        for i in range(len(coin['Date'])):
            year, month, day = coin['Date'][i].split()[0].split('-')
            d = date(int(year), int(month), int(day))
            newData[d] = coin['Low'][i]
        data['cryptoData'][coinName] = newData

def transformSoftwareData(data):
    games = data['softwareData']['videogame_sales']
    newData = {}
    for i in range(len(games['Name'])):
        if games['Global_Sales'][i] < 5.00:
            continue
        year = games['Year'][i]
        if math.isnan(year):
            continue
        newData[games['Name'][i]] = date(int(year), 1, 1)
    data['softwareData']['videogame_sales'] = newData

def transformTrendData(data):
    trends = data['trendData']['googleTrendData']
    newData = {}
    for cardName in trends:
        if cardName == 'date':
            continue
        newData[cardName] = {}
        for i in range(len(trends['date'])):
            year, month, day = trends['date'][i].split('-')
            d = date(int(year), int(month), int(day))
            newData[cardName][d] = trends[cardName][i]
    data['trendData']['googleTrendData'] = newData

def transformDates(data):
    transformCardData(data)         #card data
    transformCardPriceHistory(data) #card price history
    transformCovidData(data)        #covid data
    transformCryptoData(data)       #crypto data
    transformSoftwareData(data)     #softwareData
    transformTrendData(data)        #trend data
    makeContinuous(data)

def _makeContinuous(fdeltaTime, data):
    ndata = {}
    currDate = data + timedelta(fdeltaTime)

    inc = 1 if fdeltaTime < 0 else -1
    n = 0
    while currDate != data:
        ndata[currDate] = n/abs(fdeltaTime)
        currDate += timedelta(inc)
        n += 1
    return ndata

def makeContinuous(data):
    keys = data['cardPriceHistory'].keys()
    for continuousData in data.keys():
        if continuousData in ['cardPriceHistory', 'covidData', 'cryptoData', 'trendData', 'cryptoCoins']:
            continue
        for d, pd, p in getNestedData(data[continuousData]):
            fd = (date.today() - d).days
            if fd > 4000:
                del pd[p]
            else:
                pd[p] = {**_makeContinuous(-80, d), **_makeContinuous(fd, d)}
    
    
def getNestedData(data, parentData = {}, parentProp=''):
    if isinstance(data, date):
        yield data, parentData, parentProp
        return
    for prop in list(data):
        if prop == 'cryptoCoins':
            continue
        if isinstance(prop, date):
            yield data, parentData, parentProp
            break
        else:
            yield from getNestedData(data[prop], data, prop)

def getCC(d1, f1, d2, f2):
    dsmall = min(d1, d2, key=lambda x: len(x))
    dlarge = max(d1, d2, key=lambda x: len(x))

    dcommon = [k for k in dsmall if k in dlarge]
    if len(dcommon) <= 2:
        return None

    data1 = [v for k,v in dsmall.items() if k in dcommon]
    data2 = [v for k,v in dlarge.items() if k in dcommon]
    corr, _ = spearmanr(data1, data2)
    if math.isnan(corr):
        return None

    return {'gpu': f1, 'factor': f2, 'correlation': corr}

def getCCAll(data1, data2):
    corrs = []
    for d1, _, f1 in getNestedData(data1):
        for d2, _, f2 in getNestedData(data2):
            corr = getCC(d1, f1, d2, f2)
            if corr is not None:
                corrs.append(corr)
    return corrs


def main():
    datadir = '../data/raw'
    data = loadDir(datadir)    
    
    #get dates data
    transformDates(data)

    priceHistory = data['cardPriceHistory']
    others = {k: data[k] for k in data.keys() if k != 'cardPriceHistory'}


    corrs = getCCAll(priceHistory, others) 
    corrs = sorted(corrs, key=lambda x: x['correlation'], reverse=True)

    for corr in corrs:
        print(corr)


    return
            
if __name__ == "__main__":
    main()
