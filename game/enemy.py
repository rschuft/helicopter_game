import pygame
import random
import numpy as np
import math

def generate_rotor_sound(rotor_speed_func, volume=0.28, sample_rate=44100):
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
            base_freq = 55 * pitch_shift
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
            whumps_per_sec = max(1.5, min(8, revs_per_sec * 3))
            pitch_shift = 1.0 + 0.25 * ((whumps_per_sec - 1.5) / (8 - 1.5))
            return whumps_per_sec, pitch_shift
        def set_pitch(self, pitch_shift):
            # For compatibility: update pitch and restart sound if needed
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

class EnemyHelicopter(pygame.sprite.Sprite):
    def __init__(self, player_world_x, player_world_y, spawn_outside_radar=False, radar_radius=3600, pause_time=0, avoid_positions=None):
        super().__init__()
        self.width = 60
        self.height = 30
        self.rotor_radius = max(self.width, self.height) * 1.2
        self.rotor_diameter = int(self.rotor_radius * 2)
        self.body_x = self.rotor_diameter // 2 - self.width // 2
        self.body_y = self.rotor_diameter // 2 - self.height // 2
        self.body_image = pygame.Surface((self.rotor_diameter, self.rotor_diameter), pygame.SRCALPHA)
        pygame.draw.ellipse(self.body_image, (220, 40, 40), (self.body_x, self.body_y, self.width, self.height))
        pygame.draw.rect(self.body_image, (180, 0, 0), (self.body_x + 40, self.body_y + 10, 15, 10), border_radius=3)
        self.image = self.body_image.copy()
        self.body_rect = pygame.Rect(self.body_x, self.body_y, self.width, self.height)
        self.rect = self.body_rect.copy()
        # Spawn at a random position
        if spawn_outside_radar:
            angle = random.uniform(0, 2 * math.pi)
            dist = radar_radius + 200 + random.uniform(0, 200)
            # Avoid spawning too close to avoid_positions
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
        self.angle = 0
        self.speed = 4.5
        self.rotor_angle = 0
        self.rotor_speed = 18
        self.fire_cooldown = 0
        self.bullets = []
        self.max_bullets = 1  # Fewer simultaneous bullets
        self.bullet_speed = 13
        self.bullet_cooldown_time = random.randint(90, 180)  # More sporadic fire (1.5-3s at 60fps)
        self.rotor_sound = generate_rotor_sound(lambda: self.rotor_speed)
        self.avoid_distance = self.width * 3.5 * 1.3  # 30% more space than before
        self.circle_speed = 4.5
        self.circle_dir = 1 if random.random() < 0.5 else -1  # Randomize circling direction
        self.crashing = False
        self.crash_timer = 0
        self.pause_time = pause_time  # frames to pause before pursuing
        self.paused = pause_time > 0

    def update(self, player_world_x, player_world_y, other_enemies=None):
        if self.crashing:
            self.crash_timer -= 1
            self.world_y += 6  # Crash downward
            self.rotor_angle = (self.rotor_angle + self.rotor_speed * 2) % 360
            if self.crash_timer <= 0:
                return 'remove'
            return None
        if self.paused:
            self.pause_time -= 1
            if self.pause_time <= 0:
                self.paused = False
            # Idle rotor animation
            self.rotor_angle = (self.rotor_angle + self.rotor_speed) % 360
            self.rotor_sound.update()
            return None
        # Aim at player
        dx = player_world_x - self.world_x
        dy = player_world_y - self.world_y
        dist = math.hypot(dx, dy)
        # Avoid other enemies
        if other_enemies:
            for other in other_enemies:
                if other is not self and not getattr(other, 'crashing', False):
                    odx = other.world_x - self.world_x
                    ody = other.world_y - self.world_y
                    odist = math.hypot(odx, ody)
                    if odist < self.avoid_distance:
                        # Move away from other enemy
                        angle_away = math.atan2(-ody, -odx)
                        self.world_x += math.cos(angle_away) * 2
                        self.world_y -= math.sin(angle_away) * 2
        # Smoothly rotate toward player
        target_angle = math.degrees(math.atan2(-dy, dx))
        angle_diff = (target_angle - self.angle + 180) % 360 - 180
        if abs(angle_diff) > 3:
            self.angle += 3 * (1 if angle_diff > 0 else -1)
        else:
            self.angle = target_angle
        self.angle %= 360
        # --- Avoid collision and circle if too close ---
        if dist < self.avoid_distance:
            # Circle around the player at a fixed radius
            # Calculate tangent direction (perpendicular to vector to player)
            tangent_angle = math.atan2(-dy, dx) + self.circle_dir * math.pi / 2
            move_angle = math.degrees(tangent_angle)
            rad = math.radians(move_angle)
            self.world_x += math.cos(rad) * self.circle_speed
            self.world_y -= math.sin(rad) * self.circle_speed
        else:
            # Move toward player
            rad = math.radians(self.angle)
            self.world_x += math.cos(rad) * self.speed
            self.world_y -= math.sin(rad) * self.speed
        # Animate rotor
        self.rotor_angle = (self.rotor_angle + self.rotor_speed) % 360
        # Update rotor sound
        self.rotor_sound.update()
        # Fire at player if in range and cooldown is over
        if self.fire_cooldown > 0:
            self.fire_cooldown -= 1
        elif dist < 1100 and len(self.bullets) < self.max_bullets:
            self.fire_bullet()
            # Randomize next cooldown for sporadic fire
            self.bullet_cooldown_time = random.randint(90, 180)
            self.fire_cooldown = self.bullet_cooldown_time
        # Update bullets
        for bullet in self.bullets[:]:
            bullet.update()
            if bullet.lifetime <= 0:
                self.bullets.remove(bullet)
        return None

    def start_crash(self):
        self.crashing = True
        self.crash_timer = 40  # frames for crash animation
        self.rotor_sound.stop()

    def fire_bullet(self):
        rad = math.radians(self.angle)
        bx = self.world_x + math.cos(rad) * (self.width // 2)
        by = self.world_y - math.sin(rad) * (self.height // 2)
        self.bullets.append(EnemyBullet(bx, by, self.angle, self.bullet_speed))

    def draw(self, screen, camera_x, camera_y, WIDTH, HEIGHT):
        # Draw helicopter
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
        self.image = pygame.transform.rotate(self.image, self.angle)
        self.rect = self.image.get_rect(center=(int(self.world_x - camera_x + WIDTH // 2), int(self.world_y - camera_y + HEIGHT // 2)))
        screen.blit(self.image, self.rect)
        # Draw bullets
        for bullet in self.bullets:
            bullet.draw(screen, camera_x, camera_y, WIDTH, HEIGHT)

    def distance_to(self, x, y):
        return math.hypot(self.world_x - x, self.world_y - y)

    def get_world_rect(self):
        return pygame.Rect(self.world_x - self.width // 2, self.world_y - self.height // 2, self.width, self.height)

class EnemyBullet:
    def __init__(self, x, y, angle, speed=13):
        self.length = 16
        self.width = 4
        base_image = pygame.Surface((self.length, self.width), pygame.SRCALPHA)
        pygame.draw.rect(base_image, (255, 80, 80), (0, 0, self.length, self.width), border_radius=2)
        self.image = pygame.transform.rotate(base_image, angle)
        self.rect = self.image.get_rect(center=(x, y))
        self.angle = angle
        self.speed = speed
        rad = math.radians(self.angle)
        self.vx = math.cos(rad) * self.speed
        self.vy = -math.sin(rad) * self.speed
        self.world_x = x
        self.world_y = y
        self.lifetime = 120  # frames

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
