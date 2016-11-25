__author__ = 'rsimpson'
# submission Richard Sharrott

from constraintSatisfaction import *
from scrape import import_data
from itertools import combinations

NFL_WEEKS = 13
ACTIVE_POSITIONS = ["qb", "rb1", "rb2", "wr1", "wr2", "wr3", "te", "k"]
category = {
    "qb": "qb",
    "rb1": "rb",
    "rb2": "rb",
    "wr1": "wr",
    "wr2": "wr",
    "wr3": "wr",
    "te": "te",
    "k": "k"
}
team_bye_weeks = [ [], [], [], [],
    ["gb", "phi"],
    ["jax", "kc", "no", "sea"],
    ["min", "tb"],
    ["car", "dal"],
    ["bal", "stl", "mia", "nyg", "pit", "sf"], # note st. louis became la
    ["ari", "chi", "cin", "hou", "ne", "wsh"],
    ["buf", "det", "ind", "oak"],
    ["atl", "den", "nyj", "sd"],
    [],
    ["cle", "ten"]
]
nfl_players, nfl_players_info = import_data(False) # true from smaller data set

def check_tuples(tail, head):
    """ Checks if tail (player name) exists anywhere in head (list of tuples).

    :param tail: player name string
    :param head: list of tuples of player combinations
    :return: Boolean
    """
    for tup in head:
        if tail in tup:
            return True

def remove_tuples(tail, head, position):
    """Removes tuples that do not contain the tail value (player name) in the head (list of tuples).

    :param tail: player name string
    :param head: list of tuples of player combinations
    :param position: player category
    """
    if position == 'qb' or position == "k" or position == "te":
        head = [tup for tup in head if tail in tup] + [tup for tup in head if tup[1] == tail]
    elif position == 'rb':
        head = [tup for tup in head if tail in tup] + [tup for tup in head if tup[1] == tail] +\
               [tup for tup in head if tup[2] == tail] + [tup for tup in head if tup[3] == tail]
    elif position == 'wr':
        head = [tup for tup in head if tail in tup] + [tup for tup in head if tup[1] == tail] +\
               [tup for tup in head if tup[2] == tail]

def create_position_possibilities(position):
    """Creates the combination of players for a given position.
    Not sure if the function works at large values of combinations. (nCr)

    :param position: position category
    :return: list of string tuples from length 1 to 5.
    """
    valid_possibilities = []
    if position == "qb" or position == "k" or position == "te":
        valid_possibilities = list(combinations(nfl_players[position],1))
        valid_possibilities = valid_possibilities + list(combinations(nfl_players[position],2))
    elif position == "rb":
        valid_possibilities = list(combinations(nfl_players[position],2))
        valid_possibilities = valid_possibilities + list(combinations(nfl_players[position],3))
        valid_possibilities = valid_possibilities + list(combinations(nfl_players[position],4))
        valid_possibilities = valid_possibilities + list(combinations(nfl_players[position],5))
    elif position == "wr":
        valid_possibilities = list(combinations(nfl_players[position],3))
        valid_possibilities = valid_possibilities + list(combinations(nfl_players[position],4))
        valid_possibilities = valid_possibilities + list(combinations(nfl_players[position],5))
    return valid_possibilities

def filter_bye_weeks(nfl_players, week, position):
    return filter(lambda x: nfl_players_info[position][x]["team"].lower() not in team_bye_weeks[week], nfl_players)

class CSPGraphFantasyFootball(CSPGraph):
    def __init__(self):
        # call parent constructor
        CSPGraph.__init__(self)

    def objectiveFunction(self):
        """
        Returns a measure of how 'good' the current solution is - the function below returns a count
        of satisfied constraints. It is possible (recommended) to implement a more problem-
        specific objective function in your CSPGraph subclass.
        """
        # start at zero
        ofValue = 0
        # loop through all of the constraints
        for constraint in self.constraints:
            # if the constraint is satisfied, then increase the count
            if (not constraint.satisfied(constraint.tail.value, constraint.head.value)):
                ofValue += 1
        # return the count of satisfied constraints
        return ofValue

class CSPConstraintMaxPlayerNumber(CSPConstraint):
    """ Checks if the possible combination of players can exist and removes players combinations from
            the domain if not.
    """
    def __init__(self, _ftrTail, _ftrHead):
        # call the parent constructor
        CSPConstraint.__init__(self, _ftrTail, 'in', _ftrHead)

    def satisfied(self, _tailValue, _headValue):
        """ Checks if the possible combination of players can exist and removes players combinations from
            the domain if not.
            :param _tailValue: the player name
            :param _headValue: a list of tuples that contain possible player combinations for a position
            Note self.head.name[3:] grabs the position category.
        """
        # if the head or the tail haven't been assigned, then the constraint is satisfied
        if _headValue is None or _tailValue is None:
            return True

        # if both the head and the tail have been assigned
        # check if the player name is in the possible tuple combinations
        # if it is remove all tuples not containing that player name
        # if not the constraint is violated return false
        if check_tuples(_tailValue, _headValue):
            remove_tuples(_tailValue, _headValue, self.head.name[3:])
            return True
        return False

class CSPConstraintOnePlayerPerPosition(CSPConstraint):
    def __init__(self, _ftrTail, _ftrHead):
        # call the parent constructor
        CSPConstraint.__init__(self, _ftrTail, '!=', _ftrHead)

    def satisfied(self, _tailValue, _headValue):
        """A player cannot play multiple active positions a week.

        :param _tailValue: the player name for one position in one week (e.g. Week 1 RB1)
        :param _headValue: another player name for one position in the same week (e.g. Week 1 RB2)
        """
        # if the head or the tail haven't been assigned, then the constraint is satisfied
        if _headValue is None or _tailValue is None:
            return True
        # if both the head and the tail have been assigned and they have different values
        # then the constraint is satisfied

        if _tailValue != _headValue:
            return True
        # otherwise, they have the same value so the constraint is not satisfied
        return False

class CSPFeaturePositionPlayer(CSPFeature):
    """
    A nfl player for a given position at a given week in the fantasy season.
    Takes the string form of "week number, active position, position category".
    Domain is a list of possible nfl players for a given position.
    """

    def __init__(self, _strName, _lstDomain):
        # call parent constructor
        CSPFeature.__init__(self, _strName, _lstDomain)

class CSPFeaturePositionPossibilities(CSPFeature):
    """
    Feature that hold the string for which position this feature corresponds to and
    a list of possible tuple values of players for a given position.
    Takes the string form of "max{position category}".
    """

    def __init__(self, _strName, _lstDomain):
        # call parent constructor
        CSPFeature.__init__(self, _strName, _lstDomain)

def FantasyFootball():
    # create a csp graph
    cspGraph = CSPGraphFantasyFootball()

    #
    # add features
    #

    """Sets domain for each weeks' position.
    [
        week1qb, week1rb1, week1rb2, week1wr1, week1wr2,
        week1wr3, week1te, week1k, week2qb, week2rb1, week2rb2,
        week2wr1, week2wr2, week2wr3, week2te, week2k,...
    ]
    """
    for week in range(1, NFL_WEEKS + 1):
        for position in ACTIVE_POSITIONS:
            cspGraph.addFeature(CSPFeaturePositionPlayer("{0},{1},{2}".format(week, position,
                                                                              category[position]),
                                                                              filter_bye_weeks(nfl_players[position[:2]],
                                                                                               week,
                                                                                               position[:2])))

    # max position features
    for position in ["qb", "rb", "wr", "te", "k"]:
        cspGraph.addFeature(CSPFeaturePositionPossibilities("max{}".format(position),
                                                            create_position_possibilities(position)))

    #
    # add constraints
    #

    # max players in weeks

    """
    REDO FOR TAIL VALUES TO BE REMOVED!
    """

    for position in ACTIVE_POSITIONS:
        for week in range(1, NFL_WEEKS + 1):
            feature = "{0},{1},{2}".format(week, position, category[position])
            cspGraph.addConstraint(CSPConstraintMaxPlayerNumber(cspGraph.getFeature(feature),
                                                                cspGraph.getFeature("max{}".format(category[position]))))
    #
    # Players cannot player multiple acitve positions
    #

    for week in range(1, NFL_WEEKS + 1):
        featureRB1 = "{0},{1},{2}".format(week, "rb1", "rb")
        featureRB2 = "{0},{1},{2}".format(week, "rb2", "rb")
        featureWR1 = "{0},{1},{2}".format(week, "wr1", "wr")
        featureWR2 = "{0},{1},{2}".format(week, "wr2", "wr")
        featureWR3 = "{0},{1},{2}".format(week, "wr3", "wr")
        cspGraph.addConstraint(CSPConstraintOnePlayerPerPosition(
                cspGraph.getFeature(featureRB1),
                cspGraph.getFeature(featureRB2))) # rb1 != rb2
        cspGraph.addConstraint(CSPConstraintOnePlayerPerPosition(
                cspGraph.getFeature(featureRB2),
                cspGraph.getFeature(featureRB1))) # rb2 != rb1
        cspGraph.addConstraint(CSPConstraintOnePlayerPerPosition(
                cspGraph.getFeature(featureWR1),
                cspGraph.getFeature(featureWR2))) # wr1 != wr2
        cspGraph.addConstraint(CSPConstraintOnePlayerPerPosition(
                cspGraph.getFeature(featureWR2),
                cspGraph.getFeature(featureWR1))) # wr2 != wr1
        cspGraph.addConstraint(CSPConstraintOnePlayerPerPosition(
                cspGraph.getFeature(featureWR1),
                cspGraph.getFeature(featureWR3))) # wr1 != wr3
        cspGraph.addConstraint(CSPConstraintOnePlayerPerPosition(
                cspGraph.getFeature(featureWR3),
                cspGraph.getFeature(featureWR1))) # wr3 != wr1
        cspGraph.addConstraint(CSPConstraintOnePlayerPerPosition(
                cspGraph.getFeature(featureWR2),
                cspGraph.getFeature(featureWR3))) # wr2 != wr3
        cspGraph.addConstraint(CSPConstraintOnePlayerPerPosition(
                cspGraph.getFeature(featureWR3),
                cspGraph.getFeature(featureWR2))) # wr3 != wr2

    # call hill climbing search
    hillClimbingSearch(cspGraph)


FantasyFootball()
