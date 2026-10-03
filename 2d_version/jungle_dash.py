import tkinter as tk
import random
import json

WINDOW_WIDTH = 1000
WINDOW_HEIGHT = 600
PLAYER_BASE_Y = 460
FPS_MS = 25
SETTINGS_FILE = "jungle_dash_settings.json"

LANE_X = [300, 500, 700]

COLOR_SKY_TOP = "#0a1a3a"
COLOR_SKY_BOTTOM = "#7ec8e3"
COLOR_CLOUD = "#f0f8ff"
COLOR_MTN_FAR = "#3a5a6a"
COLOR_MTN_NEAR = "#2a4d3e"
COLOR_BUILDING = "#4a5a6a"
COLOR_BUILDING_WIN = "#ffd966"
COLOR_TREE_FAR = "#1a4d2e"
COLOR_TREE_MID = "#2d6a4f"
COLOR_TREE_NEAR = "#3a8a5f"
COLOR_TRUNK = "#5d4037"
COLOR_ROAD = "#3d3d3d"
COLOR_ROAD_LINE = "#ffd700"
COLOR_GRASS = "#52b788"
COLOR_GROUND = "#2a1a0f"
COLOR_SKIN = "#f5c89e"
COLOR_HAIR = "#4a2c2a"
COLOR_SHIRT = "#e63946"
COLOR_PANTS = "#1d3557"
COLOR_SHOES = "#2a2a2a"
COLOR_TITLE = "#f1faee"
COLOR_BTN_BG = "#2d6a4f"
COLOR_BTN_ACTIVE = "#40916c"
COLOR_BTN_TEXT = "#f1faee"
COLOR_PANEL = "#1a2a3a"
COLOR_HUD = "#0d1b2a"
COLOR_COIN = "#ffd700"
COLOR_COIN_DK = "#b8860b"
COLOR_LOG = "#8b4513"
COLOR_LOG_DK = "#5d3a1a"
COLOR_ROCK = "#6c757d"
COLOR_TRAIN = "#8b0000"
COLOR_TRAIN_WIN = "#ffd966"
CAR_COLORS = ["#e63946", "#457b9d", "#f4a261", "#2a9d8f"]

def load_settings():
    try:
        with open(SETTINGS_FILE, "r") as f:
            return json.load(f)
    except Exception:
        return {"tutorial_seen": False}

def save_settings(s):
    try:
        with open(SETTINGS_FILE, "w") as f:
            json.dump(s, f)
    except Exception:
        pass

class JungleDash:
    def __init__(self, root):
        self.root = root
        self.root.title("Jungle Dash")
        self.root.configure(bg=COLOR_SKY_BOTTOM)
        self.root.resizable(False, False)
        self.state = "MENU"
        self.loop_id = None
        self.settings = load_settings()
        self.shake = 0
        self.flash = 0
        self.canvas = tk.Canvas(self.root, width=WINDOW_WIDTH, height=WINDOW_HEIGHT, bg=COLOR_SKY_BOTTOM, highlightthickness=0)
        self.menu_frame = tk.Frame(self.root, bg=COLOR_SKY_BOTTOM)
        self.howto_frame = tk.Frame(self.root, bg=COLOR_SKY_BOTTOM)
        self.go_frame = tk.Frame(self.root, bg=COLOR_SKY_BOTTOM)
        self.tut_frame = tk.Frame(self.root, bg=COLOR_SKY_BOTTOM)
        self._build_menu()
        self._build_howto()
        self._build_game_over()
        self._build_tutorial()
        self.show_menu()
        self.root.bind("<space>", lambda e: self.on_jump())
        self.root.bind("<Up>", lambda e: self.on_jump())
        self.root.bind("<Left>", lambda e: self.on_left())
        self.root.bind("<Right>", lambda e: self.on_right())
        self.root.bind("<a>", lambda e: self.on_left())
        self.root.bind("<d>", lambda e: self.on_right())
        self.root.bind("<A>", lambda e: self.on_left())
        self.root.bind("<D>", lambda e: self.on_right())
        self.root.bind("<p>", lambda e: self.toggle_pause())
        self.root.bind("<P>", lambda e: self.toggle_pause())
        self.root.bind("<Return>", lambda e: self.on_enter())
        self.root.bind("<Escape>", lambda e: self.show_menu())

    def _btn(self, parent, text, cmd, bg=COLOR_BTN_BG, sz=16, w=18):
        return tk.Button(parent, text=text, font=("Helvetica", sz, "bold"), width=w, bg=bg, fg=COLOR_BTN_TEXT, activebackground=COLOR_BTN_ACTIVE, relief="flat", cursor="hand2", command=cmd)

    def _build_menu(self):
        tk.Label(self.menu_frame, text="JUNGLE DASH", font=("Helvetica", 52, "bold"), bg=COLOR_SKY_BOTTOM, fg=COLOR_TITLE).pack(pady=(80, 5))
        tk.Label(self.menu_frame, text="RUN JUMP SURVIVE", font=("Helvetica", 18), bg=COLOR_SKY_BOTTOM, fg=COLOR_GRASS).pack(pady=(0, 50))
        self._btn(self.menu_frame, "START GAME", self.start_game, sz=20).pack(pady=8)
        self._btn(self.menu_frame, "HOW TO PLAY", self.show_howto, bg="#6f4e37", sz=16).pack(pady=8)
        self._btn(self.menu_frame, "EXIT", self.root.quit, bg="#8b2c2c", sz=16).pack(pady=8)
        tk.Label(self.menu_frame, text="Press ENTER to start", font=("Helvetica", 11), bg=COLOR_SKY_BOTTOM, fg="#b8c5d6").pack(pady=(30, 0))

    def _build_howto(self):
        tk.Label(self.howto_frame, text="HOW TO PLAY", font=("Helvetica", 40, "bold"), bg=COLOR_SKY_BOTTOM, fg=COLOR_TITLE).pack(pady=(50, 25))
        for k, a in [("LEFT/RIGHT or A/D", "Switch lane"), ("SPACE or UP", "Jump"), ("P", "Pause/Resume")]:
            row = tk.Frame(self.howto_frame, bg=COLOR_SKY_BOTTOM)
            row.pack(pady=5)
            tk.Label(row, text=k, font=("Helvetica", 14, "bold"), width=22, bg=COLOR_PANEL, fg=COLOR_GRASS).pack(side="left", padx=8)
            tk.Label(row, text=a, font=("Helvetica", 14), width=14, bg=COLOR_PANEL, fg=COLOR_TITLE).pack(side="left", padx=8)
        for line in ["Switch lanes to avoid obstacles.", "Jump over obstacles.", "Collect coins for score.", "One collision = Game Over."]:
            tk.Label(self.howto_frame, text=line, font=("Helvetica", 13), bg=COLOR_SKY_BOTTOM, fg="#b8c5d6").pack(pady=2)
        self._btn(self.howto_frame, "BACK", self.show_menu, bg="#6f4e37", sz=16).pack(pady=15)

    def _build_game_over(self):
        tk.Label(self.go_frame, text="GAME OVER - YOU ARE OUT!", font=("Helvetica", 34, "bold"), bg=COLOR_SKY_BOTTOM, fg="#e63946").pack(pady=(100, 30))
        self.go_score = tk.Label(self.go_frame, text="SCORE: 0", font=("Helvetica", 22, "bold"), bg=COLOR_SKY_BOTTOM, fg=COLOR_TITLE)
        self.go_score.pack(pady=8)
        self.go_coins = tk.Label(self.go_frame, text="COINS: 0", font=("Helvetica", 20), bg=COLOR_SKY_BOTTOM, fg=COLOR_COIN)
        self.go_coins.pack(pady=8)
        self._btn(self.go_frame, "PLAY AGAIN", self.start_game, sz=18).pack(pady=15)
        self._btn(self.go_frame, "MAIN MENU", self.show_menu, bg="#6f4e37", sz=16).pack(pady=8)

    def _build_tutorial(self):
        tk.Label(self.tut_frame, text="WELCOME!", font=("Helvetica", 30, "bold"), bg=COLOR_SKY_BOTTOM, fg=COLOR_TITLE).pack(pady=(50, 15))
        tk.Label(self.tut_frame, text="First Time Tutorial", font=("Helvetica", 16), bg=COLOR_SKY_BOTTOM, fg=COLOR_GRASS).pack(pady=(0, 20))
        for k, a in [("LEFT/RIGHT or A/D", "Switch lane"), ("SPACE or UP", "Jump"), ("P", "Pause/Resume")]:
            row = tk.Frame(self.tut_frame, bg=COLOR_SKY_BOTTOM)
            row.pack(pady=5)
            tk.Label(row, text=k, font=("Helvetica", 14, "bold"), width=22, bg=COLOR_PANEL, fg=COLOR_GRASS).pack(side="left", padx=8)
            tk.Label(row, text=a, font=("Helvetica", 14), width=18, bg=COLOR_PANEL, fg=COLOR_TITLE).pack(side="left", padx=8)
        for line in ["Avoid obstacles by switching lanes.", "Jump over obstacles.", "Collect coins.", "One collision = Game Over."]:
            tk.Label(self.tut_frame, text=line, font=("Helvetica", 13), bg=COLOR_SKY_BOTTOM, fg="#b8c5d6").pack(pady=2)
        self._btn(self.tut_frame, "START PLAYING", self.dismiss_tutorial, sz=18).pack(pady=20)

    def _stop_loop(self):
        if self.loop_id is not None:
            self.root.after_cancel(self.loop_id)
            self.loop_id = None

    def show_menu(self):
        self._stop_loop()
        self.state = "MENU"
        self.canvas.pack_forget()
        for f in [self.howto_frame, self.go_frame, self.tut_frame]:
            f.place_forget()
        self.menu_frame.place(x=0, y=0, width=WINDOW_WIDTH, height=WINDOW_HEIGHT)

    def show_howto(self):
        self.state = "HOWTO"
        self.canvas.pack_forget()
        for f in [self.menu_frame, self.go_frame, self.tut_frame]:
            f.place_forget()
        self.howto_frame.place(x=0, y=0, width=WINDOW_WIDTH, height=WINDOW_HEIGHT)

    def show_game_over(self):
        self._stop_loop()
        self.state = "GAMEOVER"
        self.go_score.config(text=f"SCORE: {self.score}")
        self.go_coins.config(text=f"COINS: {self.coin_count}")
        self.go_frame.place(x=0, y=0, width=WINDOW_WIDTH, height=WINDOW_HEIGHT)

    def start_game(self):
        self._stop_loop()
        self.current_lane = 1
        self.player_x = float(LANE_X[1])
        self.player_y = float(PLAYER_BASE_Y)
        self.player_vy = 0.0
        self.on_ground = True
        self.anim_frame = 0
        self.anim_counter = 0
        self.score = 0
        self.coin_count = 0
        self.speed = 6
        self.paused = False
        self.obstacles = []
        self.coins = []
        self.bg = [0.0] * 8
        self.train_x = -300.0
        self.train_active = False
        self.train_timer = random.randint(200, 500)
        self.cars = []
        self.car_timer = 0
        self.obs_timer = 0
        self.coin_timer = 0
        self.shake = 0
        self.flash = 0
        self.cave_progress = 0.0
        self.pickup_effects = []
        if not self.settings.get("tutorial_seen", False):
            self.state = "TUTORIAL"
            for f in [self.menu_frame, self.howto_frame, self.go_frame]:
                f.place_forget()
            self.tut_frame.place(x=0, y=0, width=WINDOW_WIDTH, height=WINDOW_HEIGHT)
        else:
            self._begin_play()

    def dismiss_tutorial(self):
        self.settings["tutorial_seen"] = True
        save_settings(self.settings)
        self._begin_play()

    def _begin_play(self):
        self._stop_loop()
        self.state = "PLAYING"
        for f in [self.menu_frame, self.howto_frame, self.go_frame, self.tut_frame]:
            f.place_forget()
        self.canvas.pack()
        self.game_loop()

    def on_enter(self):
        if self.state in ("MENU", "GAMEOVER"):
            self.start_game()
        elif self.state == "TUTORIAL":
            self.dismiss_tutorial()

    def on_jump(self):
        if self.state == "PLAYING" and not self.paused and self.on_ground:
            self.player_vy = -15.0
            self.on_ground = False

    def on_left(self):
        if self.state == "PLAYING" and not self.paused:
            if self.current_lane > 0:
                self.current_lane -= 1

    def on_right(self):
        if self.state == "PLAYING" and not self.paused:
            if self.current_lane < 2:
                self.current_lane += 1

    def toggle_pause(self):
        if self.state == "PLAYING":
            self.paused = not self.paused

    def game_loop(self):
        if self.state != "PLAYING":
            return
        if not self.paused:
            self.update()
        if self.state != "PLAYING":
            return
        self.draw()
        self.loop_id = self.root.after(FPS_MS, self.game_loop)

    def update(self):
        target_x = LANE_X[self.current_lane]
        self.player_x += (target_x - self.player_x) * 0.25
        self.player_vy += 0.8
        self.player_y += self.player_vy
        if self.player_y >= PLAYER_BASE_Y:
            self.player_y = float(PLAYER_BASE_Y)
            self.player_vy = 0.0
            self.on_ground = True
        self.anim_counter += 1
        if self.anim_counter >= 5:
            self.anim_counter = 0
            self.anim_frame = 1 - self.anim_frame
        self.score += 1
        self.speed = 6 + self.score // 500
        self.cave_progress = min(1.0, self.score / 800.0)
        if self.shake > 0: self.shake -= 1
        if self.flash > 0: self.flash -= 1
        for i in range(len(self.bg)):
            self.bg[i] = (self.bg[i] + self.speed * [0.2, 0.3, 0.5, 0.7, 0.9, 1.0, 0.4, 1.0][i]) % [500, 400, 250, 180, 140, 40, 300, 60][i]
        self.obs_timer += 1
        if self.obs_timer > 70 + random.randint(0, 50):
            self.obs_timer = 0
            lane = random.randint(0, 2)
            otype = random.choice(["log", "log", "rock"])
            if otype == "log":
                self.obstacles.append({"x": LANE_X[lane] - 35, "y": -50, "w": 70, "h": 35, "type": "log", "lane": lane})
            else:
                self.obstacles.append({"x": LANE_X[lane] - 25, "y": -50, "w": 50, "h": 40, "type": "rock", "lane": lane})
        self.coin_timer += 1
        if self.coin_timer > 100 + random.randint(0, 60):
            self.coin_timer = 0
            self._spawn_coin_pattern()
        for o in self.obstacles: o["y"] += self.speed
        self.obstacles = [o for o in self.obstacles if o["y"] < WINDOW_HEIGHT + 50]
        for c in self.coins: c["y"] += self.speed
        self.coins = [c for c in self.coins if c["y"] < WINDOW_HEIGHT + 50]
        for ef in self.pickup_effects:
            ef["y"] -= 2
            ef["r"] += 1
            ef["alpha"] -= 0.05
        self.pickup_effects = [e for e in self.pickup_effects if e["alpha"] > 0]
        self.car_timer += 1
        if self.car_timer > 80 + random.randint(0, 60):
            self.car_timer = 0
            self.cars.append({"x": WINDOW_WIDTH + 50, "y": 180 + random.randint(0, 30), "color": random.choice(CAR_COLORS), "w": 50, "h": 25})
        for car in self.cars: car["x"] -= self.speed * 1.5
        self.cars = [c for c in self.cars if c["x"] > -100]
        if self.train_active:
            self.train_x -= self.speed * 1.2
            if self.train_x < -400:
                self.train_active = False
                self.train_timer = random.randint(300, 600)
        else:
            self.train_timer -= 1
            if self.train_timer <= 0:
                self.train_active = True
                self.train_x = float(WINDOW_WIDTH + 50)
        self._check_collisions()

    def _rect_overlap(self, x1, y1, w1, h1, x2, y2, w2, h2):
        return x1 < x2 + w2 and x1 + w1 > x2 and y1 < y2 + h2 and y1 + h1 > y2

    def _check_collisions(self):
        px = self.player_x - 18
        py = self.player_y - 30
        pw = 36
        ph = 60
        for o in self.obstacles:
            if self._rect_overlap(px + 4, py + 4, pw - 8, ph - 8, o["x"], o["y"], o["w"], o["h"]):
                self.shake = 15
                self.flash = 15
                self.show_game_over()
                return
        collected = []
        for i, c in enumerate(self.coins):
            if self._rect_overlap(px, py, pw, ph, c["x"] - c["r"], c["y"] - c["r"], c["r"] * 2, c["r"] * 2):
                self.coin_count += 1
                collected.append(i)
                self.pickup_effects.append({"x": c["x"], "y": c["y"], "r": 12, "alpha": 1.0})
        if collected:
            self.coins = [c for i, c in enumerate(self.coins) if i not in collected]

    def draw(self):
        self.canvas.delete("all")
        self._draw_sky()
        self._draw_clouds()
        self._draw_mountains()
        self._draw_river()
        self._draw_jungle_sides()
        self._draw_trees()
        self._draw_jungle_floor()
        self._draw_road()
        self._draw_obstacles()
        self._draw_coins()
        self._draw_player()
        self._draw_lighting()
        self._draw_cave()
        self._draw_pickup_effects()
        self._draw_hud()
        if self.flash > 0:
            self.canvas.create_rectangle(2, 2, WINDOW_WIDTH - 2, WINDOW_HEIGHT - 2, outline="red", width=6)
        if self.paused:
            self.canvas.create_rectangle(0, 0, WINDOW_WIDTH, WINDOW_HEIGHT, fill="#000000", stipple="gray50")
            self.canvas.create_text(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2, text="PAUSED", font=("Helvetica", 52, "bold"), fill=COLOR_TITLE)
            self.canvas.create_text(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 60, text="Press P to resume", font=("Helvetica", 16), fill="#b8c5d6")

    def _draw_sky(self):
        for y in range(0, WINDOW_HEIGHT, 6):
            ratio = y / WINDOW_HEIGHT
            r = int(0x0a + (0x7e - 0x0a) * ratio)
            g = int(0x1a + (0xc8 - 0x1a) * ratio)
            b = int(0x3a + (0xe3 - 0x3a) * ratio)
            self.canvas.create_line(0, y, WINDOW_WIDTH, y, fill=f"#{r:02x}{g:02x}{b:02x}")

    def _draw_clouds(self):
        for i in range(6):
            x = int((i * 220 - self.bg[0]) % (WINDOW_WIDTH + 200) - 100)
            y = 30 + i * 20
            self.canvas.create_oval(x, y, x + 80, y + 30, fill=COLOR_CLOUD, outline="")
            self.canvas.create_oval(x + 20, y - 10, x + 60, y + 20, fill=COLOR_CLOUD, outline="")

    def _draw_mountains(self):
        for i in range(4):
            x = int((i * 300 - self.bg[1]) % (WINDOW_WIDTH + 300) - 150)
            self.canvas.create_polygon(x, 400, x + 150, 180, x + 300, 400, fill=COLOR_MTN_FAR, outline="")
        for i in range(3):
            x = int((i * 350 - self.bg[1] * 1.3) % (WINDOW_WIDTH + 350) - 175)
            self.canvas.create_polygon(x, 400, x + 175, 230, x + 350, 400, fill=COLOR_MTN_NEAR, outline="")
        for i in range(8):
            x = int((i * 150 - self.bg[1] * 0.5) % (WINDOW_WIDTH + 150) - 75)
            self.canvas.create_oval(x, 330, x + 120, 380, fill="#a8d5ba", outline="")

    def _draw_jungle_sides(self):
        for i in range(5):
            x = int((i * 80 - self.bg[6]) % 220 - 110)
            self.canvas.create_oval(x, 200, x + 80, 310, fill=COLOR_TREE_FAR, outline="")
        for i in range(4):
            x = int((i * 110 - self.bg[4]) % 220 - 110)
            self.canvas.create_rectangle(x + 35, 290, x + 48, 400, fill=COLOR_TRUNK, outline="")
            self.canvas.create_oval(x, 200, x + 85, 300, fill=COLOR_TREE_MID, outline="")
            self.canvas.create_oval(x + 10, 180, x + 75, 270, fill=COLOR_TREE_NEAR, outline="")
        for i in range(5):
            x = int((i * 80 - self.bg[6]) % 220 + 790)
            self.canvas.create_oval(x, 200, x + 80, 310, fill=COLOR_TREE_FAR, outline="")
        for i in range(4):
            x = int((i * 110 - self.bg[4]) % 220 + 790)
            self.canvas.create_rectangle(x + 35, 290, x + 48, 400, fill=COLOR_TRUNK, outline="")
            self.canvas.create_oval(x, 200, x + 85, 300, fill=COLOR_TREE_MID, outline="")
            self.canvas.create_oval(x + 10, 180, x + 75, 270, fill=COLOR_TREE_NEAR, outline="")
        for i in range(4):
            vx = 30 + i * 50
            vl = 120 + (i * 40) % 80
            self.canvas.create_line(vx, 80, vx, 80 + vl, fill="#2d6a4f", width=3)
            self.canvas.create_oval(vx - 10, 80 + vl, vx + 10, 100 + vl, fill="#3a8a5f", outline="")
        for i in range(4):
            vx = 820 + i * 45
            vl = 100 + (i * 35) % 70
            self.canvas.create_line(vx, 80, vx, 80 + vl, fill="#2d6a4f", width=3)
            self.canvas.create_oval(vx - 10, 80 + vl, vx + 10, 100 + vl, fill="#3a8a5f", outline="")

    def _draw_river(self):
        self.canvas.create_rectangle(0, 340, WINDOW_WIDTH, 395, fill="#1a5276", outline="")
        for i in range(20):
            wx = int((i * 60 - self.bg[5] * 2) % (WINDOW_WIDTH + 60) - 30)
            self.canvas.create_rectangle(wx, 345, wx + 30, 350, fill="#2e86c1", outline="")
            self.canvas.create_rectangle(wx + 15, 360, wx + 40, 364, fill="#3498db", outline="")
            self.canvas.create_rectangle(wx, 375, wx + 25, 379, fill="#2e86c1", outline="")

    def _draw_trees(self):
        for i in range(8):
            x = int((i * 180 - self.bg[2]) % (WINDOW_WIDTH + 180) - 90)
            self.canvas.create_oval(x, 180, x + 140, 280, fill=COLOR_TREE_FAR, outline="")
        for i in range(7):
            x = int((i * 160 - self.bg[3]) % (WINDOW_WIDTH + 160) - 80)
            self.canvas.create_rectangle(x + 70, 280, x + 82, 400, fill=COLOR_TRUNK, outline="")
            self.canvas.create_oval(x, 200, x + 150, 320, fill=COLOR_TREE_MID, outline="")
            self.canvas.create_oval(x + 20, 180, x + 130, 280, fill=COLOR_TREE_MID, outline="")
        for i in range(5):
            x = int((i * 220 - self.bg[4]) % (WINDOW_WIDTH + 220) - 110)
            self.canvas.create_rectangle(x + 95, 310, x + 115, 400, fill=COLOR_TRUNK, outline="")
            self.canvas.create_oval(x, 220, x + 200, 360, fill=COLOR_TREE_NEAR, outline="")
            self.canvas.create_oval(x + 30, 190, x + 170, 310, fill=COLOR_TREE_NEAR, outline="")
            self.canvas.create_oval(x + 60, 170, x + 140, 260, fill="#52b788", outline="")

    def _draw_jungle_floor(self):
        for i in range(12):
            x = int((i * 90 - self.bg[7]) % (WINDOW_WIDTH + 90) - 45)
            if x < 200 or x > 750:
                self.canvas.create_oval(x, 380, x + 60, 410, fill="#2d6a4f", outline="")
                self.canvas.create_oval(x + 10, 375, x + 50, 400, fill="#3a8a5f", outline="")
        for i in range(6):
            x = int((i * 180 - self.bg[7] * 1.5) % (WINDOW_WIDTH + 180) - 90)
            if x < 180 or x > 800:
                self.canvas.create_oval(x, 390, x + 35, 410, fill="#6c757d", outline="")
                self.canvas.create_oval(x + 5, 388, x + 15, 395, fill="#adb5bd", outline="")

    def _draw_road(self):
        self.canvas.create_rectangle(0, 400, WINDOW_WIDTH, WINDOW_HEIGHT, fill=COLOR_ROAD, outline="")
        self.canvas.create_rectangle(0, 395, WINDOW_WIDTH, 400, fill=COLOR_GRASS, outline="")
        for x in range(-60, WINDOW_WIDTH + 60, 60):
            gx = int(x - self.bg[7])
            self.canvas.create_rectangle(gx, 470, gx + 30, 475, fill=COLOR_ROAD_LINE, outline="")
            self.canvas.create_rectangle(gx, 560, gx + 30, 565, fill=COLOR_ROAD_LINE, outline="")
        self.canvas.create_line(400, 400, 400, WINDOW_HEIGHT, fill="#555", width=2, dash=(20, 10))
        self.canvas.create_line(600, 400, 600, WINDOW_HEIGHT, fill="#555", width=2, dash=(20, 10))

    def _draw_obstacles(self):
        for o in self.obstacles:
            x, y, w, h = int(o["x"]), int(o["y"]), o["w"], o["h"]
            if o["type"] == "log":
                self.canvas.create_rectangle(x, y, x + w, y + h, fill=COLOR_LOG, outline=COLOR_LOG_DK, width=2)
                self.canvas.create_oval(x - 5, y, x + 12, y + h, fill=COLOR_LOG, outline=COLOR_LOG_DK, width=2)
                self.canvas.create_oval(x + w - 12, y, x + w + 5, y + h, fill=COLOR_LOG, outline=COLOR_LOG_DK, width=2)
                for lx in range(x + 15, x + w, 20):
                    self.canvas.create_line(lx, y + 5, lx, y + h - 5, fill=COLOR_LOG_DK, width=1)
            else:
                self.canvas.create_oval(x, y, x + w, y + h, fill=COLOR_ROCK, outline="#495057")
                self.canvas.create_oval(x + 8, y + 5, x + 18, y + 12, fill="#adb5bd", outline="")

    def _draw_coins(self):
        for c in self.coins:
            x, y, r = int(c["x"]), int(c["y"]), c["r"]
            self.canvas.create_oval(x - r, y - r, x + r, y + r, fill=COLOR_COIN, outline=COLOR_COIN_DK, width=2)
            self.canvas.create_oval(x - r + 4, y - r + 4, x + r - 4, y + r - 4, fill=COLOR_COIN_DK, outline="")

    def _draw_player(self):
        sx = random.randint(-3, 3) if self.shake >0 else 0
        sy = random.randint(-3, 3) if self.shake >0 else 0
        x = int(self.player_x) + sx
        y = int(self.player_y) + sy
        head_y = y - 30
        self.canvas.create_oval(x + 6, head_y, x + 30, head_y + 24, fill=COLOR_SKIN, outline="")
        self.canvas.create_oval(x + 3, head_y - 5, x + 33, head_y + 10, fill=COLOR_HAIR, outline="")
        self.canvas.create_oval(x + 3, head_y, x + 12, head_y + 15, fill=COLOR_HAIR, outline="")
        self.canvas.create_oval(x + 11, head_y + 8, x + 15, head_y + 12, fill="black", outline="")
        self.canvas.create_oval(x + 20, head_y + 8, x + 24, head_y + 12, fill="black", outline="")
        self.canvas.create_arc(x + 13, head_y + 12, x + 24, head_y + 18, start=0, extent=-180, style="arc", fill="black", width=1)
        body_y = head_y + 22
        self.canvas.create_oval(x + 4, body_y, x + 32, body_y + 25, fill=COLOR_SHIRT, outline="")
        if self.anim_frame == 0:
            self.canvas.create_line(x + 8, body_y + 5, x - 2, body_y + 18, fill=COLOR_SKIN, width=5)
            self.canvas.create_line(x + 28, body_y + 5, x + 36, body_y + 12, fill=COLOR_SKIN, width=5)
            self.canvas.create_line(x + 12, body_y + 22, x + 5, body_y + 38, fill=COLOR_PANTS, width=6)
            self.canvas.create_line(x + 24, body_y + 22, x + 32, body_y + 35, fill=COLOR_PANTS, width=6)
            self.canvas.create_oval(x, body_y + 35, x + 12, body_y + 42, fill=COLOR_SHOES, outline="")
            self.canvas.create_oval(x + 28, body_y + 32, x + 40, body_y + 39, fill=COLOR_SHOES, outline="")
        else:
            self.canvas.create_line(x + 8, body_y + 5, x, body_y + 12, fill=COLOR_SKIN, width=5)
            self.canvas.create_line(x + 28, body_y + 5, x + 38, body_y + 18, fill=COLOR_SKIN, width=5)
            self.canvas.create_line(x + 12, body_y + 22, x + 18, body_y + 38, fill=COLOR_PANTS, width=6)
            self.canvas.create_line(x + 24, body_y + 22, x + 15, body_y + 35, fill=COLOR_PANTS, width=6)
            self.canvas.create_oval(x + 13, body_y + 35, x + 25, body_y + 42, fill=COLOR_SHOES, outline="")
            self.canvas.create_oval(x + 10, body_y + 32, x + 22, body_y + 39, fill=COLOR_SHOES, outline="")

    def _draw_hud(self):
        self.canvas.create_rectangle(0, 0, WINDOW_WIDTH, 40, fill=COLOR_HUD, outline="")
        self.canvas.create_text(20, 20, text=f"SCORE: {self.score}", anchor="w", font=("Helvetica", 16, "bold"), fill=COLOR_TITLE)
        self.canvas.create_text(WINDOW_WIDTH // 2, 20, text=f"COINS: {self.coin_count}", font=("Helvetica", 16, "bold"), fill=COLOR_COIN)
        self.canvas.create_text(WINDOW_WIDTH - 20, 20, text=f"SPEED: {self.speed}", anchor="e", font=("Helvetica", 14, "bold"), fill=COLOR_TITLE)
        lane_name = ["LEFT", "CENTER", "RIGHT"][self.current_lane]
        self.canvas.create_text(WINDOW_WIDTH // 2, 55, text=f"Lane: {lane_name}", font=("Helvetica", 12), fill="#b8c5d6")

    def _spawn_coin_pattern(self):
        pt = random.choice(["line", "line", "curve", "zigzag"])
        if pt == "line":
            lane = random.randint(0, 2)
            for i in range(random.randint(5, 8)):
                self.coins.append({"x": LANE_X[lane], "y": -50 - i * 45, "r": 12, "lane": lane})
        elif pt == "curve":
            sl = random.randint(0, 2)
            el = random.randint(0, 2)
            if sl == el:
                el = (el + 1) % 3
            for i in range(7):
                t = i / 6.0
                lane = min(2, max(0, int(round(sl + (el - sl) * t))))
                self.coins.append({"x": LANE_X[lane], "y": -50 - i * 45, "r": 12, "lane": lane})
        elif pt == "zigzag":
            l1 = random.randint(0, 2)
            l2 = (l1 + 1) % 3
            for i in range(8):
                lane = l1 if i % 2 == 0 else l2
                self.coins.append({"x": LANE_X[lane], "y": -50 - i * 45, "r": 12, "lane": lane})

    def _draw_cave(self):
        ca = 1.0 - self.cave_progress
        if ca < 0.01:
            return
        stip = "gray75" if ca > 0.6 else "gray50" if ca > 0.3 else "gray25"
        self.canvas.create_rectangle(0, 0, WINDOW_WIDTH, WINDOW_HEIGHT, fill="#0a0a1a", stipple=stip)
        wall_w = int(200 * ca)
        if wall_w > 10:
            self.canvas.create_polygon(0, 0, wall_w, 50, wall_w, 350, 0, 400, fill="#2a2a3e", outline="")
            self.canvas.create_polygon(0, 400, wall_w, 350, wall_w, 400, fill="#2a2a3e", outline="")
            self.canvas.create_polygon(WINDOW_WIDTH, 0, WINDOW_WIDTH - wall_w, 50, WINDOW_WIDTH - wall_w, 350, WINDOW_WIDTH, 400, fill="#2a2a3e", outline="")
            self.canvas.create_polygon(WINDOW_WIDTH, 400, WINDOW_WIDTH - wall_w, 350, WINDOW_WIDTH - wall_w, 400, fill="#2a2a3e", outline="")
        if ca > 0.4:
            for i in range(5):
                x = 250 + i * 120
                h = int((50 + (i * 20) % 40) * ca)
                self.canvas.create_polygon(x - 18, 0, x + 18, 0, x, h, fill="#3a3a4e", outline="")
            for i in range(4):
                x = 280 + i * 150
                h = int((35 + (i * 15) % 25) * ca)
                self.canvas.create_polygon(x - 12, 400, x + 12, 400, x, 400 - h, fill="#3a3a4e", outline="")
        if ca > 0.2:
            for i in range(4):
                x = 120 + i * 250
                self.canvas.create_oval(x - 10, 340, x + 10, 365, fill="#4ecdc4", outline="")
                self.canvas.create_oval(x - 5, 345, x + 5, 360, fill="#7fdbff", outline="")

    def _draw_lighting(self):
        if self.cave_progress > 0.3:
            for i in range(4):
                x = 150 + i * 200
                self.canvas.create_polygon(x, 0, x + 40, 0, x + 80, 200, x + 20, 200, fill="#fff8dc", stipple="gray25")
        ca = 1.0 - self.cave_progress
        if ca > 0.3:
            for i in range(3):
                x = 200 + i * 300
                self.canvas.create_oval(x - 60, 300, x + 60, 400, fill="#4ecdc4", stipple="gray25", outline="")

    def _draw_pickup_effects(self):
        for ef in self.pickup_effects:
            x = int(ef["x"])
            y = int(ef["y"])
            r = int(ef["r"])
            self.canvas.create_oval(x - r, y - r, x + r, y + r, outline="#ffd700", width=2)
            if ef["alpha"] > 0.3:
                self.canvas.create_text(x, y, text="+1", font=("Helvetica", 12, "bold"), fill="#ffd700")


def main():
    root = tk.Tk()
    root.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")
    JungleDash(root)
    root.mainloop()


if __name__ == "__main__":
    main()
