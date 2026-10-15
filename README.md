# Python Auto Defense: Overdrive

A vertical neon sci-fi auto-defense shooter inspired by the uploaded video, expanded with more combat systems and progression.

## Features
- Neon sci-fi vertical arena with 9 lanes and animated starfield
- Auto-fire dual cannons and escalating enemy waves
- Three enemy types: scout, swift and tank
- Score, saved best score, combo multiplier, hull health and wave progression
- Random upgrades: rapid fire, spread shot, shield, hull repair, homing drones and Nexus Pulse
- Particle bursts, hit feedback, glowing projectiles and power-up effects
- Keyboard, mouse and touch movement
- Pause, restart and fullscreen
- GitHub Actions workflow builds a Windows EXE artifact

## Run locally
```bash
python -m pip install pygame
python python_auto_defense.py
```

## Build using GitHub mobile
1. Upload `python_auto_defense.py` to the repository root.
2. Create `.github/workflows/main.yml`.
3. Paste the contents of the provided `main.yml`.
4. Commit to `main` or `master`.
5. Open **Actions** and run **Python Auto Defense Build** if it did not start automatically.
6. Download the `Python-Auto-Defense-Windows` artifact after a successful run.

This workflow creates a Windows EXE, not an Android APK.
