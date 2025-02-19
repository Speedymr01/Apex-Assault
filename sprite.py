import pygame

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
        self.mask = pygame.mask.from_surface(self.image)
        self.rect = self.image.get_rect(center=pos)
        self.pos = pygame.math.Vector2(self.rect.center)
        self.direction = direction
        self.speed = 1500
        self.shooter = shooter  # Add shooter attribute
    
    def update(self, dt):
        self.pos += self.direction * self.speed * dt
        self.rect.center = (round(self.pos.x), round(self.pos.y))

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

