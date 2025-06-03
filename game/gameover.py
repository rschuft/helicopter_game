import pygame

def show_score_entry_screen(screen, font, WIDTH, HEIGHT, score):
    name = ""
    entry_clock = pygame.time.Clock()
    entry_running = True
    error_msg = ""
    # Add 'Main Menu' and 'Quit' buttons side by side
    menu_rect = pygame.Rect(WIDTH // 2 - 150, HEIGHT // 2 + 120, 140, 48)
    quit_rect = pygame.Rect(WIDTH // 2 + 10, HEIGHT // 2 + 120, 140, 48)
    result = None  # 'menu', 'quit', or None
    while entry_running:
        screen.fill((34, 139, 34))
        over_text = font.render("GAME OVER", True, (255, 0, 0))
        screen.blit(over_text, (WIDTH // 2 - over_text.get_width() // 2, HEIGHT // 2 - 120))
        score_text = font.render(f"Score: {score}", True, (255, 255, 255))
        screen.blit(score_text, (WIDTH // 2 - score_text.get_width() // 2, HEIGHT // 2 - 60))
        prompt_text = font.render("Enter your name (optional):", True, (255, 255, 255))
        screen.blit(prompt_text, (WIDTH // 2 - prompt_text.get_width() // 2, HEIGHT // 2 - 10))
        name_display = name[:16]  # Limit to 16 chars
        name_text = font.render(name_display + ("_" if pygame.time.get_ticks() // 500 % 2 == 0 else ""), True, (255, 255, 0))
        screen.blit(name_text, (WIDTH // 2 - name_text.get_width() // 2, HEIGHT // 2 + 30))
        enter_text = font.render("Press Enter to submit", True, (200, 200, 200))
        screen.blit(enter_text, (WIDTH // 2 - enter_text.get_width() // 2, HEIGHT // 2 + 70))
        # Draw menu and quit buttons
        pygame.draw.rect(screen, (120, 120, 0), menu_rect, border_radius=8)
        menu_text = font.render("Main Menu", True, (255, 255, 255))
        screen.blit(menu_text, (menu_rect.centerx - menu_text.get_width() // 2, menu_rect.centery - menu_text.get_height() // 2))
        pygame.draw.rect(screen, (120, 0, 0), quit_rect, border_radius=8)
        quit_text = font.render("Quit", True, (255, 255, 255))
        screen.blit(quit_text, (quit_rect.centerx - quit_text.get_width() // 2, quit_rect.centery - quit_text.get_height() // 2))
        # Show error if needed
        if error_msg:
            error_render = font.render(error_msg, True, (255, 80, 80))
            screen.blit(error_render, (WIDTH // 2 - error_render.get_width() // 2, HEIGHT // 2 + 90))
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    entry_running = False
                    result = None  # Default: just submit
                elif event.key == pygame.K_BACKSPACE:
                    name = name[:-1]
                elif event.unicode.isprintable() and len(name) < 16:
                    name += event.unicode
            if event.type == pygame.MOUSEBUTTONDOWN:
                if menu_rect.collidepoint(event.pos):
                    entry_running = False
                    result = 'menu'
                elif quit_rect.collidepoint(event.pos):
                    entry_running = False
                    result = 'quit'
        entry_clock.tick(30)
    return name_display.strip(), result
