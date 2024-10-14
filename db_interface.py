from peewee import Model, SqliteDatabase, CharField, IntegerField, ForeignKeyField, DateTimeField
from models import City as CityDantic
from httpx_interface import next_christmas
from datetime import datetime









def update_cache(city: CityDantic) -> None:
    # check if resolved address already exists
    resolved_city = ResolvedCity.get_or_none(ResolvedCity.name == city.resolved_name)
    if not resolved_city:
        #add to table
        resolved_city = ResolvedCity.create(name = city.resolved_name, 
                                            most_recent=city.most_recent, 
                                            next_predicted=city.next_predicted,
                                            expires=next_christmas())
    
    # add city to cache
    city = City.create(name=city.name, resolved_city=resolved_city)

    return None


def get_city(query_city: str) -> CityDantic:
    q = ResolvedCity.select().join(City).where(City.name == query_city)
    rc = [p for p in q]
    rc = rc[0] # should only be 1
    return CityDantic(name=query_city, 
                      resolved_name=rc.name, 
                      most_recent=rc.most_recent,
                      next_predicted=rc.next_predicted)


def check_cache(query_city: str) -> CityDantic | None:
    # q = ResolvedCity.select()
    # rc = [p for p in q]
    # if not rc: # dont try to join if RC is empty
    #     return None

    q = ResolvedCity.select().join(City).where(City.name == query_city)
    rc = [p for p in q]
    if rc:
      rc = rc[0] # should only be 1
      if datetime.now() < rc.expires:
          return CityDantic(name=query_city, 
                        resolved_name=rc.name, 
                        most_recent=rc.most_recent,
                        next_predicted=rc.next_predicted)
      else:
          # at least one record is expired, so lets delete all expired 
          q = ResolvedCity.delete().where(ResolvedCity.expires < datetime.now())
          q.execute()
          return None # a new record will be created on update_cache
    else:
        return None # not found, need to lookup



if __name__ == "__main__":
  print(ResolvedCity.table_exists())
  print(ResolvedCity._meta.table_name)