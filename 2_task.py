import random


class Cell:
    def __init__(self, around_mines=0, mine=False):
        self.around_mines = around_mines
        self.mine = mine
        self.fl_open = False


class GamePole:
    def __init__(self, N, M):
        self.N = N
        self.M = M
        self.pole = [[Cell() for _ in range(N)] for _ in range(N)]
        self.init()

    def init(self):
        mines_placed = 0
        while mines_placed < self.M:
            x = random.randint(0, self.N - 1)
            y = random.randint(0, self.N - 1)
            if not self.pole[x][y].mine:
                self.pole[x][y].mine = True
                mines_placed += 1
                for dx in range(-1, 2):
                    for dy in range(-1, 2):
                        if 0 <= x + dx < self.N and 0 <= y + dy < self.N:
                            if not (dx == 0 and dy == 0):
                                self.pole[x + dx][y + dy].around_mines += 1

    def show(self):
        for row in self.pole:
            row_display = []
            for cell in row:
                if cell.fl_open:
                    if cell.mine:
                        row_display.append('*')
                    else:
                        row_display.append(str(cell.around_mines))
                else:
                    row_display.append('#')
            print(' '.join(row_display))

    def open_cell(self, x, y):
        if x < 0 or x >= self.N or y < 0 or y >= self.N or self.pole[x][y].fl_open:
            return False
        self.pole[x][y].fl_open = True
        if self.pole[x][y].mine:
            print("Вы проиграли! Попали на мину.")
            return True
        if self.pole[x][y].around_mines == 0:
            for dx in range(-1, 2):
                for dy in range(-1, 2):
                    if not (dx == 0 and dy == 0):
                        self.open_cell(x + dx, y + dy)
        return False

    def check_win(self):
        for row in self.pole:
            for cell in row:
                if not cell.fl_open and not cell.mine:
                    return False
        return True


pole_game = GamePole(10, 12)

