import pygame
import random
import numpy as np
import math

class EngineSound:
    def __init__(self, base_freq=80, move_freq=120, volume=0.2, duration=1.0, sample_rate=44100):
        self.base_freq = base_freq
        self.move_freq = move_freq
        self.volume = volume
        self.duration = duration
        self.sample_rate = sample_rate
        self.base_sound = self._generate_rumble(self.base_freq)
        self.move_sound = self._generate_rumble(self.move_freq)
        self.channel = None

    def _generate_rumble(self, freq):
        t = np.linspace(0, self.duration, int(self.sample_rate * self.duration), False)
        # Rumble: sum of two close sine waves for beating, plus noise
        wave = 0.7 * np.sin(2 * np.pi * freq * t) + 0.3 * np.sin(2 * np.pi * (freq + 2) * t)
        wave += 0.1 * np.random.normal(0, 1, t.shape)
        wave = (wave * 32767 * self.volume).astype(np.int16)
        # Ensure stereo output for the mixer (2D array)
        if wave.ndim == 1:
            wave = np.column_stack((wave, wave))
        sound = pygame.sndarray.make_sound(wave)
        sound.set_volume(self.volume)
        return sound

    def play(self, moving=False):
        if self.channel is None or not self.channel.get_busy():
            self.channel = self.base_sound.play(loops=-1)
        self.set_pitch(moving)

    def set_pitch(self, moving):
        if self.channel is not None:
            if moving:
                self.channel.stop()
                self.channel = self.move_sound.play(loops=-1)
            else:
                self.channel.stop()
                self.channel = self.base_sound.play(loops=-1)

    def stop(self):
        if self.channel is not None:
            self.channel.stop()
            self.channel = None

def generate_explosion_sound(duration=0.3, sample_rate=44100, volume=0.5):
    t = np.linspace(0, duration, int(sample_rate * duration), False)
    # White noise burst, envelope for fade out
    noise = np.random.normal(0, 1, t.shape)
    envelope = np.exp(-5 * t)
    wave = noise * envelope
    wave = (wave * 32767 * volume).astype(np.int16)
    if wave.ndim == 1:
        wave = np.column_stack((wave, wave))
    return pygame.sndarray.make_sound(wave)

def generate_bullet_fire_sound(duration=0.18, freq=180, sample_rate=44100, volume=0.7):
    import numpy as np
    t = np.linspace(0, duration, int(sample_rate * duration), False)
    # Lower-pitched, percussive boom: sine + noise, fast decay
    envelope = np.exp(-8 * t)
    wave = 0.7 * np.sin(2 * np.pi * freq * t) * envelope
    wave += 0.3 * np.random.normal(0, 0.7, t.shape) * envelope
    wave = (wave * 32767 * volume).astype(np.int16)
    if wave.ndim == 1:
        wave = np.column_stack((wave, wave))
    return pygame.sndarray.make_sound(wave)

class Enemy(pygame.sprite.Sprite):
    def __init__(self, width, height):
        super().__init__()
        self.width = width
        self.height = height
        self.enemy_width = 40
        self.enemy_height = 40
        self.image = pygame.Surface((self.enemy_width, self.enemy_height), pygame.SRCALPHA)
        pygame.draw.rect(self.image, (200, 0, 0), (0, 0, self.enemy_width, self.enemy_height), border_radius=8)
        pygame.draw.rect(self.image, (255, 255, 0), (10, 10, 20, 20), border_radius=4)
        self.rect = self.image.get_rect()
        self.rect.x = random.randint(0, width - self.rect.width)
        self.rect.y = random.randint(-150, -40)
        self.speedy = random.randint(3, 7)

    def update(self):
        self.rect.y += self.speedy
        if self.rect.top > self.height:
            self.rect.y = random.randint(-100, -40)
            self.rect.x = random.randint(0, self.width - self.rect.width)

class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, screen_width, angle, speed=16):
        super().__init__()
        self.image = pygame.Surface((16, 4), pygame.SRCALPHA)
        pygame.draw.rect(self.image, (255, 255, 0), (0, 0, 16, 4), border_radius=2)
        self.rect = self.image.get_rect(center=(x, y))
        self.screen_width = screen_width
        self.angle = angle
        self.speed = speed
        # Calculate velocity components
        rad = math.radians(self.angle)
        self.vx = math.cos(rad) * self.speed
        self.vy = -math.sin(rad) * self.speed

    def update(self):
        self.rect.x += self.vx
        self.rect.y += self.vy
        # Off-screen check (right, left, top, bottom)
        if (
            self.rect.right < 0 or self.rect.left > self.screen_width or
            self.rect.bottom < 0 or self.rect.top > 2000  # 2000: generous for tall screens
        ):
            self.kill()
