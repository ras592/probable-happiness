from scrape import import_data

nfl_players, nfl_players_info = import_data()

for player in nfl_players:
    for individual_player in nfl_players[player]:
        print individual_player

print "players info"

for player in nfl_players_info:
    for individual_player in nfl_players_info[player]:
        print nfl_players_info[player][individual_player]