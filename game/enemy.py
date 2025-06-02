import pygame
import random

class Enemy(pygame.sprite.Sprite):
    def __init__(self, image_path, width, height):
        super().__init__()
        self.image = pygame.image.load(image_path).convert_alpha()
        self.rect = self.image.get_rect()
        self.rect.x = random.randint(0, width - self.rect.width)
        self.rect.y = random.randint(-150, -40)
        self.speedy = random.randint(3, 7)

    def update(self):
        self.rect.y += self.speedy
        if self.rect.top > height:
            self.rect.y = random.randint(-100, -40)
            self.rect.x = random.randint(0, width - self.rect.width)
