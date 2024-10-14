from pydantic import BaseModel

class CityDantic(BaseModel): 
    name: str 
    resolved_name: str 
    most_recent: str 
    next_predicted: str