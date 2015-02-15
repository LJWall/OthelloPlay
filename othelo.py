
def tuple_offset(t1, t2, k=1):
    """Offset t1 by k*t2."""
    ret = ()
    for x in range(len(t1)):
        ret = ret + (t1[x] + k*t2[x], )
    return ret

class InvalidMoveError(Exception):
    pass

class OtheloBoardClass(dict):
    def __init__(self, size):
        self.players = ('X', 'O')
        self._size = size
        x = size / 2
        self[(x-1, x-1)] = self.players[1]
        self[(x, x)] = self.players[1]
        self[(x-1, x)] = self.players[0]
        self[(x, x-1)] = self.players[0]
        self.current_turn = self.players[0]
        
    
    def __str__(self):
        ret = ''
        for y in range(self._size):
            for x in range(self._size):
                ret +=  self.get((x,y), '-') + ' '
            ret += '\n'
        return ret
            
    
    def play_move(self, x, y):
        if x<0 or x>=self._size or y<0 or y>=self._size:
            raise KeyError
        if self.get((x,y), 0):
            raise InvalidMoveError
        # for each direction vector, check if we have any pieces to flip in that
        # direction, keeping count of number flipped
        flip_count = 0
        for vec in [(0,1),(1,0),(0,-1),(-1,0)]:
            for m in range(1, self._size):
                if not self.get(tuple_offset((x, y), vec, m)):
                    break
                if self.get(tuple_offset((x, y), vec, m)) == self.current_turn:
                    # have found a piece matching current players in the line,
                    # with only opposing peices in between (note - number of
                    # opposin gpieces counld be zero!)
                    for n in range(m-1):
                        flip_count += 1
                        self[tuple_offset((x, y), vec, n+1)] = self.current_turn
                    
        if flip_count > 0:
            self[(x,y)] = self.current_turn
            self.current_turn = self.players[1 - self.players.index(self.current_turn)]
        else:
            raise InvalidMoveError
    

if __name__ == '__main__':
    board = OtheloBoardClass(6)
    print(board)
    board.play_move(2, 1)
    print(board)
    board.play_move(1, 3)
    print(board)