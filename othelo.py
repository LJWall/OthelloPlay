
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
        for x in range(self._size):
            for y in range(self._size):
                ret +=  self.get((x,y), '-') + ' '
            ret += '\n'
        return ret
            
    
    def play_move(self, x, y):
        if x<0 or x>=self._size or y<0 or y>=self._size:
            raise KeyError
        if self.get((x,y), 0):
            raise InvalidMoveError
        self[(x,y)] = self.current_turn
        self.current_turn = self.players[1 - self.players.index(self.current_turn)]
    

if __name__ == '__main__':
    board = OtheloBoardClass(12)
    print(board)