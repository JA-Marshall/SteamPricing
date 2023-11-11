#Gets the last 30 days of sales data for a given steam item name, removing any outliers using a hampel filter 

import requests
import json
import datetime
import hampel
import time
import pandas as pd

def get_market_data_from_name(name,game_id,cookie):
    name_http = name.replace(' ','%20')
    name_http = name_http.replace('&','%26')

    response = requests.get(f'https://steamcommunity.com/market/pricehistory/?appid={game_id}&market_hash_name={name_http}&currency=2', cookies=cookie)
    print(f'got {response} from steam')

    if response.status_code==400:
        raise Exception("Error 400, Cookie might be expried")
    elif response.status_code==404:
        raise Exception("Error 404, something wrong with url")
    
    elif response.status_code==200:
        item = response.content
        item = json.loads(item)
        if item['prices'] !=None: 
            unpack_pricedata(item)
        else:
            #no price data avaliable (no sales)
            return(0.00) 
    else:
        raise Exception(f"got repsonse code{response.status_code}...?")


def unpack_pricedata(item):
  
    prices = item['prices']
    #
    #prices = [mm dd yyyy hh: +0, x.xx,'y']   x = price in gbp, y = vol
    ##eg  [['Oct 06 2  022 01: +0', 1.053, '340'], ['Oct 07 2022 01: +0', 0.68, '870']]
    
    #convert it into indiviusal transactions as a tuple using unix timestamps 
    #((1691276400, 0.362), (1691276400, 0.362), (1691276400, 0.362), (1691276400, 0.362),
    
    new_price_list = []
    
    #data is sorted oldest to newest and goes back 10 years on some item we only want 1 month,
    prices.reverse()
   
    cutoff_time = round(time.time()) - 2592000      # 30 days ago 

    for price in prices:

        date = price[0]
        date = date[:-7]
    
        timestamp = get_timestamp(date)
        volume = int(price[2])
        gbp_price =float(price[1])
        if cutoff_time > timestamp:
             break
        else:
            for i in range(volume):

                new_price_list.append((timestamp,gbp_price))
    new_price_list.reverse()

    tuplelist = tuple(new_price_list)
    filter_price_anomalies(tuplelist)


def get_timestamp(date):
    months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    date = date.split(" ")
    day = int(date[1])
    year = int(date[2])
    month = int(months.index(date[0])) + 1
    timestamp = round(datetime.datetime(year,month,day).timestamp())
    
    return timestamp

def filter_price_anomalies(data):
    timestamps,prices=zip(*data)
    ts = pd.Series(prices)
    ts_imputation = hampel(ts, window_size=5, n=3, imputation=True)

    return ts.to_numpy()
