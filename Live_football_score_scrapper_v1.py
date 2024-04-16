import requests
from bs4 import BeautifulSoup
import os, pytz, datetime, re
from pprint import pprint
from dateutil import tz
from dateutil.parser import parse


class Live_football_data_scrapper:
    def __init__(self):
        pass

    def validate_date(self, date_text):
        try:
            return parse(date_text)
        except ValueError:
            return False

    def swap_positions(self, list, pos1, pos2):
        """
        Function to swap item positions in a list.

        Called later
        """

        list[pos1], list[pos2] = list[pos2], list[pos1]

    def clean_data(self, list):
        """
        Changing all instances of 'Premier League' to 'English Premier League' for better consistency.
        Also chops away all unnecessary string data.

        Called later
        """

        prem_header = ">Premier League</h3>"
        EPL_header = ">English Premier League</h3>"
        prem_span = "$0Premier League"
        EPL_span = "$0English Premier League"

        for indx, item in enumerate(list):
            if prem_header in item:
                list[indx] = list[indx].replace(prem_header, EPL_header)
            elif prem_span in item:
                list[indx] = list[indx].replace(prem_span, EPL_span)
            else:
                item

        leagues = [
            "English Premier League",
            "Spanish La Liga",
            "German Bundesliga",
            "Italian Serie A",
            "French Ligue 1",
            "Champions League",
            "United States Major League Soccer",
            "FIFA World Cup",
            "Europa League",
            "Europa Conference League",
            "CONMEBOL Copa America",
        ]

        list = [i[-145:] for i in list]
        left, right = '">', "</"
        # print(list)
        list = [
            [l[l.index(left) + len(left): l.index(right)] for l in list if i in l]
            for i in leagues
        ]

        return list

    def home_and_away(self, list):
        """
        For games that haven't occured yet, our scraper will return Home Team, Away Team, and game time.
        There will be an empty spot '' where our scraper tried to scrape the minute the game is in, but since
        the game has yet to start it is empty.

        This function fills the blank space with an (H) to signify home team, then creates a new blank space
        and fills it with an (A) to signify away team, and re-orders the list so it reads:

        'Home Team, (H), Away Team, (A), Game time'

        Called later
        """

        for i in list:
            while "" in i:
                self.swap_positions(i, i.index(""), i.index("") - 2)
                blank = i.index("")
                blank_2 = i.index("") + 2
                i[blank] = "(H)"
                i.insert(blank_2, "(A)")

    def scraping(self, getLocalDate):
        """
        Web scraping code
        """

        url = "https://www.bbc.com/sport/football/scores-fixtures/" + getLocalDate

        html_content = requests.get(url).text

        soup = BeautifulSoup(html_content, "html.parser")

        tags = ["span", "h3"]
        classes = [
            "gs-u-display-none gs-u-display-block@m qa-full-team-name sp-c-fixture__team-name-trunc",
            "sp-c-fixture__status-wrapper qa-sp-fixture-status",
            "sp-c-fixture__number sp-c-fixture__number--time",
            "sp-c-fixture__number sp-c-fixture__number--home",
            "sp-c-fixture__number sp-c-fixture__number--home sp-c-fixture__number--ft",
            "sp-c-fixture__number sp-c-fixture__number--home sp-c-fixture__number--live-sport",
            "sp-c-fixture__number sp-c-fixture__number--away sp-c-fixture__number--live-sport",
            "sp-c-fixture__number sp-c-fixture__number--away sp-c-fixture__number--ft",
            "sp-c-fixture__win-message",
            "gel-minion sp-c-match-list-heading",
        ]

        scraper = soup.find_all(tags, attrs={"class": classes})
        data = [str(l) for l in scraper]

        data = self.clean_data(data)  # Functiom call
        self.home_and_away(data)  # Function call

        data = [l for l in data if len(l) != 0]

        return data

    def dataSerializing(self, raw, utcdate):
        from_zone = pytz.timezone("GMT")
        to_zone = tz.tzlocal()
        data = {}
        # print(raw)
        for league in raw:
            league_name = league[0]
            data[league_name] = []
            data_id = 1
            while data_id < len(league):
                try:
                    game = league[data_id: data_id + 5]
                    # print(game)

                    gameTime = game[4]

                    status = "fulltime"

                    if gameTime == "HT":
                        status = "halftime"

                    if "(H)" in game[1]:
                        londontime = datetime.datetime.strptime(
                            utcdate.strftime("%Y-%m-%d-") + gameTime, "%Y-%m-%d-%H:%M"
                        )
                        londontime = londontime.replace(tzinfo=from_zone)
                        central = londontime.astimezone(to_zone)
                        gameTime = central.strftime("%H:%M")
                        status = "not_played"

                    if "span" in gameTime:
                        soup = BeautifulSoup(gameTime, "html.parser")
                        gameTime = soup.find("span").text
                        status = "live"

                    gameObject = {
                        "h_team": game[0].replace("&amp;", "&"),
                        "h_score": game[1],
                        "a_team": game[2].replace("&amp;", "&"),
                        "a_score": game[3],
                        "time": gameTime,
                        "status": status,
                    }

                    if gameTime == "AET":
                        gameObject["AET"] = league[data_id + 5]
                        # print(league[data_id+5])
                        data_id += 1

                    # print(data_id)

                    data[league_name].append(gameObject)
                    data_id += 5
                except:
                    break

        finalData = {"date": utcdate.strftime("%Y-%m-%d %Z"), "result": data}
        return finalData

    def getFootballLiveFixtures(self, getLocalDate=None):
        if getLocalDate == None:
            dt_now = datetime.datetime.now(pytz.timezone("GMT"))
            getLocalDate = dt_now.strftime("%Y-%m-%d")
        else:
            valiadatedDate = dataScrapper.validate_date(getLocalDate)
            if not valiadatedDate:
                raise Exception("In-Valid Date or date Format")
            else:
                to_zone = pytz.timezone("GMT")
                from_zone = tz.tzlocal()
                print(valiadatedDate)
                valiadatedDate = valiadatedDate.replace(tzinfo=from_zone)
                dt_now = valiadatedDate.astimezone(to_zone)

        data = self.scraping(getLocalDate)
        sData = self.dataSerializing(data, dt_now)
        return sData


if __name__ == "__main__":
    dataScrapper = Live_football_data_scrapper()
    sData = dataScrapper.getFootballLiveFixtures()
    pprint(sData)
