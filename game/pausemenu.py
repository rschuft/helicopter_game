# --- pausemenu.py ---
import pygame

def draw_pause_menu(screen, font, WIDTH, HEIGHT, pause_rect_resume, pause_rect_restart, pause_rect_quit_start, pause_rect_quit_desktop):
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