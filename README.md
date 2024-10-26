# Weather Service API

![Weather API](https://raw.githubusercontent.com/dlfelps/dlfelps.github.io/refs/heads/main/assets/images/weather-api-f8i1q.png)

This project was inspired by [Roadmap's Weather Service API](https://roadmap.sh/projects/weather-api-wrapper-service). But with a Christmas twist! This service tells the user two things. For a given (input) city:
1. When was the last White Christmas?
2. How long until there is at least one more White Christmas (within 95% confidence)?

It is written in Python using [FastAPI](https://fastapi.tiangolo.com/) to provide the REST interface and [SQLModel](https://sqlmodel.tiangolo.com/) as the ORM. 

NOTE: This project does not implement a frontend client. The backend web service sends/recieves posts in JSON form. 

## Goals
The goals of this project are to:
- Demonstrate the use of 3rd party APIs
- Demonstrate caching
- Demonstrate the use of environment variables to hide secret keys

## Prerequisites
This service relies on the [Visual Crossing Weather API](https://www.visualcrossing.com/weather-api). Please register to obtain your own API key. Then save the key as an environment varaible ```WEATHER_API_KEY```.

## Installation
1. Clone the repo (git clone https://github.com/dlfelps/let-it-snow.git)
2. Install dependencies (pip install -r requirements.txt)
3. Initialize the ASGI web server (fastapi dev ./main.py)

## Organization of code
The code is divided between four files:
- main.py contains all of the [FastAPI](https://fastapi.tiangolo.com/) code to create the REST interface
- models.py contains the ORM models associated with the service
- db_interface.py contains all of the [SQLModel](https://sqlmodel.tiangolo.com/) code to interface with the cache
- httpx_interface.py contains the 3rd party Visual Crossing interface

## Code highlights
### Environment variables
```
import os 
WEATHER_API_KEY= os.getenv("WEATHER_API_KEY")
```

### Statistical models
```
from scipy.stats import nbinom
ppf = nbinom.ppf(q=0.95,n=1,p=probability) # 95% confidence to the next snow given probability of snow (history)
ppf_year = int(ppf) + get_current_year()
```

### Cache expiration
```
if date.today() < resolved_city.expires:
    return resolved_city #still fresh
else:
    snow_data = lookup_city(query_city)
    update_expired_cache(snow_data, session) 
    results = session.exec(statement)
    resolved_city = results.one() 
    return resolved_city
```

## Example output

### Get White Christmas Info for Paris, France

```
GET /cities/Paris%2C%20France
```
The endpoint should return a `200 OK` status code with the resolved city info:
```json
{
  "id": 1,
  "name": "Paris, Île-de-France, France",
  "most_recent": "The most recent white Christmas in Paris, Île-de-France, France was in 2010.",
  "expires": "2024-12-25",
  "next_predicted": "The next predicted white Christmas in Paris, Île-de-France, France will be before 2079 (with 95% confidence)."
}
```

Notice that the resolved name may be different (more complete) than the query string (e.g. "Paris, France"). The Weather service provides this feature and the cache is implemented using this as a key. The cache expires every year on Christmas and will automatically fetch updated results.

