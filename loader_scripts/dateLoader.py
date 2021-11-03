import os
import json
import math
from datetime import date, timedelta
import pandas as pd

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
            data[fileName] = {'__type__': 'structure'}
            loadDirR(filePath, data[fileName])
        else:
            pn = fn2pn(fileName)
            data[pn] = loadFile(filePath)
            data[pn]['__type__'] = 'data'
    return data

def loadDir(path):
    return loadDirR(path, {})

def _transformCardPriceHistory(data):
    newData = {'__type__': 'file'}
    for prop in data:
        if prop == '__type__':
            continue
        datum = data[prop]
        year, month, day = datum['day'].split('-')
        d = date(int(year), int(month), int(day))
        newData[d] = datum['lo']
    return newData

def transformCardPriceHistory(data):
    for propName, card in data['cardPriceHistory'].items():
        if propName == '__type__':
            continue
        for fname in card:
            if fname == '__type__':
                continue
            card[fname] = _transformCardPriceHistory(card[fname])



def _transformCardData(data):
    month, day, year = data['Release Date'].split()
    month = ['jan', 'feb', 'mar', 'apr', 'may', 'jun', 'jul', 'aug', 'sep', 'oct', 'nov', 'dec'].index(month.lower())+1
    day = ''.join([d for d in day if d.isdigit()])
    return date(int(year), int(month), int(day))


def transformCardData(data):
    data['cardData'] = data['cardData']['cardData']
    for propName in data['cardData']:
        if propName == '__type__':
            continue
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
        if coinName == '__type__':
            continue
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
        year = games['Year'][i]
        if math.isnan(year):
            continue
        newData[games['Name'][i]] = date(int(year), 1, 1)
    data['softwareData']['videogame_sales'] = newData

def transformTrendData(data):
    trends = data['trendData']['googleTrendData']
    newData = {}
    for cardName in trends:
        if cardName == 'date' or cardName == '__type__':
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


def _makeContinuous(data):
    dates = [key for key in data if isinstance(key, date)]
    curr = min(dates)
    end = max(dates)
    fill = -1
    while curr != end:
        curr += timedelta(days=1)
        if curr not in data:
            data[curr] = fill


def _makeContinuousR(data):
    for prop in list(data):
        if prop == '__type__':
            continue
        elif isinstance(prop, date):
            _makeContinuous(data)
        else:
            _makeContinuousR(data[prop])

def makeContinuous(data):
    for continuousData in ['cardPriceHistory', 'covidData', 'cryptoData', 'trendData']:
        _makeContinuousR(data[continuousData])
        
def main():
    datadir = '../data/raw'
    data = loadDir(datadir)    
    
    #get dates data
    transformDates(data)
    
    #fill in gaps
    #makeContinuous(data)

    return
            
if __name__ == "__main__":
    main()
