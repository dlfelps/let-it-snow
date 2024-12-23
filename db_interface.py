from httpx_interface import next_christmas, lookup_city
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

    
    # add city to cache if not there
    statement = select(City).where(City.name == snow_data.name)
    results = session.exec(statement)
    city = results.first() # may be None if not found
    if not city:
        city = City(name=snow_data.name, resolved_city=resolved_city.id)
        session.add(city)
        session.commit()
        session.refresh(city)

    return None


def update_expired_cache(snow_data: SnowData, session: Session) -> None:
    # only used to update ResolvedCity table

    # check if resolved address already exists
    statement = select(ResolvedCity).where(ResolvedCity.name == snow_data.resolved_name)
    results = session.exec(statement)
    resolved_city = results.one() # may be None if not found
    resolved_city.most_recent = snow_data.most_recent
    resolved_city.next_predicted = snow_data.most_recent
    resolved_city.expires = next_christmas()
    session.add(resolved_city)
    session.commit()
    session.refresh(resolved_city)
    

    return None


def get_city(query_city: str, session: Session) -> ResolvedCity:
    statement = select(ResolvedCity).join(City).where(City.name == query_city)
    results = session.exec(statement)
    resolved_city = results.first()

    if resolved_city:
        if date.today() < resolved_city.expires:
            return resolved_city #still fresh
        else:
            snow_data = lookup_city(query_city)
            update_expired_cache(snow_data, session) 
            results = session.exec(statement)
            resolved_city = results.one() 
            return resolved_city
    else:
        return None
    

