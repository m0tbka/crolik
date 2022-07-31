from sys import argv, exit
from random import randint
from time import ctime
import pygame


class Board:
    COLOURS = [(100, 100, 100), "blue", "green", "red", (100, 100, 180), (180, 100, 100), (100, 180, 100),
               (180, 180, 180)]

    def __init__(self, width, height, cell_size, color_pole, color_cell):
        self.width = width
        self.height = height
        self.board = [[1] * width for _ in range(height)]
        self.need_update = [[0] * width for _ in range(height)]
        self.left = cell_size // 5 + 1
        self.top = cell_size // 2 + 1
        self.cell_size = cell_size
        self.colours = {1: color_pole, -1: color_cell}

    """Возвращает индексы клетки по заданным координатам с поля"""

    def get_cell(self, coordinates):
        return (coordinates[1] - self.top) // self.cell_size, (coordinates[0] - self.left) // self.cell_size


def draw_line(board: Board, surface: pygame.Surface, color):
    pygame.draw.line(surface, color, (board.left, board.top * 0.5), (board.left + board.cell_size * board.width, board.top * 0.5), board.cell_size // 10 + 1)


def draw_board(board: Board, surface: pygame.Surface):
    pygame.draw.rect(surface, "pink", (
        board.left - 10, board.top - 10, board.height * board.cell_size + 20,
        board.width * board.cell_size + 20))
    pygame.draw.rect(surface, board.colours[1], (
        board.left, board.top, board.height * board.cell_size - 10,
        board.width * board.cell_size - 10))
    for i in range(board.height):
        for j in range(board.width):
            pygame.draw.rect(surface, "black", (
                board.left + j * board.cell_size, board.top + i * board.cell_size, board.cell_size + 1,
                board.cell_size + 1), 1)
    for i in range(board.width):
        for j in range(board.width):
            pygame.draw.rect(surface, board.colours[board.board[i][j]], (
                board.left + j * board.cell_size + 1, board.top + i * board.cell_size + 1, board.cell_size - 1,
                board.cell_size - 1))


def update_board(board: Board, screen: pygame.Surface):
    for i in range(board.width):
        for j in range(board.width):
            if board.need_update[i][j] == 1:
                board.need_update[i][j] = 0
                pygame.draw.rect(screen, board.colours[board.board[i][j]], (
                    board.left + j * board.cell_size + 1, board.top + i * board.cell_size + 1, board.cell_size - 1,
                    board.cell_size - 1))
    return board


class Mode:
    NEW = 0
    WORK = 1


def change_mode(mode):
    if mode == Mode.NEW:
        return Mode.WORK
    return Mode.NEW


class Monitor:
    MAX_HISTORY_DEPTH = 100000

    def __init__(self, kwargs):
        kwargs = kwargs[1:]
        data = [10, 35, "#9D3F50", "#84D7D0"]
        for i, e in enumerate(kwargs):
            data[i] = e
        data[0], data[1] = map(int, data[:2])
        self.n = data[0]
        self.size = self.n * data[1] + data[1] * 2
        self.screen = pygame.display.set_mode((self.size, self.size))
        self.board = Board(self.n, self.n, data[1], data[2], data[3])
        self.history = []
        self.history_dict = dict()
        self.history_pos = -1
        self.need_board = None
        self.mode = Mode.NEW
        self.finding_sol = False
        draw_board(self.board, self.screen)
        self.new()

    def random_solution(self, clicked=0):
        if clicked:
            if self.finding_sol:
                self.finding_sol = False
                return
            self.finding_sol = True
        i, j = randint(0, self.n - 1), randint(0, self.n - 1)
        ev = pygame.event.Event(pygame.KEYDOWN, {'button': 1})
        self.clicker(ev, 0, (i, j))

    def new(self):
        self.clear()
        self.mode = change_mode(self.mode)

    def new_click(self, indexes, change):
        self.board.board[indexes[0]][indexes[1]] *= -1
        self.board.need_update[indexes[0]][indexes[1]] = 1
        if change:
            self.history_pos -= 1
        else:
            self.history_pos += 1
            self.history[self.history_pos:] = [indexes]
            self.history_dict[indexes] = self.history_dict.get(indexes, 0) + 1

    def end_new(self):
        self.need_board = self.board.board
        self.clear()
        self.mode = Mode.WORK
        self.finding_sol = False
        draw_line(self.board, self.screen, "green")

    def check_need_board(self):
        if self.need_board == self.board.board:
            draw_line(self.board, self.screen, "red")
            self.finding_sol = False
            pre_time = ctime().replace(' ', '_').replace(':', '-')
            self.save(f"correct_solution_{pre_time[pre_time.index('_') + 1:-1 - pre_time[::-1].index('_')]}")
        else:
            draw_line(self.board, self.screen, "green")

    def clear(self):
        self.finding_sol = False
        self.history = []
        self.history_dict = dict()
        self.history_pos = -1
        self.board = Board(self.board.width, self.board.height, self.board.cell_size, self.board.colours[1], self.board.colours[-1])
        draw_board(self.board, self.screen)

    def save(self, name=None):
        if self.mode == Mode.WORK:
            if name is None:
                pre_time = ctime().replace(' ', '_').replace(':', '-')
                name = f"game_{pre_time[pre_time.index('_') + 1:-1 - pre_time[::-1].index('_')]}"
            with open(f"{name}.txt", 'w') as file:
                path = []
                for indexes in self.history_dict:
                    if self.history_dict[indexes] % 2:
                        path.append(indexes)
                file.write(str(len(path)) + '\n')
                for indexes in path:
                    file.write(f"{indexes[0]} {indexes[1]}\n")
        elif self.mode == Mode.NEW:
            if name is None:
                pre_time = ctime().replace(' ', '_').replace(':', '-')
                name = f"board_{pre_time[pre_time.index('_') + 1:-1 - pre_time[::-1].index('_')]}"
            with open(f"{name}.txt", 'w') as file:
                file.write(str(self.n) + '\n')
                for i in range(self.n):
                    board = []
                    for j in range(self.n):
                        board.append(self.board.board[i][j])
                        if board[j] == -1:
                            board[j] = 0
                    print(*board, file=file)

    def check_history_depth(self, depth=MAX_HISTORY_DEPTH):
        if len(self.history) < depth:
            return
        self.history = self.history[max(depth - 1000, 0):]
        self.history_pos = len(self.history) - 1

    def clicker(self, event, change=0, indexes=None):
        if indexes is None:
            indexes = self.board.get_cell(event.pos)
        if indexes[0] >= self.board.height or indexes[1] >= self.board.width:
            return None
        if event.button == 1:
            if self.mode == Mode.WORK:
                for i in range(self.n):
                    self.board.board[i][indexes[1]] *= -1
                    self.board.need_update[i][indexes[1]] = 1
                for i in range(self.n):
                    self.board.board[indexes[0]][i] *= -1
                    self.board.need_update[indexes[0]][i] = 1
                self.board.board[indexes[0]][indexes[1]] *= -1
                if change:
                    self.history_pos -= 1
                else:
                    self.history_pos += 1
                    self.history[self.history_pos:] = [indexes]
                    self.history_dict[indexes] = self.history_dict.get(indexes, 0) + 1
                self.check_need_board()
                self.check_history_depth()
            elif self.mode == Mode.NEW:
                self.new_click(indexes, change)


def main():
    # Minesweaper(кол-во клеток по горизонтали, кол-во клеток по вертикали, кол-во мин, размер одной клетки)
    game = Monitor(argv[:5])
    running = True
    while running:
        if game.finding_sol:
            game.random_solution()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                game.clicker(event)
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    if game.mode == Mode.NEW:
                        game.end_new()
                if pygame.key.get_mods() & pygame.KMOD_CTRL:
                    if event.key == pygame.K_c:
                        game.clear()
                    if event.key == pygame.K_z:
                        if game.history_pos > -1:
                            event.button = 1
                            game.clicker(event, change=1, indexes=game.history[game.history_pos])
                    if event.key == pygame.K_r:
                        game.random_solution(clicked=1)
                    if event.key == pygame.K_n:
                        game.new()
                    if event.key == pygame.K_s:
                        game.save()
                    if event.key == pygame.K_q:
                        exit(0)
        game.board = update_board(game.board, game.screen)
        pygame.display.flip()


if __name__ == '__main__':
    main()
