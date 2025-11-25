import pygame
import random
import math
from colorsys import hsv_to_rgb

# Initialize Pygame
pygame.init()

# Screen settings
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Advanced Particle Animation")
clock = pygame.time.Clock()
FPS = 60

# Particle class
class Particle:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.size = random.uniform(2, 6)
        self.color = (255, 255, 255)
        self.hue = random.random()
        self.speed = random.uniform(1, 4)
        self.angle = random.uniform(0, 2 * math.pi)
        self.lifetime = random.randint(60, 120)
        self.age = 0
        self.glow = pygame.Surface((self.size * 4, self.size * 4), pygame.SRCALPHA)
        self.update_glow()

    def update_glow(self):
        self.glow.fill((0, 0, 0, 0))
        glow_color = hsv_to_rgb(self.hue, 0.8, 1.0)
        glow_color = (int(glow_color[0] * 255), int(glow_color[1] * 255), int(glow_color[2] * 255))
        pygame.draw.circle(self.glow, (*glow_color, 100), (self.size * 2, self.size * 2), self.size * 2)
        pygame.draw.circle(self.glow, (*glow_color, 255), (self.size * 2, self.size * 2), self.size)

    def update(self, mouse_pos):
        self.age += 1
        # Move towards mouse with some randomness
        dx = mouse_pos[0] - self.x
        dy = mouse_pos[1] - self.y
        distance = math.hypot(dx, dy)
        if distance > 10:
            attraction = 0.02 * self.speed
            self.x += dx * attraction + math.cos(self.angle) * self.speed
            self.y += dy * attraction + math.sin(self.angle) * self.speed
        self.hue = (self.hue + 0.01) % 1.0
        self.update_glow()
        return self.age < self.lifetime

    def draw(self, surface):
        surface.blit(self.glow, (self.x - self.size * 2, self.y - self.size * 2), special_flags=pygame.BLEND_RGBA_ADD)

# Gradient background
def create_gradient_background():
    background = pygame.Surface((WIDTH, HEIGHT))
    for y in range(HEIGHT):
        t = y / HEIGHT
        color = (
            int(20 + 80 * t),
            int(20 + 100 * t),
            int(100 + 155 * t)
        )
        pygame.draw.line(background, color, (0, y), (WIDTH, y))
    return background

# Main loop
def main():
    particles = []
    background = create_gradient_background()
    running = True
    mouse_pos = (WIDTH // 2, HEIGHT // 2)

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEMOTION:
                mouse_pos = event.pos

        # Add new particles
        if random.random() < 0.3:
            particles.append(Particle(random.randint(0, WIDTH), random.randint(0, HEIGHT)))

        # Update and draw
        screen.blit(background, (0, 0))
        particles = [p for p in particles if p.update(mouse_pos)]
        for particle in particles:
            particle.draw(screen)

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()

if __name__ == "__main__":
    main()