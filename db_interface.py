from httpx_interface import next_christmas
from datetime import date
from models import City, ResolvedCity, SnowData
from sqlmodel import Session, select

def update_cache(snow_data: SnowData, session: Session) -> None:
    # check if resolved address already exists
    statement = select(ResolvedCity).where(ResolvedCity.name == snow_data.resolved_name)
    results = session.exec(statement)
    resolved_city = results.first() # may be None if not found
    if not resolved_city: # if not found
        #add to table
        resolved_city = ResolvedCity(name = snow_data.resolved_name, 
                                      most_recent=snow_data.most_recent, 
                                      next_predicted=snow_data.next_predicted,
                                      expires=next_christmas())
        session.add(resolved_city)
        session.commit()
        session.refresh(resolved_city)
    
    # add city to cache
    city = City(name=snow_data.name, resolved_city=resolved_city.id)
    session.add(city)
    session.commit()
    session.refresh(city)

    return None



def get_city(query_city: str, session: Session) -> ResolvedCity:
    statement = select(ResolvedCity).join(City).where(City.name == query_city)
    results = session.exec(statement)
    resolved_city = results.first()

    return resolved_city


# def check_cache(query_city: str) -> CityDantic | None:
#     # q = ResolvedCity.select()
#     # rc = [p for p in q]
#     # if not rc: # dont try to join if RC is empty
#     #     return None

#     q = ResolvedCity.select().join(City).where(City.name == query_city)
#     rc = [p for p in q]
#     if rc:
#       rc = rc[0] # should only be 1
#       if datetime.now() < rc.expires:
#           return CityDantic(name=query_city, 
#                         resolved_name=rc.name, 
#                         most_recent=rc.most_recent,
#                         next_predicted=rc.next_predicted)
#       else:
#           # at least one record is expired, so lets delete all expired 
#           q = ResolvedCity.delete().where(ResolvedCity.expires < datetime.now())
#           q.execute()
#           return None # a new record will be created on update_cache
#     else:
#         return None # not found, need to lookup



# if __name__ == "__main__":
#   print(ResolvedCity.table_exists())
#   print(ResolvedCity._meta.table_name)