import pygame
import random
import numpy as np
import math

class EngineSound:
    def __init__(self, base_bpm=120, volume=0.25, duration=1.0, sample_rate=44100):
        self.base_bpm = base_bpm  # base 'whump' rate in beats per minute
        self.volume = volume
        self.duration = duration
        self.sample_rate = sample_rate
        self.base_sound = self._generate_whump(self.base_bpm)
        self.fast_sound = self._generate_whump(self.base_bpm * 1.5)
        self.channel = None
        self.is_fast = False

    def _generate_whump(self, bpm):
        # Whump: repeating low-passed thump (3-5 per second)
        whump_freq = bpm / 60.0  # whumps per second
        t = np.linspace(0, self.duration, int(self.sample_rate * self.duration), False)
        # Make a pulse train: 1 for whump, 0 otherwise
        pulse = np.zeros_like(t)
        whump_interval = int(self.sample_rate / whump_freq)
        for i in range(0, len(t), whump_interval):
            # Each whump: short burst, then decay
            whump_len = int(self.sample_rate * 0.07)  # 70ms per whump
            end = min(i + whump_len, len(t))
            envelope = np.exp(-np.linspace(0, 3, end - i))
            # Low thump: sine + noise
            whump = 0.7 * np.sin(2 * np.pi * 60 * t[i:end])
            whump += 0.3 * np.random.normal(0, 0.7, end - i)
            whump *= envelope
            pulse[i:end] += whump
        # Normalize
        pulse = pulse / (np.max(np.abs(pulse)) + 1e-6)
        pulse = (pulse * 32767 * self.volume).astype(np.int16)
        if pulse.ndim == 1:
            pulse = np.column_stack((pulse, pulse))
        sound = pygame.sndarray.make_sound(pulse)
        sound.set_volume(self.volume)
        return sound

    def play(self, fast=False):
        if self.channel is None or not self.channel.get_busy():
            self.channel = self.base_sound.play(loops=-1)
        self.set_pitch(fast)

    def set_pitch(self, fast):
        # fast=True: use faster whump
        if self.channel is not None:
            if fast and not self.is_fast:
                self.channel.stop()
                self.channel = self.fast_sound.play(loops=-1)
                self.is_fast = True
            elif not fast and self.is_fast:
                self.channel.stop()
                self.channel = self.base_sound.play(loops=-1)
                self.is_fast = False

    def stop(self):
        if self.channel is not None:
            self.channel.stop()
            self.channel = None
            self.is_fast = False

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
