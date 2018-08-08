class Stream:
    def __init__(self, data):
        self.pos = 0
        self.buffer = data

    def read(self, num):
        rtn = self.buffer[self.pos:self.pos + num]
        self.pos = self.pos + num
        return rtn

    def peek(self):
        return self.buffer[self.pos]
