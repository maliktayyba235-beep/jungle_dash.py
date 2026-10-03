import math
import json
import random
import sys
from ursina import *

LANE_X = [-2.5, 0, 2.5]
SETTINGS_FILE = "jungle_dash_3d_settings.json"
SPAWN_Z = -120
DESPAWN_Z = 15
ROAD_WIDTH = 9
CAVE_END_SCORE = 800

C_SKIN = color.rgb32(245, 200, 158)
C_HAIR = color.rgb32(74, 44, 42)
C_SHIRT = color.rgb32(230, 57, 70)
C_PANTS = color.rgb32(29, 53, 87)
C_SHOES = color.rgb32(42, 42, 42)
C_ROAD = color.rgb32(100, 100, 100)
C_GRASS = color.rgb32(82, 183, 136)
C_COIN = color.rgb32(255, 215, 0)
C_LOG = color.rgb32(139, 69, 19)
C_ROCK = color.rgb32(108, 117, 125)
C_TRUNK = color.rgb32(93, 64, 55)
C_LEAF = color.rgb32(45, 106, 79)
C_CAVE = color.rgb32(42, 42, 62)
C_CRYSTAL = color.rgb32(78, 205, 196)

def load_settings():
    try:
        with open(SETTINGS_FILE, "r") as f:
            return json.load(f)
    except:
        return {"tutorial_seen": False}

def save_settings(s):
    try:
        with open(SETTINGS_FILE, "w") as f:
            json.dump(s, f)
    except:
        pass

class Runner:
    def __init__(self):
        self.entity = Entity()
        self.head = Entity(parent=self.entity, model='sphere', scale=(0.35,0.4,0.35), y=1.7, color=C_SKIN)
        self.hair = Entity(parent=self.entity, model='sphere', scale=(0.42,0.28,0.42), y=1.85, color=C_HAIR)
        self.body = Entity(parent=self.entity, model='cube', scale=(0.5,0.7,0.25), y=1.05, color=C_SHIRT)
        self.arm_l = Entity(parent=self.entity, model='cube', scale=(0.12,0.55,0.12), position=(-0.35,1.15,0), color=C_SKIN)
        self.arm_r = Entity(parent=self.entity, model='cube', scale=(0.12,0.55,0.12), position=(0.35,1.15,0), color=C_SKIN)
        self.leg_l = Entity(parent=self.entity, model='cube', scale=(0.18,0.65,0.18), position=(-0.15,0.35,0), color=C_PANTS)
        self.leg_r = Entity(parent=self.entity, model='cube', scale=(0.18,0.65,0.18), position=(0.15,0.35,0), color=C_PANTS)
        self.shoe_l = Entity(parent=self.entity, model='cube', scale=(0.22,0.1,0.32), position=(-0.15,0.05,0.05), color=C_SHOES)
        self.shoe_r = Entity(parent=self.entity, model='cube', scale=(0.22,0.1,0.32), position=(0.15,0.05,0.05), color=C_SHOES)
        self.anim_time = 0
        self.target_x = 0
        self.jumping = False
        self.jump_vel = 0
        self.y_offset = 0

    def set_lane(self, lane):
        self.target_x = LANE_X[lane]

    def jump(self):
        if not self.jumping:
            self.jumping = True
            self.jump_vel = 9

    def update_runner(self, dt, speed):
        self.anim_time += dt * speed * 0.6
        swing = math.sin(self.anim_time * 9)
        if not self.jumping:
            self.arm_l.rotation_x = swing * 55
            self.arm_r.rotation_x = -swing * 55
            self.leg_l.rotation_x = -swing * 55
            self.leg_r.rotation_x = swing * 55
        else:
            self.arm_l.rotation_x = -45
            self.arm_r.rotation_x = -45
            self.leg_l.rotation_x = 35
            self.leg_r.rotation_x = -25
        self.entity.x += (self.target_x - self.entity.x) * dt * 12
        if self.jumping:
            self.jump_vel -= 28 * dt
            self.y_offset += self.jump_vel * dt
            if self.y_offset <= 0:
                self.y_offset = 0
                self.jumping = False
                self.jump_vel = 0
        self.entity.y = self.y_offset

class JungleDash3D:
    def __init__(self):
        self.app = Ursina(title="Jungle Dash 3D", fullscreen=False, size=(1280, 720))
        self.app.exit_on_escape = False
        self.settings = load_settings()
        self.state = "MENU"
        self.sun = DirectionalLight(color=color.white)
        self.sun.look_at(Vec3(1, -1, -1))
        self.ambient = AmbientLight(color=color.rgba32(80, 80, 100, 255))
        scene.fog_density = 0.008
        scene.fog_color = color.rgb32(135, 206, 235)
        camera.position = (0, 8, 15)
        camera.rotation_x = 25
        self.runner = Runner()
        self.runner.entity.visible = False
        self.current_lane = 1
        self.score = 0
        self.coin_count = 0
        self.speed = 8
        self.cave_progress = 0
        self.paused = False
        scene.fog_density = 0.006
        scene.fog_color = color.rgb32(100, 130, 160)
        self.coins = []
        self.obstacles = []
        self.env_objects = []
        self.road_marks = []
        self.pickup_effects = []
        self.coin_timer = 0
        self.obs_timer = 0
        self.env_timer = 0
        self.mark_timer = 0
        self.road = Entity(model='plane', scale=(ROAD_WIDTH, 1, 250), position=(0, 0, -100), color=C_ROAD)
        self.road.collider = None
        self.grass_l = Entity(model='plane', scale=(30, 1, 250), position=(-20, -0.01, -100), color=C_GRASS)
        self.grass_l.collider = None
        self.grass_r = Entity(model='plane', scale=(30, 1, 250), position=(20, -0.01, -100), color=C_GRASS)
        self.grass_r.collider = None
        self._build_ui()

    def _build_ui(self):
        self.ui_elements = []
        self.score_text = Text(text="SCORE: 0", position=(-0.85, 0.45), scale=1.5, color=color.white, visible=False)
        self.coin_text = Text(text="COINS: 0", position=(-0.2, 0.45), scale=1.5, color=color.yellow, visible=False)
        self.speed_text = Text(text="SPEED: 8", position=(0.5, 0.45), scale=1.3, color=color.white, visible=False)
        self.ui_elements.extend([self.score_text, self.coin_text, self.speed_text])
        self.menu_title = Text(text="JUNGLE DASH 3D", position=(-0.3, 0.3), scale=3, color=color.white)
        self.menu_sub = Text(text="RUN JUMP SURVIVE", position=(-0.16, 0.2), scale=1.5, color=color.green)
        self.btn_start = Button(text="START GAME", position=(0, 0.05), scale=(0.3, 0.08), color=color.green)
        self.btn_howto = Button(text="HOW TO PLAY", position=(0, -0.05), scale=(0.3, 0.08), color=color.brown)
        self.btn_exit = Button(text="EXIT", position=(0, -0.15), scale=(0.3, 0.08), color=color.red)
        self.btn_start.on_click = self.start_game
        self.btn_howto.on_click = self.show_howto
        self.btn_exit.on_click = sys.exit
        self.ui_elements.extend([self.menu_title, self.menu_sub, self.btn_start, self.btn_howto, self.btn_exit])
        self.howto_title = Text(text="HOW TO PLAY", position=(-0.18, 0.35), scale=2.5, color=color.white, visible=False)
        self.howto_lines = []
        ht = [("LEFT/RIGHT or A/D", "Switch lane"), ("SPACE or UP", "Jump"), ("P", "Pause/Resume"), ("ESC", "Back to menu")]
        for i, (k, a) in enumerate(ht):
            t1 = Text(text=k, position=(-0.4, 0.15 - i * 0.1), scale=1.2, color=color.green, visible=False)
            t2 = Text(text=a, position=(0.1, 0.15 - i * 0.1), scale=1.2, color=color.white, visible=False)
            self.howto_lines.extend([t1, t2])
        for line in ["Collect coins for score", "Avoid obstacles", "Girl runs automatically", "One collision = Game Over"]:
            t = Text(text=line, position=(-0.2, -0.25 - self.howto_lines.__len__() * 0), scale=1, color=color.light_gray, visible=False)
            self.howto_lines.append(t)
        self.btn_howto_back = Button(text="BACK", position=(0, -0.4), scale=(0.2, 0.07), color=color.brown, visible=False)
        self.btn_howto_back.on_click = self.show_menu
        self.ui_elements.extend([self.howto_title] + self.howto_lines + [self.btn_howto_back])
        self.go_title = Text(text="GAME OVER", position=(-0.15, 0.3), scale=3, color=color.red, visible=False)
        self.go_sub = Text(text="YOU ARE OUT!", position=(-0.12, 0.2), scale=2, color=color.white, visible=False)
        self.go_score = Text(text="SCORE: 0", position=(-0.1, 0.08), scale=1.5, color=color.white, visible=False)
        self.go_coins = Text(text="COINS: 0", position=(-0.1, 0.0), scale=1.5, color=color.yellow, visible=False)
        self.btn_again = Button(text="PLAY AGAIN", position=(0, -0.15), scale=(0.3, 0.08), color=color.green, visible=False)
        self.btn_menu = Button(text="MAIN MENU", position=(0, -0.25), scale=(0.3, 0.08), color=color.brown, visible=False)
        self.btn_again.on_click = self.start_game
        self.btn_menu.on_click = self.show_menu
        self.ui_elements.extend([self.go_title, self.go_sub, self.go_score, self.go_coins, self.btn_again, self.btn_menu])
        self.tut_title = Text(text="WELCOME!", position=(-0.1, 0.35), scale=3, color=color.white, visible=False)
        self.tut_sub = Text(text="First Time Tutorial", position=(-0.12, 0.25), scale=1.5, color=color.green, visible=False)
        self.tut_lines = []
        tt = [("LEFT/RIGHT or A/D", "Switch lane"), ("SPACE or UP", "Jump"), ("P", "Pause/Resume")]
        for i, (k, a) in enumerate(tt):
            t1 = Text(text=k, position=(-0.4, 0.1 - i * 0.1), scale=1.2, color=color.green, visible=False)
            t2 = Text(text=a, position=(0.1, 0.1 - i * 0.1), scale=1.2, color=color.white, visible=False)
            self.tut_lines.extend([t1, t2])
        for line in ["Girl runs automatically forward", "Collect coins", "Avoid obstacles", "One collision = Game Over"]:
            t = Text(text=line, position=(-0.15, -0.2 - len(self.tut_lines) * 0), scale=1, color=color.light_gray, visible=False)
            self.tut_lines.append(t)
        self.btn_tut_start = Button(text="START PLAYING", position=(0, -0.35), scale=(0.3, 0.08), color=color.green, visible=False)
        self.btn_tut_start.on_click = self.dismiss_tutorial
        self.ui_elements.extend([self.tut_title, self.tut_sub] + self.tut_lines + [self.btn_tut_start])
        self.pause_text = Text(text="PAUSED", position=(-0.08, 0.1), scale=3, color=color.white, visible=False)
        self.pause_sub = Text(text="Press P to resume", position=(-0.12, 0.0), scale=1.5, color=color.light_gray, visible=False)
        self.ui_elements.extend([self.pause_text, self.pause_sub])

    def _hide_all_ui(self):
        for el in self.ui_elements:
            el.visible = False

    def show_menu(self):
        self.state = "MENU"
        self._hide_all_ui()
        self.menu_title.visible = True
        self.menu_sub.visible = True
        self.btn_start.visible = True
        self.btn_howto.visible = True
        self.btn_exit.visible = True
        self.runner.entity.visible = False
        for c in self.coins:
            destroy(c)
        for o in self.obstacles:
            destroy(o)
        for e in self.env_objects:
            destroy(e)
        for m in self.road_marks:
            destroy(m)
        for p in self.pickup_effects:
            destroy(p)
        self.coins.clear()
        self.obstacles.clear()
        self.env_objects.clear()
        self.road_marks.clear()
        self.pickup_effects.clear()

    def show_howto(self):
        self.state = "HOWTO"
        self._hide_all_ui()
        self.howto_title.visible = True
        for el in self.howto_lines:
            el.visible = True
        self.btn_howto_back.visible = True

    def show_game_over(self):
        self.state = "GAMEOVER"
        self._hide_all_ui()
        self.go_title.visible = True
        self.go_sub.visible = True
        self.go_score.text = f"SCORE: {self.score}"
        self.go_coins.text = f"COINS: {self.coin_count}"
        self.go_score.visible = True
        self.go_coins.visible = True
        self.btn_again.visible = True
        self.btn_menu.visible = True
        self.runner.entity.visible = False

    def start_game(self):
        self._hide_all_ui()
        self.current_lane = 1
        self.score = 0
        self.coin_count = 0
        self.speed = 8
        self.cave_progress = 0
        self.paused = False
        scene.fog_density = 0.006
        scene.fog_color = color.rgb32(100, 130, 160)
        self.coin_timer = 0
        self.obs_timer = 0
        self.env_timer = 0
        self.mark_timer = 0
        for c in self.coins:
            destroy(c)
        for o in self.obstacles:
            destroy(o)
        for e in self.env_objects:
            destroy(e)
        for m in self.road_marks:
            destroy(m)
        for p in self.pickup_effects:
            destroy(p)
        self.coins.clear()
        self.obstacles.clear()
        self.env_objects.clear()
        self.road_marks.clear()
        self.pickup_effects.clear()
        self.runner.entity.visible = True
        self.runner.entity.x = 0
        self.runner.entity.y = 0
        self.runner.target_x = 0
        self.runner.jumping = False
        self.runner.jump_vel = 0
        self.runner.y_offset = 0
        self.state = "PLAYING"
        self.score_text.visible = True
        self.coin_text.visible = True
        self.speed_text.visible = True
        self._spawn_initial_world()

    def dismiss_tutorial(self):
        self.settings["tutorial_seen"] = True
        save_settings(self.settings)
        self._hide_all_ui()
        self.state = "PLAYING"
        self.score_text.visible = True
        self.coin_text.visible = True
        self.speed_text.visible = True

    def _spawn_initial_world(self):
        for i in range(15):
            z = -10 - i * 8
            for side in [-1, 1]:
                tx = side * (ROAD_WIDTH / 2 + random.uniform(2, 8))
                tree = Entity(position=(tx, 0, z))
                Entity(parent=tree, model='cube', scale=(0.5, 3, 0.5), y=1.5, color=C_TRUNK)
                Entity(parent=tree, model='sphere', scale=(2.5, 2.5, 2.5), y=3.5, color=C_LEAF)
                tree.speed_mult = 1.0
                self.env_objects.append(tree)
        for i in range(5):
            z = -20 - i * 15
            lane = random.randint(0, 2)
            x = LANE_X[lane]
            c = Entity(model='cube', scale=(0.4, 0.4, 0.1), position=(x, 1.2, z), color=C_COIN)
            self.coins.append(c)
        for i in range(3):
            z = -30 - i * 20
            lane = random.randint(0, 2)
            x = LANE_X[lane]
            otype = random.choice(["log", "rock", "barrier"])
            if otype == "log":
                o = Entity(model=Cylinder(), scale=(0.4, 1.8, 0.4), position=(x, 0.5, z), color=C_LOG, rotation_z=90)
                o.collision_height = 0.9
            elif otype == "rock":
                o = Entity(model='sphere', scale=(0.7, 0.6, 0.7), position=(x, 0.5, z), color=C_ROCK)
                o.collision_height = 0.9
            else:
                o = Entity(model='cube', scale=(1.8, 1.2, 0.3), position=(x, 0.6, z), color=color.red)
                o.collision_height = 1.5
            self.obstacles.append(o)
        for i in range(4):
            for x in [-1.25, 1.25]:
                m = Entity(model='cube', scale=(0.15, 0.02, 2.5), position=(x, 0.02, -i * 10), color=color.white)
                self.road_marks.append(m)

    def toggle_pause(self):
        if self.state == "PLAYING":
            self.paused = not self.paused
            if self.paused:
                self.pause_text.visible = True
                self.pause_sub.visible = True
            else:
                self.pause_text.visible = False
                self.pause_sub.visible = False

    def handle_input(self, key):
        if key == "escape":
            if self.state in ("HOWTO", "GAMEOVER"):
                self.show_menu()
            elif self.state == "PLAYING":
                self.toggle_pause()
            elif self.state == "PAUSED":
                self.toggle_pause()
            return
        if self.state == "TUTORIAL" and key == "space":
            self.dismiss_tutorial()
            return
        if self.state != "PLAYING" or self.paused:
            return
        if key in ("a", "left arrow"):
            if self.current_lane > 0:
                self.current_lane -= 1
                self.runner.set_lane(self.current_lane)
        elif key in ("d", "right arrow"):
            if self.current_lane < 2:
                self.current_lane += 1
                self.runner.set_lane(self.current_lane)
        elif key in ("space", "up arrow"):
            self.runner.jump()
        elif key == "p":
            self.toggle_pause()

    def _cleanup(self, entities, max_z):
        kept = []
        for e in entities:
            try:
                if e.z < max_z:
                    kept.append(e)
                else:
                    destroy(e)
            except:
                pass
        return kept

    def _spawn_coin_pattern(self):
        pt = random.choice(["line", "line", "curve", "zigzag"])
        if pt == "line":
            lane = random.randint(0, 2)
            for i in range(random.randint(5, 8)):
                c = Entity(model='cube', scale=(0.4, 0.4, 0.1), position=(LANE_X[lane], 1.2, SPAWN_Z + i * 4), color=C_COIN)
                self.coins.append(c)
        elif pt == "curve":
            sl = random.randint(0, 2)
            el = random.randint(0, 2)
            if sl == el:
                el = (el + 1) % 3
            for i in range(7):
                t = i / 6.0
                lane = min(2, max(0, int(round(sl + (el - sl) * t))))
                c = Entity(model='cube', scale=(0.4, 0.4, 0.1), position=(LANE_X[lane], 1.2, SPAWN_Z + i * 4), color=C_COIN)
                self.coins.append(c)
        elif pt == "zigzag":
            l1 = random.randint(0, 2)
            l2 = (l1 + 1) % 3
            for i in range(8):
                lane = l1 if i % 2 == 0 else l2
                c = Entity(model='cube', scale=(0.4, 0.4, 0.1), position=(LANE_X[lane], 1.2, SPAWN_Z + i * 4), color=C_COIN)
                self.coins.append(c)

    def _spawn_obstacle(self):
        lane = random.randint(0, 2)
        otype = random.choice(["log", "log", "rock", "barrier"])
        x = LANE_X[lane]
        if otype == "log":
            o = Entity(model=Cylinder(), scale=(0.4, 1.8, 0.4), position=(x, 0.5, SPAWN_Z), color=C_LOG, rotation_z=90)
            o.collision_height = 0.9
        elif otype == "rock":
            o = Entity(model='sphere', scale=(0.7, 0.6, 0.7), position=(x, 0.5, SPAWN_Z), color=C_ROCK)
            o.collision_height = 0.9
        else:
            o = Entity(model='cube', scale=(1.8, 1.2, 0.3), position=(x, 0.6, SPAWN_Z), color=color.red)
            o.collision_height = 1.5
        self.obstacles.append(o)

    def _spawn_environment(self):
        cp = self.cave_progress
        if cp < 0.6:
            side = random.choice([-1, 1])
            x = side * (ROAD_WIDTH / 2 + 2)
            wall = Entity(model='cube', scale=(3, 10, 8), position=(x, 5, SPAWN_Z), color=C_CAVE)
            wall.speed_mult = 1.0
            self.env_objects.append(wall)
            if random.random() < 0.3:
                cx = side * (ROAD_WIDTH / 2 + 1)
                crystal = Entity(model='sphere', scale=(0.3, 0.5, 0.3), position=(cx, random.uniform(1, 5), SPAWN_Z), color=C_CRYSTAL)
                crystal.speed_mult = 1.0
                self.env_objects.append(crystal)
            if random.random() < 0.2:
                sx = random.uniform(-ROAD_WIDTH / 2, ROAD_WIDTH / 2)
                stal = Entity(model=Cone(), scale=(0.6, 2.5, 0.6), position=(sx, 8, SPAWN_Z), color=C_CAVE)
                stal.speed_mult = 1.0
                self.env_objects.append(stal)
        if cp > 0.2:
            side = random.choice([-1, 1])
            tx = side * (ROAD_WIDTH / 2 + random.uniform(2, 10))
            tree = Entity(position=(tx, 0, SPAWN_Z))
            Entity(parent=tree, model='cube', scale=(0.5, 3, 0.5), y=1.5, color=C_TRUNK)
            Entity(parent=tree, model='sphere', scale=(2.5, 2.5, 2.5), y=3.5, color=C_LEAF)
            tree.speed_mult = 1.0
            self.env_objects.append(tree)
        if cp > 0.5 and random.random() < 0.15:
            mx = random.uniform(-50, 50)
            mountain = Entity(model=Cone(), scale=(15, 12, 15), position=(mx, 0, SPAWN_Z - 40), color=color.rgb32(58, 90, 106))
            mountain.speed_mult = 0.3
            self.env_objects.append(mountain)

    def _spawn_road_marks(self):
        for x in [-1.25, 1.25]:
            m = Entity(model='cube', scale=(0.15, 0.02, 2.5), position=(x, 0.02, SPAWN_Z), color=color.white)
            self.road_marks.append(m)

    def _check_collisions(self):
        px = self.runner.entity.x
        py = self.runner.y_offset
        for o in self.obstacles:
            if abs(o.z) < 1.5 and abs(o.x - px) < 1.3:
                if py < getattr(o, 'collision_height', 1.0):
                    self.show_game_over()
                    return
        collected = []
        for c in self.coins:
            if abs(c.z) < 1.2 and abs(c.x - px) < 1.0:
                self.coin_count += 1
                effect = Entity(model='sphere', scale=0.4, position=(c.x, c.y, c.z), color=C_COIN)
                effect.alpha = 1.0
                self.pickup_effects.append(effect)
                destroy(c)
                collected.append(c)
        if collected:
            self.coins = [c for c in self.coins if c not in collected]

    def update_game(self):
        if self.state != "PLAYING" or self.paused:
            return
        dt = time.dt
        if dt > 0.1:
            dt = 0.1
        self.runner.update_runner(dt, self.speed)
        self.score += 1
        self.speed = 8 + self.score // 500
        self.cave_progress = min(1.0, self.score / CAVE_END_SCORE)
        move_dist = self.speed * dt
        for c in self.coins:
            c.z += move_dist
            c.rotation_y += 180 * dt
        self.coins = self._cleanup(self.coins, DESPAWN_Z)
        for o in self.obstacles:
            o.z += move_dist
        self.obstacles = self._cleanup(self.obstacles, DESPAWN_Z)
        for e in self.env_objects:
            sm = getattr(e, 'speed_mult', 1.0)
            e.z += move_dist * sm
        self.env_objects = self._cleanup(self.env_objects, DESPAWN_Z + 30)
        for m in self.road_marks:
            m.z += move_dist
        self.road_marks = self._cleanup(self.road_marks, DESPAWN_Z)
        kept_fx = []
        for p in self.pickup_effects:
            p.z += move_dist
            p.y += 2 * dt
            p.scale_x += 3 * dt
            p.scale_y += 3 * dt
            p.scale_z += 3 * dt
            p.alpha -= 2 * dt
            if p.alpha > 0:
                kept_fx.append(p)
            else:
                destroy(p)
        self.pickup_effects = kept_fx
        self.coin_timer += dt
        if self.coin_timer > 2.0 + random.random():
            self.coin_timer = 0
            self._spawn_coin_pattern()
        self.obs_timer += dt
        if self.obs_timer > 1.5 + random.random() * 0.5:
            self.obs_timer = 0
            self._spawn_obstacle()
        self.env_timer += dt
        if self.env_timer > 0.4:
            self.env_timer = 0
            self._spawn_environment()
        self.mark_timer += dt
        if self.mark_timer > 0.25:
            self.mark_timer = 0
            self._spawn_road_marks()
        self._check_collisions()
        if self.state != "PLAYING":
            return
        camera.x = self.runner.entity.x * 0.3
        camera.y = 8 + self.runner.y_offset * 0.3
        fr = int(100 + 30 * self.cave_progress)
        fg = int(130 + 70 * self.cave_progress)
        fb = int(160 + 70 * self.cave_progress)
        scene.fog_color = color.rgb32(fr, fg, fb)
        scene.fog_density = 0.006 - 0.002 * self.cave_progress
        self.score_text.text = f"SCORE: {self.score}"
        self.coin_text.text = f"COINS: {self.coin_count}"
        self.speed_text.text = f"SPEED: {self.speed}"


game = None

def update():
    if game:
        game.update_game()

def input(key):
    if game:
        game.handle_input(key)

if __name__ == "__main__":
    game = JungleDash3D()
    game.app.run()
 