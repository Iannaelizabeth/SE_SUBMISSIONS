from board import Board


class Minesweeper:
    def __init__(self, mode="Easy"):
        modes = {
            "Easy": (6, 6, 6),
            "Medium": (8, 8, 10),
            "Hard": (10, 10, 20)
        }

        rows, cols, mines = modes[mode]
        self.board = Board(rows, cols, mines)
        self.mode = mode

    def display(self, reveal_mines=False):
        b = self.board
        print("\n   " + " ".join(str(c + 1) for c in range(b.cols)))
        for r in range(b.rows):
            cells = []
            for c in range(b.cols):
                pos = (r, c)
                if reveal_mines and pos in b.mines:
                    ch = "*"
                elif pos in b.flags:
                    ch = "F"
                elif pos not in b.revealed:
                    ch = "#"
                elif pos in b.mines:
                    ch = "*"
                else:
                    ch = str(b.adjacent_mines(r, c))
                cells.append(ch)
            print(f"{r + 1:2} " + " ".join(cells))

    def run(self):
        print("Minesweeper")
        print("Choose difficulty:")
        print("1. Easy")
        print("2. Medium")
        print("3. Hard")

        choices = {
            "1": "Easy",
            "2": "Medium",
            "3": "Hard"
        }

        while True:
            choice = input("> ").strip()

            if choice in choices:
                self.mode = choices[choice]
                rows, cols, mines = {
                    "Easy": (6, 6, 6),
                    "Medium": (8, 8, 10),
                    "Hard": (10, 10, 20)
                }[self.mode]

                self.board = Board(rows, cols, mines)
                break

            print("Choose 1, 2 or 3.")

        print(f"{self.mode} mode: {self.board.rows}x{self.board.cols}, {self.board.mine_total} mines")
        print("Commands: r row col | f row col | q")
        while True:
            self.display()
            raw = input("> ").strip().lower()
            if raw == "q":
                return
            parts = raw.split()
            if len(parts) != 3 or parts[0] not in {"r", "f"}:
                print("Use r row col or f row col.")
                continue
            try:
                r, c = int(parts[1]) - 1, int(parts[2]) - 1
            except ValueError:
                print("Coordinates must be numbers.")
                continue
            if not self.board.in_bounds(r, c):
                print("Outside the board.")
                continue

            if parts[0] == "f":
                self.board.toggle_flag((r, c))
                continue

            if parts[0] == "r":
                if (r, c) in self.board.flags:
                    print("Cell is flagged.")
                    continue

                if (r, c) in self.board.revealed:
                    print("Cell already revealed.")
                    continue

                hit_mine = self.board.reveal((r, c))

                if hit_mine:
                    print("Boom! You hit a mine.")
                elif self.board.won():
                    print("You win!")
                else:
                    print("Cell revealed.")

                continue
