import pygame
import random
from sprite import Sprite
from monster import Coffin, Cactus
from settings import PATHS, DIFFICULTY

class Spawner(Sprite):
    def __init__(self, pos, groups, collision_sprites, player, create_bullet):
        image_path = './graphics/other/spawner_.png'
        surf = pygame.image.load(image_path).convert_alpha()
        super().__init__(pos, surf, groups)
        self.collision_sprites = collision_sprites
        self.player = player
        self.create_bullet = create_bullet
        self.frame_index = 0
        self.frames = [
            pygame.image.load('./graphics/other/spawner_.png').convert_alpha(),
            pygame.image.load('./graphics/other/spawner_x.png').convert_alpha(),
            pygame.image.load('./graphics/other/spawner_xx.png').convert_alpha(),
            pygame.image.load('./graphics/other/spawner_xxx.png').convert_alpha()
        ]
        self.health = 3
        self.spawn_radius = 100  # Radius around the spawner to spawn enemies
        self.spawn_cooldown = 5000  # Cooldown in milliseconds
        self.last_spawn_time = pygame.time.get_ticks()

    def damage(self):
        self.health -= 1
        if self.health >= 0:
            self.frame_index += 1
            self.image = self.frames[self.frame_index]
        if self.health <= 0:
            self.kill()

    def spawn_enemy(self):
        enemy_type = 'Coffin' if DIFFICULTY % 2 == 0 else 'Cactus'
        angle = random.uniform(0, 2 * 3.14159)
        distance = random.uniform(0, self.spawn_radius)
        spawn_x = self.rect.centerx + distance * pygame.math.cos(angle)
        spawn_y = self.rect.centery + distance * pygame.math.sin(angle)
        spawn_pos = (spawn_x, spawn_y)
        
        if enemy_type == 'Coffin':
            Coffin(spawn_pos, [self.groups()[0], self.groups()[1]], PATHS['coffin'], self.collision_sprites, self.player)
        else:
            Cactus(spawn_pos, [self.groups()[0], self.groups()[1]], PATHS['cactus'], self.collision_sprites, self.player, self.create_bullet)

    def player_in_line_of_sight(self):
        start_pos = pygame.math.Vector2(self.rect.center)
        end_pos = pygame.math.Vector2(self.player.rect.center)
        direction = (end_pos - start_pos).normalize()
        distance = start_pos.distance_to(end_pos)
        for i in range(int(distance)):
            pos = start_pos + direction * i
            if any(sprite.rect.collidepoint(pos) for sprite in self.collision_sprites):
                return False
        return True

    def update(self, dt):
        current_time = pygame.time.get_ticks()
        if current_time - self.last_spawn_time > self.spawn_cooldown:
            if self.player_in_line_of_sight():
                self.spawn_enemy()
                self.last_spawn_time = current_time