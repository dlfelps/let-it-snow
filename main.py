
from typing import Annotated
from contextlib import asynccontextmanager
from peewee import Model, SqliteDatabase, CharField, IntegerField, ForeignKeyField, DateTimeField
from fastapi import FastAPI
from models import CityDantic

from db_interface import  get_city, update_cache, check_cache
from httpx_interface import lookup_city


db = SqliteDatabase(':memory:', pragmas={
  'journal_mode': 'wal',
  'cache_size': -1 * 64000,  # 64MB
  'foreign_keys': 1,
  'ignore_check_constraints': 0,
  'synchronous': 0})


class BaseModel(Model):
    class Meta:
        database = db
        legacy_table_names=False

class ResolvedCity(BaseModel):
    id = IntegerField(primary_key=True)
    name = CharField(max_length=255)
    most_recent = CharField(max_length=255)
    next_predicted = CharField(max_length=255) 
    # expires = DateTimeField()

class CityDB(BaseModel):
    id = IntegerField(primary_key=True)
    name = CharField(max_length=255)
    resolved_city = ForeignKeyField(ResolvedCity, backref='aliases', on_delete='CASCADE') # CASCADE deletes this city if its resolved city is deleted




@asynccontextmanager
async def lifespan(app: FastAPI):

  db.connect()
  db.create_tables([ResolvedCity, CityDB])
  yield
  db.close()

app = FastAPI(lifespan=lifespan)



@app.get("/cities/{query_city}", status_code=200)
def get_post(query_city: str) -> CityDantic:
  # city = check_cache(query_city) 
  city = None
  if not city: #not found in cache

    city = lookup_city(query_city)

    # #add to cache
    update_cache(city)  
    # print("updated cache")
    # # retrieve from db
    city = get_city(query_city) 
    # print(city)

  return city
    
