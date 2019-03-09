from strategy import *

def main():
    np.random.seed(100)
    
    SAVE_IMG = True

    NUM_ITER = 50
    NUM_PLAYERS = 8
    NUM_REPETITIONS = 100

    print("Testing {} iterations of 2-people IPD".format(NUM_ITER))

    # define k for strategy probabilities
    k_strategies = Strategy.generatePlayers(NUM_PLAYERS, replace=False)
                 
    for first in range(NUM_PLAYERS):
        for second in range(first, NUM_PLAYERS):
            k1 = k_strategies[first]
            k2 = k_strategies[second]

            p1 = Player(k1)
            p2 = Player(k2)
            rew1 = np.zeros_like(NUM_ITER)
            rew2 = np.zeros_like(NUM_ITER)
            print("Evaluating {} - {}...".format(p1.s, p2.s))

            # repeat the match to get some statistics (mean and std)
            cum_results = { k1:[], k2:[] }
            for _ in range(NUM_REPETITIONS):
                p1.clear_history()
                p2.clear_history()
                p1.play_iter(p2, NUM_ITER)
            
                rew1 = np.cumsum(p1.payoffHist)
                rew2 = np.cumsum(p2.payoffHist)
                cum_results[k1].append(rew1[-1])
                cum_results[k2].append(rew2[-1])
                
            # boxplots for 100 matches -> A vs B
            plt.boxplot([cum_results[k1], cum_results[k2]])
            plt.xticks([1, 2], [p1.s, p2.s])
            plt.ylabel('Reward')
            plt.title("Meand and std for {} iterations".format(NUM_REPETITIONS))
            if SAVE_IMG:
                plt.savefig('../img/ipd2p-boxplot-{}-{}.png'.format(p1.s,p2.s))
                plt.close()
            else:
                plt.show()
            
            # plot cumulative rewards
            # show only the last iteration's plot
            plt.figure(figsize=(12,5))    
            plt.plot(rew1)
            plt.plot(rew2)
            for i in range(rew1.size):
                if p1.playedHist[i] == COOPERATE:
                    plt.plot(i, rew1[i], 'bx', markersize=8)
                else:
                    plt.plot(i, rew1[i], 'rx', markersize=8)

                if p2.playedHist[i] == COOPERATE:
                    plt.plot(i, rew2[i], 'bo', markersize=5)
                else:
                    plt.plot(i, rew2[i], 'ro', markersize=5)

            plt.title("2 pl. game: {} - {}".format(p1.s,p2.s))
            plt.xlabel('Iteration')
            plt.ylabel('Cum. reward')
            # 0 = cooperate = blue
            plt.legend(handles=[
                Line2D([0], [0], color='w', marker='x', label='P.1 Defect', markeredgecolor='r'), 
                Line2D([0], [0], color='w', marker='x', label='P.1 Cooperate', markeredgecolor='b'),      
                Line2D([0], [0], color='w', marker='o', label='P.2 Defect', markerfacecolor='r'), 
                Line2D([0], [0], color='w', marker='o', label='P.2 Cooperate', markerfacecolor='b')
            ])
            if SAVE_IMG:
                plt.savefig('../img/ipd2p-rewards-{}-{}.png'.format(p1.s,p2.s))
                plt.close()
            else:
                plt.show()

if __name__ == "__main__":
    main()