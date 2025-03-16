import pygame
from pygame.math import Vector2 as vector
from os import walk
from settings import *

class Entity(pygame.sprite.Sprite):
    def __init__(self, pos, groups, path, collision_sprites):
        super().__init__(groups)

        self.animations = self.import_assets(path)
        self.frame_index = 0
        self.status = 'Idle'

        # Ensure the status key exists in the animations dictionary

        print(self.animations)
        self.image = self.animations[self.status][self.frame_index]    
        self.rect = self.image.get_rect(center=pos)
        self.scale_factor = 1.5

        self.pos = vector(self.rect.center)
        self.direction = vector()
        self.speed = 250

        # collision
        self.hitbox = self.rect.inflate(-self.rect.width * 0.5, 1)
        self.collision_sprites = collision_sprites
        self.mask = pygame.mask.from_surface(self.image)

        # Attack
        self.attacking = False
        self.attack_frame = 2
        self.coffin_damage = False
        self.ammo = AMMO

        # health
        self.health = 3
        self.is_vulnerable = True
        self.hit_time = None
        self.score = 0

        self.hit_sound = pygame.mixer.Sound('./sound/ouch.mp3')
        self.hit_sound.set_volume(DAMAGE_SOUND_VOLUME)
        self.shoot_sound = pygame.mixer.Sound('./sound/shoot.mp3')
        self.shoot_sound.set_volume(SHOOT_SOUND_VOLUME)

    @staticmethod
    def bresenham(x1, y1, x2, y2):
        """Generates all points along a line using Bresenham's algorithm."""
        points = []
        dx = abs(x2 - x1)
        dy = abs(y2 - y1)
        sx = 1 if x1 < x2 else -1
        sy = 1 if y1 < y2 else -1
        err = dx - dy

        while True:
            points.append((x1, y1))
            if x1 == x2 and y1 == y2:
                break
            e2 = err * 2
            if e2 > -dy:
                err -= dy
                x1 += sx
            if e2 < dx:
                err += dx
                y1 += sy

        return points

    def is_obstructed(self, start_pos, end_pos):
        """
        Checks if there is an obstruction (wall or solid object) between two positions.
        """
        # Correct way to call Bresenham now
        line_points = list(Entity.bresenham(int(start_pos[0]), int(start_pos[1]), int(end_pos[0]), int(end_pos[1])))

        # Check if any point collides with a wall sprite
        for point in line_points:
            for sprite in self.collision_sprites:
                if sprite.rect.collidepoint(point):  # If any wall covers this point
                    return True  # Obstruction detected

        return False  # No obstruction

    




    def vulnerability_timer(self):
        if not self.is_vulnerable:
            current_time = pygame.time.get_ticks()
            if (current_time - self.hit_time) > 400:
                self.is_vulnerable = True
   
    def import_assets(self, path):
        animations = {}

        for index, folder in enumerate(walk(path)):
            if index == 0:
                for name in folder[1]:
                    animations[name] = []
            else:
                for file_name in sorted(folder[2], key=lambda string: int(string.split('.')[0])):
                    path = folder[0].replace("\\", "/") + '/' + file_name
                    surf = pygame.image.load(path).convert_alpha()
                    key = folder[0].split('\\')[1]
                    animations[key].append(surf)
        print(animations)
        return animations

    def move(self, dt):
        # Normalize
        if self.direction.magnitude() != 0:
            self.direction = self.direction.normalize()

        # Horizontal
        self.pos.x += self.direction.x * self.speed * dt
        self.hitbox.centerx = round(self.pos.x)
        self.rect.centerx = self.hitbox.centerx
        self.collision('horizontal')
        # Vertical
        self.pos.y += self.direction.y * self.speed * dt
        self.hitbox.centery = round(self.pos.y)
        self.rect.centery = self.hitbox.centery
        self.collision('vertical')

    def collision(self, direction):
        for sprite in self.collision_sprites.sprites():
            if sprite.hitbox.colliderect(self.hitbox):
                if direction == 'horizontal':
                    if self.direction.x > 0:  # moving right 
                        self.hitbox.right = sprite.hitbox.left
                    if self.direction.x < 0:  # moving left
                        self.hitbox.left = sprite.hitbox.right
                    self.rect.centerx = self.hitbox.centerx
                    self.pos.x = self.hitbox.centerx
                else:  # vertical
                    if self.direction.y > 0:  # moving down
                        self.hitbox.bottom = sprite.hitbox.top
                    if self.direction.y < 0:  # moving up
                        self.hitbox.top = sprite.hitbox.bottom
                    self.rect.centery = self.hitbox.centery
                    self.pos.y = self.hitbox.centery
