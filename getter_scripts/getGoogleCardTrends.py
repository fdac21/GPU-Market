import json
import pandas as pd
from pytrends.request import TrendReq
pytrends = TrendReq(hl='en-US', tz=240)

def main():

    with open('../products.json') as f:
        products = json.load(f)
        
        data = pd.DataFrame()
        for card in products['cards']:
            pytrends.build_payload([card], timeframe='all')
            pds = pytrends.interest_over_time()
            pds = pds.loc[:, pds.columns != 'isPartial']
            data = pd.concat([data, pds], axis=1)
        
        data.to_csv('googleTrendData.csv')

if __name__ == "__main__":
    main()
