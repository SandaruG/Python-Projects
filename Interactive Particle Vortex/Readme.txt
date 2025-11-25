Project Name: Interactive Particle Vortex

Description:
A visually dynamic particle animation built using Python and Pygame. This project creates hundreds of glowing particles that drift, swirl, and move toward the mouse cursor while cycling through vivid HSV-based colors. The effect resembles a neon particle vortex with smooth motion, gradient background, and additive-blend glow rendering.

This program demonstrates advanced particle physics, color transitions, and GPU-friendly rendering techniques using Pygame’s alpha-blended surfaces.

--------------------------------------------------------------------

Features:
- Interactive particle attraction using mouse position.
- Each particle has:
  - Glow effect built using layered alpha circles.
  - Dynamic hue cycling (HSV → RGB conversion).
  - Randomized speed, size, direction, and lifetime.
- Additive blending for intense glow effects.
- Smooth gradient background.
- Highly optimized rendering loop.
- Customizable frame rate and screen size.
- Fully portable (runs on any OS with Python + Pygame).

--------------------------------------------------------------------

Technologies Used:
- Python 3
- Pygame
- Math / HSV-to-RGB color manipulation
- Alpha-blended surfaces (for glow)

--------------------------------------------------------------------

Installation:

1. Install Python (https://python.org)
2. Install Pygame:
   pip install pygame

3. Run the script:
   python main.py

--------------------------------------------------------------------

Controls:
- Move your mouse anywhere on the screen.
- Particles are attracted toward the cursor.
- Closing the window ends the program.

--------------------------------------------------------------------

How It Works:

1. Particles are randomly generated around the screen.
2. Each particle:
   - Moves with a mix of randomness and attraction force.
   - Cycles its hue for rainbow-like transitions.
   - Renders with a glow using additive blending.
3. The gradient background refreshes each frame for a smooth layered appearance.
4. Dead particles (expired lifetime) are removed automatically to keep performance high.

--------------------------------------------------------------------

File Structure:

interactive-particle-vortex/
│── main.py
│── README.txt

--------------------------------------------------------------------

Customization:

You can modify several settings at the top of the script:

SCREEN SIZE:
WIDTH, HEIGHT = 800, 600

PARTICLE SPAWNING RATE:
if random.random() < 0.3:

PARTICLE PROPERTIES:
size, hue, speed, angle, lifetime

GRADIENT BACKGROUND:
Modify create_gradient_background() function.

--------------------------------------------------------------------

Performance Notes:
- Runs smoothly at 60 FPS on most systems.
- Particle list is automatically pruned every frame.
- Uses separate surfaces to avoid redraw artifacts.

--------------------------------------------------------------------

License:
You are free to modify and use this project for learning or artistic purposes.

--------------------------------------------------------------------

Contact:
If you want a more advanced version (e.g., GPU particles, shaders, sound-reactive particles, 4K mode), feel free to request an upgrade.
