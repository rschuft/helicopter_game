import pygame
import random

def draw_ground_and_trees(screen, camera_x, camera_y, WIDTH, HEIGHT):
    # Low-res ground: large tiles for smooth motion
    tile_size = 160  # Much larger for smooth, slow-moving ground
    start_x = int((camera_x - WIDTH // 2) // tile_size) * tile_size
    start_y = int((camera_y - HEIGHT // 2) // tile_size) * tile_size
    end_x = int((camera_x + WIDTH // 2) // tile_size) * tile_size + tile_size
    end_y = int((camera_y + HEIGHT // 2) // tile_size) * tile_size + tile_size
    grass_color = (34, 139, 34)
    for wx in range(start_x, end_x, tile_size):
        for wy in range(start_y, end_y, tile_size):
            sx = int(wx - camera_x + WIDTH // 2)
            sy = int(wy - camera_y + HEIGHT // 2)
            pygame.draw.rect(screen, grass_color, (sx, sy, tile_size, tile_size))
            # Draw a few tufts of grass per tile (deterministic)
            tx = wx // tile_size
            ty = wy // tile_size
            seed = (tx * 92821 + ty * 68917) & 0xFFFFFFFF
            rng = random.Random(seed)
            for _ in range(4):
                gx = sx + rng.randint(10, tile_size - 10)
                gy = sy + rng.randint(10, tile_size - 10)
                length = rng.randint(10, 18)
                y2 = int(gy - length)
                pygame.draw.line(screen, (60, 180, 60), (gx, gy), (gx, y2), 2)
                if rng.random() < 0.7:
                    offset = rng.randint(-3, 3)
                    pygame.draw.line(screen, (80, 200, 80), (gx + offset, gy), (gx + offset, y2 + rng.randint(-2, 2)), 1)
    # No trees for this field view

def draw_radar(screen, player_world_x, player_world_y, enemies, WIDTH, HEIGHT):
    # Radar settings
    radar_radius = 100
    radar_center = (radar_radius + 24, HEIGHT - radar_radius - 24)
    radar_bg = (20, 40, 20)
    radar_outline = (80, 200, 80)
    radar_enemy = (255, 60, 60)
    radar_player = (255, 255, 0)
    max_radar_dist = 3600  # Double the previous range for offscreen detection
    # Draw radar background
    pygame.draw.circle(screen, radar_bg, radar_center, radar_radius)
    pygame.draw.circle(screen, radar_outline, radar_center, radar_radius, 2)
    # Draw crosshairs
    pygame.draw.line(screen, radar_outline, (radar_center[0] - radar_radius, radar_center[1]), (radar_center[0] + radar_radius, radar_center[1]), 1)
    pygame.draw.line(screen, radar_outline, (radar_center[0], radar_center[1] - radar_radius), (radar_center[0], radar_center[1] + radar_radius), 1)
    # Draw player at center
    pygame.draw.circle(screen, radar_player, radar_center, 7)
    # Draw enemies (including offscreen, clipped to radar edge if needed)
    for enemy in enemies:
        dx = enemy.world_x - player_world_x
        dy = enemy.world_y - player_world_y
        dist = (dx ** 2 + dy ** 2) ** 0.5
        if dist < max_radar_dist:
            # Convert world offset to radar offset
            radar_dx = int(dx / max_radar_dist * radar_radius)
            radar_dy = int(dy / max_radar_dist * radar_radius)
            # Clamp to radar edge if outside
            mag = (radar_dx ** 2 + radar_dy ** 2) ** 0.5
            if mag > radar_radius - 8:
                scale = (radar_radius - 8) / mag
                radar_dx = int(radar_dx * scale)
                radar_dy = int(radar_dy * scale)
            ex = radar_center[0] + radar_dx
            ey = radar_center[1] + radar_dy
            pygame.draw.circle(screen, radar_enemy, (ex, ey), 6)
    # Optional: add a border shadow
    pygame.draw.circle(screen, (0,0,0), radar_center, radar_radius+4, 4)