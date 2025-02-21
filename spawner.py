import pygame
import random
from sprite import Sprite
from monster import Coffin, Cactus, HybridEnemy
from settings import PATHS, DIFFICULTY
import math

class Spawner(Sprite):
    def __init__(self, pos, groups, collision_sprites, player, create_bullet, enemy_groups):
        image_path = './graphics/other/spawner_.png'
        surf = pygame.image.load(image_path).convert_alpha()
        super().__init__(pos, surf, groups)
        self.collision_sprites = collision_sprites
        self.player = player
        self.create_bullet = create_bullet
        self.frame_index = 0
        self.enemy_groups = enemy_groups
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
        print('spawning enemy')
        angle = random.uniform(0, 2 * 3.14159)
        distance = random.uniform(0, self.spawn_radius)
        spawn_x = self.rect.centerx + distance * math.cos(angle)
        spawn_y = self.rect.centery + distance * math.sin(angle)
        spawn_pos = (spawn_x, spawn_y)
        HybridEnemy(spawn_pos, self.enemy_groups, './graphics/enemy', self.collision_sprites, self.player, self.create_bullet)

    def player_in_line_of_sight(self):
        start_pos = self.rect.center
        end_pos = self.player.rect.center
        
        for sprite in self.collision_sprites:
            if sprite.rect.clipline(start_pos, end_pos):
                return True  # Line is blocked

        return False

    def update(self, dt):
        current_time = pygame.time.get_ticks()
        if self.player_in_line_of_sight():
            print('player in line of sight')
            if current_time - self.last_spawn_time > self.spawn_cooldown:
                self.spawn_enemy()
                self.last_spawn_time = current_time