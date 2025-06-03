import pygame

def show_settings_screen(screen, font, settings, save_settings):
    WIDTH, HEIGHT = settings["WIDTH"], settings["HEIGHT"]
    fullscreen_rect = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2 - 40, 200, 50)
    save_rect = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2 + 30, 200, 50)
    running = True
    settings_clock = pygame.time.Clock()
    while running:
        screen.fill((30, 30, 30))
        title = font.render("Settings", True, (255, 255, 255))
        screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 80))
        fs_val = settings.get('FULLSCREEN', False)
        fs_text = f"Fullscreen: {'ON' if fs_val else 'OFF'}"
        fs_render = font.render(fs_text, True, (255, 255, 0))
        pygame.draw.rect(screen, (60, 60, 60), fullscreen_rect, border_radius=8)
        screen.blit(fs_render, (fullscreen_rect.centerx - fs_render.get_width() // 2, fullscreen_rect.centery - fs_render.get_height() // 2))
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
