import pygame
from .settings import WIDTH, HEIGHT, FPS
from .player import Player
from .leaderboard import add_score

def run():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Helicopter Game")
    clock = pygame.time.Clock()

    # Load assets
    bg_tile = pygame.image.load("assets/images/tile_grass.png").convert()
    helicopter_sound = pygame.mixer.Sound("assets/sounds/engine.wav")
    player = Player("assets/images/helicopter.png")
    all_sprites = pygame.sprite.Group(player)

    helicopter_sound.play(-1)
    running = True
    score = 0

    while running:
        clock.tick(FPS)
        score += 1  # Simple timer as score

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        keys = pygame.key.get_pressed()
        player.update(keys)

        for x in range(0, WIDTH, 64):
            for y in range(0, HEIGHT, 64):
                screen.blit(bg_tile, (x, y))

        all_sprites.draw(screen)
        pygame.display.flip()

    helicopter_sound.stop()
    name = input("Enter your name for the leaderboard: ")
    add_score(name, score)
    pygame.quit()
