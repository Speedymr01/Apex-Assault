import pygame
from pygame.math import Vector2 as vector

class Sprite(pygame.sprite.Sprite):
    def __init__(self, pos, surf, groups):
        super().__init__(groups)
        self.image = surf
        self.rect = self.image.get_rect(topleft=pos)
        self.hitbox = self.rect.inflate(0, -self.rect.height / 3)
        self.mask = pygame.mask.from_surface(self.image)

class Bullet(pygame.sprite.Sprite):
    def __init__(self, pos, direction, surf, groups, shooter):
        super().__init__(groups)
        self.image = surf
        self.rect = self.image.get_rect(center=pos)
        self.pos = vector(self.rect.center)
        self.direction = direction.normalize()
        self.speed = 400
        self.shooter = shooter  # Store the reference to the shooter

    def update(self, dt):
        self.pos += self.direction * self.speed * dt
        self.rect.center = self.pos

        

class Button(pygame.sprite.Sprite):
    def __init__(self, pos, image_path, groups, door=None):
        super().__init__(groups)
        self.image = pygame.image.load(image_path).convert_alpha()
        self.rect = self.image.get_rect(topleft=pos)
        self.hitbox = self.rect.inflate(0, -self.rect.height / 3)
        self.mask = pygame.mask.from_surface(self.image)
        self.pressed = False
        self.door = door  # Add door attribute
        self.number = self.extract_number_from_path(image_path)

    def extract_number_from_path(self, path):
        # Assuming the number is part of the filename, e.g., "1.png"
        filename = path.split('/')[-1]
        number = int(filename.split('.')[0])
        return number

