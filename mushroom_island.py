# Simple terminal game: Mushroom Island
# A spiritual successor to Dig Dug 2

import curses
import random
import sys

# Cell types
MUSHROOM = '#'
EMPTY = ' '
PLAYER = 'P'
ALIEN = 'A'

# Map arrow keys to deltas
DIRECTIONS = {
    curses.KEY_UP: (-1, 0),
    curses.KEY_DOWN: (1, 0),
    curses.KEY_LEFT: (0, -1),
    curses.KEY_RIGHT: (0, 1),
}

class Game:
    def __init__(self, height=15, width=30, num_aliens=3):
        self.height = height
        self.width = width
        self.board = [[MUSHROOM for _ in range(width)] for _ in range(height)]
        self.player = (height // 2, width // 2)
        self.aliens = []
        random.seed()
        for _ in range(num_aliens):
            while True:
                r = random.randint(1, height - 2)
                c = random.randint(1, width - 2)
                if (r, c) != self.player and (r, c) not in self.aliens:
                    self.aliens.append((r, c))
                    break

    def in_bounds(self, pos):
        r, c = pos
        return 0 <= r < self.height and 0 <= c < self.width

    def neighbors(self, pos):
        r, c = pos
        for dr, dc in [(-1,0), (1,0), (0,-1), (0,1)]:
            nr, nc = r + dr, c + dc
            if self.in_bounds((nr, nc)):
                yield nr, nc

    def dig(self, pos):
        r, c = pos
        if self.board[r][c] == MUSHROOM:
            self.board[r][c] = EMPTY
            self.remove_disconnected()

    def remove_disconnected(self):
        """Remove islands not connected to the border"""
        visited = [[False]*self.width for _ in range(self.height)]
        queue = []
        for r in range(self.height):
            for c in range(self.width):
                if r==0 or r==self.height-1 or c==0 or c==self.width-1:
                    if self.board[r][c] != EMPTY:
                        queue.append((r,c))
                        visited[r][c] = True
        head = 0
        while head < len(queue):
            r,c = queue[head]; head += 1
            for nr, nc in self.neighbors((r,c)):
                if not visited[nr][nc] and self.board[nr][nc] != EMPTY:
                    visited[nr][nc] = True
                    queue.append((nr,nc))
        # any mushroom not visited falls into the sea
        new_aliens = []
        for r in range(self.height):
            for c in range(self.width):
                if self.board[r][c] != EMPTY and not visited[r][c]:
                    self.board[r][c] = EMPTY
                if (r,c) in self.aliens and visited[r][c]:
                    new_aliens.append((r,c))
        self.aliens = new_aliens

    def move_player(self, direction):
        dr, dc = DIRECTIONS.get(direction, (0,0))
        nr, nc = self.player[0] + dr, self.player[1] + dc
        if not self.in_bounds((nr,nc)) or self.board[nr][nc] == EMPTY:
            return
        self.player = (nr,nc)
        if self.player in self.aliens:
            raise RuntimeError("Alien caught you!")

    def move_aliens(self):
        new_positions = []
        for r,c in self.aliens:
            moves = list(self.neighbors((r,c)))
            random.shuffle(moves)
            moved=False
            for nr,nc in moves:
                if self.board[nr][nc] != EMPTY and (nr,nc) not in self.aliens:
                    if self.board[nr][nc] == MUSHROOM:
                        self.board[nr][nc] = EMPTY
                        self.remove_disconnected()
                    new_positions.append((nr,nc))
                    moved=True
                    break
            if not moved:
                new_positions.append((r,c))
        self.aliens = new_positions
        if self.player in self.aliens:
            raise RuntimeError("Alien caught you!")

    def draw(self, stdscr):
        for r in range(self.height):
            line = ''
            for c in range(self.width):
                pos = (r,c)
                ch = self.board[r][c]
                if pos == self.player:
                    ch = PLAYER
                elif pos in self.aliens:
                    ch = ALIEN
                line += ch
            stdscr.addstr(r, 0, line)
        stdscr.refresh()

    def run(self, stdscr):
        curses.curs_set(False)
        stdscr.nodelay(True)
        while True:
            stdscr.erase()
            self.draw(stdscr)
            if not self.aliens:
                stdscr.addstr(self.height, 0, "You cleared all aliens! Press q to quit.")
                stdscr.refresh()
                while stdscr.getch() != ord('q'):
                    pass
                return
            key = stdscr.getch()
            try:
                if key in DIRECTIONS:
                    self.move_player(key)
                elif key in (ord(' '), ord('d')):
                    self.dig(self.player)
                elif key == ord('q'):
                    return
                self.move_aliens()
            except RuntimeError as e:
                stdscr.addstr(self.height, 0, str(e) + ' Press q to quit.')
                stdscr.refresh()
                while stdscr.getch() != ord('q'):
                    pass
                return


def main():
    try:
        curses.wrapper(Game().run)
    except curses.error:
        print("Terminal window too small.")
        sys.exit(1)

if __name__ == '__main__':
    main()
