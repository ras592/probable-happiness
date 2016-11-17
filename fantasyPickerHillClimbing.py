__author__ = 'rsimpson'
# Submission Richard Sharrott

from constraintSatisfaction import *
from scrape import import_data

NFL_WEEKS = 13
ACTIVE_POSITIONS = ["qb", "rb1", "rb2", "wr1", "wr2", "wr3", "te", "k"]
nfl_players, nfl_players_info = import_data()

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

class CSPFeaturePositionPlayer(CSPFeature):
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
            cspGraph.addFeature(CSPFeaturePositionPlayer("week {0}\tposition {1: <3}\t".format(week, position), nfl_players[position[:2]]))




    # call hill climbing search
    hillClimbingSearch(cspGraph)


FantasyFootball()