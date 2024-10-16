from models import City, ResolvedCity
from httpx_interface import lookup_city
from datetime import date
import os
from sqlmodel import create_engine, Session, SQLModel, select
from sqlmodel.pool import StaticPool

engine = create_engine(
        "sqlite://",  
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,  
    )

SQLModel.metadata.create_all(engine)

def test_db():
  with Session(engine) as session:    
    rc = ResolvedCity(name = "Moscow, Russia", most_recent="", next_predicted="", expires=date.today())
    session.add(rc)
    session.commit()

    c = City(name="Moscow, RU", resolved_city=rc.id)
    session.add(c)
    session.commit()

    statement = select(City)
    results = session.exec(statement)
    print(results.first())


def test_httpx():
  print(lookup_city('Paris, France'))

def test_session_type():
  with Session(engine) as session:
    print(type(session))

def test_blank():
  with Session(engine) as session:
    statement = select(ResolvedCity)
    results = session.exec(statement)
    resolved_city = results.first()
    print(resolved_city)

def test_api_key():
  WEATHER_API_KEY= os.getenv("WEATHER_API_KEY")
  print(WEATHER_API_KEY)

if __name__ == "__main__":
  test_blank()
  