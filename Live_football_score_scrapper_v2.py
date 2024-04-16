import json
from json import JSONDecodeError
import requests
from bs4 import BeautifulSoup
import os, pytz, datetime, re
from pprint import pprint
from dateutil import tz


class Scrapper:
    def __init__(self) -> None:
        self.data = {}
        self.leagues = []
        self.sourceUrl = "https://www.goal.com/en-in/fixtures/"
        self.apiUrl = "https://www.goal.com/api/live-scores/refresh?edition=en-in&date={date}&tzoffset=0"

    def getFootballData(self, fixturedate=None):
        try:
            if fixturedate==None:
                dt_now = datetime.datetime.now(pytz.timezone("GMT"))
                fixturedate = dt_now.strftime("%Y-%m-%d")
            url=self.apiUrl.format(date=fixturedate)
            data = requests.get(url).json()
            data["FixtureDate"]=fr"{fixturedate} GMT"
            pprint(data)
            return data

        except Exception as e:
            print(e)
            return {}


scrapper = Scrapper()
scrapper.getFootballData()

