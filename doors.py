import pygame
from sprite import Sprite

class PistonDoor(Sprite):
    def __init__(self, pos, image_path, groups, pair=None):
        print(f"Loading image from path: {image_path}")  # Debugging print
        surf = pygame.image.load(image_path).convert_alpha()
        super().__init__(pos, surf, groups)
        self.path = image_path
        self.rect = self.image.get_rect(topleft=pos)
        self.hitbox = self.rect.inflate(0, -self.rect.height / 3)
        self.mask = pygame.mask.from_surface(self.image)
        self.speed = 250  # Adjust the speed as needed
        self.moving = False
        self.direction = self.find_direction()
        self.pair = pair  # Add pair attribute

    def start_moving(self):
        self.moving = True
        print('Moving')
        if self.pair and not self.pair.moving:
            self.pair.start_moving()

    def stop_moving(self):
        self.moving = False
        print('Stopped')

    def find_direction(self):
        if "down" in self.path:
            return "up"
        elif "up" in self.path:
            return "down"
        elif "left" in self.path:
            return "right"
        elif "right" in self.path:
            return "left"
        return None

    def update(self, dt, walls):
        if self.moving:
            if self.direction == 'up':
                self.rect.y -= self.speed * dt
            elif self.direction == 'down':
                self.rect.y += self.speed * dt
            elif self.direction == 'left':
                self.rect.x -= self.speed * dt
            elif self.direction == 'right':
                self.rect.x += self.speed * dt

            # Update hitbox position
            self.hitbox.topleft = self.rect.topleft



            # Check for collision with walls
            if pygame.sprite.spritecollide(self, walls, False, pygame.sprite.collide_mask):
                self.stop_moving()
                print('Collision detected with wall')
