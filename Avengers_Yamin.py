from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import math
import time

# ================= YAMIN'S PART (Standalone Test) =================

# --- Global Variables ---
GAME_STATE = "START"  # "START", "PLAYING", "GAME_OVER", "VICTORY"
player_health = 100
score = 0
game_time = 120.0

shield_active = False
shield_timer = 0.0
SHIELD_DURATION = 5.0
cheat_mode = False

player_projectiles = []
PROJECTILE_SPEED = 15.0
last_frame_time = time.time()

# Mock player variables for testing
pl_x, pl_y, pl_z = 0, 0, 0
pl_angle = 0
stones_collected = 2

# --- Template's draw_text function ---
def draw_text(x, y, text, font=GLUT_BITMAP_HELVETICA_18): 
    glColor3f(1,1,1) 
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

# --- Yamin's Functions ---
def get_delta_time():
    global last_frame_time
    current_time = time.time()
    dt = current_time - last_frame_time
    last_frame_time = current_time
    return dt

def fire_projectile():
    global player_projectiles, pl_x, pl_y, pl_z, pl_angle
    dx = math.sin(math.radians(pl_angle))
    dy = math.cos(math.radians(pl_angle))
    dz = 0.0
    spawn_x = pl_x + dx * 30
    spawn_y = pl_y + dy * 30
    spawn_z = pl_z + 20
    player_projectiles.append([spawn_x, spawn_y, spawn_z, dx, dy, dz])

def update_projectiles(delta_time):
    global player_projectiles
    for p in player_projectiles:
        p[0] += p[3] * PROJECTILE_SPEED * delta_time
        p[1] += p[4] * PROJECTILE_SPEED * delta_time
        p[2] += p[5] * PROJECTILE_SPEED * delta_time
    GRID_LIMIT = 600
    player_projectiles = [p for p in player_projectiles if abs(p[0]) < GRID_LIMIT and abs(p[1]) < GRID_LIMIT]

def activate_shield():
    global shield_active, shield_timer, cheat_mode
    if not cheat_mode:
        shield_active = True
        shield_timer = SHIELD_DURATION

def update_shield(delta_time):
    global shield_active, shield_timer, cheat_mode
    if cheat_mode:
        shield_active = True
        return
    if shield_active:
        shield_timer -= delta_time
        if shield_timer <= 0:
            shield_active = False
            shield_timer = 0.0

def draw_shield():
    global pl_x, pl_y, pl_z, shield_active, cheat_mode
    if shield_active or cheat_mode:
        glColor4f(0.0, 0.5, 1.0, 0.3) # Blue, 30% transparent
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glPushMatrix()
        glTranslatef(pl_x, pl_y, pl_z + 20)
        glutSolidSphere(50, 20, 20)
        glPopMatrix()
        glDisable(GL_BLEND)

def toggle_cheat_mode():
    global cheat_mode, player_health, shield_active
    cheat_mode = not cheat_mode
    if cheat_mode:
        player_health = 9999
        shield_active = True
        print("CHEAT MODE: ON")
    else:
        player_health = 100
        shield_active = False
        print("CHEAT MODE: OFF")

def update_game_state(delta_time):
    global GAME_STATE, game_time, player_health
    if GAME_STATE == "PLAYING":
        game_time -= delta_time
        if game_time <= 0:
            game_time = 0
            GAME_STATE = "GAME_OVER"
        if player_health <= 0 and not cheat_mode:
            GAME_STATE = "GAME_OVER"

def reset_game():
    global GAME_STATE, player_health, score, game_time, shield_active, shield_timer, cheat_mode, player_projectiles
    GAME_STATE = "PLAYING"
    player_health = 100
    score = 0
    game_time = 120.0
    shield_active = False
    shield_timer = 0.0
    cheat_mode = False
    player_projectiles = []

def draw_hud():
    global GAME_STATE, game_time, player_health, score, cheat_mode, stones_collected
    if GAME_STATE in ["PLAYING", "GAME_OVER", "VICTORY"]:
        draw_text(10, 770, f"Score: {score}")
        draw_text(10, 740, f"Health: {int(player_health)}")
        draw_text(10, 710, f"Stones: {stones_collected}/6")
        draw_text(10, 680, f"Time: {int(game_time)}s")
        if cheat_mode:
            draw_text(10, 650, "CHEAT MODE: ON")
            
    if GAME_STATE == "START":
        draw_text(300, 450, "AVENGERS: RISE OF THE RIFT")
        draw_text(380, 400, "Press 'R' to Start")
    elif GAME_STATE == "GAME_OVER":
        draw_text(420, 400, "GAME OVER")
        draw_text(380, 350, "Press 'R' to Restart")
    elif GAME_STATE == "VICTORY":
        draw_text(380, 400, "VICTORY!")
        draw_text(320, 350, "The Universe is Saved!")
        draw_text(380, 300, "Press 'R' to Restart")

def draw_projectiles():
    glColor3f(0.0, 1.0, 1.0) # Cyan energy color
    for p in player_projectiles:
        glPushMatrix()
        glTranslatef(p[0], p[1], p[2])
        glutSolidSphere(5, 10, 10)
        glPopMatrix()

# ================= GLUT CALLBACKS =================

def keyboardListener(key, x, y):
    global GAME_STATE, pl_angle
    if key == b'r':
        reset_game()
    elif key == b'c':
        toggle_cheat_mode()
    elif key == b' ':
        if GAME_STATE == "PLAYING":
            activate_shield()
    elif key == b'w':
        pl_angle += 15 # Simulate turning
    glutPostRedisplay()

def mouseListener(button, state, x, y):
    global GAME_STATE
    if button == GLUT_LEFT_BUTTON and state == GLUT_DOWN:
        if GAME_STATE == "PLAYING":
            fire_projectile()
    glutPostRedisplay()

def idle():
    dt = get_delta_time()
    update_projectiles(dt)
    update_shield(dt)
    update_game_state(dt)
    glutPostRedisplay()

def showScreen():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()
    glViewport(0, 0, 1000, 800)
    
    # Simple 3D setup matching your template's camera
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(120, 1000/800, 0.1, 1500)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    gluLookAt(0, 500, 500, 0, 0, 0, 0, 0, 1)
    
    # 1. Draw 3D elements
    draw_projectiles()
    draw_shield()
    
    # 2. Draw 2D HUD (draw_text handles its own matrix reset)
    draw_hud()
    
    glutSwapBuffers()

def main():
    glutInit()
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    glutInitWindowSize(1000, 800)
    glutInitWindowPosition(0, 0)
    glutCreateWindow(b"Yamin's Part Test")
    
    glEnable(GL_DEPTH_TEST)
    
    glutDisplayFunc(showScreen)
    glutKeyboardFunc(keyboardListener)
    glutMouseFunc(mouseListener)
    glutIdleFunc(idle)
    
    glutMainLoop()

if __name__ == "__main__":
    main()