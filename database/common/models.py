from peewee import Model, CharField, IntegerField, FloatField, TextField, DateTimeField
from database.core import db
import datetime

class BaseModel(Model):
    class Meta:
        database = db

class SearchHistory(BaseModel):
    user_id = IntegerField()
    query = CharField()
    date = DateTimeField(default=datetime.datetime.now)

class Movie(BaseModel):
    title = CharField()
    description = TextField()
    rating = FloatField()
    year = IntegerField()
    genre = CharField()
    age_rating = CharField()
    poster_url = CharField()
