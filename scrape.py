#from bs4 import BeautifulSoup
from urllib import urlopen
import pickle
import os
from scraping_vars import import_vars

year_used = 2015

object_dirname = 'obj'
nfl_players_path = 'nfl_players'
nfl_players_info_path = 'nfl_players_info'

url_prefix, url_postfix, url_prefix_2015, positions, player_table_class, player_row_class, \
    player_name_class, player_stats_class = import_vars()


def save_data(obj, data_path):
    """
    Utility method to save dictionary containing nfl data.
    :param obj: the dictionary to be saved
    :param data_path: the name of the file
    """
    with open('obj/' + data_path + '.pkl', 'wb+') as f:
        pickle.dump(obj, f, pickle.HIGHEST_PROTOCOL)


def load_data(data_path):
    """
    Utility method to load dictionary containing nfl data.
    :param data_path: name of pickled file
    """
    with open('obj/' + data_path + '.pkl', 'rb') as f:
        return pickle.load(f)


def get_bs_obj(position):
    if year_used == 2016:
        html = urlopen(url_prefix + str(position) + url_postfix)
    elif year_used == 2015:
        html = urlopen(url_prefix_2015 + str(position))
    else:
        html = urlopen(url_prefix_2015 + str(position))
    return BeautifulSoup(html.read(), "html.parser")


def get_player_table(bs_obj):
    return bs_obj.find('table', {'class', player_table_class})


def parse_res(bs_obj):
    players = {}
    player_list = bs_obj.findAll('tr', {'class': player_row_class})
    for player in player_list:
        player_dict = to_player_dict(player)
        players[player_dict["name"]] = player_dict
    return players


def to_player_dict(player):

    # players column
    player_name_list = player.find('td', {'class': player_name_class}).get_text().split(',')
    player_name = player_name_list[0]
    player_team, player_position = player_name_list[1].split(' ')

    print "scraping {}...".format(player_name)

    player_table_stats = player.findAll('td', {'class': player_stats_class})

    # passing column
    # completions / attempts
    passing_completions, passing_attempts = player_table_stats[0].get_text().split('/')
    # yds
    passing_yds = player_table_stats[1].get_text()
    # td
    passing_td = player_table_stats[2].get_text()
    # int
    passing_int = player_table_stats[3].get_text()

    # rushing column
    # rush
    rushing_rush = player_table_stats[4].get_text()
    # yds
    rushing_yds = player_table_stats[5].get_text()
    # td
    rushing_td = player_table_stats[6].get_text()

    # receiving column
    # rec
    receiving_rec = player_table_stats[7].get_text()
    # yds
    receiving_yds = player_table_stats[8].get_text()
    # td
    receiving_td = player_table_stats[9].get_text()
    # tar
    receiving_tar = player_table_stats[10].get_text()
    # Misc column
    # 2PC
    misc_2pc = player_table_stats[11].get_text()
    # fuml
    misc_fuml = player_table_stats[12].get_text()
    # td
    misc_td = player_table_stats[13].get_text()

    # total column
    # pts
    total_pts = player_table_stats[14].get_text()

    return {
        "name": player_name,
        "team": player_team,
        "position": player_position,
        "passing_completions": passing_completions,
        "passing_attempts": passing_attempts,
        "passing_yards": passing_yds,
        "passing_tds": passing_td,
        "passing_ints": passing_int,
        "rushing_rushes": rushing_rush,
        "rushing_yards": rushing_yds,
        "rushing_tds": rushing_td,
        "receiving_receptions": receiving_rec,
        "receiving_yards": receiving_yds,
        "receiving_tds": receiving_td,
        "receiving_targets": receiving_tar,
        "misc_two_point_conversions": misc_2pc,
        "misc_fumbles": misc_fuml,
        "misc_tds": misc_td,
        "total_points": total_pts
    }


def to_list(player_dict):
    players = []
    for key in player_dict:
        players.append(key)
    return players


def scrape_player_data():
    global year_used

    # if you want 2016 data
    # year_used = 2016

    # qb
    res_qb = get_bs_obj(positions["qb"])
    player_table_qb = get_player_table(res_qb)
    qb_dict = parse_res(player_table_qb)

    res_rb = get_bs_obj(positions["rb"])
    player_table_rb = get_player_table(res_rb)
    rb_dict = parse_res(player_table_rb)

    res_wr = get_bs_obj(positions["wr"])
    player_table_wr = get_player_table(res_wr)
    wr_dict = parse_res(player_table_wr)

    res_te = get_bs_obj(positions["te"])
    player_table_te = get_player_table(res_te)
    te_dict = parse_res(player_table_te)

    res_k = get_bs_obj(positions["k"])
    player_table_k = get_player_table(res_k)
    k_dict = parse_res(player_table_k)

    nfl_players_info = {
        "qb": qb_dict,
        "rb": rb_dict,
        "wr": wr_dict,
        "te": te_dict,
        "k": k_dict
    }

    nfl_players = {
        "qb": to_list(qb_dict),
        "rb": to_list(rb_dict),
        "wr": to_list(wr_dict),
        "te": to_list(te_dict),
        "k": to_list(k_dict)
    }

    save_data(nfl_players_info, nfl_players_info_path)
    save_data(nfl_players, nfl_players_path)


def import_data(testing):
    if testing:
        return ({
                "qb": ['Tom Brady', 'Peyton Manning'],
                "rb": ['DeMarco Murray', 'Melvin Gordon', 'David Johnson', 'LeGarrette Blount'],
                "wr": ['Julio Jones', 'Mike Evans', 'Antonio Brown', 'A.J. Green',
                       'Jordy Nelson', 'T.Y. Hilton'],
                "te": ['Rob Gronkowski', 'Jimmy Graham', 'Kyle Rudolph'],
                "k": ['Matt Bryant', 'Adam Vinatieri', 'Justin Tucker', 'Dustin Hopkins']
                }, {
                "qb": {"Tom Brady": {"team": "ne"}, "Peyton Manning": {"team": "ind"}},
                "rb": {'DeMarco Murray': {"team": "ten"}, 'Melvin Gordon': {"team": "sd"},
                    'David Johnson': {"team": "ari"}, 'LeGarrette Blount': {"team": "ne"}},
                "wr": {'Julio Jones': {"team": "atl"}, 'Mike Evans': {"team": "tb"},
                    'Antonio Brown': {"team": "pit"}, 'A.J. Green': {"team": "cin"},
                    'Jordy Nelson': {"team": "gb"}, 'T.Y. Hilton': {"team": "ind"}},
                "te": {'Rob Gronkowski': {"team": "ne"}, 'Jimmy Graham': {"team": "no"},
                    'Kyle Rudolph': {"team": "min"}},
                "k": {'Matt Bryant': {"team": "atl"}, 'Adam Vinatieri': {"team": "ind"},
                    'Justin Tucker': {"team": "bal"}, 'Dustin Hopkins': {"team": "wsh"}}
                })
    try:
        if os.path.isfile(os.path.join('.', object_dirname, nfl_players_path + '.pkl')) and \
           os.path.isfile(os.path.join('.', object_dirname, nfl_players_info_path + '.pkl')):
            return load_data(nfl_players_path), load_data(nfl_players_info_path)
        else:
            cmd = raw_input("Data files not found... scrape data(y/n)")
            if cmd.strip().lower() == 'y':
                print "Trying to import bs4..."
                from bs4 import BeautifulSoup
                scrape_player_data()
                import_data()
            else:
                return ({
                        "qb": ['Tom Brady', 'Peyton Manning'],
                        "rb": ['DeMarco Murray', 'Melvin Gordon', 'David Johnson', 'LeGarrette Blount'],
                        "wr": ['Julio Jones', 'Mike Evans', 'Antonio Brown', 'A.J. Green',
                               'Jordy Nelson', 'T.Y. Hilton'],
                        "te": ['Rob Gronkowski', 'Jimmy Graham', 'Kyle Rudolph'],
                        "k": ['Matt Bryant', 'Adam Vinatieri', 'Justin Tucker', 'Dustin Hopkins']
                        }, {
                        "qb": {"Tom Brady": {"team": "ne"}, "Peyton Manning": {"team": "ind"}},
                        "rb": {'DeMarco Murray': {"team": "ten"}, 'Melvin Gordon': {"team": "sd"},
                            'David Johnson': {"team": "ari"}, 'LeGarrette Blount': {"team": "ne"}},
                        "wr": {'Julio Jones': {"team": "atl"}, 'Mike Evans': {"team": "tb"},
                            'Antonio Brown': {"team": "pit"}, 'A.J. Green': {"team": "cin"},
                            'Jordy Nelson': {"team": "gb"}, 'T.Y. Hilton': {"team": "ind"}},
                        "te": {'Rob Gronkowski': {"team": "ne"}, 'Jimmy Graham': {"team": "no"},
                            'Kyle Rudolph': {"team": "min"}},
                        "k": {'Matt Bryant': {"team": "atl"}, 'Adam Vinatieri': {"team": "ind"},
                            'Justin Tucker': {"team": "bal"}, 'Dustin Hopkins': {"team": "wsh"}}
                        })
    except Exception as e:
        print "An error has occurred. {}".format(e.message)
        return ({
                    "qb": ['Tom Brady', 'Peyton Manning'],
                    "rb": ['DeMarco Murray', 'Melvin Gordon', 'David Johnson', 'LeGarrette Blount'],
                    "wr": ['Julio Jones', 'Mike Evans', 'Antonio Brown', 'A.J. Green', 'Jordy Nelson', 'T.Y. Hilton'],
                    "te": ['Rob Gronkowski', 'Jimmy Graham', 'Kyle Rudolph'],
                    "k": ['Matt Bryant', 'Adam Vinatieri', 'Justin Tucker', 'Dustin Hopkins']
                }, {
                    "qb": {},
                    "rb": {},
                    "wr": {},
                    "te": {},
                    "k": {}
                })


def main():
    try:
        scrape_player_data()
    except Exception as e:
        print "An error has occurred. {}".format(e.message)


if __name__ == '__main__':
    main()
