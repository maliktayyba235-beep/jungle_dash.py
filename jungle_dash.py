import tkinter as tk
import random

WINDOW_WIDTH = 1000
WINDOW_HEIGHT = 600
GROUND_HEIGHT = 80
GROUND_Y = WINDOW_HEIGHT - GROUND_HEIGHT
FPS_MS = 30

COLOR_SKY_TOP = "#0d1b3e"
COLOR_SKY_MID = "#1e4d6b"
COLOR_SKY_BOTTOM = "#5a8c9c"
COLOR_MTN_FAR = "#2d4a5a"
COLOR_MTN_NEAR = "#1a3d2e"
COLOR_CANOPY_FAR = "#1a4d2e"
COLOR_CANOPY_MID = "#2d6a4f"
COLOR_CANOPY_NEAR = "#3a8a5f"
COLOR_TREE_TRUNK = "#5d4037"
COLOR_TREE_LIGHT = "#4caf50"
COLOR_GROUND_TOP = "#3d2b1f"
COLOR_GROUND_BOTTOM = "#2a1a0f"
COLOR_GRASS = "#52b788"
COLOR_GRASS_DARK = "#2d6a4f"
COLOR_SKIN = "#f5c89e"
COLOR_HAIR = "#4a2c2a"
COLOR_SHIRT = "#e63946"
COLOR_PANTS = "#1d3557"
COLOR_SHOES = "#2a2a2a"
COLOR_TITLE = "#f1faee"
COLOR_BTN_BG = "#2d6a4f"
COLOR_BTN_ACTIVE = "#40916c"
COLOR_BTN_TEXT = "#f1faee"
COLOR_PANEL_BG = "#1a2a3a"
COLOR_HUD_BG = "#0d1b2a"
COLOR_COIN = "#ffd700"
COLOR_COIN_DARK = "#b8860b"
COLOR_SHIELD = "#00b4d8"
COLOR_OBSTACLE_ROCK = "#6c757d"
COLOR_OBSTACLE_LOG = "#8b4513"
COLOR_LIFE = "#e63946"


class JungleDash:
    def __init__(self, root):
        self.root = root
        self.root.title("Jungle Dash")
        self.root.configure(bg=COLOR_SKY_BOTTOM)
        self.root.resizable(False, False)

        self.state = "MENU"
        self.game_loop_id = None

        self.canvas = tk.Canvas(
            self.root, width=WINDOW_WIDTH, height=WINDOW_HEIGHT,
            bg=COLOR_SKY_BOTTOM, highlightthickness=0,
        )
        self.menu_frame = tk.Frame(self.root, bg=COLOR_SKY_BOTTOM)
        self.howto_frame = tk.Frame(self.root, bg=COLOR_SKY_BOTTOM)
        self.game_over_frame = tk.Frame(self.root, bg=COLOR_SKY_BOTTOM)

        self._build_menu()
        self._build_how_to_play()
        self._build_game_over()
        self.show_menu()

        self.root.bind("<space>", lambda e: self.on_jump())
        self.root.bind("<Up>", lambda e: self.on_jump())
        self.root.bind("<Down>", lambda e: self.on_slide())
        self.root.bind("<p>", lambda e: self.toggle_pause())
        self.root.bind("<P>", lambda e: self.toggle_pause())
        self.root.bind("<Return>", lambda e: self.on_enter())
        self.root.bind("<Escape>", lambda e: self.show_menu())

    def _make_btn(self, parent, text, command, bg=COLOR_BTN_BG, fg=COLOR_BTN_TEXT, size=16, width=18):
        return tk.Button(
            parent, text=text, font=("Helvetica", size, "bold"), width=width,
            bg=bg, fg=fg, activebackground=COLOR_BTN_ACTIVE, activeforeground=fg,
            relief="flat", cursor="hand2", command=command,
        )

    def _build_menu(self):
        tk.Label(self.menu_frame, text="JUNGLE DASH", font=("Helvetica", 52, "bold"), bg=COLOR_SKY_BOTTOM, fg=COLOR_TITLE).pack(pady=(100, 5))
        tk.Label(self.menu_frame, text="RUN \\u2022 JUMP \\u2022 SURVIVE", font=("Helvetica", 18), bg=COLOR_SKY_BOTTOM, fg=COLOR_GRASS).pack(pady=(0, 60))
        self._make_btn(self.menu_frame, "START GAME", self.start_game, size=20).pack(pady=8)
        self._make_btn(self.menu_frame, "HOW TO PLAY", self.show_how_to_play, bg="#6f4e37", size=16).pack(pady=8)
        self._make_btn(self.menu_frame, "EXIT", self.root.quit, bg="#8b2c2c", size=16).pack(pady=8)
        tk.Label(self.menu_frame, text="Press ENTER to start  |  ESC to return to menu", font=("Helvetica", 11), bg=COLOR_SKY_BOTTOM, fg="#b8c5d6").pack(pady=(40, 0))

    def _build_how_to_play(self):
        tk.Label(self.howto_frame, text="HOW TO PLAY", font=("Helvetica", 40, "bold"), bg=COLOR_SKY_BOTTOM, fg=COLOR_TITLE).pack(pady=(60, 30))
        for key, action in [("SPACE / UP ARROW", "Jump"), ("DOWN ARROW", "Slide"), ("P", "Pause / Resume")]:
            row = tk.Frame(self.howto_frame, bg=COLOR_SKY_BOTTOM)
            row.pack(pady=6)
            tk.Label(row, text=key, font=("Helvetica", 16, "bold"), width=20, bg=COLOR_PANEL_BG, fg=COLOR_GRASS).pack(side="left", padx=10)
            tk.Label(row, text=action, font=("Helvetica", 16), width=12, bg=COLOR_PANEL_BG, fg=COLOR_TITLE).pack(side="left", padx=10)
        tk.Label(self.howto_frame, text="", font=("Helvetica", 14), bg=COLOR_SKY_BOTTOM, fg="#b8c5d6").pack(pady=(20, 5))
        tk.Label(self.howto_frame, text="Click START GAME to begin.", font=("Helvetica", 14), bg=COLOR_SKY_BOTTOM, fg="#b8c5d6").pack(pady=2)
        tk.Label(self.howto_frame, text="The girl runs automatically.", font=("Helvetica", 14), bg=COLOR_SKY_BOTTOM, fg="#b8c5d6").pack(pady=2)
        tk.Label(self.howto_frame, text="Use SPACE or UP to jump.", font=("Helvetica", 14), bg=COLOR_SKY_BOTTOM, fg="#b8c5d6").pack(pady=2)
        tk.Label(self.howto_frame, text="Use DOWN to slide.", font=("Helvetica", 14), bg=COLOR_SKY_BOTTOM, fg="#b8c5d6").pack(pady=2)
        self._make_btn(self.howto_frame, "BACK TO MENU", self.show_menu, bg="#6f4e37", size=16).pack(pady=10)

    def _build_game_over(self):
        tk.Label(self.game_over_frame, text="GAME OVER", font=("Helvetica", 48, "bold"), bg=COLOR_SKY_BOTTOM, fg=COLOR_LIFE).pack(pady=(100, 20))
        self.go_score_label = tk.Label(self.game_over_frame, text="FINAL SCORE: 0", font=("Helvetica", 22, "bold"), bg=COLOR_SKY_BOTTOM, fg=COLOR_TITLE)
        self.go_score_label.pack(pady=8)
        self.go_coins_label = tk.Label(self.game_over_frame, text="COINS: 0", font=("Helvetica", 20), bg=COLOR_SKY_BOTTOM, fg=COLOR_COIN)
        self.go_coins_label.pack(pady=8)
        self._make_btn(self.game_over_frame, "PLAY AGAIN", self.start_game, size=18).pack(pady=15)
        self._make_btn(self.game_over_frame, "MAIN MENU", self.show_menu, bg="#6f4e37", size=16).pack(pady=8)

    def show_menu(self):
        self._stop_game_loop()
        self.state = "MENU"
        self.canvas.pack_forget()
        self.howto_frame.place_forget()
        self.game_over_frame.place_forget()
        self.menu_frame.place(x=0, y=0, width=WINDOW_WIDTH, height=WINDOW_HEIGHT)

    def show_how_to_play(self):
        self.state = "HOWTO"
        self.canvas.pack_forget()
        self.menu_frame.place_forget()
        self.game_over_frame.place_forget()
        self.howto_frame.place(x=0, y=0, width=WINDOW_WIDTH, height=WINDOW_HEIGHT)

    def start_game(self):
        self._stop_game_loop()
        self.state = "PLAYING"
        self.player_x = 150
        self.player_y = GROUND_Y - 60
        self.player_w = 36
        self.player_h = 60
        self.player_vy = 0
        self.on_ground = True
        self.sliding = False
        self.slide_timer = 0
        self.anim_frame = 0
        self.anim_counter = 0
        self.shield_active = False
        self.score = 0
        self.coins_collected = 0
        self.lives = 3
        self.speed = 6
        self.paused = False
        self.collision_cooldown = 0
        self.bg_clouds = 0
        self.bg_mtn = 0
        self.bg_far = 0
        self.bg_mid = 0
        self.bg_near = 0
        self.bg_ground = 0
        self.obstacles = []
        self.coin_list = []
        self.shields = []
        self.obstacle_timer = 0
        self.coin_timer = 0
        self.shield_timer = 0
        self.menu_frame.place_forget()
        self.howto_frame.place_forget()
        self.game_over_frame.place_forget()
        self.canvas.pack()
        self.game_loop()

    def show_game_over(self):
        self._stop_game_loop()
        self.state = "GAMEOVER"
        self.go_score_label.config(text=f"FINAL SCORE: {self.score}")
        self.go_coins_label.config(text=f"COINS: {self.coins_collected}")
        self.game_over_frame.place(x=0, y=0, width=WINDOW_WIDTH, height=WINDOW_HEIGHT)

    def _stop_game_loop(self):
        if self.game_loop_id is not None:
            self.root.after_cancel(self.game_loop_id)
            self.game_loop_id = None

    def on_enter(self):
        if self.state == "MENU" or self.state == "GAMEOVER":
            self.start_game()

    def on_jump(self):
        if self.state == "PLAYING" and not self.paused and self.on_ground:
            self.player_vy = -15
            self.on_ground = False
            self.sliding = False

    def on_slide(self):
        if self.state == "PLAYING" and not self.paused and self.on_ground:
            self.sliding = True
            self.slide_timer = 30

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
        self.draw_scene()
        self.game_loop_id = self.root.after(FPS_MS, self.game_loop)

    def update(self):
        self.player_vy += 0.8
        self.player_y += self.player_vy
        if self.player_y >= GROUND_Y - self.player_h:
            self.player_y = GROUND_Y - self.player_h
            self.player_vy = 0
            self.on_ground = True
        if self.sliding:
            self.slide_timer -= 1
            if self.slide_timer <= 0:
                self.sliding = False
        self.anim_counter += 1
        if self.anim_counter >= 5:
            self.anim_counter = 0
            self.anim_frame = 1 - self.anim_frame
        self.score += 1
        self.speed = 6 + self.score // 500
        if self.collision_cooldown > 0:
            self.collision_cooldown -= 1
        self.bg_clouds = (self.bg_clouds + self.speed * 0.2) % 400
        self.bg_mtn = (self.bg_mtn + self.speed * 0.3) % 350
        self.bg_far = (self.bg_far + self.speed * 0.5) % 200
        self.bg_mid = (self.bg_mid + self.speed * 0.7) % 160
        self.bg_near = (self.bg_near + self.speed * 0.9) % 120
        self.bg_ground = (self.bg_ground + self.speed) % 40
        self.obstacle_timer += 1
        if self.obstacle_timer > 60 + random.randint(0, 40):
            self.obstacle_timer = 0
            self._spawn_obstacle()
        self.coin_timer += 1
        if self.coin_timer > 40 + random.randint(0, 30):
            self.coin_timer = 0
            self._spawn_coin()
        self.shield_timer += 1
        if self.shield_timer > 500 + random.randint(0, 300):
            self.shield_timer = 0
            self._spawn_shield()
        for obs in self.obstacles:
            obs["x"] -= self.speed
        self.obstacles = [o for o in self.obstacles if o["x"] > -100]
        for coin in self.coin_list:
            coin["x"] -= self.speed
        self.coin_list = [c for c in self.coin_list if c["x"] > -50]
        for s in self.shields:
            s["x"] -= self.speed
        self.shields = [s for s in self.shields if s["x"] > -50]
        self._check_collisions()

    def _spawn_obstacle(self):
        obs_type = random.choice(["rock", "log", "branch"])
        if obs_type == "rock":
            self.obstacles.append({"x": WINDOW_WIDTH + 50, "y": GROUND_Y - 35, "w": 45, "h": 35, "type": "rock"})
        elif obs_type == "log":
            self.obstacles.append({"x": WINDOW_WIDTH + 50, "y": GROUND_Y - 25, "w": 70, "h": 25, "type": "log"})
        else:
            self.obstacles.append({"x": WINDOW_WIDTH + 50, "y": GROUND_Y - 55, "w": 60, "h": 20, "type": "branch"})

    def _spawn_coin(self):
        y = GROUND_Y - 80 - random.randint(0, 60)
        self.coin_list.append({"x": WINDOW_WIDTH + 50, "y": y, "r": 12})

    def _spawn_shield(self):
        y = GROUND_Y - 80 - random.randint(0, 40)
        self.shields.append({"x": WINDOW_WIDTH + 50, "y": y, "r": 18})

    def _check_collisions(self):
        px = self.player_x
        pw = self.player_w
        if self.sliding:
            py = GROUND_Y - 30
            ph = 30
        else:
            py = self.player_y
            ph = self.player_h
        for obs in self.obstacles:
            if self._rect_overlap(px, py, pw, ph, obs["x"], obs["y"], obs["w"], obs["h"]):
                if self.collision_cooldown <= 0:
                    if self.shield_active:
                        self.shield_active = False
                        self.collision_cooldown = 30
                    else:
                        self.lives -= 1
                        self.collision_cooldown = 60
                        if self.lives <= 0:
                            self.show_game_over()
                            return
                break
        collected = []
        for i, coin in enumerate(self.coin_list):
            if self._rect_overlap(px, py, pw, ph, coin["x"] - coin["r"], coin["y"] - coin["r"], coin["r"] * 2, coin["r"] * 2):
                self.coins_collected += 1
                collected.append(i)
        if collected:
            self.coin_list = [c for i, c in enumerate(self.coin_list) if i not in collected]
        collected_s = []
        for i, s in enumerate(self.shields):
            if self._rect_overlap(px, py, pw, ph, s["x"] - s["r"], s["y"] - s["r"], s["r"] * 2, s["r"] * 2):
                self.shield_active = True
                collected_s.append(i)
        if collected_s:
            self.shields = [s for i, s in enumerate(self.shields) if i not in collected_s]

    def _rect_overlap(self, x1, y1, w1, h1, x2, y2, w2, h2):
        return x1 < x2 + w2 and x1 + w1 > x2 and y1 < y2 + h2 and y1 + h1 > y2

    def draw_scene(self):
        self.canvas.delete("all")
        self._draw_sky()
        self._draw_clouds()
        self._draw_mountains()
        self._draw_canopy_layers()
        self._draw_ground()
        self._draw_obstacles()
        self._draw_coins()
        self._draw_shields()
        self._draw_player()
        self._draw_hud()
        if self.collision_cooldown > 40:
            self.canvas.create_rectangle(2, 2, WINDOW_WIDTH - 2, WINDOW_HEIGHT - 2, outline="red", width=6)
        if self.paused:
            self._draw_pause_overlay()

    def _draw_sky(self):
        for y in range(0, GROUND_Y, 4):
            ratio = y / GROUND_Y
            if ratio < 0.5:
                r = int(0x0d + (0x1e - 0x0d) * (ratio * 2))
                g = int(0x1b + (0x4d - 0x1b) * (ratio * 2))
                b = int(0x3e + (0x6b - 0x3e) * (ratio * 2))
            else:
                r = int(0x1e + (0x5a - 0x1e) * ((ratio - 0.5) * 2))
                g = int(0x4d + (0x8c - 0x4d) * ((ratio - 0.5) * 2))
                b = int(0x6b + (0x9c - 0x6b) * ((ratio - 0.5) * 2))
            self.canvas.create_line(0, y, WINDOW_WIDTH, y, fill=f"#{r:02x}{g:02x}{b:02x}")

    def _draw_clouds(self):
        for i in range(5):
            x = (i * 250 - self.bg_clouds) % (WINDOW_WIDTH + 200) - 100
            y = 40 + i * 25
            self.canvas.create_oval(x, y, x + 80, y + 30, fill="#e8f0f5", outline="")

    def _draw_mountains(self):
        for i in range(4):
            x = (i * 300 - self.bg_mtn) % (WINDOW_WIDTH + 300) - 150
            self.canvas.create_polygon(x, GROUND_Y, x + 150, GROUND_Y - 200, x + 300, GROUND_Y, fill=COLOR_MTN_FAR, outline="")
        for i in range(3):
            x = (i * 350 - self.bg_mtn * 1.3) % (WINDOW_WIDTH + 350) - 175
            self.canvas.create_polygon(x, GROUND_Y, x + 175, GROUND_Y - 150, x + 350, GROUND_Y, fill=COLOR_MTN_NEAR, outline="")

    def _draw_canopy_layers(self):
        for i in range(8):
            x = (i * 200 - self.bg_far) % (WINDOW_WIDTH + 200) - 100
            y = GROUND_Y - 180
            self.canvas.create_oval(x, y, x + 120, y + 80, fill=COLOR_CANOPY_FAR, outline="")
        for i in range(7):
            x = (i * 160 - self.bg_mid) % (WINDOW_WIDTH + 160) - 80
            y = GROUND_Y - 140
            self.canvas.create_oval(x, y, x + 100, y + 70, fill=COLOR_CANOPY_MID, outline="")
            self.canvas.create_rectangle(x + 45, y + 50, x + 55, GROUND_Y, fill=COLOR_TREE_TRUNK, outline="")
        for i in range(6):
            x = (i * 120 - self.bg_near) % (WINDOW_WIDTH + 120) - 60
            y = GROUND_Y - 100
            self.canvas.create_oval(x, y, x + 80, y + 60, fill=COLOR_CANOPY_NEAR, outline="")

    def _draw_ground(self):
        self.canvas.create_rectangle(0, GROUND_Y, WINDOW_WIDTH, WINDOW_HEIGHT, fill=COLOR_GROUND_TOP, outline="")
        self.canvas.create_rectangle(0, GROUND_Y + 30, WINDOW_WIDTH, WINDOW_HEIGHT, fill=COLOR_GROUND_BOTTOM, outline="")
        self.canvas.create_rectangle(0, GROUND_Y - 5, WINDOW_WIDTH, GROUND_Y, fill=COLOR_GRASS, outline="")
        for x in range(-40, WINDOW_WIDTH + 40, 20):
            gx = x - self.bg_ground
            self.canvas.create_line(gx, GROUND_Y - 5, gx + 8, GROUND_Y - 15, fill=COLOR_GRASS_DARK, width=2)

    def _draw_obstacles(self):
        for obs in self.obstacles:
            x, y, w, h = obs["x"], obs["y"], obs["w"], obs["h"]
            if obs["type"] == "rock":
                self.canvas.create_oval(x, y, x + w, y + h, fill=COLOR_OBSTACLE_ROCK, outline="#495057")
                self.canvas.create_oval(x + 8, y + 5, x + 18, y + 12, fill="#adb5bd", outline="")
            elif obs["type"] == "log":
                self.canvas.create_rectangle(x, y, x + w, y + h, fill=COLOR_OBSTACLE_LOG, outline="#5d3a1a")
                self.canvas.create_oval(x - 5, y, x + 10, y + h, fill=COLOR_OBSTACLE_LOG, outline="#5d3a1a")
                self.canvas.create_oval(x + w - 5, y, x + w + 5, y + h, fill=COLOR_OBSTACLE_LOG, outline="#5d3a1a")
            elif obs["type"] == "branch":
                self.canvas.create_line(x, y + h, x + w, y, fill=COLOR_TREE_TRUNK, width=8)
                for lx in range(0, int(w), 15):
                    ly = y + h - (lx * h / w)
                    self.canvas.create_line(x + lx, ly, x + lx + 10, ly - 15, fill=COLOR_TREE_LIGHT, width=3)

    def _draw_coins(self):
        for coin in self.coin_list:
            x, y, r = coin["x"], coin["y"], coin["r"]
            self.canvas.create_oval(x - r, y - r, x + r, y + r, fill=COLOR_COIN, outline=COLOR_COIN_DARK, width=2)
            self.canvas.create_oval(x - r + 4, y - r + 4, x + r - 4, y + r - 4, fill=COLOR_COIN_DARK, outline="")

    def _draw_shields(self):
        for s in self.shields:
            x, y, r = s["x"], s["y"], s["r"]
            self.canvas.create_oval(x - r, y - r, x + r, y + r, fill=COLOR_SHIELD, outline="#0096c7", width=2)
            self.canvas.create_text(x, y, text="S", font=("Helvetica", 12, "bold"), fill="white")

    def _draw_player(self):
        x = self.player_x
        y = self.player_y
        w = self.player_w
        h = self.player_h
        if self.sliding:
            sy = GROUND_Y - 30
            self.canvas.create_oval(x, sy, x + 50, sy + 25, fill=COLOR_SHIRT, outline="")
            self.canvas.create_oval(x + 40, sy - 5, x + 55, sy + 15, fill=COLOR_SKIN, outline="")
            self.canvas.create_oval(x + 38, sy - 8, x + 58, sy + 2, fill=COLOR_HAIR, outline="")
            self.canvas.create_oval(x + 5, sy + 15, x + 15, sy + 25, fill=COLOR_SHOES, outline="")
            self.canvas.create_line(x + 20, sy + 12, x + 40, sy + 5, fill=COLOR_SKIN, width=4)
        else:
            head_y = y
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
        if self.shield_active:
            self.canvas.create_oval(x - 8, y - 8, x + w + 8, y + h + 8, outline=COLOR_SHIELD, width=3, dash=(4, 2))

    def _draw_hud(self):
        self.canvas.create_rectangle(0, 0, WINDOW_WIDTH, 45, fill=COLOR_HUD_BG, outline="")
        self.canvas.create_text(20, 22, text=f"SCORE: {self.score}", anchor="w", font=("Helvetica", 16, "bold"), fill=COLOR_TITLE)
        self.canvas.create_text(WINDOW_WIDTH // 2, 22, text=f"COINS: {self.coins_collected}", font=("Helvetica", 16, "bold"), fill=COLOR_COIN)
        self.canvas.create_text(WINDOW_WIDTH - 170, 22, text="LIVES:", anchor="e", font=("Helvetica", 14, "bold"), fill=COLOR_TITLE)
        for i in range(3):
            color = COLOR_LIFE if i < self.lives else "#444444"
            lx = WINDOW_WIDTH - 130 + i * 35
            self.canvas.create_oval(lx, 14, lx + 18, 32, fill=color, outline="")

    def _draw_pause_overlay(self):
        self.canvas.create_rectangle(0, 0, WINDOW_WIDTH, WINDOW_HEIGHT, fill="#000000", stipple="gray50")
        self.canvas.create_text(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2, text="PAUSED", font=("Helvetica", 52, "bold"), fill=COLOR_TITLE)
        self.canvas.create_text(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 60, text="Press P to resume", font=("Helvetica", 16), fill="#b8c5d6")


def main():
    root = tk.Tk()
    root.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")
    JungleDash(root)
    root.mainloop()


if __name__ == "__main__":
    main()
