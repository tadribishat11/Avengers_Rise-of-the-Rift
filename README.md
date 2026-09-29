# Avengers: Rise of the Rift

**A 3D Marvel-Inspired Adventure Game**

## 1. Project Overview

Avengers: Rise of the Rift is a simple 3D action-survival game inspired by the Avengers universe. The player enters a small battlefield where six Infinity Stones are scattered in different locations. The objective is to collect all six stones, survive enemy attacks, activate the escape portal, and defeat a final boss before time runs out.

The project is built around introductory 3D OpenGL concepts: 3D primitives, transformations, animation, collision detection, keyboard and mouse input, camera control, and on-screen text.

## 2. Core Features

### 2.1 Infinity Stone Collection
Six colored Infinity Stones are placed around the battlefield. When the player reaches a stone, it is collected and removed from the map. The number of collected stones is displayed on screen, for example, `Stones: 3/6`.

### 2.2 Enemy Spawn and Movement
Several enemy characters are placed around the battlefield. Enemies stand still around the Infinity Stones. When the player comes near a stone while trying to collect it, the enemies start shooting at the player.

### 2.3 Enemy Attack
Enemies periodically attack the player. A simple projectile, such as a small red and yellow bullet (a combination of a triangle and a rectangle), is created and moved toward the player.

### 2.4 Player Attack
The player can fire energy projectiles. A projectile is created in front of the player and moves in the direction the player is facing. When it reaches an enemy, the enemy loses health or is removed.

### 2.5 Enemy Collision and Damage
The game checks the distance between the player and nearby enemies. While collecting Infinity Stones, if the player comes near or touches an enemy, the player loses health. The current health value is displayed on screen. If the player stays within range of, or in contact with, enemies for a certain amount of time, the health bar is completely drained and the player loses the game.

### 2.6 Health Pickups
Health pickup objects are placed at selected locations. When the player touches a pickup, it restores part of the player's health and disappears.

### 2.7 Temporary Avengers Shield
The player can activate a temporary energy shield. While the shield is active, enemy attacks do not reduce the player's health. A timer controls how long the shield remains active, after which it disappears automatically.

### 2.8 Locked Areas and Stone Gates
Some parts of the battlefield are separated by simple gates. A gate remains closed until the player activates a nearby switch.

### 2.9 Portal Activation
The escape portal remains inactive until all six Infinity Stones have been collected. After the final stone is collected, the portal becomes active.

### 2.10 Final Boss Battle
After activating the portal, the player must defeat a Thanos-style final boss. The player wins this stage by hitting the boss a fixed number of times.

### 2.11 Infinity Power Cheat Mode
Pressing **C** toggles Cheat Mode. While it is active:

- All six Infinity Stones become visible through glowing markers.
- The player's health cannot decrease.
- Energy projectiles are unlimited.
- The temporary shield remains active.
- Enemies continue to move and attack, but their attacks cannot damage the player.
- The screen displays `CHEAT MODE: ON`.

Pressing **C** again returns the game to normal gameplay.

### 2.12 Score, Timer, and Game States
The game displays score, health, collected stones, and remaining time. It has four states: **Start**, **Playing**, **Victory**, and **Game Over**. The player wins after collecting all stones and defeating the final boss. The player loses when health reaches zero or the timer expires.

## 3. Controls

| Key / Input | Action |
| --- | --- |
| `W` / `S` | Move forward / backward |
| `A` / `D` | Rotate or move the player left / right |
| Left Mouse | Fire an energy projectile |
| `Space` | Activate the temporary shield |
| Arrow Keys | Adjust the camera angle or height |
| `E` | Open locked areas or stone gates |
| `R` | Restart the game |
| `C` | Activate / deactivate Infinity Power Cheat Mode |

## 4. Win and Lose Conditions

- The player **wins** after collecting all six Infinity Stones and defeating the final boss.
- The portal becomes active only after all six stones are collected.
- The player loses health when hit by an enemy or enemy projectile.
- The game ends if the player's health reaches zero.
- The game also ends if the countdown timer reaches zero.
- Pressing `R` restarts the current game.

