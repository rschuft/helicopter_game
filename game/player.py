import pygame
import math

class Player(pygame.sprite.Sprite):
    def __init__(self, x=100, y=100):
        """
        Player sprite. x and y default to 100, but main.py now passes the screen center.
        The rotor blade is purely visual and does not affect collisions.
        """
        super().__init__()
        self.player_width = 60
        self.player_height = 30
        # Make base image large enough for rotor
        self.rotor_radius = max(self.player_width, self.player_height) * 1.2
        self.rotor_diameter = int(self.rotor_radius * 2)
        self.body_x = self.rotor_diameter // 2 - self.player_width // 2
        self.body_y = self.rotor_diameter // 2 - self.player_height // 2
        # Pre-render static body (NO rotor oval/circle)
        self.body_image = pygame.Surface((self.rotor_diameter, self.rotor_diameter), pygame.SRCALPHA)
        pygame.draw.ellipse(self.body_image, (0, 180, 255), (self.body_x, self.body_y, self.player_width, self.player_height))
        pygame.draw.rect(self.body_image, (0, 100, 200), (self.body_x + 40, self.body_y + 10, 15, 10), border_radius=3)
        self.image = self.body_image.copy()
        # The body_rect is used for collisions and position, not the full image
        self.body_rect = pygame.Rect(self.body_x, self.body_y, self.player_width, self.player_height)
        self.rect = self.body_rect.copy()
        self.rect.center = (x, y)
        self.pos = pygame.Vector2(x, y)
        self.angle = 0  # Facing right
        self.speed = 0
        self.max_speed = 7
        self.acceleration = 0.5
        self.rotation_speed = 4  # degrees per frame
        # Rotor animation
        self.rotor_angle = 0
        self.rotor_speed = 18  # degrees per frame

    def update(self, keys):
        # Rotation
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.angle += self.rotation_speed
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.angle -= self.rotation_speed
        # Forward/backward
        move = 0
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            move = 1
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            move = -1
        # Update speed and position
        if move != 0:
            self.speed += self.acceleration * move
        else:
            # Gradually slow down
            self.speed *= 0.92
        # Clamp speed
        if self.speed > self.max_speed:
            self.speed = self.max_speed
        if self.speed < -self.max_speed:
            self.speed = -self.max_speed
        # Move in facing direction
        rad = math.radians(self.angle)
        dx = math.cos(rad) * self.speed
        dy = -math.sin(rad) * self.speed
        self.pos.x += dx
        self.pos.y += dy
        # Update only the body_rect's center for collisions
        self.body_rect.center = (int(self.pos.x), int(self.pos.y))
        # Animate rotor
        self.rotor_angle = (self.rotor_angle + self.rotor_speed) % 360
        # Redraw image: start from static body, then draw spinning blades
        self.image = self.body_image.copy()
        center = (self.rotor_diameter // 2, self.rotor_diameter // 2)
        blade_length = int(self.rotor_radius * 0.95)
        blade_width = 8
        blade_color = (60, 60, 60, 180)
        for i in range(3):
            angle = self.rotor_angle + i * 120
            rad = math.radians(angle)
            x2 = center[0] + math.cos(rad) * blade_length
            y2 = center[1] + math.sin(rad) * blade_length
            pygame.draw.line(self.image, blade_color, center, (x2, y2), blade_width)
        # Rotate image and update self.rect for drawing
        self.image = pygame.transform.rotate(self.image, self.angle)
        self.rect = self.image.get_rect(center=self.body_rect.center)
