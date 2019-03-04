import pandas as pd
import matplotlib.pyplot as plt

from mgen import generatePayoffMatrix
from strategy import *

def IPDRoundRobin(k_strategies, num_iter, itself = True):
    n = num_strat = k_strategies.size
    num_rounds = int( ((n-1)/2) * n)

    # initialize players with given strategies
    round_robin_p = np.array([])
    for k in k_strategies:
        p = MultiPlayer(k)
        round_robin_p = np.append(round_robin_p, p)

    # each player plays against another in a round robin scheme
    for (i, p1) in zip(np.arange(n), round_robin_p):
        #todo reason if A vs A makes sense
        for (j, p2) in zip(np.arange(i if itself else i+1 ,n), round_robin_p[i if itself else i+1:]):
            # todo: for _ in range(NUM_REPETITIONS): -> CLEVER but get_points needs change
            p1.play_iter(p2, num_iter)

    # calculate ranking and matches dataframes
    # has to be done after the tournament

    ranking_df = pd.DataFrame()
    # all matches played sorted by time
    matches_df = pd.DataFrame()

    # calculate points sum
    sum_points = 0
    for p in round_robin_p:
        points = p.get_points_alt()
        sum_points += int(points[-1])

    for (i, p) in zip(np.arange(n), round_robin_p):
        points = p.get_points_alt()
        df = pd.DataFrame(
            [[p.s, int(points[-1]), int(points[-1])/sum_points, p]],
            columns=['Player','points','percentage','rrp']
        )
        ranking_df = ranking_df.append(df)
        ranking_df = ranking_df.sort_values(['points'], ascending=[False])
        for j in range(i, len(p.results)):
            # can now access any property from p1 or p2 for plots
            # each match can be explored

            df = pd.DataFrame(
                    [[p.s, p.prevOpponent[j].s, p.results[j], p.prevOpponent[j].results[i]]],
                    columns=['p1','p2','p1-score','p2-score']
            )
            matches_df = matches_df.append(df)
    
    round_robin_p = np.array(ranking_df['rrp'])
    ranking_df = ranking_df[['Player','points','percentage']]    
    return round_robin_p, ranking_df, matches_df
    
def main():
    np.random.seed(1234)
    pd.set_option('display.max_columns', None)

    # number of iterations
    NUM_ITER = 100
    # number of players
    NUM_PLAYERS = 6
    NUM_REPETITIONS = 20
    PERCENTAGE = 0.3
    print("Testing repeated {}-times round-robin tournament with {}-people".format(NUM_REPETITIONS, NUM_PLAYERS))

    repeated_round_robin_p = []
    prev_winning_k = None

    
    #random initialization 
    # k_strategies = Strategy.generatePlayer(NUM_PLAYERS=NUM_PLAYERS, allowRep=True)
    
    #equal split initialization
    #kH = np.random.randint(51,100)
    #kL = np.random.randint(0,50)
    #k_strategies = [0, 100, kL, kH, 50, -1]
    #for i in range(NUM_PLAYERS//6-1):
    #    k_strategies.extend(k_strategies)
    #if(NUM_PLAYERS%6 != 0):
    #    k_strategies.extend(k_strategies[:(NUM_PLAYERS)%6])
    #k_strategies = np.array(k_strategies)

    # fixed initialization
    k_strategies = np.array([0, 100, 50, -1, 25, 75])
    
    for r in range(NUM_REPETITIONS):
        round_robin_p, ranking_df, matches_df = IPDRoundRobin(k_strategies, NUM_ITER)
        repeated_round_robin_p.append(round_robin_p)
        # easy fix (depending on task)
        # add one winner strategy or multiple previous winners?
        # for i in range(0,int(NUM_PLAYERS * PERCENTAGE)):
            # k_strategies = np.append(k_strategies,round_robin_p[i].s.k)
            # k_strategies = np.delete(k_strategies,np.argmax(round_robin_p[NUM_PLAYERS-i-1].s.k if str(round_robin_p[NUM_PLAYERS-i-1].s) != 'TitForTat' else -1))
            # k_strategies = np.append(k_strategies, )
        for i in range(0,6):
            # add as many as told by percentage
                k_strategies = np.append(k_strategies, k_strategies[i])
        NUM_PLAYERS = k_strategies.size

        # print(matches_df)
        # ranking_df = pd.DataFrame(ranking_df)
        # matches_df = pd.DataFrame(matches_df)
        # display(ranking_df)
        # display(matches_df)

    # save plots
    for (r, round_robin_p) in zip(np.arange(NUM_REPETITIONS), repeated_round_robin_p):
        for p in round_robin_p:
            points = p.get_points_alt()
            plt.plot(points, label=p.s)
            plt.title("Multi pl. game: {}".format(NUM_PLAYERS))
            plt.xlabel('Match number')
            plt.ylabel('Points')

        plt.legend()
        plt.show()
        #plt.savefig('../img_v1/ridpmp-scores-{}-r{}.png'.format(NUM_PLAYERS, r))
        #plt.close()

if __name__ == "__main__":
    main()
