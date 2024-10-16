from sqlmodel import SQLModel, Field
from datetime import date
from typing import NamedTuple


class ResolvedCity(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str
    most_recent: str
    next_predicted: str
    expires: date

class City(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str
    resolved_city: int | None = Field(default=None, foreign_key="resolvedcity.id") 


SnowData = NamedTuple("SnowData", [('name', str), ('resolved_name', str), ('most_recent',str), ('next_predicted', str)])