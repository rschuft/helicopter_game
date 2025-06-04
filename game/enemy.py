import pygame
import random
import numpy as np
import math

def generate_rotor_sound(rotor_speed_func, volume=0.18, sample_rate=44100):
    # Returns a function that manages a looping rotor sound, updating pitch with rotor_speed_func
    class RotorSound:
        def __init__(self):
            self.sample_rate = sample_rate
            self.duration = 1.0
            self.volume = volume
            self.sound = None
            self.channel = None
            self.last_rate = None
            self.last_pitch = None
        def set_volume(self, v):
            self.volume = v
            if self.channel:
                self.channel.set_volume(v)
        def _generate_whump(self, whumps_per_sec, pitch_shift=1.0):
            t = np.linspace(0, self.duration, int(self.sample_rate * self.duration), False)
            pulse = np.zeros_like(t)
            whump_interval = int(self.sample_rate / whumps_per_sec)
            base_freq = 38 * pitch_shift  # Lower base frequency for lower pitch
            for i in range(0, len(t), whump_interval):
                whump_len = int(self.sample_rate * 0.07)
                end = min(i + whump_len, len(t))
                envelope = np.exp(-np.linspace(0, 3, end - i))
                whump = 0.7 * np.sin(2 * np.pi * base_freq * t[i:end])
                whump += 0.3 * np.random.normal(0, 0.7, end - i)
                whump *= envelope
                pulse[i:end] += whump
            pulse = pulse / (np.max(np.abs(pulse)) + 1e-6)
            pulse = (pulse * 32767 * self.volume).astype(np.int16)
            if pulse.ndim == 1:
                pulse = np.column_stack((pulse, pulse))
            sound = pygame.sndarray.make_sound(pulse)
            sound.set_volume(self.volume)
            return sound
        def play(self):
            whumps_per_sec, pitch_shift = self._calc_whumps_and_pitch()
            self.sound = self._generate_whump(whumps_per_sec, pitch_shift)
            self.channel = self.sound.play(loops=-1)
            self.last_rate = whumps_per_sec
            self.last_pitch = pitch_shift
        def update(self):
            whumps_per_sec, pitch_shift = self._calc_whumps_and_pitch()
            if (abs(whumps_per_sec - (self.last_rate or 0)) > 0.1) or (abs(pitch_shift - (self.last_pitch or 1.0)) > 0.01):
                if self.channel:
                    self.channel.stop()
                self.sound = self._generate_whump(whumps_per_sec, pitch_shift)
                self.channel = self.sound.play(loops=-1)
                self.last_rate = whumps_per_sec
                self.last_pitch = pitch_shift
        def stop(self):
            if self.channel:
                self.channel.stop()
                self.channel = None
        def _calc_whumps_and_pitch(self):
            rotor_speed = rotor_speed_func()  # deg/frame
            fps = 60
            revs_per_sec = (rotor_speed * fps) / 360.0
            whumps_per_sec = max(1.0, min(5, revs_per_sec * 2.2))  # Lower whump rate for lower pitch
            pitch_shift = 0.7 + 0.18 * ((whumps_per_sec - 1.0) / (5 - 1.0))  # Lower pitch overall
            return whumps_per_sec, pitch_shift
        def set_pitch(self, pitch_shift):
            whumps_per_sec, _ = self._calc_whumps_and_pitch()
            if (abs(pitch_shift - (self.last_pitch or 1.0)) > 0.01):
                if self.channel:
                    self.channel.stop()
                self.sound = self._generate_whump(whumps_per_sec, pitch_shift)
                self.channel = self.sound.play(loops=-1)
                self.last_pitch = pitch_shift
    return RotorSound()

def generate_bullet_fire_sound(duration=0.18, freq=180, sample_rate=44100, volume=0.7):
    t = np.linspace(0, duration, int(sample_rate * duration), False)
    envelope = np.exp(-8 * t)
    wave = 0.7 * np.sin(2 * np.pi * freq * t) * envelope
    wave += 0.3 * np.random.normal(0, 0.7, t.shape) * envelope
    wave = (wave * 32767 * volume).astype(np.int16)
    if wave.ndim == 1:
        wave = np.column_stack((wave, wave))
    return pygame.sndarray.make_sound(wave)

def generate_explosion_sound(duration=0.3, sample_rate=44100, volume=0.5):
    t = np.linspace(0, duration, int(sample_rate * duration), False)
    noise = np.random.normal(0, 1, t.shape)
    envelope = np.exp(-5 * t)
    wave = noise * envelope
    wave = (wave * 32767 * volume).astype(np.int16)
    if wave.ndim == 1:
        wave = np.column_stack((wave, wave))
    return pygame.sndarray.make_sound(wave)

def generate_crash_sound(duration=0.5, sample_rate=44100, volume=0.7):
    t = np.linspace(0, duration, int(sample_rate * duration), False)
    # A low, noisy thud with a sharp attack and slow decay
    noise = np.random.normal(0, 1, t.shape)
    envelope = np.exp(-6 * t)
    thud = 0.7 * np.sin(2 * np.pi * 60 * t) * np.exp(-12 * t)
    wave = (noise * 0.5 + thud) * envelope
    wave = (wave * 32767 * volume).astype(np.int16)
    if wave.ndim == 1:
        wave = np.column_stack((wave, wave))
    return pygame.sndarray.make_sound(wave)

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

class EnemyTank(pygame.sprite.Sprite):
    def __init__(self, player_world_x, player_world_y, spawn_outside_radar=False, radar_radius=3600, pause_time=0, avoid_positions=None):
        super().__init__()
        self.width = 60
        self.height = 32
        self.turret_length = 38
        self.turret_width = 8
        self.body_image = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        pygame.draw.rect(self.body_image, (80, 80, 80), (0, 8, self.width, 16), border_radius=6)  # body
        pygame.draw.rect(self.body_image, (60, 60, 60), (8, 0, self.width-16, 32), border_radius=8)  # hull
        pygame.draw.circle(self.body_image, (120, 120, 120), (self.width//2, self.height//2), 12)  # turret base
        self.image = self.body_image.copy()
        self.rect = self.body_image.get_rect()
        # Spawn at a random position
        if spawn_outside_radar:
            angle = random.uniform(0, 2 * math.pi)
            dist = radar_radius + 200 + random.uniform(0, 200)
            if avoid_positions:
                for _ in range(20):
                    angle = random.uniform(0, 2 * math.pi)
                    candidate_x = player_world_x + math.cos(angle) * dist
                    candidate_y = player_world_y + math.sin(angle) * dist
                    if all(math.hypot(candidate_x - x, candidate_y - y) > self.width * 5 for (x, y) in avoid_positions):
                        break
                self.world_x = candidate_x
                self.world_y = candidate_y
            else:
                self.world_x = player_world_x + math.cos(angle) * dist
                self.world_y = player_world_y + math.sin(angle) * dist
        else:
            angle = random.uniform(0, 2 * math.pi)
            dist = random.uniform(900, 1400)
            self.world_x = player_world_x + math.cos(angle) * dist
            self.world_y = player_world_y + math.sin(angle) * dist
        self.turret_angle = 0
        self.speed = 3.2
        self.fire_cooldown = 0
        self.bullets = []
        self.max_bullets = 1
        self.bullet_speed = 14
        self.bullet_cooldown_time = random.randint(90, 180)
        self.pause_time = pause_time
        self.paused = pause_time > 0
        self.exploding = False
        self.explode_timer = 0

    def update(self, player_world_x, player_world_y, screen_width=1920, screen_height=1080):
        if self.exploding:
            self.explode_timer -= 1
            if self.explode_timer <= 0:
                return 'remove'  # Signal to remove this tank
            return None
        if self.paused:
            self.pause_time -= 1
            if self.pause_time <= 0:
                self.paused = False
            return None
        # Move toward the player's visible ground position (ignore height)
        dx = player_world_x - self.world_x
        dy = player_world_y - self.world_y
        dist = math.hypot(dx, dy)
        edge_dist = max(screen_width, screen_height) * 0.48
        preferred_dist = edge_dist * 0.92
        if dist > preferred_dist:
            move_angle = math.atan2(dy, dx)
            self.world_x += math.cos(move_angle) * self.speed
            self.world_y += math.sin(move_angle) * self.speed
        else:
            # Circle the player on the ground
            tangent_angle = math.atan2(dy, dx) + math.pi / 2
            self.world_x += math.cos(tangent_angle) * self.speed * 0.7
            self.world_y += math.sin(tangent_angle) * self.speed * 0.7
        # Aim turret at player
        self.turret_angle = math.degrees(math.atan2(dy, dx))
        # Fire at player
        if self.fire_cooldown > 0:
            self.fire_cooldown -= 1
        elif dist < edge_dist * 1.05 and len(self.bullets) < self.max_bullets:
            self.fire_bullet()
            self.bullet_cooldown_time = random.randint(90, 180)
            self.fire_cooldown = self.bullet_cooldown_time
        for bullet in self.bullets[:]:
            bullet.update()
            if bullet.lifetime <= 0:
                self.bullets.remove(bullet)
        return None

    def fire_bullet(self):
        rad = math.radians(self.turret_angle)
        bx = self.world_x + math.cos(rad) * (self.width // 2 + self.turret_length // 2)
        by = self.world_y + math.sin(rad) * (self.height // 2 + self.turret_length // 2)
        self.bullets.append(TankBullet(bx, by, self.turret_angle, self.bullet_speed))

    def start_explode(self):
        self.exploding = True
        self.explode_timer = 36  # ~0.6s at 60 FPS

    def draw(self, screen, camera_x, camera_y, WIDTH, HEIGHT):
        screen_x = int(self.world_x - camera_x + WIDTH // 2)
        screen_y = int(self.world_y - camera_y + HEIGHT // 2)
        if self.exploding:
            # Draw explosion (simple expanding yellow/orange circle)
            t = 36 - self.explode_timer
            radius = 24 + t * 2
            color = (255, 200 - t*4, 60)
            pygame.draw.circle(screen, color, (screen_x, screen_y), radius)
            if t > 12:
                pygame.draw.circle(screen, (255, 255, 255), (screen_x, screen_y), radius // 2)
            return
        # Draw tank body
        screen.blit(self.body_image, (screen_x - self.width // 2, screen_y - self.height // 2))
        # Draw turret
        turret_rad = math.radians(self.turret_angle)
        turret_base = (screen_x, screen_y)
        turret_tip = (int(screen_x + math.cos(turret_rad) * self.turret_length), int(screen_y + math.sin(turret_rad) * self.turret_length))
        pygame.draw.line(screen, (100, 200, 100), turret_base, turret_tip, self.turret_width)
        pygame.draw.circle(screen, (120, 120, 120), turret_base, 12)
        # Draw bullets
        for bullet in self.bullets:
            bullet.draw(screen, camera_x, camera_y, WIDTH, HEIGHT)

    def get_world_rect(self):
        return pygame.Rect(self.world_x - self.width // 2, self.world_y - self.height // 2, self.width, self.height)

class TankBullet:
    def __init__(self, x, y, angle, speed=14):
        self.length = 18
        self.width = 6
        base_image = pygame.Surface((self.length, self.width), pygame.SRCALPHA)
        pygame.draw.rect(base_image, (200, 255, 80), (0, 0, self.length, self.width), border_radius=2)
        # Fix orientation: rotate by angle-90 so the bullet points in the firing direction
        self.image = pygame.transform.rotate(base_image, angle - 90)
        self.rect = self.image.get_rect(center=(x, y))
        self.angle = angle
        self.speed = speed
        rad = math.radians(self.angle)
        self.vx = math.cos(rad) * self.speed
        self.vy = math.sin(rad) * self.speed
        self.world_x = x
        self.world_y = y
        self.lifetime = 120

    def update(self):
        self.world_x += self.vx
        self.world_y += self.vy
        self.lifetime -= 1

    def draw(self, screen, camera_x, camera_y, WIDTH, HEIGHT):
        screen_x = int(self.world_x - camera_x + WIDTH // 2)
        screen_y = int(self.world_y - camera_y + HEIGHT // 2)
        self.rect = self.image.get_rect(center=(screen_x, screen_y))
        screen.blit(self.image, self.rect)

    def get_world_rect(self):
        return pygame.Rect(self.world_x - self.length // 2, self.world_y - self.width // 2, self.length, self.width)

def generate_damage_sound(duration=0.22, freq=110, sample_rate=44100, volume=0.55):
    t = np.linspace(0, duration, int(sample_rate * duration), False)
    envelope = np.exp(-7 * t)
    # A metallic clang + static burst
    wave = 0.6 * np.sin(2 * np.pi * freq * t) * envelope
    wave += 0.5 * np.random.normal(0, 0.7, t.shape) * envelope * (1 - t / duration)
    wave += 0.2 * np.sin(2 * np.pi * (freq * 2.7) * t) * envelope * (1 - t / duration)
    wave = (wave * 32767 * volume).astype(np.int16)
    if wave.ndim == 1:
        wave = np.column_stack((wave, wave))
    return pygame.sndarray.make_sound(wave)

def generate_tank_fire_sound(duration=0.22, freq=60, sample_rate=44100, volume=0.7):
    t = np.linspace(0, duration, int(sample_rate * duration), False)
    envelope = np.exp(-5 * t)
    # Low boom: sine + noise
    wave = 0.7 * np.sin(2 * np.pi * freq * t) * envelope
    wave += 0.3 * np.random.normal(0, 0.5, t.shape) * envelope
    wave = (wave * 32767 * volume).astype(np.int16)
    if wave.ndim == 1:
        wave = np.column_stack((wave, wave))
    return pygame.sndarray.make_sound(wave)
