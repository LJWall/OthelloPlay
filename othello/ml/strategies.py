import random
from othello.othello import OthelloBoardClass, GameCompleteError, InvalidMoveError, NoAvailablePlayError

# Used to provide a dictionary of strategy functions
class FunctionDict(dict):
    def register(self, name):
        def assign_func_name(func):
            self[name] = func
        return assign_func_name
strategies = FunctionDict()
            
@strategies.register('random')
def random_strategy(game):
    """Plays a move at random."""
    if game.game_complete:
        raise GameCompleteError
    play_results = game.get_plays(simple=True)
    if len(play_results):
        i = random.randint(0, len(play_results)-1)
        play = sorted(play_results.keys())[i]
        game.play_move(*play)
    else:
        raise NoAvailablePlayError

@strategies.register('best_score')    
def best_score_strategy(game):
    """Plays the move that gives the best immediate score."""
    if game.game_complete:
        raise GameCompleteError
    play_results = game.get_plays(simple=True)
    if len(play_results):
        max_flips = max([play_results[x] for x in play_results])
        plays = [key for key in play_results if play_results[key]==max_flips]
        i = random.randint(0, len(plays)-1)
        game.play_move(*plays[i])
    else:
        raise NoAvailablePlayError

if __name__ == '__main__':
    print(strategies)