from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import math
import random

# ================= TADRIB'S PART (Standalone Test) =================
# Features implemented here:
#   2.1  Infinity Stone Collection
#   2.6  Health Pickups
#   2.8  Locked Areas and Stone Gates
#   2.9  Portal Activation

random.seed(7)  # fixed seed so the battlefield layout is the same every run

# --- Global Variables (shared / merge target) ---
GAME_STATE = "PLAYING"
player_health = 100
score = 0

# --- Battlefield size ---
GRID_LENGTH = 1200
TILE = 100
MOVE_LIMIT = GRID_LENGTH - TILE

# --- Player (Y-UP: pl_x/pl_z = ground position, pl_y = height) ---
pl_x, pl_z = -900.0, -900.0
pl_y = 0.0
pl_angle = 0.0
MOVE_SPEED = 10.0

# --- Orbit camera (arrow keys) - identical scheme to A3_Task1.py ---
orbit_angle = 0.0
orbit_height = 260.0
orbit_radius = 850.0
fovY = 100

COLLECT_RADIUS = 55

# --- Infinity Stones (Feature 2.1) — exactly 6, all yellow. 2 stay
# fixed inside the glass boxes (only reachable once a box is opened via
# its switch), the other 4 are scattered randomly across the field. ---
stones_collected = 0
TOTAL_STONES = 6
STONE_COLOR = (1.0, 1.0, 0.0)

BOX_A_POS = (-300, 0)
BOX_B_POS = (300, 0)
SWITCH_A_POS = (-300, 220)
SWITCH_B_POS = (300, -220)
_PLACEMENT_MARGIN = 120          # keep clear of the outer fence
_CENTER_CLEAR_RADIUS = 300       # keep clear of the portal at (0,0)
_POINT_CLEAR_RADIUS = 150        # minimum spacing between placed items


def _sector_point(sector_index, total_sectors, avoid_points):
    """Pick a random (x, z) inside one angular slice of the field
    (360 / total_sectors degrees wide) at a random radius. Placing one
    item per sector guarantees the whole set ends up spread out evenly
    all the way around the battlefield instead of randomly clustering
    on one side."""
    sector_width = 360.0 / total_sectors
    base_angle = sector_index * sector_width
    max_radius = GRID_LENGTH - _PLACEMENT_MARGIN
    for _ in range(200):
        angle = math.radians(base_angle + random.uniform(0, sector_width))
        radius = random.uniform(_CENTER_CLEAR_RADIUS, max_radius)
        x = math.sin(angle) * radius
        z = math.cos(angle) * radius
        if any(math.hypot(x - ax, z - az) < _POINT_CLEAR_RADIUS for ax, az in avoid_points):
            continue
        return x, z
    return x, z  # fallback after max attempts, extremely unlikely to hit


_placed_points = [BOX_A_POS, BOX_B_POS, SWITCH_A_POS, SWITCH_B_POS, (0, 0), (pl_x, pl_z)]

# 4 free stones + 4 health pickups = 8 items, one per 45-degree sector
# around the whole field, in alternating order so stones and pickups
# don't end up bunched next to each other.
_sector_order = list(range(8))
random.shuffle(_sector_order)

_free_stone_spots = []
for _i in range(4):
    _pt = _sector_point(_sector_order[_i], 8, _placed_points)
    _free_stone_spots.append(_pt)
    _placed_points.append(_pt)

stones = [
    {"name": "Space Stone",   "x": BOX_A_POS[0], "z": BOX_A_POS[1], "y": 30, "color": STONE_COLOR, "collected": False},  # inside Gate A box
    {"name": "Mind Stone",    "x": BOX_B_POS[0], "z": BOX_B_POS[1], "y": 30, "color": STONE_COLOR, "collected": False},  # inside Gate B box
    {"name": "Reality Stone", "x": _free_stone_spots[0][0], "z": _free_stone_spots[0][1], "y": 30, "color": STONE_COLOR, "collected": False},
    {"name": "Power Stone",   "x": _free_stone_spots[1][0], "z": _free_stone_spots[1][1], "y": 30, "color": STONE_COLOR, "collected": False},
    {"name": "Time Stone",    "x": _free_stone_spots[2][0], "z": _free_stone_spots[2][1], "y": 30, "color": STONE_COLOR, "collected": False},
    {"name": "Soul Stone",    "x": _free_stone_spots[3][0], "z": _free_stone_spots[3][1], "y": 30, "color": STONE_COLOR, "collected": False},
]

# --- Health Pickups (Feature 2.6) — exactly 4, red, in the remaining
# 4 sectors so the full set of 8 items rings the whole battlefield ---
HEAL_AMOUNT = 25
HEALTH_COLOR = (1.0, 0.0, 0.0)

_free_pickup_spots = []
for _i in range(4, 8):
    _pt = _sector_point(_sector_order[_i], 8, _placed_points)
    _free_pickup_spots.append(_pt)
    _placed_points.append(_pt)

health_pickups = [
    {"x": _free_pickup_spots[0][0], "z": _free_pickup_spots[0][1], "y": 20, "collected": False},
    {"x": _free_pickup_spots[1][0], "z": _free_pickup_spots[1][1], "y": 20, "collected": False},
    {"x": _free_pickup_spots[2][0], "z": _free_pickup_spots[2][1], "y": 20, "collected": False},
    {"x": _free_pickup_spots[3][0], "z": _free_pickup_spots[3][1], "y": 20, "collected": False},
]

# --- Gates (Feature 2.8) — locked glass boxes. Each is opened either by
# collecting the required number of stones, OR by activating its nearby
# blue switch (walk up to it and press 'E'). The lid then swings open
# (stepped animation, no interpolation) so the stone inside can be taken.
BOX_SIZE = 90
SWITCH_SIZE = 30
SWITCH_RADIUS = 70
SWITCH_COLOR = (0.1, 0.35, 1.0)
LID_OPEN_ANGLE = 100
LID_STEP = 4
gates = [
    {
        "name": "Gate A",
        "x": BOX_A_POS[0], "z": BOX_A_POS[1],
        "switch_x": SWITCH_A_POS[0], "switch_z": SWITCH_A_POS[1],
        "required_stones": 2,
        "open": False,
        "switch_activated": False,
        "lid_angle": 0,
    },
    {
        "name": "Gate B",
        "x": BOX_B_POS[0], "z": BOX_B_POS[1],
        "switch_x": SWITCH_B_POS[0], "switch_z": SWITCH_B_POS[1],
        "required_stones": 4,
        "open": False,
        "switch_activated": False,
        "lid_angle": 0,
    },
]

# --- Portal (Feature 2.9) ---
portal_x, portal_z, portal_y = 0, 0, 220
portal_active = False
portal_spin = 0.0
portal_swirl = 0.0
stone_spin = 0.0

# ================= BATTLEFIELD =================

POLE_COUNT = 32
POLE_RING_DIST = GRID_LENGTH
POLE_HEIGHT = 300
POLE_RADIUS = 22
POLE_TILT = 12
POLE_SPACING = (GRID_LENGTH * 2) / 8.0

# pulsing "current running through it" effect for the energy barrier
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


def draw_ground():
    """Green checkered plains."""
    glBegin(GL_QUADS)
    for gx in range(-GRID_LENGTH, GRID_LENGTH, TILE):
        for gz in range(-GRID_LENGTH, GRID_LENGTH, TILE):
            checker = (gx // TILE + gz // TILE) % 2
            if checker == 0:
                glColor3f(0.16, 0.42, 0.18)
            else:
                glColor3f(0.20, 0.50, 0.22)
            glVertex3f(gx, 0, gz)
            glVertex3f(gx + TILE, 0, gz)
            glVertex3f(gx + TILE, 0, gz + TILE)
            glVertex3f(gx, 0, gz + TILE)
    glEnd()


def update_energy_pulse():
    """Simple step-based flicker (if/else logic, no interpolation math)
    so the border shield looks like current is running through it."""
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
    """Tall poles around the border connected by a glowing blue energy
    wall, like Wakanda's border force-field generators."""
    # Poles
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

    # Glowing blue energy panels connecting each pole to the next
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    glColor4f(0.1, 0.5, 1.0, energy_pulse)
    glBegin(GL_QUADS)
    for i in range(POLE_COUNT):
        x1, z1 = pole_positions[i]
        x2, z2 = pole_positions[(i + 1) % POLE_COUNT]
        glVertex3f(x1, 0, z1)
        glVertex3f(x1, POLE_HEIGHT * 0.85, z1)
        glVertex3f(x2, POLE_HEIGHT * 0.85, z2)
        glVertex3f(x2, 0, z2)
    glEnd()
    glDisable(GL_BLEND)



def draw_battlefield_environment():
    draw_ground()
    draw_border_shield()


# --- Template's draw_text function (unchanged) ---
def draw_text(x, y, text, font=GLUT_BITMAP_HELVETICA_18):
    glColor3f(1, 1, 1)
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
    """Copied exactly from A3_Task1.py."""
    rad = math.radians(angle_deg)
    return -math.sin(rad), -math.cos(rad)


# ================= FEATURE 2.1: INFINITY STONE COLLECTION =================

def update_stones():
    global stones_collected, score
    for stone in stones:
        if not stone["collected"]:
            if distance_2d(pl_x, pl_z, stone["x"], stone["z"]) < COLLECT_RADIUS:
                stone["collected"] = True
                stones_collected += 1
                score += 100
                print(f"Collected {stone['name']}! ({stones_collected}/{TOTAL_STONES})")


STONE_SCALE = (28, 28, 28)   # glutSolidOctahedron() is a fixed unit size -
                             # it must be scaled up or it's an invisible speck
                             # (kept small enough vertically to still fit
                             # inside the boxes without poking through the lid)


def draw_stones():
    for stone in stones:
        if not stone["collected"]:
            glPushMatrix()
            glColor3f(*stone["color"])
            glTranslatef(stone["x"], stone["y"], stone["z"])
            glRotatef(stone_spin, 0, 1, 0)  # slow spin so the gem catches the eye
            glScalef(*STONE_SCALE)
            glutSolidOctahedron()
            glPopMatrix()


# ================= FEATURE 2.6: HEALTH PICKUPS =================

def update_health_pickups():
    global player_health
    for pickup in health_pickups:
        if not pickup["collected"]:
            if distance_2d(pl_x, pl_z, pickup["x"], pickup["z"]) < COLLECT_RADIUS:
                pickup["collected"] = True
                player_health += HEAL_AMOUNT
                if player_health > 100:
                    player_health = 100
                print(f"Picked up health! Health: {int(player_health)}")


def draw_health_pickups():
    for pickup in health_pickups:
        if not pickup["collected"]:
            glPushMatrix()
            glColor3f(*HEALTH_COLOR)
            glTranslatef(pickup["x"], pickup["y"], pickup["z"])
            glutSolidCube(20)
            glPopMatrix()


# ================= FEATURE 2.8: LOCKED AREAS - OPENABLE BOXES =================

def try_activate_switch():
    """Called on 'E' key press. Activates the nearest blue switch if the
    player is standing close enough to it, opening that box."""
    for gate in gates:
        if not gate["switch_activated"]:
            if distance_2d(pl_x, pl_z, gate["switch_x"], gate["switch_z"]) < SWITCH_RADIUS:
                gate["switch_activated"] = True
                print(f"{gate['name']} switch activated!")


def update_gates():
    for gate in gates:
        if not gate["open"]:
            if stones_collected >= gate["required_stones"] or gate["switch_activated"]:
                gate["open"] = True
                print(f"{gate['name']} is now open!")
        # Step the lid open a bit each frame once unlocked (if/else
        # logic, no interpolation math) until it reaches full open angle.
        if gate["open"]:
            if gate["lid_angle"] < LID_OPEN_ANGLE:
                gate["lid_angle"] += LID_STEP


def draw_box_gate(gate):
    """A locked glass-walled box container. The base stays put; the lid
    is hinged at the back edge and swings open once the box unlocks.
    Both are semi-transparent so the diamond stored inside stays
    visible even while the box is locked. A blue switch box sits nearby
    - walk up to it and press 'E' to open the glass box."""
    gx, gz = gate["x"], gate["z"]
    s = BOX_SIZE
    lid_h = s * 0.25

    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

    # Base of the box (body) - transparent glass
    glPushMatrix()
    glColor4f(0.4, 0.7, 0.9, 0.35)
    glTranslatef(gx, (s - lid_h) / 2.0, gz)
    glScalef(1.0, (s - lid_h) / s, 1.0)
    glutSolidCube(s)
    glPopMatrix()

    # Hinged lid: pivot at the back edge of the box, rotates up when open
    glPushMatrix()
    glTranslatef(gx, s - lid_h, gz - s / 2.0)
    glRotatef(-gate["lid_angle"], 1, 0, 0)
    glTranslatef(0, 0, s / 2.0)
    if gate["open"]:
        glColor4f(0.55, 0.85, 1.0, 0.35)   # unlocked - brighter glass
    else:
        glColor4f(0.4, 0.7, 0.9, 0.35)
    glScalef(1.0, lid_h / s, 1.0)
    glutSolidCube(s)
    glPopMatrix()

    glDisable(GL_BLEND)

    # Blue switch box - solid, not activated it glows brighter blue,
    # once activated it dims to show it has already been used.
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


# ================= FEATURE 2.9: PORTAL ACTIVATION =================

def update_portal():
    global portal_active, portal_spin, portal_swirl
    if stones_collected >= TOTAL_STONES:
        if not portal_active:
            portal_active = True
            print("All stones collected! The portal is now ACTIVE.")
    portal_spin += 1.2
    if portal_spin >= 360:
        portal_spin = 0
    portal_swirl -= 3.5
    if portal_swirl <= -360:
        portal_swirl = 0


def draw_portal():
    """A floating vertical ring gateway (like the sky-portals in the
    Avengers movies): a solid outer ring, a thin glowing inner trim,
    a swirling semi-transparent vortex disk inside, and small embers
    orbiting the rim. Built entirely from GLU disks/cylinders and GL
    primitives - no textures."""
    outer_r = 150
    mid_r = 128
    inner_r = 118

    if portal_active:
        ring_color = (0.15, 0.85, 0.95)
        vortex_color = (0.05, 0.9, 1.0, 0.45)
        glow_color = (0.6, 1.0, 1.0)
    else:
        ring_color = (0.35, 0.35, 0.4)
        vortex_color = (0.3, 0.3, 0.35, 0.25)
        glow_color = (0.5, 0.5, 0.55)

    glPushMatrix()
    glTranslatef(portal_x, portal_y, portal_z)

    # Slow turntable spin so the whole gateway feels alive
    glRotatef(portal_spin, 0, 0, 1)

    # --- Outer stone/metal ring (a thick annulus) ---
    glColor3f(*ring_color)
    quad = gluNewQuadric()
    gluDisk(quad, mid_r, outer_r, 40, 3)

    # --- Thin bright inner trim ring, brighter than the body ---
    glColor3f(*glow_color)
    gluDisk(quad, inner_r, mid_r, 40, 2)

    # --- Swirling vortex inside the ring (semi-transparent, spins the
    # opposite way and faster, like energy churning through the gate) ---
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    glPushMatrix()
    glRotatef(portal_swirl, 0, 0, 1)
    for layer in range(3):
        r = inner_r - layer * 28
        if r <= 10:
            continue
        a = vortex_color[3] * (1.0 - layer * 0.25)
        glColor4f(vortex_color[0], vortex_color[1], vortex_color[2], a)
        gluDisk(quad, 0, r, 30, 2)
    glPopMatrix()
    glDisable(GL_BLEND)

    # --- Small glowing embers orbiting the rim ---
    EMBER_COUNT = 10
    glColor3f(*glow_color)
    for i in range(EMBER_COUNT):
        ember_angle = math.radians(i * (360.0 / EMBER_COUNT) - portal_spin * 1.5)
        ex = math.cos(ember_angle) * (outer_r + 12)
        ey = math.sin(ember_angle) * (outer_r + 12)
        glPushMatrix()
        glTranslatef(ex, ey, 6)
        gluSphere(quad, 6, 8, 8)
        glPopMatrix()

    glPopMatrix()


# ================= HUD (test-only, merge into teammate's draw_hud) =================

def draw_hud():
    draw_text(10, 770, f"Score: {score}")
    draw_text(10, 740, f"Health: {int(player_health)}")
    draw_text(10, 710, f"Stones: {stones_collected}/{TOTAL_STONES}")
    open_gates = sum(1 for g in gates if g["open"])
    draw_text(10, 680, f"Gates Open: {open_gates}/{len(gates)}")
    draw_text(10, 650, f"Portal: {'ACTIVE' if portal_active else 'inactive'}")
    draw_text(220, 20, "Move: W/S/A/D  |  Camera: Arrow Keys  |  Switch: E")

    # --- Color legend, top-right corner (same font size as top-left HUD) ---
    draw_text(650, 770, "Yellow = Infinity Stone")
    draw_text(650, 740, "Red = Health Pickups")
    draw_text(650, 710, "Blue Box = Gate Switch")



# ================= GLUT CALLBACKS (copied exactly from A3_Task1.py) =================

def keyboardListener(key, x, y):
    global pl_x, pl_z, pl_angle
    dx, dz = facing_vector(pl_angle)
    if key == b'w':
        pl_x += dx * MOVE_SPEED
        pl_z += dz * MOVE_SPEED
    elif key == b's':
        pl_x -= dx * MOVE_SPEED
        pl_z -= dz * MOVE_SPEED
    elif key == b'a':
        pl_angle += 3
    elif key == b'd':
        pl_angle -= 3
    elif key == b'e':
        try_activate_switch()
    pl_x = max(-MOVE_LIMIT, min(MOVE_LIMIT, pl_x))
    pl_z = max(-MOVE_LIMIT, min(MOVE_LIMIT, pl_z))
    glutPostRedisplay()


def specialKeyListener(key, x, y):
    """Identical to A3_Task1.py's specialKeyListener."""
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
    # Reserved for player attack (Feature 2.4), handled by another teammate.
    pass


def update_stone_spin():
    global stone_spin
    stone_spin += 1.0
    if stone_spin >= 360:
        stone_spin = 0


def idle():
    if GAME_STATE == "PLAYING":
        update_stones()
        update_health_pickups()
        update_gates()
        update_portal()
    update_stone_spin()
    update_energy_pulse()
    glutPostRedisplay()


def setupCamera():
    """Identical formula to A3_Task1.py's setupCamera (non-first-person
    branch): orbit_angle/orbit_height/orbit_radius, Y-up."""
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(fovY, 1000 / 800, 0.1, 4000)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    eye_x = math.sin(orbit_angle) * orbit_radius
    eye_z = math.cos(orbit_angle) * orbit_radius
    gluLookAt(eye_x, orbit_height, eye_z, 0, 0, 0, 0, 1, 0)


def showScreen():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glViewport(0, 0, 1000, 800)

    setupCamera()

    draw_battlefield_environment()
    draw_stones()
    draw_health_pickups()
    draw_gates()
    draw_portal()

    draw_hud()

    glutSwapBuffers()


def main():
    glutInit()
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    glutInitWindowSize(1000, 800)
    glutInitWindowPosition(400, 100)
    glutCreateWindow(b"AVENGERS: RISE OF THE RIFT")

    glEnable(GL_DEPTH_TEST)

    glutDisplayFunc(showScreen)
    glutKeyboardFunc(keyboardListener)
    glutSpecialFunc(specialKeyListener)
    glutMouseFunc(mouseListener)
    glutIdleFunc(idle)

    glutMainLoop()


if __name__ == "__main__":
    main()
