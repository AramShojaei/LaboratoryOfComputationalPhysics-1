import pandas as pd
import matplotlib.pyplot as plt

from ipdmp import IPDRoundRobin
from mgen import generatePayoffMatrix
from strategy import *

def IPDRR2(k_strategies, num_iter):
    """REMOVE. Use generalized original in ipdmp instead."""
    n = num_strat = k_strategies.size
    num_rounds = int( ((n-1)/2) * n)

    # initialize players with given strategies
    round_robin_p = np.array([])
    for k in k_strategies:
        p = MultiPlayer(k=k, changing=True)
        round_robin_p = np.append(round_robin_p, p)

    # each player plays against another in a round robin scheme
    for (i, p1) in zip(np.arange(n), round_robin_p):
        for (j, p2) in zip(np.arange(i+1,n), round_robin_p[i+1:]):
            # print(i, j)
            p1.play_iter(p2, num_iter)

    return round_robin_p
    
def main():
    np.random.seed(100)
    pd.set_option('display.max_columns', None)

    SAVE_IMG = False

    NUM_ITER = 50
    NUM_PLAYERS = 10
    print("Testing changing round-robin tournament with {}-people".format(NUM_PLAYERS))

    # define k for strategy probabilities
    # append NUM_PLAYERS-6 strategies with k between 1 and 99 included
    k_strategies = Strategy.generatePlayers(NUM_PLAYERS)
    
    # todo: when using changing strategies, no points and ranking are computed (done in main)
    players = IPDRoundRobin(k_strategies, NUM_ITER, changing_str=True)

    # serie A table
    # todo: store final rewards sum as well as opponent rewards sum
    # (Goal Fatti, Goal Subiti)
    ranking_df = pd.DataFrame()
    # all matches played sorted by time
    matches_df = pd.DataFrame()

    for (i, p) in zip(np.arange(NUM_PLAYERS), players):
        points = p.get_points()
        plt.plot(points, label='P. {}'.format(i))
        plt.title("Multi pl. game: {}".format(NUM_PLAYERS))
        plt.xlabel('Match number')
        plt.ylabel('Points')

        df = pd.DataFrame(
            [[i, p.count_wins(), p.count_draws(), p.count_losses(), int(points[-1])]],
            columns=['Player','W','D','L','points']
        )
        ranking_df = ranking_df.append(df)

       #for j in range(i+1, len(p.results)):
       #    # can now access any property from p1 or p2 for plots
       #    # each match can be explored
       #    # print(i, j)
       #    df = pd.DataFrame(
       #            [[p.s, p.prevOpponent[j].s, p.results[j], p.prevOpponent[j].results[i], np.sum(p.prevPayoffHist[j]), np.sum(p.prevOpponent[j].prevPayoffHist[i])]],
       #            columns=['p1','p2','p1-result', 'p2-result','p1-score','p2-score']
       #    )
       #    matches_df = matches_df.append(df)

    plt.legend()
    if SAVE_IMG:
        plt.savefig('../img/cipdmp-scores-{}.png'.format(NUM_PLAYERS))
        plt.close()
    else:
        plt.show()

    ranking_df = ranking_df.sort_values(['W', 'D', 'L'], ascending=[False, False, True])
    print(ranking_df.to_latex())
    print(matches_df.to_latex())

if __name__ == "__main__":
    main()
