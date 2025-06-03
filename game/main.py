import pygame
import random
import math
from .settings import WIDTH, HEIGHT, FPS
from .player import Player
from .enemy import EnemyHelicopter, generate_rotor_sound, generate_bullet_fire_sound, generate_explosion_sound, generate_crash_sound
from .leaderboard import add_score, load_leaderboard
from .menu import draw_main_menu
from .ui import show_settings_screen
from .gameover import show_score_entry_screen
from .world import draw_ground_and_trees, draw_radar
from .pausemenu import draw_pause_menu

def run():
    pygame.init()
    font = pygame.font.SysFont(None, 36)

    while True:
        # --- SETTINGS & SCREEN INIT ---
        from .settings import load_settings, save_settings
        settings = load_settings()
        if settings.get("FULLSCREEN"):
            info = pygame.display.Info()
            settings["WIDTH"], settings["HEIGHT"] = info.current_w, info.current_h
            save_settings(settings)
        WIDTH, HEIGHT, FPS = settings["WIDTH"], settings["HEIGHT"], settings["FPS"]
        flags = pygame.FULLSCREEN if settings.get("FULLSCREEN") else 0
        screen = pygame.display.set_mode((WIDTH, HEIGHT), flags)
        font = pygame.font.SysFont(None, 36)

        # --- UI BUTTONS ---
        button_rect = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2, 200, 60)
        settings_rect = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2 + 80, 200, 50)
        quit_rect = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2 + 160, 200, 50)
        waiting = True
        settings_clock = pygame.time.Clock()
        # --- Prevent sound effects on start screen ---
        pygame.mixer.stop()
        while waiting:
            draw_main_menu(screen, font, WIDTH, HEIGHT, button_rect, settings_rect, quit_rect, load_leaderboard)
            pygame.display.flip()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    return
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if button_rect.collidepoint(event.pos):
                        waiting = False
                    if settings_rect.collidepoint(event.pos):
                        settings = show_settings_screen(screen, font, settings, save_settings)
                        flags = pygame.FULLSCREEN if settings.get("FULLSCREEN") else 0
                        screen = pygame.display.set_mode((WIDTH, HEIGHT), flags)
                        font = pygame.font.SysFont(None, 36)
                    if quit_rect.collidepoint(event.pos):
                        pygame.quit()
                        return
            settings_clock.tick(30)

        # --- GAME SETUP ---
        player = Player(WIDTH // 2, HEIGHT // 2)
        player.world_x = 0
        player.world_y = 0
        def get_dynamic_rotor_speed():
            return player.rotor_speed + max(0.1, abs(player.speed)) * 120
        rotor_sound = generate_rotor_sound(get_dynamic_rotor_speed)
        bullet_fire_sound = generate_bullet_fire_sound()
        explosion_sound = generate_explosion_sound()
        crash_sound = generate_crash_sound()
        # --- ENEMY SYSTEM REFACTOR ---
        # Use a list of enemies
        enemies = [EnemyHelicopter(player.world_x, player.world_y)]
        bullets = []
        rotor_sound.play()
        running = True
        score = 0
        game_over = False
        name = ""
        show_gameover_menu = False
        play_again_rect = pygame.Rect(WIDTH // 2 - 180, HEIGHT // 2 + 100, 110, 50)
        to_start_rect = pygame.Rect(WIDTH // 2 - 55, HEIGHT // 2 + 100, 110, 50)
        quit_rect_gameover = pygame.Rect(WIDTH // 2 + 70, HEIGHT // 2 + 100, 110, 50)
        paused = False
        pause_rect_resume = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2 - 120, 200, 50)
        pause_rect_restart = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2 - 50, 200, 50)
        pause_rect_quit_start = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2 + 20, 200, 50)
        pause_rect_quit_desktop = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2 + 90, 200, 50)

        game_clock = pygame.time.Clock()
        camera_x = player.world_x
        camera_y = player.world_y
        # --- Add this flag for in-game restart ---
        in_game_restart = False
        while running:
            game_clock.tick(FPS)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    return
                # Pause menu logic
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE and not game_over:
                    paused = not paused
                    if paused:
                        pygame.mixer.stop()  # Stop all sound effects
                if paused:
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        if pause_rect_resume.collidepoint(event.pos):
                            paused = False
                        elif pause_rect_restart.collidepoint(event.pos):
                            # --- In-game restart: reset all game state, but do not break to menu ---
                            player = Player(WIDTH // 2, HEIGHT // 2)
                            player.world_x = 0
                            player.world_y = 0
                            enemies = [EnemyHelicopter(player.world_x, player.world_y)]
                            bullets = []
                            score = 0
                            game_over = False
                            name = ""
                            show_gameover_menu = False
                            paused = False
                            camera_x = player.world_x
                            camera_y = player.world_y
                            continue  # Resume game immediately
                        elif pause_rect_quit_start.collidepoint(event.pos):
                            running = False
                            break
                        elif pause_rect_quit_desktop.collidepoint(event.pos):
                            pygame.quit()
                            return
                    continue  # Don't process other events while paused
                if game_over and not show_gameover_menu and event.type == pygame.KEYDOWN:
                    # Remove name_entered check, just allow Enter to submit
                    if event.key == pygame.K_RETURN:
                        add_score(name if name.strip() else "Anonymous", score)
                        show_gameover_menu = True
                    elif event.key == pygame.K_BACKSPACE:
                        name = name[:-1]
                    elif event.unicode.isprintable() and len(name) < 12:
                        name += event.unicode
                if game_over and show_gameover_menu and event.type == pygame.MOUSEBUTTONDOWN:
                    if play_again_rect.collidepoint(event.pos):
                        running = False  # break to outer loop to restart
                    elif to_start_rect.collidepoint(event.pos):
                        running = False  # break to outer loop, will show start screen again
                    elif quit_rect_gameover.collidepoint(event.pos):
                        pygame.quit()
                        return
                if not game_over and event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        bullet_length = player.player_width // 2
                        rad = math.radians(player.angle)
                        world_bullet_x = player.world_x + math.cos(rad) * bullet_length
                        world_bullet_y = player.world_y - math.sin(rad) * bullet_length
                        # Create a player bullet as a simple dict/object
                        bullet = type('PlayerBullet', (), {})()
                        bullet.length = 16
                        bullet.width = 4
                        base_image = pygame.Surface((bullet.length, bullet.width), pygame.SRCALPHA)
                        pygame.draw.rect(base_image, (255, 255, 0), (0, 0, bullet.length, bullet.width), border_radius=2)
                        bullet.image = pygame.transform.rotate(base_image, player.angle)
                        bullet.rect = bullet.image.get_rect(center=(world_bullet_x, world_bullet_y))
                        bullet.angle = player.angle
                        bullet.speed = 16
                        rad = math.radians(bullet.angle)
                        bullet.vx = math.cos(rad) * bullet.speed
                        bullet.vy = -math.sin(rad) * bullet.speed
                        bullet.world_x = world_bullet_x
                        bullet.world_y = world_bullet_y
                        bullet.get_world_rect = lambda b=bullet: pygame.Rect(b.world_x - b.length // 2, b.world_y - b.width // 2, b.length, b.width)
                        bullet.update = lambda b=bullet: (setattr(b, 'world_x', b.world_x + b.vx), setattr(b, 'world_y', b.world_y + b.vy))
                        bullet.draw = lambda screen, camera_x, camera_y, WIDTH, HEIGHT, b=bullet: screen.blit(b.image, b.image.get_rect(center=(int(b.world_x - camera_x + WIDTH // 2), int(b.world_y - camera_y + HEIGHT // 2))))
                        bullets.append(bullet)
                        bullet_fire_sound.play()
        # --- Update rotor sound pitch based on player speed ---
            rotor_sound.set_volume(min(1.0, max(0.0, player.speed / player.max_speed)))
            rotor_sound.set_pitch(1.0 + player.speed / player.max_speed * 2.0)

            if paused:
                draw_pause_menu(screen, font, WIDTH, HEIGHT, pause_rect_resume, pause_rect_restart, pause_rect_quit_start, pause_rect_quit_desktop)
                pygame.display.flip()
                continue  # Skip game update/draw while paused

            if not game_over:
                keys = pygame.key.get_pressed()
                # Only update player.world_x/world_y by input
                prev_world_x = player.world_x
                prev_world_y = player.world_y
                # Calculate movement from input (copy from Player.update, but don't move player.pos)
                move = 0
                if keys[pygame.K_UP] or keys[pygame.K_w]:
                    move = 1
                if keys[pygame.K_DOWN] or keys[pygame.K_s]:
                    move = -1
                if move != 0:
                    player.speed += player.acceleration * move
                else:
                    player.speed *= 0.92
                if player.speed > player.max_speed:
                    player.speed = player.max_speed
                if player.speed < -player.max_speed:
                    player.speed = -player.max_speed
                # Rotation
                if keys[pygame.K_LEFT] or keys[pygame.K_a]:
                    player.angle += player.rotation_speed
                if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                    player.angle -= player.rotation_speed
                rad = math.radians(player.angle)
                dx = math.cos(rad) * player.speed
                dy = -math.sin(rad) * player.speed
                player.world_x += dx
                player.world_y += dy
                # Camera always follows player
                camera_x = player.world_x
                camera_y = player.world_y
                # Animate rotor and update image
                player.rotor_angle = (player.rotor_angle + player.rotor_speed) % 360
                player.image = player.body_image.copy()
                center = (player.rotor_diameter // 2, player.rotor_diameter // 2)
                blade_length = int(player.rotor_radius * 0.95)
                blade_width = 8
                blade_color = (60, 60, 60, 180)
                for i in range(3):
                    angle = player.rotor_angle + i * 120
                    rad_blade = math.radians(angle)
                    x2 = center[0] + math.cos(rad_blade) * blade_length
                    y2 = center[1] + math.sin(rad_blade) * blade_length
                    pygame.draw.line(player.image, blade_color, center, (x2, y2), blade_width)
                player.image = pygame.transform.rotate(player.image, player.angle)
                player.rect = player.image.get_rect(center=(WIDTH // 2, HEIGHT // 2))
                # Update bullets in world space
                for bullet in bullets[:]:
                    bullet.update()
                    screen_x = bullet.world_x - camera_x + WIDTH // 2
                    screen_y = bullet.world_y - camera_y + HEIGHT // 2
                    if (
                        screen_x < -100 or screen_x > WIDTH + 100 or
                        screen_y < -100 or screen_y > HEIGHT + 100
                    ):
                        bullets.remove(bullet)
                # Update all enemies
                for enemy in enemies[:]:
                    result = enemy.update(player.world_x, player.world_y, [e for e in enemies if e is not enemy])
                    if result == 'remove':
                        enemies.remove(enemy)
                # --- Bullet-enemy collision (player bullets hit enemy heli) ---
                hits = []
                for bullet in bullets[:]:
                    for enemy in enemies:
                        if not getattr(enemy, 'crashing', False) and enemy.get_world_rect().colliderect(bullet.get_world_rect()):
                            hits.append((bullet, enemy))
                for bullet, enemy in hits:
                    bullets.remove(bullet)
                    score += 1
                    explosion_sound.play()
                    enemy.start_crash()
                    # When enemy is hit, spawn 2 new enemies outside radar, paused
                    avoid_positions = [(player.world_x, player.world_y)] + [(e.world_x, e.world_y) for e in enemies]
                    for _ in range(2):
                        new_enemy = EnemyHelicopter(player.world_x, player.world_y, spawn_outside_radar=True, radar_radius=3600, pause_time=FPS*10, avoid_positions=avoid_positions)
                        enemies.append(new_enemy)
                        avoid_positions.append((new_enemy.world_x, new_enemy.world_y))
                # --- Enemy bullet hits player ---
                player_rect = pygame.Rect(player.world_x - player.player_width // 2, player.world_y - player.player_height // 2, player.player_width, player.player_height)
                for enemy in enemies:
                    for bullet in enemy.bullets[:]:
                        if player_rect.colliderect(bullet.get_world_rect()):
                            game_over = True
                            rotor_sound.stop()
                            crash_sound.play()
                            show_gameover_menu = False
                # --- Enemy heli collides with player ---
                for enemy in enemies:
                    if player_rect.colliderect(enemy.get_world_rect()) and not getattr(enemy, 'crashing', False):
                        game_over = True
                        rotor_sound.stop()
                        crash_sound.play()
                        show_gameover_menu = False
            # Draw ground and trees (world background)
            draw_ground_and_trees(screen, camera_x, camera_y, WIDTH, HEIGHT)
            # Draw all enemies
            for enemy in enemies:
                enemy.draw(screen, camera_x, camera_y, WIDTH, HEIGHT)
            # Draw bullets
            for bullet in bullets:
                bullet.draw(screen, camera_x, camera_y, WIDTH, HEIGHT)
            # Draw player (always centered)
            screen.blit(player.image, player.rect)
            # Draw radar (after world, before UI)
            draw_radar(screen, player.world_x, player.world_y, enemies, WIDTH, HEIGHT)
            # Display score
            score_text = font.render(f"Score: {score}", True, (255, 255, 255))
            screen.blit(score_text, (10, 10))

            if game_over and not show_gameover_menu:
                name, result = show_score_entry_screen(screen, font, WIDTH, HEIGHT, score)
                # Use 'Anonymous' if name is empty or only whitespace
                add_score(name if name.strip() else "Anonymous", score)
                show_gameover_menu = True
                if result == 'quit':
                    pygame.quit()
                    return
                # Immediately break out of the inner game loop to return to the start screen
                running = False
                break
            if game_over and show_gameover_menu:
                final_score = font.render(f"Your Score: {score}", True, (255, 255, 255))
                screen.blit(final_score, (WIDTH // 2 - final_score.get_width() // 2, HEIGHT // 2 + 10))
                pygame.draw.rect(screen, (0, 120, 0), play_again_rect, border_radius=8)
                pygame.draw.rect(screen, (120, 120, 0), to_start_rect, border_radius=8)
                pygame.draw.rect(screen, (120, 0, 0), quit_rect_gameover, border_radius=8)
                again_text = font.render("Play Again", True, (255, 255, 255))
                start_text = font.render("To Start", True, (255, 255, 255))
                quit_text = font.render("Quit", True, (255, 255, 255))
                screen.blit(again_text, (play_again_rect.centerx - again_text.get_width() // 2, play_again_rect.centery - again_text.get_height() // 2))
                screen.blit(start_text, (to_start_rect.centerx - start_text.get_width() // 2, to_start_rect.centery - start_text.get_height() // 2))
                screen.blit(quit_text, (quit_rect_gameover.centerx - quit_text.get_width() // 2, quit_rect_gameover.centery - quit_text.get_height() // 2))

            pygame.display.flip()
            if not running:
                break

    pygame.quit()
