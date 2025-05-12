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

#I wonder if there is a way to save it time from constantly having to crawl down certain paths

def score(broad_game_data):
            
    home_team_score = requests.get(broad_game_data["competitions"][0]["competitors"][0]["score"]["$ref"])
    home_team_score = home_team_score.json()
    home_score = home_team_score["value"]

    away_team_score = requests.get(broad_game_data["competitions"][0]["competitors"][1]["score"]["$ref"])
    away_team_score = away_team_score.json()
    away_score = away_team_score["value"]

    if "winner" in broad_game_data["competitions"][0]["competitors"][0]:
        if broad_game_data["competitions"][0]["competitors"][0]["winner"] == "True" or broad_game_data["competitions"][0]["competitors"][1]["winner"] == "True":
            game_end = True
    
        else:
            game_end = False
    else:
        game_end = False
    
    return home_score, away_score, game_end

def schedule_links():
    schedule_data = requests.get("https://site.api.espn.com/apis/site/v2/sports/baseball/college-softball/teams/698/schedule")  #2181
    #https://site.api.espn.com/apis/site/v2/sports/basketball/mens-college-basketball/teams/2181/schedule
    schedule_data = schedule_data.json()
    game_info_links = []

    for game in schedule_data["events"]:
        game_id = game["id"]
        game_info_links.append("http://sports.core.api.espn.com/v2/sports/baseball/leagues/college-softball/events/" + game_id + "?lang=en&region=us")
        #http://sports.core.api.espn.com/v2/sports/basketball/leagues/mens-college-basketball/events/" + game_id + "?lang=en&region=us
    
    return game_info_links


def get_game_info():
    
    game_info_links = schedule_links()

    all_data = []

    for i in game_info_links:
        each_game_data = {}

        broad_game_data = requests.get(i)
        broad_game_data = broad_game_data.json()
        
        game_date = broad_game_data["date"]

        current_utc_time = str(datetime.now(timezone.utc))
        current_utc_time = datetime.fromisoformat(current_utc_time)
        current_utc_time = current_utc_time.date()
        game_date = datetime.fromisoformat(game_date.replace("Z", "+00.00"))
        game_date = game_date.date()

        if game_date >= current_utc_time:
            game_date = str(game_date)

            game_name = broad_game_data["name"]
            away, home = game_name.split(" at ")
            away = away.strip()
            home = home.strip()

            if "Drake" in home or "Drake" in away:
                home_dict = {}
                home_dict["name"] = home
                
                away_dict = {}
                away_dict["name"] = away

                each_game_data["homeInfo"] = home_dict
                each_game_data["awayInfo"] = away_dict
                each_game_data["date"] = game_date
                
                """home_score, away_score, _ = score(broad_game_data)
                home_dict["curr_score"] = home_score
                away_dict["curr_score"] = away_score"""

                game_id = broad_game_data["id"]
                each_game_data["id"] = game_id

                if "odds" in broad_game_data["competitions"][0]:
                    odds_data = requests.get(broad_game_data["competitions"][0]["odds"]["$ref"])
                    odds_data = odds_data.json()

                    home_team_odds = {}
                    home_team_odds["pointSpread"] = odds_data["items"][0]["homeTeamOdds"]["current"]['pointSpread']['alternateDisplayValue']
                    home_team_odds["spread"] = odds_data["items"][0]["homeTeamOdds"]["current"]['spread']['alternateDisplayValue']

                    away_team_odds = {}
                    away_team_odds["pointSpread"] = odds_data["items"][0]["homeTeamOdds"]["current"]['pointSpread']['alternateDisplayValue']
                    away_team_odds["spread"] = odds_data["items"][0]["homeTeamOdds"]["current"]['spread']['alternateDisplayValue']

                    home_dict["odds"] = home_team_odds
                    away_dict["odds"] = away_team_odds

                    """home_dict["home_team_odds"] = odds_data["items"][0]["homeTeamOdds"]["current"]
                    away_dict["away_team_odds"] = odds_data["items"][0]["awayTeamOdds"]["current"]"""

                    game_bet = {}
                    game_bet["overUnder"] = odds_data["items"][0]["overUnder"]
                    game_bet["overOdds"] = odds_data["items"][0]["overOdds"]
                    game_bet["underOdds"] = odds_data["items"][0]["underOdds"]

                    home_dict["moneyLine"] = odds_data["items"][0]["homeTeamOdds"]["current"]['moneyLine']['alternateDisplayValue']
                    away_dict["moneyLine"] = odds_data["items"][0]["awayTeamOdds"]["current"]['moneyLine']['alternateDisplayValue']

                    
                    each_game_data["homeInfo"] = home_dict
                    each_game_data["awayInfo"] = away_dict
                    each_game_data["scoreBetting"] = game_bet
                
                else:
                    each_game_data["scoreBetting"] = "unavailable"
            
            all_data.append(each_game_data)
    
    return all_data

def daily_game_check(game_info_dataset):
    games_today = []

    if len(game_info_dataset) != 0:
        for games in game_info_dataset:
            
            broad_game_data = requests.get(games)
            broad_game_data = broad_game_data.json()

            game_time = broad_game_data["date"]
            game_time = game_time[:10]
            current_utc_time = str(datetime.now(timezone.utc))
            current_utc_time = datetime.fromisoformat(current_utc_time)
            current_utc_time = current_utc_time.date()
            current_utc_time = str(current_utc_time)

            if game_time == current_utc_time:
                games_today.append(broad_game_data)
    
    return games_today

#store games today as a variable when calling function
def live_score(games_today):
    all_games = []

    if len(games_today) != 0:
        for games in games_today:
            
            broad_game_data = requests.get("http://sports.core.api.espn.com/v2/sports/basketball/leagues/mens-college-basketball/events/" + games["id"] + "?lang=en&region=us")
            broad_game_data = broad_game_data.json()

            home_score, away_score, game_end = score(broad_game_data)            

            individual_games = [games["id"], home_score, away_score, game_end]
            all_games.append(individual_games)

    return all_games

print(get_game_info())
#print(daily_game_check(schedule_links()))
#print(live_score(daily_game_check(schedule_links())))

#before game: name, home team odds, spread value and the moneyline, display value for moneyline and the spread same for away, then the over under
#do a date comparison for future games.


#use status to check if there is a winner after the game:
#http://sports.core.api.espn.com/v2/sports/basketball/leagues/mens-college-basketball/events/401721442/competitions/401721442/status?lang=en&region=us