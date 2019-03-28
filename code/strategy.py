import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
#from mgen import generatePayoffMatrix

# Define global variables to have groundtruth about strategies
COOPERATE = 0
DEFECT = 1

NICE = 0
IND  = 50
BAD  = 100

TFT  = -1
TF2T = -2
GRT  = -3
PRBL = -10 # just placeholders
PRBH = -11

class Strategy:
    """Abstract Strategy class to derive other."""
    TOT_STRAT = 8

    def __str__(self):
        return "Base"

    def get(self):
        pass

    @staticmethod
    def generatePlayers(num_players, replace=False, fixed=False):
        """Generates a set of players with random strategies."""
        str_choices = [NICE, BAD, IND, TFT, TF2T, GRT, PRBL, PRBH]
        k = np.random.choice(str_choices, num_players, replace=replace)

        # substitute with useful values if needed
        maskL = k==PRBL # 1 to 49 exclude nice, indifferent
        k[maskL] = np.repeat(25, maskL.sum()) if fixed else np.random.choice(49, size=maskL.sum(), replace=replace) + 1
        maskH = k==PRBH # 51 to 99 exclude bad, indifferent
        k[maskH] = np.repeat(75, maskH.sum()) if fixed else np.random.choice(49, size=maskH.sum(), replace=replace) + 51

        return k

    def generatePlayersWithID(ID, coop, bound=-1):
        """Generates a set of players with random strategies based on current ID of a player."""
        str_choices = [TFT, TF2T, GRT]
        max_k_generated = 6

        if not coop:
            if bound == -1:
                bound = BAD
            if ID < NICE: #checks if strategy is not probabilistic
                ID = NICE-1 # since adding
            # print(ID+1, bound+1)
            return np.append(str_choices, np.random.randint(ID+1, bound+1, size=max_k_generated))
    
        if bound == -1:
            bound = NICE
        if ID < NICE: #checks if strategy is not probabilistic
            ID = BAD+1
        # print(bound, ID)
        return np.append(str_choices, np.random.randint(bound, ID, size=max_k_generated))

class Player(object):
    """Class to describe a player with strategy and history."""

    def __str__(self):
        return "Player with strategy: {}".format(self.s)

    # optional: use M = generatePayoffMatrix()
    def __init__(self, k=0, M=np.array([[3,0],[5,1]]), changing=False):
        self.M1 = M
        self.M2 = M.T
        if changing:
            self.c = (1-k/100 if k>=0 else 0.5) # probability to change strategy at the end of the round
        else:
            self.c = 0
        self.s = self.get_strategy(k)
        self.clear_history()

    def play_iter(self, opponent, num_iter):
        """Plays the game against an opponent num_iter times."""
        for _ in range(num_iter):
            self.play(opponent)

    def play(self, opponent):
        """Plays the game against an opponent."""
        action1 = self.act(opponent)
        action2 = opponent.act(self)

        self.update(action1, action2, False)
        if opponent.s != self.s:
            opponent.update(action1, action2, True)

    def act(self, opponent):
        """Gets the action based on the strategy."""
        if type(self.s) == ProbStrategy:
            return self.s.get()
        elif type(self.s) == TitForTat or type(self.s) == GrimTrigger:
            if len(opponent.playedHist) > 0: # at least 1
                return self.s.get(opponent.playedHist[-1]) # pass opponent's move
            return COOPERATE
        elif type(self.s) == TitFor2Tat:
            if len(opponent.playedHist) > 1: # at least 2
                return self.s.get([opponent.playedHist[-2],opponent.playedHist[-1]]) # pass opponent's previous two moves
            return COOPERATE

    def update(self, action1, action2, opponent):
        """Updates the state based on the actions and if is opponent."""
        if opponent:
            self.payoffHist.append(self.M2[action1,action2])
            self.playedHist.append(action2)
            #COOP = 0 DEFECT = 1
            self.bestGivenOther.append(1 if action1 else 5)
            self.bestAch.append(5 if action2 else 3)
        else:
            self.payoffHist.append(self.M1[action1,action2])
            self.playedHist.append(action1)
            self.bestGivenOther.append(1 if action2 else 5)
            self.bestAch.append(5 if action1 else 3)

    def get_strategy(self, k):
        """Gets the strategy object given the id."""
        if k >= NICE and k <= BAD:
            return ProbStrategy(k)
        elif k == TFT:
            return TitForTat()
        elif k == TF2T:
            return TitFor2Tat()
        elif k == GRT:
            return GrimTrigger()

    def clear_history(self):
        """Clears all history of the player."""
        self.payoffHist = []
        self.playedHist = []
        self.bestGivenOther = []
        self.bestAch = []
        if self.s.id == GRT: # reset GrT trigger
            self.s.triggered = False

class MultiPlayer(Player):
    """Class to describe multiple players with strategy and history."""

    def __init__(self, k, changing=False):
        Player.__init__(self, k, changing=changing)

        # save results for multiple rounds played by user
        # this way we can save all the results from the tournament
        self.prevPlayedHist = []
        self.prevOpponent = []
        self.results = []
        self.changing = changing

    @staticmethod
    def change_strategy(players, fixed, alternative):
        """Changes the players' strategy randomly."""
        count_bad = count_good = 0
        more_coop = NICE
        less_coop = BAD
    
        # TODO GrT should only go to more coop
        if alternative == 1:
            for i in range(len(players)):
                # c in [0,1] where 0 means not cooperative, 1 means coperative
                old_c = players[i].c
                new_c = np.random.uniform(0,1)
                players[i].c = new_c
                print("old c {} \t new c {}".format(old_c, new_c))

                c_diff = old_c - new_c
                THRESHOLD = 0.1
                print("ID {} abs {}".format(players[i].s.id, np.abs(c_diff)))
                if np.abs(c_diff) > THRESHOLD:
                    if new_c < 0.5:
                        # new c is lower go to a less coop
                        if players[i].s.id < less_coop:
                            print("{} \tto less coop: ".format(players[i].s), end='')
                            count_bad += 1

                            # compute bounds
                            if players[i].s.id >= 0:
                                boundL = max(50, players[i].s.id)
                            else:
                                boundL = 50
                            boundH = (1-new_c)*100

                            if boundL > boundH: # swap if needed
                                boundL, boundH = boundH, boundL
                            print("L {} H {}".format(boundL,boundH))

                            # generate some random strategies and select one
                            k_strategies = np.append([GRT,TF2T,TFT], np.random.randint(boundL, boundH+1, size=6))
                            players[i].s = players[i].random_strategy(k_strategies)
                            print("new = {}\n".format(players[i].s))
                    else:
                        # if new c is greater than the old one go to a more coop behaviour
                        if players[i].s.id != more_coop:
                            print("{} \tto more coop: ".format(players[i].s), end='')
                            count_good += 1

                            # compute bounds
                            boundL = (1-new_c)*100
                            if players[i].s.id >= 0:   
                                boundH = min(players[i].s.id, 50)
                            else:
                                boundH = 50
                            
                            if boundL > boundH: # swap if needed
                                boundL, boundH = boundH, boundL

                            # generate some random strategies and select one
                            k_strategies = np.append([GRT,TF2T,TFT], np.random.randint(boundL, boundH+1, size=6))
                            players[i].s = players[i].random_strategy(k_strategies)
                            print("new = {}\n".format(players[i].s))
                else:
                    print("Unchanged")
					
        elif alternative == 2:
            for i in range(len(players)):
                #TODO CHOOSE
                if players[i].s.id > IND: # BAD player
                    # if high in the chart go less coop (0.1+0)/2 = 0.05
                    #     low in the chart go more coop (0.1+1)/2 = 0.55
                    players[i].c = (players[i].c + (i/len(players))**2)/2
                else:
                    # if high in the chart go more coop (0.1+(1-0))/2 = 0.55
                    #     low in the chart go less coop (0.5+(1-1))/2 = 0.25
                    players[i].c = (players[i].c + (1-i/len(players))**2)/2
					
                #if i <= len(players)/2:
                #    #TODO TUNE THIS, maybe refer to the position
                #    if players[i].s.id > IND: #I am bad
                #        players[i].c = (players[i].c + players[i].c**2)/2 # goes toward 0 so more bad
                #    else:
                #        players[i].c = (players[i].c + players[i].c**0.5)/2 # goes toward 1 so more good
                #else: #opposite
                #    if players[i].s.id > IND:
                #        players[i].c = (players[i].c + players[i].c**0.5)/2
                #    else:
                #        players[i].c = (players[i].c + players[i].c**2)/2
						
                if np.random.uniform(0,1) < i/len(players):
                    # low c: more prob going to a less cooperative behaviour
                    if np.random.uniform(0,1) > players[i].c:
                        print("{} \tto less coop: ".format(players[i].s), end='')
                        if players[i].s.id < less_coop:
                            count_bad += 1

                            # get a strategy from the randomly generated ones
                            k_strategies = Strategy.generatePlayersWithID(players[i].s.id, coop=False)
                            players[i].s = players[i].random_strategy(k_strategies)

                            print("new = {}\n\n".format(players[i].s))
                    else:
                        print("{} \tto more coop: ".format(players[i].s), end='')
                        if players[i].s.id > more_coop:
                            count_good += 1

                            k_strategies = Strategy.generatePlayersWithID(players[i].s.id, coop=True)
                            players[i].s = players[i].random_strategy(k_strategies)

                            print("new = {}\n\n".format(players[i].s))
							
        return players, count_bad, count_good

    def closest_strategy(self, k_list, more_coop=False):
        """Returns the closest strategy to current one from the list; direction set by more_coop."""
        # [34, 43, 100] given s.id=40, more_coop=False returns 43, more_coop=True returns 34
        
        # TODO bugs: grt,tf2t,tft to more/less coop = nice !!!
        # two lists with [TfT tf2t mainlyG nice] / [TfT tf2t GrT mainlyBad bad] and choose from them
        # or two lists with MainlyG/nice - MainlyB/bad, random choice

        # remove current and jolly strategies
        k_list = k_list[k_list != self.s.id]
        k_list = k_list[k_list != GRT]
        k_list = k_list[k_list != TFT]
        k_list = k_list[k_list != TF2T]

        # split list using current strategy as delimiter
        maskP = k_list > self.s.id
        maskN = k_list < self.s.id
        positive_k = k_list[maskP]
        negative_k = k_list[maskN]
        
        # more bad: lowest positive
        if positive_k.size != 0 and not more_coop:
            return self.get_strategy(positive_k[positive_k.argmin()])
        # more nice: largest negative
        elif negative_k.size != 0 and more_coop and self.s.id != GRT: # only "more bad" GRT check should not be needed
            return self.get_strategy(negative_k[negative_k.argmax()])
        return self.s

    def random_strategy(self, k_list):
        """Returns a random strategy object from the list."""
        return self.get_strategy(np.random.choice(k_list))

    def play_iter(self, opponent, num_iter):
        """Plays the game against an opponent num_iter times."""
        Player.play_iter(self, opponent, num_iter)

        # save history for both players
        self.prevPlayedHist.append(self.playedHist)
        if self.s != opponent.s:
            opponent.prevPlayedHist.append(opponent.playedHist)

        self.prevOpponent.append(opponent)
        if self.s != opponent.s:
            opponent.prevOpponent.append(self)

        # check the sum of rewards to detect the winner
        self.winner(opponent)

    def winner(self, opponent):
        """Saves the total payoff of the player."""
        self.results.append(np.sum(self.payoffHist))
        if opponent.s != self.s:
            opponent.results.append(np.sum(opponent.payoffHist))

    def get_points(self):
        """Current gained points."""
        return np.cumsum(self.results)

    def get_coop_def_count(self):
        """Number of times the user cooperated and defected."""
        cooperate_count = defect_count = 0
        for hist in self.prevPlayedHist:
            cooperate_count += hist.count(COOPERATE)
            defect_count += hist.count(DEFECT)
        return cooperate_count, defect_count

class ProbStrategy(Strategy):
    """Strategy class when probability is used.
    Spans from always nice to always bad players"""

    def __init__(self, k):
        # default value is to cooperate in case of wrong k
        self.k = k if k>=NICE and k<=BAD else NICE
        self.id = k

    def get(self):
        num = np.random.randint(0,100)
        return COOPERATE if num >= self.k else DEFECT

    def __str__(self):
        if (self.k == NICE):
            return "Nice"
        elif (self.k == BAD):
            return "Bad"
        elif (self.k > IND):
            return "MainlyBad (k={})".format(self.k)
        elif (self.k < IND):
            return "MainlyNice (k={})".format(self.k)
        else:
            return "Indifferent"

class TitForTat(Strategy):
    """Plays opponent's last move."""

    def __init__(self):
        self.id = TFT

    def __str__(self):
        return "TitForTat"

    def get(self, last_move=None):
        if last_move == None:
            return COOPERATE # first time
        return last_move # repeat past opponent move

class TitFor2Tat(TitForTat):
    """Defects only if the opponent has defected last two times."""

    def __init__(self):
        self.id = TF2T

    def __str__(self):
        return "TitFor2Tat"

    def get(self, last_moves=None):
        if last_moves == None:
            return COOPERATE
        return (last_moves[0] and last_moves[1])
        # COOPERATE = 0, DEFECT = 1. If both 1 only case to have DEFECT as output

class GrimTrigger(Strategy):
    """Cooperate at first, if opponent defects once then always defect."""

    def __init__(self):
        self.id = GRT
        self.triggered = False

    def __str__(self):
        return "GrimTrigger"

    def get(self, last_move=None):
        if not self.triggered and last_move == DEFECT:
            self.triggered = True

        if self.triggered:
            return DEFECT
        return COOPERATE
