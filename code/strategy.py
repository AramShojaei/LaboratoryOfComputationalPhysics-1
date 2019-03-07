import numpy as np

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

class Player(object):
    """Class to describe a player with strategy and history."""
    
    def __str__(self):
        return "Player with strategy: {}".format(self.s)
    
    # optional: use M = generatePayoffMatrix()
    def __init__(self, k=0, M=np.array([[3,0],[5,1]])):
        self.M1 = M
        self.M2 = M.T

        if k >= 0:
            self.s = ProbStrategy(k)
        elif k == TFT:
            self.s = TitForTat()
        elif k == TF2T:
            self.s = TitFor2Tat()
        elif k == GRT:
            self.s = GrimTrigger()
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
            if len(opponent.playedHist) > 0:
                return self.s.get(opponent.playedHist[-1]) # pass opponent's move
            return COOPERATE
        elif type(self.s) == TitFor2Tat:
            if len(opponent.playedHist) > 1:
                return self.s.get(opponent.playedHist[-2]) # pass opponent's second to lastmove
            return COOPERATE
        
    def update(self, action1, action2, opponent):
        """Updates the state based on the actions."""
        self.stratHist.append(str(self.s)) #todo check if better this or k
        if opponent:
            self.payoffHist.append(self.M2[action1,action2])
            self.playedHist.append(action2)
            self.bestPossibleHist.append(max(self.M2[:,action2]))
        else:
            self.payoffHist.append(self.M1[action1,action2])
            self.playedHist.append(action1)
            self.bestPossibleHist.append(max(self.M1[action1,:]))

    def change_strategy(self):
        """Change the strategy randomly."""
        # watch out: each player has a different kH, kL
        kH = np.random.randint(51,100)
        kL = np.random.randint(0,50)
        k_strategies = np.array([NICE, BAD, IND, TFT, TF2T, GRT, kL, kH])
        
        s_next = self.random_str(k_strategies)
        while s_next == self.s:
            s_next = self.random_str(k_strategies)

        self.s = s_next

    def random_str(self, k_list):
        k =  np.random.choice(k_list) # gene
        if k >= 0:
            return ProbStrategy(k)
        elif k == TFT:
            return TitForTat()
        elif k == TF2T:
            return TitFor2Tat()
        elif k == GRT:
            return GrimTrigger()
        
    def clear_history(self):
        """Clears all history of the player."""
        self.stratHist = []
        self.payoffHist = []
        self.playedHist = []
        self.bestPossibleHist = []

class MultiPlayer(Player):
    """Class to describe multiple players with strategy and history."""

    def __init__(self, k, changing=False):
        Player.__init__(self, k)
        
        # save results for multiple rounds played by user
        # this way we can save all the results from the tournament
        self.prevStratHist = []
        self.prevPayoffHist = []
        self.prevPlayedHist = []
        self.prevBestPossibleHist = []
        self.prevOpponent = []
        self.results = [] # 'w' = win, 'l' = loss, d' = draw
        self.changing = changing
        
    # def winner(self,opponent):
    #     if np.sum(self.payoffHist) == np.sum(opponent.payoffHist):
    #         self.results.append('d')
    #         opponent.results.append('d')
    #         if self.changing:
    #             self.change_strategy()
    #         if opponent.changing:
    #             opponent.change_strategy()
    #     elif np.sum(self.payoffHist) > np.sum(opponent.payoffHist):
    #         self.results.append('w')
    #         opponent.results.append('l')
    #         if opponent.changing:
    #             opponent.change_strategy()
    #     else:
    #         self.results.append('l')
    #         opponent.results.append('w')
    #         if self.changing:
    #             self.change_strategy()
    
    def winner_alt(self,opponent):
        self.results.append(np.sum(self.payoffHist))
        if opponent.s != self.s:
            opponent.results.append(np.sum(opponent.payoffHist))
        
    def play_iter(self, opponent, num_iter):
        Player.play_iter(self, opponent, num_iter)

        self.prevStratHist.append(self.stratHist)
        self.prevPayoffHist.append(self.payoffHist)
        self.prevPlayedHist.append(self.playedHist)
        self.prevBestPossibleHist.append(self.bestPossibleHist)
        
        if self.s != opponent.s:
            opponent.prevStratHist.append(opponent.stratHist)
            opponent.prevPayoffHist.append(opponent.payoffHist)
            opponent.prevPlayedHist.append(opponent.playedHist)
            opponent.prevBestPossibleHist.append(opponent.bestPossibleHist)
        
        self.prevOpponent.append(opponent)
        if self.s != opponent.s:
            opponent.prevOpponent.append(self)

        # who won? check the sum of rewards
        self.winner_alt(opponent)
                
        # set actual history to zero
        self.clear_history()
        opponent.clear_history()
    
    def rounds_played(self):
        """Number of rounds each user played."""
        return len(self.prevStratHist)

    # def count_wins(self):
    #     """Counts the number of rounds won by player."""
    #     return self.results.count('w')

    # def count_losses(self):
    #     """Counts the number of rounds loss by player."""
    #     return self.results.count('l')

    # def count_draws(self):
    #     """Counts the number of rounds drawn by player."""
    #     return self.results.count('d')

    # def get_points(self):
    #     """Counts the points at each match of the player w=3, d=1, l=0."""
    #     points = np.zeros(len(self.results))
    #     points[np.array(self.results) == 'd'] = 1
    #     points[np.array(self.results) == 'w'] = 3
    #     points[np.array(self.results) == 'l'] = 0
    #     return np.cumsum(points)

    def get_points_alt(self):
        # points = np.zeros(len(self.results)) #todo check if useless
        points = self.results
        return np.cumsum(points)

class Strategy:
    """Abstract Strategy class to derive other."""

    def __str__(self):
        return "Base"

    def get(self):
        pass

    @staticmethod
    def generatePlayers(num_players, allow_repetitions=False):
        str_choices = [NICE, BAD, IND, TFT, TF2T, GRT, PRBL, PRBH]
        ll = 0 if allow_repetitions else 1
        lh = 51 if allow_repetitions else 50
        hl = 50 if allow_repetitions else 51
        hh = 101 if allow_repetitions else 100
        
        k = [] # strategies for players
        while len(k) < num_players:
            val = np.random.choice(str_choices)

            # substitute with useful values if needed
            if val == PRBL:
                val = np.random.randint(ll, lh)
                if (val != IND and val not in k) or allow_repetitions:
                    k.append(val)
            elif val == PRBH:
                val = np.random.randint(hl, hh)
                if (val != IND and val not in k) or allow_repetitions:
                    k.append(val)
            else:
                k.append(val)
        return np.array(k)
    
class ProbStrategy(Strategy):
    """Strategy class when probability is used."""

    def __init__(self, k):
        # default value is to cooperate in case of wrong k
        # todo: check if throwing exception is better
        self.k = k if k>=NICE and k<=BAD else NICE

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

    def __str__(self):
        return "TitForTat"

    def get(self, last_move=None):
        if last_move == None:
            return COOPERATE # first time
        return last_move # repeat past opponent move

class TitFor2Tat(TitForTat):
    """Plays opponent's second to last move."""

    def __str__(self):
        return "TitFor2Tat"
    
    # get method remains the same, just change indexes
    # todo but in the paper it is noted to act using both last and 2-to-last actions

class GrimTrigger(Strategy):
    """Cooperate at first, if opponent defects once then always defect."""

    def __init__(self):
        self.triggered = False

    def __str__(self):
        return "GrimTrigger"

    def get(self, last_move=None):
        if last_move == DEFECT:
            self.triggered = True

        if self.triggered:
            return DEFECT
        return COOPERATE
