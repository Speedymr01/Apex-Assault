import pygame
import random
from sprite import Sprite
from monster import Coffin, Cactus, HybridEnemy
from settings import PATHS, DIFFICULTY, WINDOW_WIDTH, WINDOW_HEIGHT
import math
import pytmx

# Define custom exception
class SpawnRectNotFound(Exception):
    pass

class Spawner(Sprite):
    def __init__(self, pos, groups, collision_sprites, player, create_bullet, enemy_groups, spawn_number):
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
        self.spawn_number = spawn_number
        self.spawn_rect = self.find_spawn_rect()

    def damage(self):
        self.health -= 1
        if self.health >= 0:
            self.frame_index += 1
            self.image = self.frames[self.frame_index]
        if self.health <= 0:
            self.kill()

    def spawn_enemy(self):
        print('spawning enemy')
        for _ in range(2):  # Spawn 2 enemies
            angle = random.uniform(0, 2 * math.pi)
            distance = random.uniform(0, self.spawn_radius)
            spawn_x = self.rect.centerx + distance * math.cos(angle)
            spawn_y = self.rect.centery + distance * math.sin(angle)
            spawn_pos = (spawn_x, spawn_y)
            HybridEnemy(spawn_pos, self.enemy_groups, './graphics/enemy', self.collision_sprites, self.player, self.create_bullet)

    def find_spawn_rect(self):
        tmx_map = pytmx.load_pygame('./data/map.tmx')
        found_rects = []
        for layer in tmx_map.layers:
            if layer.name == 'Spawns':
                for obj in layer:
                    found_rects.append((obj.spawner, pygame.Rect(obj.x, obj.y, obj.width, obj.height)))
                    if obj.spawner == self.spawn_number:
                        spawn_rect = pygame.Rect(obj.x, obj.y, obj.width, obj.height)
                        print('found spawner rect:', spawn_rect, obj.spawner)
                        return spawn_rect
        raise SpawnRectNotFound(f'Spawn rectangle with spawner number {self.spawn_number} not found. Found rects: {found_rects}')

    def player_in_spawn_rect(self):
        if not self.spawn_rect:
            return False
        player_in_rect = self.spawn_rect.colliderect(self.player.rect)
        #print(f'Player rect: {self.player.rect}, Spawn rect: {self.spawn_rect}, Player in rect: {player_in_rect}')
        return player_in_rect

    def update(self, dt):
        current_time = pygame.time.get_ticks()
        if self.player_in_spawn_rect():
            print('player in spawn rectangle')
            if current_time - self.last_spawn_time > self.spawn_cooldown:
                print('spawning enemy')
                self.spawn_enemy()
                self.last_spawn_time = current_time