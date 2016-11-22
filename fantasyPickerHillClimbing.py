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
team_bye_weeks = {
    "gb": 4,
    "phi": 4,
    "jax": 5,
    "kc": 5,
    "no": 5,
    "sea": 5,
    "min": 6,
    "tb": 6,
    "car": 7,
    "dal": 7,
    "bal": 8,
    "stl": 8, # note st. louis became la
    "mia": 8,
    "nyg": 8,
    "pit": 8,
    "sf": 8,
    "ari": 9,
    "chi": 9,
    "cin": 9,
    "hou": 9,
    "ne": 9,
    "wsh": 9,
    "buf": 10,
    "det": 10,
    "ind": 10,
    "oak": 10,
    "atl": 11,
    "den": 11,
    "nyj": 11,
    "sd": 11,
    "cle": 13,
    "ten": 13
}
nfl_players, nfl_players_info = import_data(False)

def check_tuples(tail, head):
    for tup in head:
        if tail in tup:
            return True

def remove_tuples(tail, head, position):
    if position == 'qb' or position == "k" or position == "te":
        head = [tup for tup in head if tail in tup] + [tup for tup in head if tup[1] == tail]
    elif position == 'rb':
        head = [tup for tup in head if tail in tup] + [tup for tup in head if tup[1] == tail] +\
               [tup for tup in head if tup[2] == tail] + [tup for tup in head if tup[3] == tail]
    elif position == 'wr':
        head = [tup for tup in head if tail in tup] + [tup for tup in head if tup[1] == tail] +\
               [tup for tup in head if tup[2] == tail]

def create_position_possibilities(position):
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

class CSPGraphFantasyFootball(CSPGraph):
    def __init__(self):
        # call parent constructor
        CSPGraph.__init__(self)

    def count_position(self):
        pass

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
    def __init__(self, _ftrTail, _ftrHead):
        # call the parent constructor
        CSPConstraint.__init__(self, _ftrTail, 'in', _ftrHead)

    def satisfied(self, _tailValue, _headValue):
        """

        """
        # if the head or the tail haven't been assigned, then the constraint is satisfied
        if _headValue is None or _tailValue is None:
            return True
        # if both the head and the tail have been assigned and they have different values
        # then the constraint is satisfied

        if check_tuples(_tailValue, _headValue):
            remove_tuples(_tailValue, _headValue, self.head.name[3:])
            return True
        # otherwise, they have the same value so the constraint is not satisfied
        return False

class CSPConstraintByeWeek(CSPConstraint):
    def __init__(self, _ftrTail, _ftrHead):
        # call the parent constructor
        CSPConstraint.__init__(self, _ftrTail, 'not', _ftrHead)

    def satisfied(self, _tailValue, _headValue):
        """

        """
        # if the head or the tail haven't been assigned, then the constraint is satisfied
        if _headValue is None or _tailValue is None:
            return True
        # if both the head and the tail have been assigned and they have different values
        # then the constraint is satisfied

        if _tailValue in _headValue:
            return True
        # otherwise, they have the same value so the constraint is not satisfied
        return False

class CSPFeaturePositionPlayer(CSPFeature):
    def __init__(self, _strName, _lstDomain):
        # call parent constructor
        CSPFeature.__init__(self, _strName, _lstDomain)

class CSPFeaturePositionPossibilities(CSPFeature):
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
            cspGraph.addFeature(CSPFeaturePositionPlayer("{0},{1},{2}".format(week, position, category[position]), nfl_players[position[:2]]))



    for position in ["qb", "rb", "wr", "te", "k"]:
        cspGraph.addFeature(CSPFeaturePositionPossibilities("max{}".format(position), create_position_possibilities(position)))

    #
    # add constraints
    #

    # max players in weeks

    for position in ACTIVE_POSITIONS:
        for week in range(1, NFL_WEEKS + 1):
            feature = "{0},{1},{2}".format(week, position, category[position])
            cspGraph.addConstraint(CSPConstraintMaxPlayerNumber(cspGraph.getFeature(feature), cspGraph.getFeature("max{}".format(category[position]))))

    # call hill climbing search
    hillClimbingSearch(cspGraph)


FantasyFootball()