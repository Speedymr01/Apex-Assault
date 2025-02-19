import pygame
from sprite import Sprite

class PistonDoor(Sprite):
    def __init__(self, pos, image_path, groups, direction):
        surf = pygame.image.load(image_path).convert_alpha()
        super().__init__(pos, surf, groups)
        self.direction = direction
        self.speed = 100  # Adjust the speed as needed
        self.moving = False

    def start_moving(self):
        self.moving = True

    def stop_moving(self):
        self.moving = False

    def update(self, dt):
        if self.moving:
            if self.direction == 'up':
                self.rect.y -= self.speed * dt
            elif self.direction == 'down':
                self.rect.y += self.speed * dt
            elif self.direction == 'left':
                self.rect.x -= self.speed * dt
            elif self.direction == 'right':
                self.rect.x += self.speed * dt

            # Check for collision with other pistons
            for sprite in self.groups()[0]:
                if isinstance(sprite, PistonDoor) and sprite != self:
                    if self.rect.colliderect(sprite.rect):
                        self.stop_moving()
                        sprite.stop_moving()
