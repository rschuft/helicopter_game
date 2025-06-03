import pygame
import random
import math
from .settings import WIDTH, HEIGHT, FPS
from .player import Player
from .enemy import Enemy, EngineSound, Bullet, generate_explosion_sound, generate_bullet_fire_sound
from .leaderboard import add_score, load_leaderboard

def run():
    pygame.init()
    font = pygame.font.SysFont(None, 36)
    explosion_sound = generate_explosion_sound()
    bullet_fire_sound = generate_bullet_fire_sound()

    def show_settings_screen(settings):
        screen = pygame.display.set_mode((settings["WIDTH"], settings["HEIGHT"]))
        fullscreen_rect = pygame.Rect(settings["WIDTH"] // 2 - 100, settings["HEIGHT"] // 2 - 40, 200, 50)
        save_rect = pygame.Rect(settings["WIDTH"] // 2 - 100, settings["HEIGHT"] // 2 + 30, 200, 50)
        running = True
        settings_clock = pygame.time.Clock()
        while running:
            screen.fill((30, 30, 30))
            title = font.render("Settings", True, (255, 255, 255))
            screen.blit(title, (settings["WIDTH"] // 2 - title.get_width() // 2, 80))
            # Fullscreen toggle
            fs_val = settings.get('FULLSCREEN', False)
            fs_text = f"Fullscreen: {'ON' if fs_val else 'OFF'}"
            fs_render = font.render(fs_text, True, (255, 255, 0))
            pygame.draw.rect(screen, (60, 60, 60), fullscreen_rect, border_radius=8)
            screen.blit(fs_render, (fullscreen_rect.centerx - fs_render.get_width() // 2, fullscreen_rect.centery - fs_render.get_height() // 2))
            # Save button
            pygame.draw.rect(screen, (0, 120, 0), save_rect, border_radius=8)
            save_text = font.render("Save & Back", True, (255, 255, 255))
            screen.blit(save_text, (save_rect.centerx - save_text.get_width() // 2, save_rect.centery - save_text.get_height() // 2))
            pygame.display.flip()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if fullscreen_rect.collidepoint(event.pos):
                        settings["FULLSCREEN"] = not settings.get("FULLSCREEN", False)
                    if save_rect.collidepoint(event.pos):
                        save_settings(settings)
                        return settings
            settings_clock.tick(30)
        return settings

    while True:
        from .settings import load_settings, save_settings
        settings = load_settings()
        # If fullscreen, get current display size
        if settings.get("FULLSCREEN"):
            info = pygame.display.Info()
            settings["WIDTH"], settings["HEIGHT"] = info.current_w, info.current_h
            # Update settings.json so all modules use the new size
            save_settings(settings)
        WIDTH, HEIGHT, FPS = settings["WIDTH"], settings["HEIGHT"], settings["FPS"]
        flags = pygame.FULLSCREEN if settings.get("FULLSCREEN") else 0
        screen = pygame.display.set_mode((WIDTH, HEIGHT), flags)
        font = pygame.font.SysFont(None, 36)
        # Start screen loop
        button_rect = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2, 200, 60)
        settings_rect = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2 + 80, 200, 50)
        quit_rect = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2 + 160, 200, 50)
        waiting = True
        settings_clock = pygame.time.Clock()
        while waiting:
            screen.fill((34, 139, 34))
            title_text = font.render("Helicopter Game", True, (255, 255, 255))
            screen.blit(title_text, (WIDTH // 2 - title_text.get_width() // 2, HEIGHT // 2 - 100))
            # Leaderboard display in a column to the right of the buttons
            leaderboard = load_leaderboard()
            lb_x = WIDTH // 2 + 220
            lb_y = HEIGHT // 2 - 100
            lb_title = font.render("Leaderboard", True, (255, 255, 0))
            screen.blit(lb_title, (lb_x, lb_y))
            for i, entry in enumerate(leaderboard[:10]):
                entry_text = font.render(f"{i+1}. {entry['name']} - {entry['score']}", True, (255, 255, 255))
                screen.blit(entry_text, (lb_x, lb_y + 40 + i * 28))
            pygame.draw.rect(screen, (0, 100, 0), button_rect, border_radius=10)
            button_text = font.render("START", True, (255, 255, 0))
            screen.blit(button_text, (button_rect.centerx - button_text.get_width() // 2, button_rect.centery - button_text.get_height() // 2))
            pygame.draw.rect(screen, (60, 60, 60), settings_rect, border_radius=8)
            settings_text = font.render("SETTINGS", True, (255, 255, 255))
            screen.blit(settings_text, (settings_rect.centerx - settings_text.get_width() // 2, settings_rect.centery - settings_text.get_height() // 2))
            pygame.draw.rect(screen, (120, 0, 0), quit_rect, border_radius=8)
            quit_text = font.render("QUIT", True, (255, 255, 255))
            screen.blit(quit_text, (quit_rect.centerx - quit_text.get_width() // 2, quit_rect.centery - quit_text.get_height() // 2))
            pygame.display.flip()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    return
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if button_rect.collidepoint(event.pos):
                        waiting = False
                    if settings_rect.collidepoint(event.pos):
                        settings = show_settings_screen(settings)
                        # Recreate screen with new settings
                        flags = pygame.FULLSCREEN if settings.get("FULLSCREEN") else 0
                        screen = pygame.display.set_mode((WIDTH, HEIGHT), flags)
                        font = pygame.font.SysFont(None, 36)
                    if quit_rect.collidepoint(event.pos):
                        pygame.quit()
                        return
            settings_clock.tick(30)

        # Game setup
        engine_sound = EngineSound()
        player = Player(WIDTH // 2, HEIGHT // 2)
        all_sprites = pygame.sprite.Group(player)
        enemies = pygame.sprite.Group()
        bullets = pygame.sprite.Group()
        for _ in range(5):
            enemy = Enemy(WIDTH, HEIGHT)
            all_sprites.add(enemy)
            enemies.add(enemy)
        engine_sound.play()
        running = True
        score = 0
        game_over = False
        name = ""
        name_entered = False
        show_gameover_menu = False
        play_again_rect = pygame.Rect(WIDTH // 2 - 180, HEIGHT // 2 + 100, 110, 50)
        to_start_rect = pygame.Rect(WIDTH // 2 - 55, HEIGHT // 2 + 100, 110, 50)
        quit_rect_gameover = pygame.Rect(WIDTH // 2 + 70, HEIGHT // 2 + 100, 110, 50)
        paused = False
        pause_rect_resume = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2 - 120, 200, 50)
        pause_rect_restart = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2 - 50, 200, 50)
        pause_rect_quit_start = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2 + 20, 200, 50)
        pause_rect_quit_desktop = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2 + 90, 200, 50)

        def show_score_entry_screen(score):
            name = ""
            name_entered = False
            entry_clock = pygame.time.Clock()
            entry_running = True
            while entry_running:
                screen.fill((34, 139, 34))
                over_text = font.render("GAME OVER", True, (255, 0, 0))
                screen.blit(over_text, (WIDTH // 2 - over_text.get_width() // 2, HEIGHT // 2 - 120))
                score_text = font.render(f"Score: {score}", True, (255, 255, 255))
                screen.blit(score_text, (WIDTH // 2 - score_text.get_width() // 2, HEIGHT // 2 - 60))
                prompt_text = font.render("Enter your name (optional):", True, (255, 255, 255))
                screen.blit(prompt_text, (WIDTH // 2 - prompt_text.get_width() // 2, HEIGHT // 2 - 10))
                name_text = font.render(name + ("_" if pygame.time.get_ticks() // 500 % 2 == 0 else ""), True, (255, 255, 0))
                screen.blit(name_text, (WIDTH // 2 - name_text.get_width() // 2, HEIGHT // 2 + 30))
                enter_text = font.render("Press Enter to submit", True, (200, 200, 200))
                screen.blit(enter_text, (WIDTH // 2 - enter_text.get_width() // 2, HEIGHT // 2 + 70))
                pygame.display.flip()
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        exit()
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_RETURN:
                            entry_running = False
                        elif event.key == pygame.K_BACKSPACE:
                            name = name[:-1]
                        elif event.unicode.isprintable() and len(name) < 12:
                            name += event.unicode
                entry_clock.tick(30)
            return name

        game_clock = pygame.time.Clock()
        while running:
            game_clock.tick(FPS)
            if not game_over:
                score += 1

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    return
                # Pause menu logic
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE and not game_over:
                    paused = not paused
                    if paused:
                        engine_sound.stop()
                        pygame.mixer.stop()  # Stop all sound effects
                    else:
                        engine_sound.play()
                if paused:
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        if pause_rect_resume.collidepoint(event.pos):
                            paused = False
                            engine_sound.play()
                        elif pause_rect_restart.collidepoint(event.pos):
                            running = False  # break to outer loop to restart
                            paused = False
                            break
                        elif pause_rect_quit_start.collidepoint(event.pos):
                            # Return to start screen
                            running = False
                            paused = False
                            break
                        elif pause_rect_quit_desktop.collidepoint(event.pos):
                            pygame.quit()
                            return
                    continue  # Don't process other events while paused
                if game_over and not show_gameover_menu and event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN and name_entered:
                        add_score(name, score)
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
                        # Fire bullet from front of helicopter in facing direction
                        bullet_length = player.player_width // 2
                        rad = math.radians(player.angle)
                        bullet_x = player.pos.x + math.cos(rad) * bullet_length
                        bullet_y = player.pos.y - math.sin(rad) * bullet_length
                        bullet = Bullet(bullet_x, bullet_y, WIDTH, player.angle)
                        bullets.add(bullet)
                        all_sprites.add(bullet)
                        bullet_fire_sound.play()

            if paused:
                # Draw pause menu
                overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
                overlay.fill((0, 0, 0, 180))
                screen.blit(overlay, (0, 0))
                pause_text = font.render("PAUSED", True, (255, 255, 0))
                screen.blit(pause_text, (WIDTH // 2 - pause_text.get_width() // 2, HEIGHT // 2 - 180))
                pygame.draw.rect(screen, (0, 120, 0), pause_rect_resume, border_radius=10)
                pygame.draw.rect(screen, (0, 100, 200), pause_rect_restart, border_radius=10)
                pygame.draw.rect(screen, (120, 120, 0), pause_rect_quit_start, border_radius=10)
                pygame.draw.rect(screen, (120, 0, 0), pause_rect_quit_desktop, border_radius=10)
                resume_text = font.render("Resume", True, (255, 255, 255))
                restart_text = font.render("Restart", True, (255, 255, 255))
                main_menu_text = font.render("Main Menu", True, (255, 255, 255))
                quit_desktop_text = font.render("Quit to Desktop", True, (255, 255, 255))
                screen.blit(resume_text, (pause_rect_resume.centerx - resume_text.get_width() // 2, pause_rect_resume.centery - resume_text.get_height() // 2))
                screen.blit(restart_text, (pause_rect_restart.centerx - restart_text.get_width() // 2, pause_rect_restart.centery - restart_text.get_height() // 2))
                screen.blit(main_menu_text, (pause_rect_quit_start.centerx - main_menu_text.get_width() // 2, pause_rect_quit_start.centery - main_menu_text.get_height() // 2))
                screen.blit(quit_desktop_text, (pause_rect_quit_desktop.centerx - quit_desktop_text.get_width() // 2, pause_rect_quit_desktop.centery - quit_desktop_text.get_height() // 2))
                pygame.display.flip()
                continue  # Skip game update/draw while paused

            if not game_over:
                keys = pygame.key.get_pressed()
                player.update(keys)
                enemies.update()
                bullets.update()
                # Support both arrow keys and ASDW for engine sound pitch
                moving = (
                    keys[pygame.K_LEFT] or keys[pygame.K_RIGHT] or keys[pygame.K_UP] or keys[pygame.K_DOWN]
                    or keys[pygame.K_a] or keys[pygame.K_d] or keys[pygame.K_w] or keys[pygame.K_s]
                )
                engine_sound.set_pitch(moving)
                # Bullet-enemy collision
                hits = pygame.sprite.groupcollide(enemies, bullets, True, True)
                for _ in hits:
                    explosion_sound.play()
                    # Spawn a new enemy for each destroyed
                    enemy = Enemy(WIDTH, HEIGHT)
                    all_sprites.add(enemy)
                    enemies.add(enemy)
                # Use player.body_rect for collision, not player.rect
                collided = False
                for enemy in enemies:
                    if player.body_rect.colliderect(enemy.rect):
                        collided = True
                        break
                if collided:
                    game_over = True
                    engine_sound.stop()
                    show_gameover_menu = False

            # Draw grass tiles as green rectangles
            tile_size = 64
            grass_color = (34, 139, 34)
            for x in range(0, WIDTH, tile_size):
                for y in range(0, HEIGHT, tile_size):
                    pygame.draw.rect(screen, grass_color, (x, y, tile_size, tile_size))

            all_sprites.draw(screen)

            # Display score
            score_text = font.render(f"Score: {score}", True, (255, 255, 255))
            screen.blit(score_text, (10, 10))

            if game_over and not show_gameover_menu:
                name = show_score_entry_screen(score)
                # Use 'Anonymous' if name is empty or only whitespace
                add_score(name if name.strip() else "Anonymous", score)
                show_gameover_menu = True

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
