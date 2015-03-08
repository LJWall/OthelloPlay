from othello.othello import tuple_offset

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

@features.register('norm_O_score')
def norm_X_score(game):
    """White's score, normalised """
    return game.score()['O']/(game.size * game.size)


@features.register('game_progress')
def game_progress(game):
    """How far through the game, normalised """
    return len(game)/(game.size * game.size)

def and_it(it):
    for x in it:
        if not x:
            return False
    return True


def safe_pieces(game, piece_type):
    """Which pieces are safe - i.e. cannon be turned. (Not currently exhastive.)"""
    border_set = {(-1, i) for i in range(-1, game.size)}.union(
                    {(i, game.size) for i in range(-1, game.size)},
                    {(game.size, i) for i in range(game.size+1) },
                    {(i, -1) for i in range(game.size+1)})
    directions = [(1, 0), (1, 1), (0, 1), (-1, 1)]
    piece_set = {key for key in game if game[key]==piece_type}
    safe_set = set()
    num = 0
    while True:
        for spot in piece_set:
            safe_plus = border_set.union(safe_set)
            if and_it((tuple_offset(spot, d) in safe_plus) or (tuple_offset(spot, d, -1) in safe_plus) for d in directions):
                safe_set.add(spot)
        if len(safe_set) == num:
            break
        num = len(safe_set)
    return len(safe_set)/(game.size * game.size)

@features.register('safe_X')
def safe_X(game):
    """Which black are safe - i.e. cannot be turned. (Not currently exhastive.)"""
    return safe_pieces(game, 'X')

@features.register('safe_O')
def safe_O(game):
    """Which white are safe - i.e. cannot be turned. (Not currently exhastive.)"""
    return safe_pieces(game, 'O')

@features.register('corners_O')
def corners_O(game):
    x = 0
    for corner in [(0, 0), (0, game.size-1), (game.size-1, 0), (game.size-1, game.size-1)]:
        if game.get(corner, '')=='O':
            x += 1
    return x/4

@features.register('corners_X')
def corners_X(game):
    x = 0
    for corner in [(0, 0), (0, game.size-1), (game.size-1, 0), (game.size-1, game.size-1)]:
        if game.get(corner, '')=='X':
            x += 1
    return x/4


def get_game_features(game, req_features):
    """Return request list of game features """
    ret_val = list()
    for f in req_features:
        ret_val.append(features[f](game))
    return ret_val