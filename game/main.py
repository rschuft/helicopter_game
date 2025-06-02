import pygame
import random
from .settings import WIDTH, HEIGHT, FPS
from .player import Player
from .enemy import Enemy
from .leaderboard import add_score

def run():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Helicopter Game")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont(None, 36)

    # Load assets
    bg_tile = pygame.image.load("assets/images/tile_grass.png").convert()
    helicopter_sound = pygame.mixer.Sound("assets/sounds/engine.wav")
    player = Player("assets/images/helicopter.png")
    all_sprites = pygame.sprite.Group(player)

    enemies = pygame.sprite.Group()
    for _ in range(5):
        enemy = Enemy("assets/images/enemy.png", WIDTH, HEIGHT)
        all_sprites.add(enemy)
        enemies.add(enemy)

    helicopter_sound.play(-1)
    running = True
    score = 0
    game_over = False

    while running:
        clock.tick(FPS)
        if not game_over:
            score += 1

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        if not game_over:
            keys = pygame.key.get_pressed()
            player.update(keys)
            enemies.update()

            # Check collision
            if pygame.sprite.spritecollideany(player, enemies):
                game_over = True
                helicopter_sound.stop()
                name = input("Game Over! Enter your name for the leaderboard: ")
                add_score(name, score)

        for x in range(0, WIDTH, 64):
            for y in range(0, HEIGHT, 64):
                screen.blit(bg_tile, (x, y))

        all_sprites.draw(screen)

        # Display score
        score_text = font.render(f"Score: {score}", True, (255, 255, 255))
        screen.blit(score_text, (10, 10))

        if game_over:
            over_text = font.render("GAME OVER", True, (255, 0, 0))
            screen.blit(over_text, (WIDTH // 2 - over_text.get_width() // 2, HEIGHT // 2))

        pygame.display.flip()

    pygame.quit()
