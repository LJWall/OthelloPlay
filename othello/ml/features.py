
# Used to provide a dictionary of feature functions
class __FunctionDict(dict):
    def register(self, name):
        def assign_func_name(func):
            self[name] = func
        return assign_func_name
features = __FunctionDict()

@features.register('norm_X_score')
def norm_X_score(game):
    """Black's score, normalised """
    return game.score()['X']/(game.size * game.size)

@features.register('game_progress')
def norm_O_score(game):
    """How far throught the game, normalised """
    return len(game)/(game.size * game.size)


def get_game_features(game, req_features):
    """Return request list of game features """
    ret_val = list()
    for f in req_features:
        ret_val.append(features[f](game))
    return ret_val