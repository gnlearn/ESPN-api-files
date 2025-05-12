import requests

for i in range(18):
    n = str(i+1)
    team_list = requests.get("http://sports.core.api.espn.com/v2/sports/baseball/leagues/college-softball/teams?page=" + n)
    #http://sports.core.api.espn.com/v2/sports/baseball/leagues/college-softball/teams?page=1
    #https://sports.core.api.espn.com/v2/sports/basketball/leagues/mens-college-basketball/teams?page=
    team_list = team_list.json()
    
    for item in team_list["items"]:
        team_data = requests.get(item["$ref"])
        team_data = team_data.json()

        if "drake" in team_data["displayName"].lower():
            print(team_data["id"])
            print(item)

#softball: 698
#basketball mens: 2181

#http://sports.core.api.espn.com/v2/sports/baseball/leagues/college-softball/seasons/2025/teams/698?lang=en&region=us
