import pygame

def draw_main_menu(screen, font, WIDTH, HEIGHT, button_rect, settings_rect, quit_rect, load_leaderboard):
    screen.fill((34, 139, 34))
    title_text = font.render("Helicopter Game", True, (255, 255, 255))
    screen.blit(title_text, (WIDTH // 2 - title_text.get_width() // 2, HEIGHT // 2 - 100))
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
