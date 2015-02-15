
class OtheloBoardClass(dict):
    def __init__(self, size):
        self._size = size
        x = size / 2
        self[(x-1, x-1)] = "O"
        self[(x, x)] = "O"
        self[(x-1, x)] = "X"
        self[(x, x-1)] = "X"
            
    
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
            raise KeyError # should be another error
        self[(x,y)] = colour
    

if __name__ == '__main__':
    board = OtheloBoardClass(12)
    print(board)