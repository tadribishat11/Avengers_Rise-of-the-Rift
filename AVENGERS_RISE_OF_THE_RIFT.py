from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import math
import random
import copy


random.seed(7)

# Feature 2.12
GAME_STATE = "START" 
game_timer = 180.0
last_frame_time = 0

player_health = 100
score = 0

GRID_LENGTH = 1200
TILE = 100
MOVE_LIMIT = GRID_LENGTH - TILE

pl_x, pl_z = -900.0, -900.0
pl_y = 0.0
pl_angle = 0.0
MOVE_SPEED = 10.0

walk_cycle = 0.0
is_moving = False

# Features 2.7, 2.11
shield_active = False
shield_timer = 0.0
cheat_mode = False

# Feature 2.4
projectiles = []
PROJECTILE_SPEED = 400

# Features 2.2, 2.3, 2.5, 2.10
enemies = []

CHITAURI_COLOR = (0.30, 0.32, 0.35)
CHITAURI_DARK = (0.14, 0.15, 0.17)

ENEMY_SCALE = 0.25

ENEMY_ATTACK_DISTANCE = 650
ENEMY_ATTACK_COOLDOWN = 90
ENEMY_PROJECTILE_SPEED = 7.0
ENEMY_PROJECTILE_RADIUS = 10
ENEMY_PROJECTILE_DAMAGE = 10

ENEMY_DAMAGE_DISTANCE = 100
ENEMY_DAMAGE = 5
ENEMY_DAMAGE_COOLDOWN = 30

ENEMY_MAX_HEALTH = 100
ENEMY_HIT_DISTANCE = 75
ENEMY_CONTACT_DISTANCE = 100

enemy_attack_counter = 0
enemy_damage_counter = 0

enemy_projectiles = []

boss = {
    "x": 0.0, "y": 0.0, "z": 500.0, "angle": 0.0,
    "health": 10, "active": False, "defeated": False
}
BOSS_MAX_HEALTH = 10
BOSS_HIT_DISTANCE = 90
BOSS_MOVE_SPEED = 0.8
BOSS_ATTACK_DISTANCE = 700
BOSS_ATTACK_COOLDOWN = 120
BOSS_PROJECTILE_SPEED = 8.0
BOSS_PROJECTILE_RADIUS = 14
BOSS_PROJECTILE_DAMAGE = 15
BOSS_DAMAGE_DISTANCE = 160
BOSS_COLLISION_DAMAGE = 10
BOSS_DAMAGE_COOLDOWN = 60

boss_attack_counter = 0
boss_damage_counter = 0
boss_projectiles = []

orbit_angle = 0.0
orbit_height = 260.0
orbit_radius = 850.0
fovY = 100
camera_eye = (0.0, orbit_height, orbit_radius)

COLLECT_RADIUS = 55

# Feature 2.1
stones_collected = 0
TOTAL_STONES = 6
STONE_COLOR = (1.0, 1.0, 0.0)

BOX_A_POS = (-300, 0)
BOX_B_POS = (300, 0)
SWITCH_A_POS = (-300, 220)
SWITCH_B_POS = (300, -220)
_PLACEMENT_MARGIN = 120
_CENTER_CLEAR_RADIUS = 420
_POINT_CLEAR_RADIUS = 260


def _sector_point(sector_index, total_sectors, avoid_points, angle_offset=0.0):
    sector_width = 360.0 / total_sectors
    base_angle = sector_index * sector_width + angle_offset
    max_radius = GRID_LENGTH - _PLACEMENT_MARGIN
    for _ in range(200):
        angle = math.radians(base_angle + random.uniform(0, sector_width))
        radius = random.uniform(_CENTER_CLEAR_RADIUS, max_radius)
        x = math.sin(angle) * radius
        z = math.cos(angle) * radius
        if any(math.hypot(x - ax, z - az) < _POINT_CLEAR_RADIUS for ax, az in avoid_points):
            continue
        return x, z
    return x, z


_placed_points = [BOX_A_POS, BOX_B_POS, SWITCH_A_POS, SWITCH_B_POS, (0, 0), (pl_x, pl_z)]

_free_stone_spots = []
for _i in range(4):
    _pt = _sector_point(_i, 4, _placed_points, angle_offset=0.0)
    _free_stone_spots.append(_pt)
    _placed_points.append(_pt)

stones = [
    {"name": "Space Stone",   "x": BOX_A_POS[0], "z": BOX_A_POS[1], "y": 30, "color": STONE_COLOR, "collected": False, "gate": 0},
    {"name": "Mind Stone",    "x": BOX_B_POS[0], "z": BOX_B_POS[1], "y": 30, "color": STONE_COLOR, "collected": False, "gate": 1},
    {"name": "Reality Stone", "x": _free_stone_spots[0][0], "z": _free_stone_spots[0][1], "y": 30, "color": STONE_COLOR, "collected": False, "gate": None},
    {"name": "Power Stone",   "x": _free_stone_spots[1][0], "z": _free_stone_spots[1][1], "y": 30, "color": STONE_COLOR, "collected": False, "gate": None},
    {"name": "Time Stone",    "x": _free_stone_spots[2][0], "z": _free_stone_spots[2][1], "y": 30, "color": STONE_COLOR, "collected": False, "gate": None},
    {"name": "Soul Stone",    "x": _free_stone_spots[3][0], "z": _free_stone_spots[3][1], "y": 30, "color": STONE_COLOR, "collected": False, "gate": None},
]

# Feature 2.6
HEAL_AMOUNT = 25
HEALTH_COLOR = (1.0, 0.0, 0.0)

_free_pickup_spots = []
for _i in range(4):
    _pt = _sector_point(_i, 4, _placed_points, angle_offset=45.0)
    _free_pickup_spots.append(_pt)
    _placed_points.append(_pt)

health_pickups = [
    {"x": _free_pickup_spots[0][0], "z": _free_pickup_spots[0][1], "y": 20, "collected": False},
    {"x": _free_pickup_spots[1][0], "z": _free_pickup_spots[1][1], "y": 20, "collected": False},
    {"x": _free_pickup_spots[2][0], "z": _free_pickup_spots[2][1], "y": 20, "collected": False},
    {"x": _free_pickup_spots[3][0], "z": _free_pickup_spots[3][1], "y": 20, "collected": False},
]

# Feature 2.8
BOX_SIZE = 90
SWITCH_SIZE = 30
SWITCH_RADIUS = 70
SWITCH_COLOR = (0.1, 0.35, 1.0)
gates = [
    {
        "name": "Gate A",
        "x": BOX_A_POS[0], "z": BOX_A_POS[1],
        "switch_x": SWITCH_A_POS[0], "switch_z": SWITCH_A_POS[1],
        "open": False,
        "switch_activated": False,
    },
    {
        "name": "Gate B",
        "x": BOX_B_POS[0], "z": BOX_B_POS[1],
        "switch_x": SWITCH_B_POS[0], "switch_z": SWITCH_B_POS[1],
        "open": False,
        "switch_activated": False,
    },
]

_INITIAL_STONES = copy.deepcopy(stones)
_INITIAL_HEALTH_PICKUPS = copy.deepcopy(health_pickups)
_INITIAL_GATES = copy.deepcopy(gates)

# Feature 2.9
portal_x, portal_z, portal_y = 0, 0, 220
portal_active = False
portal_spin = 0.0
portal_swirl = 0.0
stone_spin = 0.0
portal_visible = True

sequence_stage = None
ray_progress = 0.0
RAY_RATE = 1.2
RAY_MAX_LENGTH = 900
flash_alpha = 0.0
FLASH_RATE = 1.5
text_hold_timer = 0.0
TEXT_HOLD_SECONDS = 2.5
cutscene_done = False


POLE_COUNT = 32
POLE_RING_DIST = GRID_LENGTH
POLE_HEIGHT = 300
POLE_RADIUS = 22
POLE_TILT = 12
POLE_SPACING = (GRID_LENGTH * 2) / 8.0

energy_pulse = 0.30
energy_pulse_rising = True
PULSE_STEP = 0.003
PULSE_MIN = 0.20
PULSE_MAX = 0.55


pole_positions = []
for _i in range(8):
    d = -GRID_LENGTH + _i * POLE_SPACING
    pole_positions.append((d, -GRID_LENGTH))
for _i in range(8):
    d = -GRID_LENGTH + _i * POLE_SPACING
    pole_positions.append((GRID_LENGTH, d))
for _i in range(8):
    d = GRID_LENGTH - _i * POLE_SPACING
    pole_positions.append((d, GRID_LENGTH))
for _i in range(8):
    d = GRID_LENGTH - _i * POLE_SPACING
    pole_positions.append((-GRID_LENGTH, d))


SKY_RADIUS = 3400
SKY_TOP_Y = 1700
SKY_BOTTOM_Y = -40
SKY_TOP_COLOR = (0.55, 0.75, 0.95)
SKY_HORIZON_COLOR = (0.85, 0.93, 1.0)
SKY_SEGMENTS = 48


def draw_sky():
    for i in range(SKY_SEGMENTS):
        ang1 = math.radians(i * (360.0 / SKY_SEGMENTS))
        ang2 = math.radians((i + 1) * (360.0 / SKY_SEGMENTS))
        x1, z1 = math.sin(ang1) * SKY_RADIUS, math.cos(ang1) * SKY_RADIUS
        x2, z2 = math.sin(ang2) * SKY_RADIUS, math.cos(ang2) * SKY_RADIUS
        glBegin(GL_QUADS)
        glColor3f(*SKY_HORIZON_COLOR)
        glVertex3f(x1, SKY_BOTTOM_Y, z1)
        glVertex3f(x2, SKY_BOTTOM_Y, z2)
        glColor3f(*SKY_TOP_COLOR)
        glVertex3f(x2, SKY_TOP_Y, z2)
        glVertex3f(x1, SKY_TOP_Y, z1)
        glEnd()


GROUND_COLOR = (0.20, 0.55, 0.22)
GROUND_RING_COLOR = (0.16, 0.45, 0.18)
GROUND_RING_COUNT = 10
GROUND_RING_WIDTH = 130
GROUND_RING_SEGMENTS = 48


def draw_ground():
    glColor3f(*GROUND_COLOR)
    glBegin(GL_QUADS)
    glVertex3f(-SKY_RADIUS, 0, -SKY_RADIUS)
    glVertex3f(SKY_RADIUS, 0, -SKY_RADIUS)
    glVertex3f(SKY_RADIUS, 0, SKY_RADIUS)
    glVertex3f(-SKY_RADIUS, 0, SKY_RADIUS)
    glEnd()

    glBegin(GL_QUADS)
    for ring in range(GROUND_RING_COUNT):
        inner_r = ring * GROUND_RING_WIDTH
        outer_r = inner_r + GROUND_RING_WIDTH
        if ring % 2 == 0:
            glColor3f(*GROUND_COLOR)
        else:
            glColor3f(*GROUND_RING_COLOR)
        for seg in range(GROUND_RING_SEGMENTS):
            a1 = 2 * math.pi * seg / GROUND_RING_SEGMENTS
            a2 = 2 * math.pi * (seg + 1) / GROUND_RING_SEGMENTS
            x1i, z1i = math.sin(a1) * inner_r, math.cos(a1) * inner_r
            x2i, z2i = math.sin(a2) * inner_r, math.cos(a2) * inner_r
            x1o, z1o = math.sin(a1) * outer_r, math.cos(a1) * outer_r
            x2o, z2o = math.sin(a2) * outer_r, math.cos(a2) * outer_r
            glVertex3f(x1i, 0, z1i)
            glVertex3f(x1o, 0, z1o)
            glVertex3f(x2o, 0, z2o)
            glVertex3f(x2i, 0, z2i)
    glEnd()


TREE_PITCH = 340
TREE_SPAWN_CHANCE = 0.35
TREE_CLEAR = 150
TREE_MARGIN = 24

_placed_points.append((0.0, 500.0))

_tree_coords = []
_tv = -GRID_LENGTH + TREE_PITCH / 2.0
while _tv < GRID_LENGTH - TREE_PITCH / 2.0 + 1:
    _tree_coords.append(_tv)
    _tv += TREE_PITCH

trees = []
for _tx in _tree_coords:
    for _tz in _tree_coords:
        if random.random() > TREE_SPAWN_CHANCE:
            continue
        _jx = _tx + random.uniform(-60, 60)
        _jz = _tz + random.uniform(-60, 60)
        if any(math.hypot(_jx - ax, _jz - az) < TREE_CLEAR for ax, az in _placed_points):
            continue
        trees.append({
            "x": _jx, "z": _jz,
            "trunk_h": random.uniform(70, 130),
            "trunk_r": random.uniform(9, 14),
            "foliage_r": random.uniform(35, 55),
        })

outer_trees = []
_OUTER_TREE_COUNT = 90
for _i in range(_OUTER_TREE_COUNT):
    _oang = random.uniform(0, 360)
    _orad = random.uniform(GRID_LENGTH + 120, GRID_LENGTH + 900)
    _ox = math.sin(math.radians(_oang)) * _orad
    _oz = math.cos(math.radians(_oang)) * _orad
    outer_trees.append({
        "x": _ox, "z": _oz,
        "trunk_h": random.uniform(80, 150),
        "trunk_r": random.uniform(10, 16),
        "foliage_r": random.uniform(40, 65),
    })


def draw_tree(t):
    quad = gluNewQuadric()
    glPushMatrix()
    glTranslatef(t["x"], 0, t["z"])
    glColor3f(0.40, 0.26, 0.13)
    glRotatef(-90, 1, 0, 0)
    gluCylinder(quad, t["trunk_r"], t["trunk_r"] * 0.8, t["trunk_h"], 8, 4)
    glPopMatrix()

    glPushMatrix()
    glTranslatef(t["x"], t["trunk_h"] + t["foliage_r"] * 0.55, t["z"])
    glColor3f(0.13, 0.42, 0.16)
    gluSphere(gluNewQuadric(), t["foliage_r"], 10, 8)
    glPopMatrix()

    glPushMatrix()
    glTranslatef(t["x"] + t["foliage_r"] * 0.35, t["trunk_h"] + t["foliage_r"] * 0.85, t["z"] - t["foliage_r"] * 0.25)
    glColor3f(0.16, 0.48, 0.19)
    gluSphere(gluNewQuadric(), t["foliage_r"] * 0.6, 8, 6)
    glPopMatrix()


def draw_trees():
    for t in trees:
        draw_tree(t)
    for t in outer_trees:
        draw_tree(t)


def is_blocked_by_tree(x, z):
    for t in trees:
        if math.hypot(x - t["x"], z - t["z"]) < t["trunk_r"] + TREE_MARGIN:
            return True
    return False


def update_energy_pulse():
    global energy_pulse, energy_pulse_rising
    if energy_pulse_rising:
        energy_pulse += PULSE_STEP
        if energy_pulse >= PULSE_MAX:
            energy_pulse_rising = False
    else:
        energy_pulse -= PULSE_STEP
        if energy_pulse <= PULSE_MIN:
            energy_pulse_rising = True


def draw_border_shield():
    glColor3f(0.55, 0.55, 0.6)
    for (px, pz) in pole_positions:
        glPushMatrix()
        glTranslatef(px, 0, pz)
        if abs(px) == GRID_LENGTH:
            glRotatef(POLE_TILT if pz > 0 else -POLE_TILT, 0, 0, 1)
        else:
            glRotatef(-POLE_TILT if pz > 0 else POLE_TILT, 1, 0, 0)
        glRotatef(-90, 1, 0, 0)
        gluCylinder(gluNewQuadric(), POLE_RADIUS, POLE_RADIUS * 0.7, POLE_HEIGHT, 12, 6)
        glPopMatrix()
        glPushMatrix()
        glTranslatef(px, POLE_HEIGHT, pz)
        glColor3f(0.7, 0.8, 1.0)
        gluSphere(gluNewQuadric(), POLE_RADIUS * 1.4, 10, 10)
        glColor3f(0.55, 0.55, 0.6)
        glPopMatrix()

    glColor3f(0.05 + 0.15 * energy_pulse, 0.25 + 0.5 * energy_pulse, 0.55 + 0.45 * energy_pulse)
    glBegin(GL_QUADS)
    for i in range(POLE_COUNT):
        x1, z1 = pole_positions[i]
        x2, z2 = pole_positions[(i + 1) % POLE_COUNT]
        glVertex3f(x1, 0, z1)
        glVertex3f(x1, POLE_HEIGHT * 0.85, z1)
        glVertex3f(x2, POLE_HEIGHT * 0.85, z2)
        glVertex3f(x2, 0, z2)
    glEnd()


def draw_battlefield_environment():
    draw_sky()
    draw_ground()
    draw_border_shield()


def draw_text(x, y, text, font=GLUT_BITMAP_HELVETICA_18, color=(1, 1, 1)):
    glColor3f(*color)
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    gluOrtho2D(0, 1000, 0, 800)
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()
    glRasterPos2f(x, y)
    for ch in text:
        glutBitmapCharacter(font, ord(ch))
    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)


def distance_2d(x1, z1, x2, z2):
    return math.sqrt((x1 - x2) ** 2 + (z1 - z2) ** 2)


def facing_vector(angle_deg):
    rad = math.radians(angle_deg)
    return -math.sin(rad), -math.cos(rad)


# Feature 2.1

def update_stones():
    global stones_collected, score
    for stone in stones:
        if not stone["collected"]:
            if stone["gate"] is not None and not gates[stone["gate"]]["open"]:
                continue
            if distance_2d(pl_x, pl_z, stone["x"], stone["z"]) < COLLECT_RADIUS:
                stone["collected"] = True
                stones_collected += 1
                score += 100

STONE_SCALE = (28, 28, 28)

def draw_single_stone(stone):
    glPushMatrix()
    glColor3f(*stone["color"])
    glTranslatef(stone["x"], stone["y"], stone["z"])

    if cheat_mode:
        glPushMatrix()
        glTranslatef(0, 250, 0)
        glScalef(3, 500, 3)
        glutSolidCube(1)
        glPopMatrix()

    glRotatef(stone_spin, 0, 1, 0)
    glScalef(*STONE_SCALE)
    glRotatef(45, 0, 1, 0)
    glRotatef(45, 1, 0, 0)
    glutSolidCube(1)
    glPopMatrix()


def draw_stones():
    for stone in stones:
        if not stone["collected"]:
            draw_single_stone(stone)


# Feature 2.6

def update_health_pickups():
    global player_health
    for pickup in health_pickups:
        if not pickup["collected"]:
            if distance_2d(pl_x, pl_z, pickup["x"], pickup["z"]) < COLLECT_RADIUS:
                pickup["collected"] = True
                player_health += HEAL_AMOUNT
                if player_health > 100:
                    player_health = 100


def draw_single_pickup(pickup):
    glPushMatrix()
    glColor3f(*HEALTH_COLOR)
    glTranslatef(pickup["x"], pickup["y"], pickup["z"])
    glutSolidCube(20)
    glPopMatrix()


def draw_health_pickups():
    for pickup in health_pickups:
        if not pickup["collected"]:
            draw_single_pickup(pickup)


# Feature 2.8

def try_activate_switch():
    for gate in gates:
        if not gate["switch_activated"]:
            if distance_2d(pl_x, pl_z, gate["switch_x"], gate["switch_z"]) < SWITCH_RADIUS:
                gate["switch_activated"] = True

def update_gates():
    for gate in gates:
        if not gate["open"] and gate["switch_activated"]:
            gate["open"] = True

def draw_box_gate(gate):
    gx, gz = gate["x"], gate["z"]
    s = BOX_SIZE

    if not gate["open"]:
        glPushMatrix()
        glColor3f(0.55, 0.78, 0.92)
        glTranslatef(gx, s / 2.0, gz)
        glutSolidCube(s)
        glPopMatrix()

    glPushMatrix()
    glTranslatef(gate["switch_x"], SWITCH_SIZE / 2.0, gate["switch_z"])
    if gate["switch_activated"]:
        glColor3f(SWITCH_COLOR[0] * 0.4, SWITCH_COLOR[1] * 0.4, SWITCH_COLOR[2] * 0.4)
    else:
        glColor3f(*SWITCH_COLOR)
    glutSolidCube(SWITCH_SIZE)
    glPopMatrix()

def draw_gates():
    for gate in gates:
        draw_box_gate(gate)


# Feature 2.9

def update_portal():
    global portal_active, portal_spin, portal_swirl, GAME_STATE, score, sequence_stage
    if stones_collected >= TOTAL_STONES:
        if not portal_active:
            portal_active = True
            sequence_stage = 0
            GAME_STATE = "PORTAL_SEQUENCE"

        if cutscene_done and portal_visible and distance_2d(pl_x, pl_z, portal_x, portal_z) < 100:
            GAME_STATE = "VICTORY"
            score += int(game_timer) * 10

    portal_spin += 1.2
    if portal_spin >= 360:
        portal_spin = 0
    portal_swirl -= 3.5
    if portal_swirl <= -360:
        portal_swirl = 0


def _ring_quads(inner_r, outer_r, segments=40):
    for i in range(segments):
        a1 = math.radians(i * (360.0 / segments))
        a2 = math.radians((i + 1) * (360.0 / segments))
        x1i, y1i = math.cos(a1) * inner_r, math.sin(a1) * inner_r
        x1o, y1o = math.cos(a1) * outer_r, math.sin(a1) * outer_r
        x2o, y2o = math.cos(a2) * outer_r, math.sin(a2) * outer_r
        x2i, y2i = math.cos(a2) * inner_r, math.sin(a2) * inner_r
        glVertex3f(x1i, y1i, 0)
        glVertex3f(x1o, y1o, 0)
        glVertex3f(x2o, y2o, 0)
        glVertex3f(x2i, y2i, 0)


def _filled_disk_quads(radius, segments=30):
    for i in range(segments):
        a1 = math.radians(i * (360.0 / segments))
        a2 = math.radians((i + 1) * (360.0 / segments))
        x1, y1 = math.cos(a1) * radius, math.sin(a1) * radius
        x2, y2 = math.cos(a2) * radius, math.sin(a2) * radius
        glVertex3f(0, 0, 0)
        glVertex3f(x1, y1, 0)
        glVertex3f(x2, y2, 0)
        glVertex3f(0, 0, 0)


def draw_portal():
    if not portal_visible:
        return
    outer_r = 150
    mid_r = 128
    inner_r = 118

    if portal_active:
        ring_color = (0.15, 0.85, 0.95)
        vortex_color = (0.05, 0.9, 1.0)
        glow_color = (0.6, 1.0, 1.0)
    else:
        ring_color = (0.35, 0.35, 0.4)
        vortex_color = (0.3, 0.3, 0.35)
        glow_color = (0.5, 0.5, 0.55)

    glPushMatrix()
    glTranslatef(portal_x, portal_y, portal_z)
    glRotatef(portal_spin, 0, 0, 1)

    glColor3f(*ring_color)
    glBegin(GL_QUADS)
    _ring_quads(mid_r, outer_r, 40)
    glEnd()

    glColor3f(*glow_color)
    glBegin(GL_QUADS)
    _ring_quads(inner_r, mid_r, 40)
    glEnd()

    glPushMatrix()
    glRotatef(portal_swirl, 0, 0, 1)
    for layer in range(3):
        r = inner_r - layer * 28
        if r <= 10:
            continue
        shade = 1.0 - layer * 0.22
        glColor3f(vortex_color[0] * shade, vortex_color[1] * shade, vortex_color[2] * shade)
        glBegin(GL_QUADS)
        _filled_disk_quads(r, 30)
        glEnd()
    glPopMatrix()

    EMBER_COUNT = 10
    glColor3f(*glow_color)
    for i in range(EMBER_COUNT):
        ember_angle = math.radians(i * (360.0 / EMBER_COUNT) - portal_spin * 1.5)
        ex = math.cos(ember_angle) * (outer_r + 12)
        ey = math.sin(ember_angle) * (outer_r + 12)
        glPushMatrix()
        glTranslatef(ex, ey, 6)
        gluSphere(gluNewQuadric(), 6, 8, 8)
        glPopMatrix()

    glPopMatrix()


def draw_portal_rays():
    if ray_progress <= 0:
        return
    quad = gluNewQuadric()
    length = ray_progress * RAY_MAX_LENGTH
    RAY_COUNT = 14
    glColor3f(1, 1, 1)
    glPushMatrix()
    glTranslatef(portal_x, portal_y, portal_z)
    for i in range(RAY_COUNT):
        angle = i * (360.0 / RAY_COUNT)
        glPushMatrix()
        glRotatef(angle, 0, 0, 1)
        glRotatef(90, 0, 1, 0)
        gluCylinder(quad, 6, 1, length, 6, 1)
        glPopMatrix()
    glPopMatrix()


def update_portal_sequence(dt):
    global sequence_stage, ray_progress, flash_alpha, text_hold_timer
    global GAME_STATE, cutscene_done, enemies, portal_visible

    if sequence_stage is None:
        return

    if sequence_stage == 0:
        ray_progress += RAY_RATE * dt
        if ray_progress >= 1.0:
            ray_progress = 1.0
            sequence_stage = 1
    elif sequence_stage == 1:
        flash_alpha += FLASH_RATE * dt
        if flash_alpha >= 1.0:
            flash_alpha = 1.0
            sequence_stage = 2
            text_hold_timer = 0.0
    elif sequence_stage == 2:
        text_hold_timer += dt
        if text_hold_timer >= TEXT_HOLD_SECONDS:
            sequence_stage = 3
    elif sequence_stage == 3:
        flash_alpha -= FLASH_RATE * dt
        if flash_alpha <= 0.0:
            flash_alpha = 0.0
            sequence_stage = 4
    elif sequence_stage == 4:
        stones.clear()
        health_pickups.clear()
        gates.clear()
        ray_progress = 0.0
        portal_visible = False
        enemies = []
        cutscene_done = True
        GAME_STATE = "PLAYING"
        sequence_stage = None


def estimate_text_width(text, font=GLUT_BITMAP_HELVETICA_18, avg_char_width=11):
    return len(text) * avg_char_width


def draw_bold_bitmap_text(x, y, text, color=(0, 0, 0)):
    glColor3f(*color)
    for ox, oy in ((0, 0), (1, 0), (0, 1), (1, 1)):
        glRasterPos2f(x + ox, y + oy)
        for ch in text:
            glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, ord(ch))


def draw_screen_flash():
    if flash_alpha <= 0:
        return
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    gluOrtho2D(0, 1000, 0, 800)
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()

    if flash_alpha > 0.85:
        shade = 1.0
    elif flash_alpha > 0.6:
        shade = 0.85
    elif flash_alpha > 0.35:
        shade = 0.6
    elif flash_alpha > 0.1:
        shade = 0.35
    else:
        shade = 0.0

    if shade > 0.0:
        glColor3f(shade, shade, shade)
        glBegin(GL_QUADS)
        glVertex3f(0, 0, 0)
        glVertex3f(1000, 0, 0)
        glVertex3f(1000, 800, 0)
        glVertex3f(0, 800, 0)
        glEnd()

    if flash_alpha > 0.5:
        title = "BRING ME THANOS"
        title_x = (1000 - estimate_text_width(title)) / 2.0
        draw_bold_bitmap_text(title_x, 400, title, color=(0.05, 0.05, 0.05))

    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)


# Features 2.7, 2.11, 2.12

def draw_player():
    global pl_x, pl_y, pl_z, pl_angle, walk_cycle, shield_active

    glPushMatrix()
    glTranslatef(pl_x, pl_y + 35, pl_z)

    dx, dz = facing_vector(pl_angle)
    model_angle = math.degrees(math.atan2(-dx, -dz))
    glRotatef(model_angle, 0, 1, 0)


    glColor3f(0.1, 0.9, 1.0)
    glBegin(GL_TRIANGLES)
    glVertex3f(0, 52, -32)
    glVertex3f(-8, 52, -18)
    glVertex3f(8, 52, -18)
    glEnd()
    glBegin(GL_QUADS)
    glVertex3f(-3, 52, -18)
    glVertex3f(3, 52, -18)
    glVertex3f(3, 52, 2)
    glVertex3f(-3, 52, 2)
    glEnd()

    swing = math.sin(walk_cycle) * 35.0 if is_moving else 0.0
    quad = gluNewQuadric()

    glColor3f(0.55, 0.035, 0.025)
    glPushMatrix()
    glScalef(1.25, 1.85, 0.82)
    glutSolidCube(20)
    glPopMatrix()


    glColor3f(0.95, 0.62, 0.08)
    glPushMatrix()
    glTranslatef(0, -3, -8.7)
    glScalef(0.65, 0.55, 0.18)
    glutSolidCube(20)
    glPopMatrix()

    glColor3f(0.92, 0.55, 0.06)
    glBegin(GL_QUADS)
    glVertex3f(-8, 17, -8.6)
    glVertex3f(8, 17, -8.6)
    glVertex3f(6, 2, -9.0)
    glVertex3f(-6, 2, -9.0)
    glEnd()


    glColor3f(0.12, 0.15, 0.18)
    glPushMatrix()
    glTranslatef(0, 10, -10.0)
    glScalef(1.0, 1.0, 0.35)
    gluSphere(quad, 5.5, 16, 12)
    glPopMatrix()


    glColor3f(0.25, 0.95, 1.0)
    glPushMatrix()
    glTranslatef(0, 10, -12.0)
    gluSphere(quad, 3.2, 12, 10)
    glPopMatrix()


    glColor3f(0.55, 1.0, 1.0)
    glBegin(GL_TRIANGLES)
    glVertex3f(0, 14, -12.2)
    glVertex3f(-3.0, 8, -12.0)
    glVertex3f(3.0, 8, -12.0)
    glEnd()


    glColor3f(0.60, 0.035, 0.025)
    glPushMatrix()
    glTranslatef(0, 29, 0)
    glScalef(0.78, 0.82, 0.72)
    gluSphere(quad, 10, 16, 12)
    glPopMatrix()


    glColor3f(0.95, 0.63, 0.08)
    glBegin(GL_QUADS)
    glVertex3f(-6.5, 34, -7.1)
    glVertex3f(6.5, 34, -7.1)
    glVertex3f(5.2, 25, -7.8)
    glVertex3f(-5.2, 25, -7.8)
    glEnd()


    glColor3f(0.82, 0.42, 0.05)
    glPushMatrix()
    glTranslatef(0, 25.0, -7.4)
    glScalef(0.42, 0.25, 0.18)
    glutSolidCube(20)
    glPopMatrix()


    glColor3f(0.25, 0.95, 1.0)
    glBegin(GL_QUADS)
    glVertex3f(-5.3, 32.0, -8.0)
    glVertex3f(-0.8, 31.3, -8.0)
    glVertex3f(-1.4, 29.2, -8.0)
    glVertex3f(-5.0, 29.7, -8.0)

    glVertex3f(0.8, 31.3, -8.0)
    glVertex3f(5.3, 32.0, -8.0)
    glVertex3f(5.0, 29.7, -8.0)
    glVertex3f(1.4, 29.2, -8.0)
    glEnd()


    glColor3f(0.08, 0.08, 0.10)
    glPushMatrix()
    glTranslatef(0, 30, 7.2)
    glScalef(0.58, 0.60, 0.18)
    glutSolidCube(20)
    glPopMatrix()


  
    glColor3f(0.95, 0.60, 0.07)
    glPushMatrix()
    glTranslatef(-15, 16, 0)
    glScalef(0.55, 0.55, 0.62)
    gluSphere(quad, 10, 12, 10)
    glPopMatrix()

    glPushMatrix()
    glTranslatef(15, 16, 0)
    glScalef(0.55, 0.55, 0.62)
    gluSphere(quad, 10, 12, 10)
    glPopMatrix()


    glPushMatrix()
    glTranslatef(-15, 10, 0)
    glRotatef(swing, 1, 0, 0)
    glRotatef(90, 1, 0, 0)
    glColor3f(0.58, 0.035, 0.025)
    gluCylinder(quad, 4.8, 3.8, 20, 10, 8)
    glPopMatrix()

    glPushMatrix()
    glTranslatef(15, 10, 0)
    glRotatef(-swing, 1, 0, 0)
    glRotatef(90, 1, 0, 0)
    glColor3f(0.58, 0.035, 0.025)
    gluCylinder(quad, 4.8, 3.8, 20, 10, 8)
    glPopMatrix()


    glPushMatrix()
    glTranslatef(-15, -8, 0)
    glRotatef(swing, 1, 0, 0)
    glRotatef(90, 1, 0, 0)
    glColor3f(0.92, 0.55, 0.06)
    gluCylinder(quad, 4.2, 3.5, 17, 10, 8)
    glPopMatrix()

    glPushMatrix()
    glTranslatef(15, -8, 0)
    glRotatef(-swing, 1, 0, 0)
    glRotatef(90, 1, 0, 0)
    glColor3f(0.92, 0.55, 0.06)
    gluCylinder(quad, 4.2, 3.5, 17, 10, 8)
    glPopMatrix()


    glColor3f(0.25, 0.95, 1.0)
    glPushMatrix()
    glTranslatef(-15, -18, -4.8)
    gluSphere(quad, 3.8, 12, 10)
    glPopMatrix()

    glPushMatrix()
    glTranslatef(15, -18, -4.8)
    gluSphere(quad, 3.8, 12, 10)
    glPopMatrix()

    glColor3f(0.58, 0.035, 0.025)
    glPushMatrix()
    glTranslatef(-6, -18, 0)
    glRotatef(-swing, 1, 0, 0)
    glTranslatef(0, -10, 0)
    glScalef(0.42, 1.15, 0.46)
    glutSolidCube(20)
    glPopMatrix()

    glPushMatrix()
    glTranslatef(6, -18, 0)
    glRotatef(swing, 1, 0, 0)
    glTranslatef(0, -10, 0)
    glScalef(0.42, 1.15, 0.46)
    glutSolidCube(20)
    glPopMatrix()


    glColor3f(0.95, 0.60, 0.07)
    glPushMatrix()
    glTranslatef(-6, -18, 0)
    glRotatef(-swing, 1, 0, 0)
    glTranslatef(0, -12, -4.0)
    glScalef(0.32, 0.25, 0.22)
    glutSolidCube(20)
    glPopMatrix()

    glPushMatrix()
    glTranslatef(6, -18, 0)
    glRotatef(swing, 1, 0, 0)
    glTranslatef(0, -12, -4.0)
    glScalef(0.32, 0.25, 0.22)
    glutSolidCube(20)
    glPopMatrix()


    glColor3f(0.12, 0.12, 0.14)
    glPushMatrix()
    glTranslatef(-6, -18, 0)
    glRotatef(-swing, 1, 0, 0)
    glTranslatef(0, -25, -2)
    glScalef(0.48, 0.40, 0.70)
    glutSolidCube(20)
    glPopMatrix()

    glPushMatrix()
    glTranslatef(6, -18, 0)
    glRotatef(swing, 1, 0, 0)
    glTranslatef(0, -25, -2)
    glScalef(0.48, 0.40, 0.70)
    glutSolidCube(20)
    glPopMatrix()

    glColor3f(0.92, 0.55, 0.06)
    glPushMatrix()
    glTranslatef(-6, -18, 0)
    glRotatef(-swing, 1, 0, 0)
    glTranslatef(0, -25, -9)
    glBegin(GL_QUADS)
    glVertex3f(-4, -3, 0)
    glVertex3f(4, -3, 0)
    glVertex3f(4, 3, 0)
    glVertex3f(-4, 3, 0)
    glEnd()
    glPopMatrix()

    glPushMatrix()
    glTranslatef(6, -18, 0)
    glRotatef(swing, 1, 0, 0)
    glTranslatef(0, -25, -9)
    glBegin(GL_QUADS)
    glVertex3f(-4, -3, 0)
    glVertex3f(4, -3, 0)
    glVertex3f(4, 3, 0)
    glVertex3f(-4, 3, 0)
    glEnd()
    glPopMatrix()

    # Feature 2.7
    if shield_active:
        glPushMatrix()
        glTranslatef(0, 48, 0)
        glColor3f(0.0, 1.0, 1.0)
        gluSphere(quad, 10, 12, 12)
        glPopMatrix()

    glPopMatrix()

def draw_single_projectile(p):
    # Feature 2.4
    x, y, z = p['x'], 35, p['z']
    vx, vz = p['dx'], p['dz']

    length = math.hypot(vx, vz)
    nx, nz = vx/length, vz/length

    glPushMatrix()
    glTranslatef(x, y, z)

    glColor3f(1.0, 1.0, 0.0)
    gluSphere(gluNewQuadric(), 6, 8, 8)

    glPushMatrix()
    glTranslatef(-nx*5, 0, -nz*5)
    glColor3f(1.0, 0.5, 0.0)
    gluSphere(gluNewQuadric(), 8, 8, 8)
    glTranslatef(-nx*5, 0, -nz*5)
    glColor3f(1.0, 0.0, 0.0)
    gluSphere(gluNewQuadric(), 9, 8, 8)
    glPopMatrix()

    glColor3f(0.3, 0.3, 0.3)
    glPushMatrix()
    glTranslatef(-nx*20, 0, -nz*20)
    gluSphere(gluNewQuadric(), 7, 8, 8)
    glTranslatef(-nx*12, 0, -nz*12)
    glColor3f(0.2, 0.2, 0.2)
    gluSphere(gluNewQuadric(), 5, 8, 8)
    glTranslatef(-nx*12, 0, -nz*12)
    glColor3f(0.1, 0.1, 0.1)
    gluSphere(gluNewQuadric(), 3, 8, 8)
    glPopMatrix()

    glPopMatrix()


def draw_projectiles():
    # Feature 2.4
    for p in projectiles:
        draw_single_projectile(p)

def update_player_projectiles(dt):
    for p in projectiles[:]:
        p['x'] += p['dx'] * PROJECTILE_SPEED * dt
        p['z'] += p['dz'] * PROJECTILE_SPEED * dt
        if abs(p['x']) > GRID_LENGTH or abs(p['z']) > GRID_LENGTH:
            projectiles.remove(p)


def draw_ultron(enemy):
    x, y, z, angle = enemy["x"], enemy["y"], enemy["z"], enemy["angle"]
    glPushMatrix()
    glTranslatef(x, y, z)
    glRotatef(angle, 0, 1, 0)
    glScalef(ENEMY_SCALE, ENEMY_SCALE, ENEMY_SCALE)
    glTranslatef(0, 50, 0)

    glColor3f(0.32, 0.34, 0.37)
    glPushMatrix(); glTranslatef(0, 120, 0); glScalef(70, 100, 45); glutSolidCube(1); glPopMatrix()

    glColor3f(0.10, 0.11, 0.13)
    glPushMatrix(); glTranslatef(0, 55, 0); glScalef(55, 50, 38); glutSolidCube(1); glPopMatrix()

    glColor3f(0.32, 0.34, 0.37)
    glPushMatrix(); glTranslatef(0, 235, 0); glScalef(55, 65, 50); glutSolidCube(1); glPopMatrix()

    glColor3f(0.10, 0.11, 0.13)
    glPushMatrix(); glTranslatef(0, 230, -27); glScalef(38, 35, 8); glutSolidCube(1); glPopMatrix()

    glColor3f(1.0, 0.0, 0.0)
    glPushMatrix(); glTranslatef(-18, 242, -32); glScalef(12, 5, 5); glutSolidCube(1); glPopMatrix()
    glPushMatrix(); glTranslatef(18, 242, -32); glScalef(12, 5, 5); glutSolidCube(1); glPopMatrix()

    glColor3f(0.26, 0.28, 0.31)
    glPushMatrix(); glTranslatef(-90, 130, 0); glRotatef(-8, 0, 0, 1); glScalef(30, 85, 30); glutSolidCube(1); glPopMatrix()
    glPushMatrix(); glTranslatef(-100, 55, 0); glRotatef(-5, 0, 0, 1); glScalef(28, 70, 28); glutSolidCube(1); glPopMatrix()
    glPushMatrix(); glTranslatef(-105, 15, 0); glScalef(35, 30, 35); glutSolidCube(1); glPopMatrix()

    glPushMatrix(); glTranslatef(90, 130, 0); glRotatef(8, 0, 0, 1); glScalef(30, 85, 30); glutSolidCube(1); glPopMatrix()
    glPushMatrix(); glTranslatef(100, 55, 0); glRotatef(5, 0, 0, 1); glScalef(28, 70, 28); glutSolidCube(1); glPopMatrix()
    glPushMatrix(); glTranslatef(105, 15, 0); glScalef(35, 30, 35); glutSolidCube(1); glPopMatrix()

    glColor3f(0.16, 0.17, 0.19)
    glPushMatrix(); glTranslatef(-32, 5, 0); glScalef(38, 100, 38); glutSolidCube(1); glPopMatrix()
    glPushMatrix(); glTranslatef(-32, -45, -15); glScalef(42, 25, 60); glutSolidCube(1); glPopMatrix()
    glPushMatrix(); glTranslatef(32, 5, 0); glScalef(38, 100, 38); glutSolidCube(1); glPopMatrix()
    glPushMatrix(); glTranslatef(32, -45, -15); glScalef(42, 25, 60); glutSolidCube(1); glPopMatrix()

    glPopMatrix()


def draw_chitauri(enemy):
    x, y, z, angle = enemy["x"], enemy["y"], enemy["z"], enemy["angle"]
    glPushMatrix()
    glTranslatef(x, y, z)
    glRotatef(angle, 0, 1, 0)
    glScalef(ENEMY_SCALE, ENEMY_SCALE, ENEMY_SCALE)
    glTranslatef(0, 50, 0)

    glColor3f(*CHITAURI_COLOR)
    glPushMatrix(); glTranslatef(0, 105, 0); glScalef(55, 85, 38); glutSolidCube(1); glPopMatrix()

    glColor3f(*CHITAURI_DARK)
    glPushMatrix(); glTranslatef(0, 45, 0); glScalef(45, 45, 32); glutSolidCube(1); glPopMatrix()

    glColor3f(*CHITAURI_COLOR)
    glPushMatrix(); glTranslatef(0, 205, 0); glScalef(48, 58, 42); gluSphere(gluNewQuadric(), 1, 16, 12); glPopMatrix()

    glColor3f(*CHITAURI_DARK)
    glPushMatrix(); glTranslatef(0, 200, -25); glScalef(32, 30, 8); glutSolidCube(1); glPopMatrix()

    glColor3f(0.8, 0.9, 0.35)
    glPushMatrix(); glTranslatef(-15, 215, -27); glScalef(10, 5, 5); glutSolidCube(1); glPopMatrix()
    glPushMatrix(); glTranslatef(15, 215, -27); glScalef(10, 5, 5); glutSolidCube(1); glPopMatrix()

    glColor3f(*CHITAURI_COLOR)
    glPushMatrix(); glTranslatef(-68, 115, 0); glRotatef(-10, 0, 0, 1); glScalef(24, 70, 24); glutSolidCube(1); glPopMatrix()
    glPushMatrix(); glTranslatef(-78, 52, 0); glRotatef(-5, 0, 0, 1); glScalef(22, 60, 22); glutSolidCube(1); glPopMatrix()
    glPushMatrix(); glTranslatef(-82, 15, 0); glScalef(28, 25, 28); gluSphere(gluNewQuadric(), 1, 10, 8); glPopMatrix()

    glPushMatrix(); glTranslatef(68, 115, 0); glRotatef(10, 0, 0, 1); glScalef(24, 70, 24); glutSolidCube(1); glPopMatrix()
    glPushMatrix(); glTranslatef(78, 52, 0); glRotatef(5, 0, 0, 1); glScalef(22, 60, 22); glutSolidCube(1); glPopMatrix()
    glPushMatrix(); glTranslatef(82, 15, 0); glScalef(28, 25, 28); gluSphere(gluNewQuadric(), 1, 10, 8); glPopMatrix()

    glColor3f(*CHITAURI_DARK)
    glPushMatrix(); glTranslatef(-24, 0, 0); glScalef(30, 90, 30); glutSolidCube(1); glPopMatrix()
    glPushMatrix(); glTranslatef(-24, -42, -14); glScalef(34, 22, 50); glutSolidCube(1); glPopMatrix()
    glPushMatrix(); glTranslatef(24, 0, 0); glScalef(30, 90, 30); glutSolidCube(1); glPopMatrix()
    glPushMatrix(); glTranslatef(24, -42, -14); glScalef(34, 22, 50); glutSolidCube(1); glPopMatrix()

    glPopMatrix()


def draw_enemy_health_bar(enemy):
    if enemy.get("defeated", False):
        return
    health = enemy["health"]
    max_health = enemy.get("max_health", ENEMY_MAX_HEALTH)
    if health <= 0:
        return
    ratio = health / max_health

    BAR_Y_OFFSET = 90
    BAR_WIDTH = 40

    glPushMatrix()
    glTranslatef(enemy["x"], enemy["y"] + BAR_Y_OFFSET, enemy["z"])

    glColor3f(0.15, 0.15, 0.15)
    glPushMatrix(); glScalef(BAR_WIDTH, 6, 4); glutSolidCube(1); glPopMatrix()

    glColor3f(1.0, 0.0, 0.0)
    glPushMatrix()
    glTranslatef(-BAR_WIDTH / 2.0 + (BAR_WIDTH / 2.0 * ratio), 0, -1)
    glScalef(BAR_WIDTH * ratio, 6, 5)
    glutSolidCube(1)
    glPopMatrix()

    glPopMatrix()


def draw_single_enemy(enemy):
    if enemy.get("defeated", False):
        return
    if enemy["type"] == "ultron":
        draw_ultron(enemy)
    elif enemy["type"] == "chitauri":
        draw_chitauri(enemy)
    draw_enemy_health_bar(enemy)


def draw_enemies():
    # Feature 2.2
    for enemy in enemies:
        draw_single_enemy(enemy)


def draw_bullet_shape(radius, quad=None):
    if quad is None:
        quad = gluNewQuadric()
    body_len = radius * 3.0
    nose_len = radius * 1.8
    half = body_len / 2.0

    glPushMatrix()
    glTranslatef(0, 0, -half)
    gluSphere(quad, radius, 10, 8)
    glPopMatrix()

    glPushMatrix()
    glTranslatef(0, 0, -half)
    gluCylinder(quad, radius, radius, body_len, 10, 1)
    glPopMatrix()

    glPushMatrix()
    glTranslatef(0, 0, half)
    gluCylinder(quad, radius, radius * 0.12, nose_len, 10, 1)
    glPopMatrix()


def draw_single_enemy_projectile(projectile):
    glPushMatrix()
    if projectile.get("type") == "ultron":
        glColor3f(1.0, 0.0, 0.0)
    else:
        glColor3f(0.8, 0.9, 0.2)
    glTranslatef(projectile["x"], projectile["y"], projectile["z"])
    angle = math.degrees(math.atan2(projectile["dx"], projectile["dz"]))
    glRotatef(angle, 0, 1, 0)
    draw_bullet_shape(ENEMY_PROJECTILE_RADIUS)
    glPopMatrix()


def draw_enemy_projectiles():
    for projectile in enemy_projectiles:
        draw_single_enemy_projectile(projectile)


# Feature 2.2


GUARD_RING_RADIUS = 110
GUARD_TYPES = ("ultron", "chitauri")


def create_enemy():
    global enemies
    enemies = []
    guard_id = 0
    for stone in stones:
        if stone["gate"] is not None:
            continue
        guard_count = 2 if guard_id % 2 == 0 else 3
        for g in range(guard_count):
            angle = math.radians(g * (360.0 / guard_count) + guard_id * 37)
            gx = stone["x"] + math.cos(angle) * GUARD_RING_RADIUS
            gz = stone["z"] + math.sin(angle) * GUARD_RING_RADIUS
            enemy_type = GUARD_TYPES[(guard_id + g) % 2]
            enemies.append({
                "type": enemy_type, "x": gx, "y": 0.0, "z": gz, "angle": 0.0,
                "guard_x": gx, "guard_z": gz,
                "health": ENEMY_MAX_HEALTH, "max_health": ENEMY_MAX_HEALTH,
                "defeated": False,
            })
        guard_id += 1


def all_enemies_defeated():
    if len(enemies) == 0:
        return True
    return all(e.get("defeated", False) for e in enemies)


# Features 2.2, 2.3, 2.5

def update_enemy_movement():
    for enemy in enemies:
        if enemy.get("defeated", False):
            continue
        dx = pl_x - enemy["x"]
        dz = pl_z - enemy["z"]
        distance = math.sqrt(dx * dx + dz * dz)
        if distance <= 0:
            continue
        enemy["angle"] = math.degrees(math.atan2(dx, dz))


def enemy_hit_check():
    # Feature 2.4
    global score
    for enemy in enemies:
        if enemy.get("defeated", False):
            continue
        for projectile in projectiles:
            dx = enemy["x"] - projectile["x"]
            dz = enemy["z"] - projectile["z"]
            distance = math.sqrt(dx * dx + dz * dz)
            if distance <= ENEMY_HIT_DISTANCE:
                enemy["health"] -= 25
                if projectile in projectiles:
                    projectiles.remove(projectile)
                if enemy["health"] <= 0:
                    enemy["health"] = 0
                    enemy["defeated"] = True
                    score += 100
                break


def enemy_attack():
    # Feature 2.3
    global enemy_attack_counter
    enemy_attack_counter += 1
    if enemy_attack_counter < ENEMY_ATTACK_COOLDOWN:
        return
    enemy_attack_counter = 0

    for enemy in enemies:
        if enemy.get("defeated", False):
            continue
        dx = pl_x - enemy["x"]
        dz = pl_z - enemy["z"]
        distance = math.sqrt(dx * dx + dz * dz)
        if distance <= 1:
            continue
        if distance <= ENEMY_ATTACK_DISTANCE:
            enemy_projectiles.append({
                "x": enemy["x"], "y": 100.0, "z": enemy["z"],
                "dx": dx / distance, "dz": dz / distance,
                "type": enemy["type"],
            })


def update_enemy_projectiles():
    for projectile in enemy_projectiles:
        projectile["x"] += projectile["dx"] * ENEMY_PROJECTILE_SPEED
        projectile["z"] += projectile["dz"] * ENEMY_PROJECTILE_SPEED
    enemy_projectiles[:] = [
        p for p in enemy_projectiles
        if abs(p["x"]) < GRID_LENGTH and abs(p["z"]) < GRID_LENGTH
    ]


def enemy_collision_damage():
    # Feature 2.5
    global enemy_damage_counter, player_health
    enemy_damage_counter += 1
    if enemy_damage_counter < ENEMY_DAMAGE_COOLDOWN:
        return
    for enemy in enemies:
        if enemy.get("defeated", False):
            continue
        dx = pl_x - enemy["x"]
        dz = pl_z - enemy["z"]
        distance = math.sqrt(dx * dx + dz * dz)
        if distance <= ENEMY_DAMAGE_DISTANCE:
            if not shield_active and not cheat_mode:
                player_health -= ENEMY_DAMAGE
                if player_health < 0:
                    player_health = 0
            enemy_damage_counter = 0
            break


def enemy_projectile_damage():
    global player_health
    hit_projectiles = []
    for projectile in enemy_projectiles:
        dx = pl_x - projectile["x"]
        dz = pl_z - projectile["z"]
        distance = math.sqrt(dx * dx + dz * dz)
        if distance <= 40:
            if not shield_active and not cheat_mode:
                player_health -= ENEMY_PROJECTILE_DAMAGE
                if player_health < 0:
                    player_health = 0
            hit_projectiles.append(projectile)
    for projectile in hit_projectiles:
        if projectile in enemy_projectiles:
            enemy_projectiles.remove(projectile)


def check_player_death():
    global GAME_STATE
    if player_health <= 0 and GAME_STATE == "PLAYING":
        GAME_STATE = "GAME_OVER"


# Feature 2.10

def draw_thanos():
    if not boss["active"] or boss["defeated"]:
        return

    glPushMatrix()
    glTranslatef(boss["x"], boss["y"], boss["z"])
    glRotatef(boss["angle"], 0, 1, 0)

    glColor3f(0.35, 0.18, 0.45)
    glPushMatrix(); glTranslatef(0, 120, 0); glScalef(80, 110, 50); glutSolidCube(1); glPopMatrix()

    glColor3f(0.20, 0.12, 0.30)
    glPushMatrix(); glTranslatef(0, 55, 0); glScalef(60, 50, 40); glutSolidCube(1); glPopMatrix()

    glColor3f(0.45, 0.28, 0.55)
    glPushMatrix(); glTranslatef(0, 240, 0); glScalef(65, 70, 60); gluSphere(gluNewQuadric(), 1, 16, 12); glPopMatrix()

    glColor3f(0.28, 0.15, 0.35)
    glPushMatrix(); glTranslatef(0, 225, -48); glScalef(45, 35, 10); glutSolidCube(1); glPopMatrix()

    glColor3f(1.0, 0.1, 0.1)
    glPushMatrix(); glTranslatef(-20, 250, -53); glScalef(12, 6, 5); glutSolidCube(1); glPopMatrix()
    glPushMatrix(); glTranslatef(20, 250, -53); glScalef(12, 6, 5); glutSolidCube(1); glPopMatrix()

    glColor3f(0.30, 0.16, 0.40)
    glPushMatrix(); glTranslatef(-100, 125, 0); glRotatef(-10, 0, 0, 1); glScalef(35, 100, 35); glutSolidCube(1); glPopMatrix()
    glPushMatrix(); glTranslatef(100, 125, 0); glRotatef(10, 0, 0, 1); glScalef(35, 100, 35); glutSolidCube(1); glPopMatrix()

    glColor3f(0.22, 0.12, 0.28)
    glPushMatrix(); glTranslatef(-35, 5, 0); glScalef(40, 100, 40); glutSolidCube(1); glPopMatrix()
    glPushMatrix(); glTranslatef(35, 5, 0); glScalef(40, 100, 40); glutSolidCube(1); glPopMatrix()

    glPopMatrix()


def update_boss():
    if not portal_active or boss["defeated"]:
        return

    if not boss["active"]:
        boss["active"] = True
        boss["health"] = BOSS_MAX_HEALTH
        boss["x"], boss["y"], boss["z"] = 0.0, 0.0, 500.0

    dx = pl_x - boss["x"]
    dz = pl_z - boss["z"]
    distance = math.sqrt(dx * dx + dz * dz)
    if distance <= 0:
        return
    boss["angle"] = math.degrees(math.atan2(dx, dz))


def boss_attack():
    global boss_attack_counter
    if not boss["active"] or boss["defeated"]:
        return
    boss_attack_counter += 1
    if boss_attack_counter < BOSS_ATTACK_COOLDOWN:
        return
    boss_attack_counter = 0

    dx = pl_x - boss["x"]
    dz = pl_z - boss["z"]
    distance = math.sqrt(dx * dx + dz * dz)
    if distance <= 1:
        return
    if distance <= BOSS_ATTACK_DISTANCE:
        boss_projectiles.append({
            "x": boss["x"], "y": 130.0, "z": boss["z"],
            "dx": dx / distance, "dz": dz / distance,
        })


def draw_single_boss_projectile(projectile):
    glPushMatrix()
    glColor3f(0.6, 0.2, 1.0)
    glTranslatef(projectile["x"], projectile["y"], projectile["z"])
    angle = math.degrees(math.atan2(projectile["dx"], projectile["dz"]))
    glRotatef(angle, 0, 1, 0)
    draw_bullet_shape(BOSS_PROJECTILE_RADIUS)
    glPopMatrix()


def draw_boss_projectiles():
    for projectile in boss_projectiles:
        draw_single_boss_projectile(projectile)


def update_boss_projectiles():
    for projectile in boss_projectiles:
        projectile["x"] += projectile["dx"] * BOSS_PROJECTILE_SPEED
        projectile["z"] += projectile["dz"] * BOSS_PROJECTILE_SPEED
    boss_projectiles[:] = [
        p for p in boss_projectiles
        if abs(p["x"]) < GRID_LENGTH and abs(p["z"]) < GRID_LENGTH
    ]


def boss_projectile_damage():
    global player_health
    hit_projectiles = []
    for projectile in boss_projectiles:
        dx = pl_x - projectile["x"]
        dz = pl_z - projectile["z"]
        distance = math.sqrt(dx * dx + dz * dz)
        if distance <= 50:
            if not shield_active and not cheat_mode:
                player_health -= BOSS_PROJECTILE_DAMAGE
                if player_health < 0:
                    player_health = 0
            hit_projectiles.append(projectile)
    for projectile in hit_projectiles:
        if projectile in boss_projectiles:
            boss_projectiles.remove(projectile)


def boss_collision_damage():
    global boss_damage_counter, player_health
    if not boss["active"] or boss["defeated"]:
        return
    boss_damage_counter += 1
    if boss_damage_counter < BOSS_DAMAGE_COOLDOWN:
        return
    dx = pl_x - boss["x"]
    dz = pl_z - boss["z"]
    distance = math.sqrt(dx * dx + dz * dz)
    if distance <= BOSS_DAMAGE_DISTANCE:
        if not shield_active and not cheat_mode:
            player_health -= BOSS_COLLISION_DAMAGE
            if player_health < 0:
                player_health = 0
        boss_damage_counter = 0


def boss_hit_check():
    if not boss["active"] or boss["defeated"]:
        return
    hit_projectiles = []
    for projectile in projectiles:
        dx = boss["x"] - projectile["x"]
        dz = boss["z"] - projectile["z"]
        distance = math.sqrt(dx * dx + dz * dz)
        if distance <= BOSS_HIT_DISTANCE:
            boss["health"] -= 1
            hit_projectiles.append(projectile)
            if boss["health"] <= 0:
                boss["health"] = 0
                boss["defeated"] = True
                boss["active"] = False
                boss_projectiles.clear()
                trigger_victory()
    for projectile in hit_projectiles:
        if projectile in projectiles:
            projectiles.remove(projectile)


def draw_boss_health_bar():
    if not boss["active"] or boss["defeated"]:
        return
    ratio = boss["health"] / BOSS_MAX_HEALTH

    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    gluOrtho2D(0, 1000, 0, 800)
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()

    glColor3f(0.15, 0.15, 0.15)
    glBegin(GL_QUADS)
    glVertex3f(300, 730, 0); glVertex3f(700, 730, 0); glVertex3f(700, 750, 0); glVertex3f(300, 750, 0)
    glEnd()

    glColor3f(0.8, 0.0, 0.8)
    glBegin(GL_QUADS)
    glVertex3f(300, 730, 0)
    glVertex3f(300 + 400 * ratio, 730, 0)
    glVertex3f(300 + 400 * ratio, 750, 0)
    glVertex3f(300, 750, 0)
    glEnd()

    glMatrixMode(GL_MODELVIEW)
    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)


def trigger_victory():
    global GAME_STATE, score
    GAME_STATE = "VICTORY"
    score += int(game_timer) * 10


def clear_all_combat_projectiles():
    enemy_projectiles.clear()
    boss_projectiles.clear()
    projectiles.clear()


def reset_arnob_combat():
    global enemy_attack_counter, enemy_damage_counter
    global boss_attack_counter, boss_damage_counter

    enemy_attack_counter = 0
    enemy_damage_counter = 0
    boss_attack_counter = 0
    boss_damage_counter = 0

    clear_all_combat_projectiles()

    boss["x"], boss["y"], boss["z"], boss["angle"] = 0.0, 0.0, 500.0, 0.0
    boss["health"] = BOSS_MAX_HEALTH
    boss["active"] = False
    boss["defeated"] = False

    create_enemy()


def reset_game():
    global GAME_STATE, game_timer, player_health, score, stones_collected
    global shield_active, shield_timer, cheat_mode, portal_active, projectiles
    global pl_x, pl_z, pl_angle
    global sequence_stage, ray_progress, flash_alpha, text_hold_timer, cutscene_done, portal_visible
    
    GAME_STATE = "PLAYING"
    game_timer = 300.0
    player_health = 100
    score = 0
    stones_collected = 0
    shield_active = False
    shield_timer = 0
    cheat_mode = False
    portal_active = False
    projectiles.clear()

    sequence_stage = None
    ray_progress = 0.0
    flash_alpha = 0.0
    text_hold_timer = 0.0
    cutscene_done = False
    portal_visible = True
    
    pl_x, pl_z = -900.0, -900.0
    pl_angle = 0.0
    
    stones[:] = copy.deepcopy(_INITIAL_STONES)
    health_pickups[:] = copy.deepcopy(_INITIAL_HEALTH_PICKUPS)
    gates[:] = copy.deepcopy(_INITIAL_GATES)

    reset_arnob_combat()

def draw_hud():
    # Feature 2.12
    if GAME_STATE == "START":
        draw_text(350, 450, "AVENGERS: RISE OF THE RIFT")
        draw_text(330, 400, "Press 'ENTER' to start the mission")
        return
        
    if GAME_STATE == "GAME_OVER":
        draw_text(400, 450, "GAME OVER!")
        draw_text(360, 400, "Press 'ENTER' to try again.")
        return
        
    if GAME_STATE == "VICTORY":
        draw_text(400, 450, "VICTORY!")
        draw_text(300, 400, f"You escaped! Final Score: {score}")
        draw_text(360, 350, "Press 'ENTER' to play again.")
        return

    draw_text(10, 770, f"Score: {score}")
    draw_text(10, 740, f"Health: {int(player_health)}")
    draw_text(10, 710, f"Stones: {stones_collected}/{TOTAL_STONES}")
    draw_text(10, 680, f"Time Left: {int(game_timer)}s")
    
    # Feature 2.11
    if cheat_mode:
        draw_text(400, 750, "CHEAT MODE: ON")
    elif shield_active:
        draw_text(400, 750, f"SHIELD ACTIVE: {int(shield_timer)}s")

    draw_text(220, 20, "Move: W/S/A/D  | Fire: L-Click | Shield: Space | Gate: E | Cheat: C")

    draw_text(750, 770, "Yellow = Stone")
    draw_text(750, 740, "Red = Health")
    draw_text(750, 710, "Blue Box = Gate Switch")


def is_blocked_by_box(x, z):
    half = BOX_SIZE / 2.0 + 20
    for gate in gates:
        if not gate["open"]:
            if abs(x - gate["x"]) < half and abs(z - gate["z"]) < half:
                return True
    return False


def is_blocked(x, z):
    return is_blocked_by_box(x, z) or is_blocked_by_tree(x, z)


def keyboardListener(key, x, y):
    global pl_x, pl_z, pl_angle, is_moving, shield_active, shield_timer, cheat_mode, GAME_STATE

    if key == b'r' or key == b'R':
        reset_game()
        glutPostRedisplay()
        return

    if key == b'\r':
        if GAME_STATE in ("START", "GAME_OVER", "VICTORY"):
            reset_game()
        return

    if GAME_STATE != "PLAYING":
        return

    dx, dz = facing_vector(pl_angle)
    is_moving = False

    if key == b'w':
        new_x = pl_x + dx * MOVE_SPEED
        new_z = pl_z + dz * MOVE_SPEED
        if not is_blocked(new_x, pl_z):
            pl_x = new_x
        if not is_blocked(pl_x, new_z):
            pl_z = new_z
        is_moving = True
    elif key == b's':
        new_x = pl_x - dx * MOVE_SPEED
        new_z = pl_z - dz * MOVE_SPEED
        if not is_blocked(new_x, pl_z):
            pl_x = new_x
        if not is_blocked(pl_x, new_z):
            pl_z = new_z
        is_moving = True
    elif key == b'a':
        pl_angle += 4
    elif key == b'd':
        pl_angle -= 4

    elif key == b'e':
        try_activate_switch()

    # Feature 2.7
    elif key == b' ': 
        if not shield_active and not cheat_mode:
            shield_active = True
            shield_timer = 5.0

    # Feature 2.11
    elif key == b'c' or key == b'C': 
        cheat_mode = not cheat_mode
        if cheat_mode: shield_active = True

    pl_x = max(-MOVE_LIMIT, min(MOVE_LIMIT, pl_x))
    pl_z = max(-MOVE_LIMIT, min(MOVE_LIMIT, pl_z))
    glutPostRedisplay()


def specialKeyListener(key, x, y):
    global orbit_angle, orbit_height
    if key == GLUT_KEY_UP:
        orbit_height += 10
    elif key == GLUT_KEY_DOWN:
        orbit_height -= 10
    elif key == GLUT_KEY_LEFT:
        orbit_angle -= 0.05
    elif key == GLUT_KEY_RIGHT:
        orbit_angle += 0.05
    glutPostRedisplay()


def mouseListener(button, state, x, y):
    # Feature 2.4
    global projectiles
    if GAME_STATE == "PLAYING" and button == GLUT_LEFT_BUTTON and state == GLUT_DOWN:
        dx, dz = facing_vector(pl_angle)


        muzzle_offset = 34.0
        projectiles.append({
            'x': pl_x + dx * muzzle_offset,
            'z': pl_z + dz * muzzle_offset,
            'dx': dx,
            'dz': dz
        })


def update_stone_spin():
    global stone_spin
    stone_spin += 1.0
    if stone_spin >= 360:
        stone_spin = 0


def idle():
    global game_timer, GAME_STATE, player_health
    global shield_active, shield_timer, cheat_mode, walk_cycle, is_moving

    dt = 1.0 / 60.0

    if GAME_STATE == "PLAYING":
        
        # Feature 2.12
        game_timer -= dt
        if game_timer <= 0 or player_health <= 0:
            GAME_STATE = "GAME_OVER"
            
        # Feature 2.11
        if cheat_mode:
            player_health = 100
            shield_active = True
        else:
            if shield_active:
                shield_timer -= dt
                if shield_timer <= 0:
                    shield_active = False

        if is_moving:
            walk_cycle += 15 * dt
        else:
            walk_cycle = 0.0

        update_stones()
        update_health_pickups()
        update_gates()
        update_portal()

        update_player_projectiles(dt)

        update_enemy_movement()
        enemy_hit_check()
        enemy_attack()
        update_enemy_projectiles()
        enemy_collision_damage()
        enemy_projectile_damage()

        update_boss()
        boss_attack()
        update_boss_projectiles()
        boss_collision_damage()
        boss_projectile_damage()
        boss_hit_check()

        check_player_death()

    elif GAME_STATE == "PORTAL_SEQUENCE":
        update_portal_sequence(dt)

    update_stone_spin()
    update_energy_pulse()
    glutPostRedisplay()


def setupCamera():
    global camera_eye
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(fovY, 1000 / 800, 0.1, 4000)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    eye_x = math.sin(orbit_angle) * orbit_radius
    eye_z = math.cos(orbit_angle) * orbit_radius
    gluLookAt(eye_x, orbit_height, eye_z, 0, 0, 0, 0, 1, 0)
    camera_eye = (eye_x, orbit_height, eye_z)


def distance_to_camera(x, y, z):
    cx, cy, cz = camera_eye
    return math.sqrt((x - cx) ** 2 + (y - cy) ** 2 + (z - cz) ** 2)


def draw_dynamic_objects():
    entries = []

    def add(x, y, z, draw_fn):
        entries.append((distance_to_camera(x, y, z), draw_fn))

    for t in trees:
        add(t["x"], t["trunk_h"] * 0.5, t["z"], lambda t=t: draw_tree(t))
    for t in outer_trees:
        add(t["x"], t["trunk_h"] * 0.5, t["z"], lambda t=t: draw_tree(t))

    for stone in stones:
        if not stone["collected"]:
            add(stone["x"], stone["y"], stone["z"],
                lambda s=stone: draw_single_stone(s))

    for pickup in health_pickups:
        if not pickup["collected"]:
            add(pickup["x"], pickup["y"], pickup["z"],
                lambda p=pickup: draw_single_pickup(p))

    for gate in gates:
        add(gate["x"], BOX_SIZE / 2.0, gate["z"],
            lambda g=gate: draw_box_gate(g))

    add(portal_x, portal_y, portal_z, lambda: (draw_portal(), draw_portal_rays()))

    add(pl_x, pl_y + 35, pl_z, draw_player)
    for p in projectiles:
        add(p["x"], 35, p["z"], lambda p=p: draw_single_projectile(p))

    for enemy in enemies:
        if not enemy.get("defeated", False):
            add(enemy["x"], enemy["y"], enemy["z"],
                lambda e=enemy: draw_single_enemy(e))
    for projectile in enemy_projectiles:
        add(projectile["x"], projectile["y"], projectile["z"],
            lambda p=projectile: draw_single_enemy_projectile(p))

    if boss["active"] and not boss["defeated"]:
        add(boss["x"], boss["y"], boss["z"], draw_thanos)
    for projectile in boss_projectiles:
        add(projectile["x"], projectile["y"], projectile["z"],
            lambda p=projectile: draw_single_boss_projectile(p))

    entries.sort(key=lambda e: e[0], reverse=True)
    for _, draw_fn in entries:
        draw_fn()


def showScreen():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glViewport(0, 0, 1000, 800)

    if GAME_STATE in ["PLAYING", "GAME_OVER", "VICTORY", "PORTAL_SEQUENCE"]:
        setupCamera()

        draw_battlefield_environment()

        draw_dynamic_objects()

    draw_hud()
    draw_boss_health_bar()
    draw_screen_flash()
    glutSwapBuffers()


def main():
    glutInit()
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    glutInitWindowSize(1000, 800)
    glutInitWindowPosition(400, 100)
    glutCreateWindow(b"AVENGERS: RISE OF THE RIFT")


    create_enemy()

    glutDisplayFunc(showScreen)
    glutKeyboardFunc(keyboardListener)
    glutSpecialFunc(specialKeyListener)
    glutMouseFunc(mouseListener)
    glutIdleFunc(idle)

    glutMainLoop()


if __name__ == "__main__":
    main()