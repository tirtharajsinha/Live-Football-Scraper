import json, os
import requests
from pprint import pprint
import datetime


class football_metadata_Scrapper:
    def __init__(self, date) -> None:
        self.data = {}
        self.leagues = {}
        self.teamByLeague = {}
        self.team = {}

        self.metadata_folder_path = "football_metadata"
        self.league_file_name = os.path.join(self.metadata_folder_path, "football_leagues.json")
        self.teamByLeague_file_name = os.path.join(self.metadata_folder_path, "football_teamsByLeague.json")
        self.team_file_name = os.path.join(self.metadata_folder_path, "football_teams.json")
        self.apiUrl = "https://www.goal.com/api/live-scores/refresh?edition=en-in&date={date}&tzoffset=0"

        self.getFootballData(date)
        self.create_metadata_files()

        self.manage_matadata()

    def create_metadata_files(self):
        # Check if the directory already exists
        if not os.path.exists(self.metadata_folder_path):
            # Create the directory
            os.makedirs(self.metadata_folder_path)

        # Check league metadata file exists
        if not os.path.isfile(self.league_file_name):
            with open(self.league_file_name, 'w') as fp:
                pass
        if not os.path.isfile(self.team_file_name):
            with open(self.team_file_name, 'w') as fp:
                pass
        if not os.path.isfile(self.teamByLeague_file_name):
            with open(self.teamByLeague_file_name, 'w') as fp:
                pass

    def manage_matadata(self):
        self.get_league_data()
        self.save_league_data()

        self.get_team_data()
        self.save_team_data()
        self.save_teamByLeage_data()

    def getFootballData(self, date):
        try:
            url = self.apiUrl.format(date=date)
            data = requests.get(url).json()
            # pprint(data)
            self.data = data

        except Exception as e:
            print(e)
            self.data = {}

    def get_league_data(self):
        leagues = {}
        livescores = self.data["liveScores"]
        for league in livescores:
            league_name = league["competition"]["id"]
            leagues[league_name] = league["competition"]

        self.leagues = leagues

    def save_league_data(self):
        with open(self.league_file_name, "r+") as file:
            saved_data = file.read()
            if saved_data == "":
                saved_data = {}
            else:
                saved_data = json.loads(saved_data)

            data = {**saved_data, **self.leagues}
            file.seek(0)
            file.truncate(0)
            file.write(json.dumps(data))
            print(len(data.keys()) - len(saved_data.keys()), "new league(s) added.")

    def get_team_data(self):
        teams = {}
        teamsbyLeague = {}
        livescores = self.data["liveScores"]
        for league in livescores:
            league_name = league["competition"]["id"]
            league_teams = {}
            matches = league["matches"]
            for match in matches:
                teamA = match["teamA"]
                teamB = match["teamB"]
                league_teams[teamA["id"]] = teamA["name"]
                league_teams[teamB["id"]] = teamB["name"]

                teams[teamA["id"]] = teamA
                teams[teamB["id"]] = teamB

            teamsbyLeague[league_name] = league_teams

        self.teams = teams
        self.teamByLeague = teamsbyLeague

        # pprint(self.teams)

    def save_team_data(self):
        with open(self.team_file_name, "r+") as file:
            saved_data = file.read()
            if saved_data == "":
                saved_data = {}
            else:
                saved_data = json.loads(saved_data)

            data = {**saved_data, **self.teams}
            file.seek(0)
            file.truncate(0)
            file.write(json.dumps(data))
            print(len(data.keys()) - len(saved_data.keys()), "new team(s) added.")

    def save_teamByLeage_data(self):
        with open(self.teamByLeague_file_name, "r+") as file:
            saved_data = file.read()
            if saved_data == "":
                saved_data = {}
            else:
                saved_data = json.loads(saved_data)

            for league in self.teamByLeague.keys():
                if league in saved_data.keys():
                    for team in self.teamByLeague[league]:
                        saved_data[league][team] = self.teamByLeague[league][team]
                else:
                    saved_data[league] = self.teamByLeague[league]

            file.seek(0)
            file.truncate(0)
            file.write(json.dumps(saved_data))


startdate = datetime.datetime(2022, 11, 20)
daylimit = 20

for i in range(daylimit):
    rdate = startdate + datetime.timedelta(days=i)
    rdate = rdate.strftime("%Y-%m-%d")
    print(rdate)
    scrapper = football_metadata_Scrapper(rdate)
    print("-"*10)
