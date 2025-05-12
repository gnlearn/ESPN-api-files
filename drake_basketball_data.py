import requests
from datetime import datetime, timezone

#relatively large issue, we don't get soccer, or baseball
#we don't have these teams
#college baseball endpoint: https://sports.core.api.espn.com/v2/sports/baseball/leagues/college-baseball
#college softball: https://sports.core.api.espn.com/v2/sports/baseball/leagues/college-softball
#2181 drake team id
#schedule: http://sports.core.api.espn.com/v2/sports/basketball/leagues/mens-college-basketball/events?lang=en&region=us
#odds: http://sports.core.api.espn.com/v2/sports/basketball/leagues/mens-college-basketball/events/401708415/competitions/401708415/odds?lang=en&region=us

#need score and win value to be constantly pulled
#games and odds

def get_basketbeach_game_data(source):

    if source == "current":
        general_data = requests.get("https://sports.core.api.espn.com/v2/sports/basketball/leagues/mens-college-basketball")
        general_data = general_data.json()

        game_list = requests.get(general_data["events"]["$ref"])
        game_list = game_list.json()

        game_info_links_dict = game_list["items"]

        game_info_links = []
        
        for i in game_info_links_dict:
            game_info_links.append(i["$ref"])

        game_info = get_game_info(game_info_links)
        game_info_refined = []

        for i in game_info:
            if bool(i) == True:
                game_info_refined.append(i)
        
        return game_info_refined

    elif source == "schedule":
        schedule_data = requests.get("https://site.api.espn.com/apis/site/v2/sports/basketball/mens-college-basketball/teams/2181/schedule")
        schedule_data = schedule_data.json()
        game_info_links = []

        for game in schedule_data["events"]:
            game_id = game["id"]
            game_info_links.append("http://sports.core.api.espn.com/v2/sports/basketball/leagues/mens-college-basketball/events/" + game_id + "?lang=en&region=us")
        
        game_info = get_game_info(game_info_links)
        return game_info

        
def get_game_info(game_info_links):
    
    all_data = []

    for i in game_info_links:
        each_game_data = {}

        broad_game_data = requests.get(i)
        broad_game_data = broad_game_data.json()
        
        game_date = broad_game_data["date"]

        current_utc_time = str(datetime.now(timezone.utc))
        current_utc_time = datetime.fromisoformat(current_utc_time)
        game_date = datetime.fromisoformat(game_date.replace("Z", "+00.00"))

        if game_date >= current_utc_time:

            game_name = broad_game_data["name"]
            away, home = game_name.split(" at ")
            away = away.strip()
            home = home.strip()

            if away == "Drake Bulldogs" or home == "Drake Bulldogs":
                home_dict = {}
                home_dict["name"] = home
                
                away_dict = {}
                away_dict["name"] = away
                
                if "winner" in broad_game_data["competitions"][0]["competitors"][0]:
                    home_dict["win"] = broad_game_data["competitions"][0]["competitors"][0]["winner"]
                    away_dict["win"] = broad_game_data["competitions"][0]["competitors"][1]["winner"]
                
                else:
                    home_dict["win"] = "False"
                    away_dict["win"] = "False"

                home_team_score = requests.get(broad_game_data["competitions"][0]["competitors"][0]["score"]["$ref"])
                home_team_score = home_team_score.json()
                home_dict["curr_score"] = home_team_score["value"]
                #also find out if game is won
                #within the home_team_score json there might be odds, it might be in the previous link also. 

                away_team_score = requests.get(broad_game_data["competitions"][0]["competitors"][1]["score"]["$ref"])
                away_team_score = away_team_score.json()
                away_dict["curr_score"] = away_team_score["value"]

                if "odds" in broad_game_data["competitions"][0]:
                    odds_data = requests.get(broad_game_data["competitions"][0]["odds"]["$ref"])
                    odds_data = odds_data.json()

                    #find this data, becuase the odds are not showing up.
                    home_dict["home_team_odds"] = odds_data["items"][0]["homeTeamOdds"]["current"]
                    away_dict["away_team_odds"] = odds_data["items"][0]["awayTeamOdds"]["current"]

                    game_bet = {}
                    game_bet["overUnder"] = odds_data["items"][0]["overUnder"]
                    game_bet["overOdds"] = odds_data["items"][0]["overOdds"]
                    #I don't Think these are correct
                    #game_bet["overPercent"] = str(round(abs(game_bet["overOdds"]) / (abs(game_bet["overOdds"]) + 100), 2))
                    game_bet["underOdds"] = odds_data["items"][0]["underOdds"]
                    #game_bet["underPercent"] = str(round(abs(game_bet["underOdds"]) / (abs(game_bet["underOdds"]) + 100),2))

                    each_game_data["date"] = game_date
                    each_game_data["home_info"] = home_dict
                    each_game_data["away_info"] = away_dict
                    each_game_data["score_betting"] = game_bet
                
                else:
                    each_game_data["score_betting"] = "unavailable"
            
            all_data.append(each_game_data)
    
    return all_data

print(get_basketbeach_game_data("schedule"))

#before game: name, home team odds, spread value and the moneyline, display value for moneyline and the spread same for away, then the over under
#do a date comparison for future games.


#use status to check if there is a winner after the game:
#http://sports.core.api.espn.com/v2/sports/basketball/leagues/mens-college-basketball/events/401721442/competitions/401721442/status?lang=en&region=us