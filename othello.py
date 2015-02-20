from copy import deepcopy


def tuple_offset(t1, t2, k=1):
    """Offset t1 by k*t2."""
    ret = ()
    for x in range(len(t1)):
        ret = ret + (t1[x] + k*t2[x], )
    return ret

class InvalidMoveError(Exception):
    pass
class NoAvailablePlayError(Exception):
    pass

class GameCompleteError(Exception):
    pass

class OthelloBoardClass(dict):
    def __init__(self, size):
        self.players = ('X', 'O')
        self.size = size
        x = int(size / 2)
        self[(x-1, x-1)] = self.players[1]
        self[(x, x)] = self.players[1]
        self[(x-1, x)] = self.players[0]
        self[(x, x-1)] = self.players[0]
        self.current_turn = self.players[0]
        self.game_complete = False
    
    def __str__(self):
        ret = ''
        for y in range(self.size):
            for x in range(self.size):
                ret +=  self.get((x,y), '-') + ' '
            ret += '\n'
        return ret
            
    
    def get_boundary(self):
        ret = set()
        for x in self:
            for vec in [(0,1),(1,0),(0,-1),(-1,0),(-1, -1),(1, 1),(-1, 1),(1, -1)]:
                y = tuple_offset(x, vec)
                if y not in self and y[0] >=0 and y[0] < self.size and y[1] >=0 and y[1] < self.size:
                    ret.add(y)
        return ret
    
    def play_move(self, x, y, test_only=False):
        if self.game_complete:
            raise GameCompleteError
        if x<0 or x>=self.size or y<0 or y>=self.size:
            raise InvalidMoveError
        if self.get((x,y), 0):
            raise InvalidMoveError
        # for each direction vector, check if we have any pieces to flip in that
        # direction, keeping count of number flipped
        flip_count = 0
        for vec in [(0,1),(1,0),(0,-1),(-1,0),(-1, -1),(1, 1),(-1, 1),(1, -1)]:
            for m in range(1, self.size):
                if not self.get(tuple_offset((x, y), vec, m)):
                    break
                if self.get(tuple_offset((x, y), vec, m)) == self.current_turn:
                    # have found a piece matching current players in the line,
                    # with only opposing peices in between (note - number of
                    # opposing pieces could be zero!)
                    for n in range(m-1):
                        flip_count += 1
                        if not test_only:
                            self[tuple_offset((x, y), vec, n+1)] = self.current_turn
                    break
                    
        if flip_count > 0:
            if not test_only:
                # make the move
                self[(x,y)] = self.current_turn
                self.current_turn = self.players[1 - self.players.index(self.current_turn)]
                # asses the state of the board. (i.e. can the new player make a valid move? if so they forfeit their turn)
                plays = self.get_plays(simple=True) # note that simple=True stops us getting it a recursion loop!
                if len(plays)==0:
                    # new player has no options, flip the turn back
                    self.current_turn = self.players[1 - self.players.index(self.current_turn)]
                    # test again
                    plays = self.get_plays(simple=True)
                    if len(plays)==0:
                        # in this case, the game is over
                        self.game_complete = True
            return flip_count
        else:
            raise InvalidMoveError
        
    def score(self):
        return {self.players[i]: len([k for k in self if self[k]==self.players[i]]) for i in [0,1]}

    def get_plays(self, simple=False):
        play_options = self.get_boundary();
        play_results = dict()
        for p in play_options:
            g1 = deepcopy(self)
            try:
                flip_count = g1.play_move(*p, test_only=simple)
            except InvalidMoveError:
                pass
            else:
                play_results[p] = (flip_count if simple else g1)
        return play_results
    
    def auto_play_move(self):
        if self.game_complete:
            raise GameCompleteError
        play_results = self.get_plays()
        if len(play_results):
            best_play = max(play_results, key=(lambda x: play_results[x].score()[self.current_turn]))
            self.play_move(*best_play)
        else:
            raise NoAvailablePlayError

if __name__ == '__main__':
    game = OthelloBoardClass(6)
    print('You are playing as X')
    print(game)
    print(game.score())    
    while True:
        try:
            game.play_move(*eval(input('Move: ')))
        except InvalidMoveError:
            print('Invalid move. Try again.')
        else:
            print(game)
            print(game.score())
            auto_play_move(game)
            print(game)
            print(game.score())
            
        
        
        
        