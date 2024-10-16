
from typing import Annotated

from fastapi import Depends, FastAPI
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool

from httpx_interface import lookup_city
from models import ResolvedCity
from db_interface import update_cache, get_city



engine = create_engine(
        "sqlite://",  
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,  
    )


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_session)]

app = FastAPI()


@app.on_event("startup")
def on_startup():
    create_db_and_tables()



@app.get("/cities/{query_city}", status_code=200)
def get_post(query_city: str, session: SessionDep) -> ResolvedCity:
  city = get_city(query_city, session) # returns None if not found

  if not city: #not found in cache

    snow_data = lookup_city(query_city)

    # #add to cache
    update_cache(snow_data, session)  
    # print("updated cache")
    # # retrieve from db
    city = get_city(query_city, session) 
    # print(city)

  return city
    
