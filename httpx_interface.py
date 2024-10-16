import httpx
import urllib.parse
from datetime import date
from functools import reduce
from scipy.stats import nbinom
from datetime import date
import os
from models import SnowData


WEATHER_API_KEY= os.getenv("WEATHER_API_KEY")
WEATHER_API_URL="https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline/"



def next_christmas() -> date:
    today = date.today()
    this_christmas = date(today.year,12,25) #christmas of the same year

    if today < this_christmas: #before end of christmas day
        next_christmas = this_christmas
    else:
        next_christmas = date(today.year + 1,12,25) # you have to wait another year
    return next_christmas

def get_current_year():
    nc = next_christmas()
    return nc.year

def get_dates():
    return [date(year,12,25) for year in range(2000,get_current_year())]
    
def get_history(query_city):
    
    def build_query(query_city, query_date):
        return f"{WEATHER_API_URL}{urllib.parse.quote(query_city)}/{str(query_date)}/{str(query_date)}?unitGroup=metric&include=days&key={WEATHER_API_KEY}&contentType=json"
    
    def get_json(query_city, query_date):
        query = build_query(query_city, query_date)
        r = httpx.get(query)
        return r.json()
        
    dates = get_dates()
    history = []
    for date in dates:
        history.append(get_json(query_city, date))
    return history

def get_snow_from_json(history):
    return history['days'][0]['snowdepth']

def get_resolved_name(history):
    return history['resolvedAddress']

def get_most_recent_white_christmas(history):
    def _last(year, date_snow_tuple):
        new_year = date_snow_tuple[0].year
        is_snow = date_snow_tuple[1]
        if is_snow:
            return new_year
        else:
            return year
    dates = get_dates()
    snow_amount = map(get_snow_from_json, history) # may include Nones
    combined = zip(dates, snow_amount)    
    return reduce(_last,combined, None)

def lookup_city(query_city):
    history = get_history(query_city)
    snow = list(map(get_snow_from_json, history))
    resolved_name=get_resolved_name(history[0])
    obs = list(filter(lambda x: x != None, snow))
    snow = list(filter(lambda x: x > 0, obs))
    
    if snow:
        probability = len(snow) / len(obs)
        ppf = nbinom.ppf(q=0.95,n=1,p=probability) # 95% confidence to the next snow (n=1) given probability of snow (history)
        ppf_year = int(ppf) + get_current_year()
        most_recent = f"The most recent white Christmas in {resolved_name} was in {get_most_recent_white_christmas(history)}."
        next_predicted = f"The next predicted white Christmas in {resolved_name} will be before {ppf_year} (with 95% confidence)."
    else:
        most_recent = f"There hasn't been a recorded white Chirstmas in {resolved_name} since 2000."
        next_predicted = f"Unable to predict next white Christmas in {resolved_name}."

    return SnowData(name=query_city, 
                resolved_name=resolved_name,
                most_recent=most_recent,
                next_predicted=next_predicted)