import tkinter as tk

WINDOW_WIDTH = 420
WINDOW_HEIGHT = 520

COLOR_BG = "#1a2a3a"
COLOR_BTN_BG = "#2d6a4f"
COLOR_BTN_ACTIVE = "#40916c"
COLOR_BTN_TEXT = "#f1faee"
COLOR_X = "#e63946"
COLOR_O = "#457b9d"
COLOR_TITLE = "#f1faee"
COLOR_WIN = "#52b788"
COLOR_PANEL = "#0d1b2a"


class TicTacToe:
    def __init__(self, root):
        self.root = root
        self.root.title("Tic Tac Toe")
        self.root.configure(bg=COLOR_BG)
        self.root.resizable(False, False)
        self.board = [""] * 9
        self.current_player = "X"
        self.game_mode = "PVP"
        self.scores = {"X": 0, "O": 0, "Draw": 0}
        self.game_active = False
        self.buttons = []
        self._build_menu()

    def _make_btn(self, parent, text, command, bg=COLOR_BTN_BG, size=14, width=15):
        return tk.Button(parent, text=text, font=("Helvetica", size, "bold"), width=width,
                         bg=bg, fg=COLOR_BTN_TEXT, activebackground=COLOR_BTN_ACTIVE,
                         relief="flat", cursor="hand2", command=command)

    def _build_menu(self):
        self.menu_frame = tk.Frame(self.root, bg=COLOR_BG)
        self.menu_frame.place(x=0, y=0, width=WINDOW_WIDTH, height=WINDOW_HEIGHT)
        tk.Label(self.menu_frame, text="TIC TAC TOE", font=("Helvetica", 34, "bold"),
                 bg=COLOR_BG, fg=COLOR_TITLE).pack(pady=(70, 5))
        tk.Label(self.menu_frame, text="Choose Game Mode", font=("Helvetica", 14),
                 bg=COLOR_BG, fg=COLOR_BTN_ACTIVE).pack(pady=(0, 40))
        self._make_btn(self.menu_frame, "PLAYER VS PLAYER", self.start_pvp, size=16).pack(pady=10)
        self._make_btn(self.menu_frame, "PLAYER VS AI", self.start_pva, bg="#6f4e37", size=16).pack(pady=10)
        self._make_btn(self.menu_frame, "EXIT", self.root.quit, bg="#8b2c2c", size=14).pack(pady=10)

    def start_pvp(self):
        self.game_mode = "PVP"
        self._start_game()

    def start_pva(self):
        self.game_mode = "PVA"
        self._start_game()

    def _start_game(self):
        self.menu_frame.place_forget()
        self.board = [""] * 9
        self.current_player = "X"
        self.game_active = True
        self.buttons = []
        self.game_frame = tk.Frame(self.root, bg=COLOR_BG)
        self.game_frame.place(x=0, y=0, width=WINDOW_WIDTH, height=WINDOW_HEIGHT)
        self.score_label = tk.Label(self.game_frame, text=self._score_text(),
                                    font=("Helvetica", 12), bg=COLOR_BG, fg=COLOR_TITLE)
        self.score_label.pack(pady=(10, 5))
        self.turn_label = tk.Label(self.game_frame, text=self._turn_text(),
                                   font=("Helvetica", 14, "bold"), bg=COLOR_BG, fg=COLOR_TITLE)
        self.turn_label.pack(pady=(0, 10))
        self.grid_frame = tk.Frame(self.game_frame, bg=COLOR_BG)
        self.grid_frame.pack(pady=10)
        for i in range(9):
            btn = tk.Button(self.grid_frame, text="", font=("Helvetica", 32, "bold"),
                            width=4, height=2, bg=COLOR_BTN_BG, fg=COLOR_BTN_TEXT,
                            activebackground=COLOR_BTN_ACTIVE, relief="flat", cursor="hand2",
                            command=lambda idx=i: self.on_click(idx))
            btn.grid(row=i // 3, column=i % 3, padx=3, pady=3)
            self.buttons.append(btn)
        btn_frame = tk.Frame(self.game_frame, bg=COLOR_BG)
        btn_frame.pack(pady=15)
        self._make_btn(btn_frame, "RESET", self._reset_board, size=12, width=8).pack(side="left", padx=5)
        self._make_btn(btn_frame, "MENU", self._back_to_menu, bg="#6f4e37", size=12, width=8).pack(side="left", padx=5)

    def _turn_text(self):
        return f"Turn: Player {self.current_player}"

    def _score_text(self):
        x = self.scores["X"]
        o = self.scores["O"]
        d = self.scores["Draw"]
        return f"X Wins: {x}  |  O Wins: {o}  |  Draws: {d}"

    def _reset_board(self):
        self.board = [""] * 9
        self.current_player = "X"
        self.game_active = True
        for btn in self.buttons:
            btn.config(text="", bg=COLOR_BTN_BG)
        self.turn_label.config(text=self._turn_text())

    def _back_to_menu(self):
        self.game_frame.place_forget()
        self.menu_frame.place(x=0, y=0, width=WINDOW_WIDTH, height=WINDOW_HEIGHT)

    def on_click(self, idx):
        if not self.game_active or self.board[idx] != "":
            return
        if self.game_mode == "PVA" and self.current_player == "O":
            return
        self._make_move(idx, self.current_player)
        if self._check_game_over():
            return
        self._switch_player()
        if self.game_mode == "PVA" and self.current_player == "O" and self.game_active:
            self.root.after(500, self._ai_move)

    def _make_move(self, idx, player):
        self.board[idx] = player
        color = COLOR_X if player == "X" else COLOR_O
        self.buttons[idx].config(text=player, fg=color)

    def _switch_player(self):
        self.current_player = "O" if self.current_player == "X" else "X"
        self.turn_label.config(text=self._turn_text())

    def _ai_move(self):
        if not self.game_active:
            return
        move = self._find_best_move()
        if move is not None:
            self._make_move(move, "O")
            if self._check_game_over():
                return
            self._switch_player()

    def _find_best_move(self):
        for i in range(9):
            if self.board[i] == "":
                self.board[i] = "O"
                if self._check_winner() == "O":
                    self.board[i] = ""
                    return i
                self.board[i] = ""
        for i in range(9):
            if self.board[i] == "":
                self.board[i] = "X"
                if self._check_winner() == "X":
                    self.board[i] = ""
                    return i
                self.board[i] = ""
        if self.board[4] == "":
            return 4
        for i in [0, 2, 6, 8]:
            if self.board[i] == "":
                return i
        for i in [1, 3, 5, 7]:
            if self.board[i] == "":
                return i
        return None

    def _check_winner(self):
        lines = [(0,1,2), (3,4,5), (6,7,8), (0,3,6), (1,4,7), (2,5,8), (0,4,8), (2,4,6)]
        for a, b, c in lines:
            if self.board[a] == self.board[b] == self.board[c] != "":
                return self.board[a]
        return None

    def _check_game_over(self):
        winner = self._check_winner()
        if winner:
            self.game_active = False
            self.scores[winner] += 1
            self._highlight_winner(winner)
            self.turn_label.config(text=f"Player {winner} Wins!")
            self.score_label.config(text=self._score_text())
            self.root.after(2000, self._reset_board)
            return True
        if "" not in self.board:
            self.game_active = False
            self.scores["Draw"] += 1
            self.turn_label.config(text="Its a Draw!")
            self.score_label.config(text=self._score_text())
            self.root.after(2000, self._reset_board)
            return True
        return False

    def _highlight_winner(self, winner):
        lines = [(0,1,2), (3,4,5), (6,7,8), (0,3,6), (1,4,7), (2,5,8), (0,4,8), (2,4,6)]
        for a, b, c in lines:
            if self.board[a] == self.board[b] == self.board[c] == winner:
                for idx in (a, b, c):
                    self.buttons[idx].config(bg=COLOR_WIN)
                break


def main():
    root = tk.Tk()
    root.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")
    TicTacToe(root)
    root.mainloop()


if __name__ == "__main__":
    main()
