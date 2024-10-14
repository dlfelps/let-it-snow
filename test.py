from db_interface import City as CityTable
from db_interface import ResolvedCity
from httpx_interface import lookup_city
from datetime import datetime
import os

def test_db():
  rc = ResolvedCity.create(name = "Moscow, Russia", most_recent="", next_predicted="", expires=datetime.now())
  c = CityTable.create(name="Moscow, RU", resolved_city=rc)
  q = ResolvedCity.select().join(CityTable).where(CityTable.name == c.name)
  found_rc = [p for p in q]
  if found_rc:    
    print(found_rc[0])
  else:
    print("No record found")


def test_httpx():
  print(lookup_city('Paris, France'))


def test_delete():
  test_db()
  ResolvedCity.delete_by_id(1)
  q = CityTable.select()
  found_rc = [p for p in q]
  if found_rc:    
    print(found_rc[0])
  else:
    print("No record found (correct answer). City was deleted because SQLITE ON_DELETE set to CASCADE")

def test_api_key():
  WEATHER_API_KEY= os.getenv("WEATHER_API_KEY")
  print(WEATHER_API_KEY)

if __name__ == "__main__":
  print(ResolvedCity.table_exists())
  print(ResolvedCity._meta.table_name)
  