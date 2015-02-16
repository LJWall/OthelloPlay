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


class OthelloBoardClass(dict):
    def __init__(self, size):
        self.players = ('X', 'O')
        self.size = size
        x = size / 2
        self[(x-1, x-1)] = self.players[1]
        self[(x, x)] = self.players[1]
        self[(x-1, x)] = self.players[0]
        self[(x, x-1)] = self.players[0]
        self.current_turn = self.players[0]
        
    
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
        if x<0 or x>=self.size or y<0 or y>=self.size:
            raise KeyError
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
                    # opposin gpieces counld be zero!)
                    for n in range(m-1):
                        flip_count += 1
                        if test_only==False:
                            self[tuple_offset((x, y), vec, n+1)] = self.current_turn
                    break
                    
        if flip_count > 0:
            if test_only==False:
                self[(x,y)] = self.current_turn
                self.current_turn = self.players[1 - self.players.index(self.current_turn)]
            return flip_count
        else:
            raise InvalidMoveError
        
    def score(self):
        return {self.players[i]: len([k for k in self if self[k]==self.players[i]]) for i in [0,1]}

def auto_play_move(game):
    play_options = game.get_boundary();
    play_results = dict()
    for p in play_options:
        g1 = deepcopy(game)
        try:
            g1.play_move(*p)
        except InvalidMoveError:
            pass
        else:
            play_results[p] = g1
    if len(play_results):
        best_play = max(play_results, key=(lambda x: play_results[x].score()[game.current_turn]))
        game.play_move(*best_play)
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
            
        
        
        
        