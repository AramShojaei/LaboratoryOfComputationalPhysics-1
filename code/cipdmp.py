from strategy import *
from base_options import *
from ipdmp import IPDRoundRobin

def main():
    np.random.seed(100)
    pd.set_option('display.max_columns', None)

    opt = BaseOptions().parse(BaseOptions.CIPDMP)
    SAVE_IMG = opt.saveimg
    NUM_ITER = opt.niter
    NUM_PLAYERS = opt.nplay
    NUM_REPETITIONS = 0 # arg override
    MAX_ALLOWED = opt.maxrep
    FIXED = opt.fixed
    LATEX = opt.latex
	
    ALTERNATIVE = opt.altern
    # PERCENTAGE = opt.percent

    print("Testing changing round-robin tournament with {}-people".format(NUM_PLAYERS))

    repeated_players = []
    strategies_df = pd.DataFrame() # strategies evolution

    # define k for strategy probabilities
    k_strategies = Strategy.generatePlayers(NUM_PLAYERS,replace=(NUM_PLAYERS > Strategy.TOT_STRAT), fixed=FIXED)

    # initialize players with given strategies
    players = np.array([MultiPlayer(k, changing=True) for k in k_strategies])
    while np.unique(k_strategies, return_counts=True)[1].max() < k_strategies.size*3/4 and NUM_REPETITIONS < MAX_ALLOWED:
        NUM_REPETITIONS += 1
        
        #plot population per strategy
        #total payoff evolution
        players, ranking_df, matches_df = IPDRoundRobin(players, NUM_ITER) 
        repeated_players.append(players)

        # create strategies history
        unique, counts = np.unique(k_strategies, return_counts=True)
        df = pd.DataFrame([counts],columns=unique)
        strategies_df = strategies_df.append(df)
    
        k_strategies = []
        for i in range(0,len(players)):
            draw = np.random.uniform(0,1)
            if(draw > i/len(players)):
                k_strategies.append(players[i].s.id)
        k_strategies = np.array(k_strategies)
        playersToAdd = np.array([MultiPlayer(k, changing=True) for k in k_strategies])
        
        players, c_b, c_g = MultiPlayer.change_strategy(players, FIXED, ALTERNATIVE)
        print("Changed {} players to a more cooperative behaviour.".format(c_g))
        print("Changed {} players to a less cooperative behaviour.".format(c_b))
        players = np.append(players, playersToAdd)
        
    if(np.unique(k_strategies, return_counts=True)[1].max() > k_strategies.size*3/4 ):
        print("Convergence speed of round-robin tournament is {} with {}-people".format(NUM_REPETITIONS, NUM_PLAYERS))
    else:
        print("Convergence not reached")
        
    # save plots
    strategies_df = strategies_df.rename(index=str,
        columns={-3: "GrimTrigger", -2: "TitForTwoTat", -1: "TitForTat", 0: "Nice", 100: "Bad", 50: "Indifferent"})
    for c in strategies_df.columns:
        if str.isdigit(str(c)):
            if c > 50:
                strategies_df = strategies_df.rename(index=str, columns={c: "MainlyBad (k={})".format(c)})
            else:
                strategies_df = strategies_df.rename(index=str, columns={c: "MainlyNice (k={})".format(c)})

    strategies_df.index = np.arange(strategies_df.index.size)
    strategies_df = strategies_df.fillna(0)
    if LATEX:
        if NUM_PLAYERS > 8:
            print(strategies_df.T.to_latex()) # too large, transpose
        else:
            print(strategies_df.to_latex(index=False))
    else:
        print(strategies_df)

    strategies_df.plot(figsize=(12,5))    
    plt.legend(ncol=int(len(strategies_df.columns)/10), bbox_to_anchor=(1, 1))
    plt.title('Strategies evolution')
    plt.ylabel('Number of strategies')
    plt.xlabel('Time')
    if SAVE_IMG:
        plt.savefig('../img/cipdmp-incr/cipdmp-evolution-increasing-pop-{}.eps'.format(NUM_PLAYERS),format='eps')
        plt.close()
    else:
        plt.show()

    for (r, players) in zip(np.arange(NUM_REPETITIONS), repeated_players):
        plt.figure(figsize=(12,5))
        for p in players:
            points = p.get_points()
            plt.plot(points, label=p.s)
            plt.title("Multi pl. game: {}".format(NUM_PLAYERS))
            plt.xlabel('Match number')
            plt.ylabel('Points')
        plt.legend(ncol=int(NUM_PLAYERS/10), bbox_to_anchor=(1, 1)) # TODO maybe use col=5 loc=2 even here

        if SAVE_IMG:
            plt.savefig('../img/cipdmp-incr/cipdmp-scores-increasing-pop-{}-r{}.eps'.format(NUM_PLAYERS, r),format='eps')
            plt.close()
        else:
            plt.show()
        
if __name__ == "__main__":
    main()
