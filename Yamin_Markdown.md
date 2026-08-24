# Yamin's Module: Avengers: Rise of the Rift

## 🎯 Assigned Features
1. **Player Attack (Feature 4)**: Fire energy projectiles (Left Mouse) that travel in the player's facing direction and destroy enemies on collision.
2. **Temporary Avengers Shield (Feature 7)**: Activate a 5-second energy shield (Spacebar) that blocks all incoming damage. Visually represented by a translucent blue sphere.
3. **Infinity Power Cheat Mode (Feature 11)**: Toggle invincibility, infinite shield, and max health using the 'C' key. Displays "CHEAT MODE: ON" on screen.
4. **Score, Timer, and Game States (Feature 12)**: Manages "START", "PLAYING", "GAME_OVER", and "VICTORY" states. Tracks a countdown timer, score, health, and collected stones.

---

## 🛠️ Integration Guide

Follow these steps to integrate this module into your main `main.py` template:

### Step 1: Add Imports and Globals
Paste the **Global Variables** and `get_delta_time()` function near the top of your main file, alongside your other global variables (like `camera_pos`, `rand_var`, etc.).

### Step 2: Add Yamin's Functions
Copy all the functions from `yamin_part.py` and paste them into your main file (e.g., right before the `main()` function).

### Step 3: Update `keyboardListener`
Add the following checks inside your existing `keyboardListener`:
```python
    if key == b' ':
        if GAME_STATE == "PLAYING":
            activate_shield()
    elif key == b'c':
        toggle_cheat_mode()
    elif key == b'r':
        reset_game()
        create_enemy() # Re-initialize enemies if you have this function