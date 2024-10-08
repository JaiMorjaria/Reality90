import soccerdata as sd
import pandas as pd
from classes import Player, Game, Event
import datetime

def correctNamingDiscrepancies(team_name:str) -> str:
    espn_fbref_discrepancies = {
        "Nott'ham Forest": "Nottingham Forest",
        "Brighton": "Brighton & Hove Albion",
        "Bournemouth": "AFC Bournemouth",
        "Manchester Utd": "Manchester United",
        "Newcastle Utd": "Newcastle United",
        "West Ham": "West Ham United",
        "Tottenham": "Tottenham Hotspur",
        "Wolves": "Wolverhampton Wanderers"
    }
    if team_name in espn_fbref_discrepancies:
        return espn_fbref_discrepancies[team_name]
    else:
        return team_name

espn = sd.ESPN(leagues="ENG-Premier League", seasons="23-24")
fbref = sd.FBref(leagues="ENG-Premier League", seasons="23-24")
epl_schedule = fbref.read_schedule()
schedule = espn.read_schedule()
game_ids = schedule["game_id"].tolist()
data = espn.read_lineup(game_ids).reset_index().drop('league', axis=1)

players = data["player"].unique()
games = data["game"].unique()
teams = data["team"].unique()

negative_events = [ "yellow_card", "red_card", "goal_conceded", "offsides", "fouls_committed", "sub_out", "bench_start", "shot_off_target", "own_goal"]
positive_events = ["goal", "goal_assist", "shot_on_target", "save", "start"]
non_event_columns = ['season', 'game', 'team', 'player', 'is_home', 'position', 'formation_place']

week_ctr = 1
gameweeks_data = pd.Series()
gameweeks = {}
for game in epl_schedule.iterrows():
    date = str(game[1]['date'])[0:11]
    time = str(game[1]['time'])
    home_team = correctNamingDiscrepancies(game[1]['home_team'])
    away_team = correctNamingDiscrepancies(game[1]['away_team'])
    week = game[1]['week']
    datetime_string = date + time
    game_date = datetime.datetime.strptime(datetime_string, '%Y-%m-%d %H:%M')
    gameweek = Game(game_date, home_team, away_team, week)
    game_str = date + home_team + "-" + away_team
    gameweeks[game_str] = gameweek.id

players_data = pd.Series()
players_mapping = {}
for player_name in players:
    player_info = data.loc[data['player'] == player_name, ['team', 'position']].iloc[0]
    player = Player(player_name, player_info['team'], player_info['position'])
    players_mapping[player_name] = player.id

events = []

for _, row in data.iterrows():
    for column, value in row.items():
        if column not in non_event_columns and value != 0:
            # Create an event for this stat
            event = Event(
                player_id=players_mapping[row.player],
                game_id=gameweeks[row.game],
                event_type=column,  # Use the column name as the event type (e.g., 'total_goals')
                quantity=value
            )
            events.append(event)

print(events)

