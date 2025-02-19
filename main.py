import os
from settings import MODS
import sys
modules = [
    'pygame',
    'pytmx'
]
def install_modules(modules):
    consent = MODS
    for module in modules:
        try:
            __import__(module)
        except ImportError:
            if consent == None:
                print('This Game requires the following modules:')
                print('1: Pygame (Supports main game operation )')
                print('2: Pytmx (Supports main graphics)')
                print('Please consent to these being installed in the settings.py file')
                sys.exit(1)
            if consent == True:
                command = f"py -m pip install {module}"
                os.system(command)
                print(f"{module} installed successfully.")
install_modules(modules)

import pygame, sys
from settings import * 
from player import Player
from pygame.math import Vector2 as vector
from pytmx.util_pygame import load_pygame
from sprite import Sprite, Bullet, Button
from monster import Coffin, Cactus
import time
from doors import PistonDoor

class Allsprites(pygame.sprite.Group):
    def __init__(self):
        super().__init__()
        self.offset = vector()
        self.display_surface = pygame.display.get_surface()
        self.bg = pygame.image.load('./graphics/other/map.png').convert()
    
    def customize_draw(self, player):
        self.offset.x = player.rect.centerx - WINDOW_WIDTH / 2 - 25
        self.offset.y = player.rect.centery - WINDOW_HEIGHT / 2 + 15

        self.display_surface.blit(self.bg, -self.offset)
        for sprite in sorted(self.sprites(), key = lambda sprite: sprite.rect.centery):
            offset_rect = sprite.image.get_rect(center = sprite.rect.center)
            offset_rect.center -= self.offset
            self.display_surface.blit(sprite.image, offset_rect)

class Game: 
    def __init__(self):
        pygame.init()
        self.display_surface = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption('Western shooter')
        self.clock = pygame.time.Clock()
        self.bullet_surf = pygame.image.load('graphics/other/bullet.png').convert_alpha()

        # Groups
        self.all_sprites = Allsprites()
        self.obstacles = pygame.sprite.Group()
        self.bullets = pygame.sprite.Group()
        self.monsters = pygame.sprite.Group()

        self.setup()
        self.font = pygame.font.Font('./font/subatomic.ttf', 50)
        #self.music = pygame.mixer.Sound('./sound/music.mp3')
        #self.music.set_volume(MUSIC_VOLUME)
        #self.music.play(loops = -1)

    def create_bullet(self, pos, direction):
        Bullet(pos, direction, self.bullet_surf, [self.all_sprites, self.bullets], self.player)

    def bullet_collision(self):
        for obstacle in self.obstacles.sprites():
            pygame.sprite.spritecollide(obstacle, self.bullets, True, pygame.sprite.collide_mask)
        for bullet in self.bullets.sprites():
            sprites = pygame.sprite.spritecollide(bullet, self.monsters, False, pygame.sprite.collide_mask)

            if sprites:
                bullet.kill()
                for sprite in sprites:
                    sprite.damage()

        # Exclude bullets fired by the player when checking for collisions with the player
        for bullet in self.bullets.sprites():
            if bullet.shooter != self.player:
                if pygame.sprite.spritecollide(self.player, self.bullets, True, pygame.sprite.collide_mask):
                    self.player.damage()

    def ammo_display(self):
        Highscore_text = f'{self.player.ammo}/{AMMO}'
        text_surf = self.font.render(Highscore_text, True, (255, 255, 255))
        text_rect = text_surf.get_rect(midbottom = (WINDOW_WIDTH / 4 * 3, WINDOW_HEIGHT - 50))
        self.display_surface.blit(text_surf, text_rect)
        pygame.draw.rect(self.display_surface, (255, 255, 255), text_rect.inflate(30, 30), width = 8, border_radius = 5)

    def Reload_display(self):
        Highscore_text = f'Reloading...'
        text_surf = self.font.render(Highscore_text, True, (255, 255, 255))
        text_rect = text_surf.get_rect(midbottom = (WINDOW_WIDTH / 5 * 4, WINDOW_HEIGHT/ 20 * 2))
        self.display_surface.blit(text_surf, text_rect)
        pygame.draw.rect(self.display_surface, (255, 255, 255), text_rect.inflate(30, 30), width = 8, border_radius = 5)


    def setup(self):
        tmx_map = load_pygame('./data/map.tmx')
        gid_to_image_path = {
            68: './graphics/tileset/IndustrialTile_45up.png',
            77: './graphics/tileset/IndustrialTile_54.png',
            88: './graphics/tileset/IndustrialTile_45down.png',
            85: './graphics/tileset/IndustrialTile_54side.png',
            86: './graphics/tileset/IndustrialTile_45left.png',
            87: './graphics/tileset/IndustrialTile_45right.png',
            # Add other mappings as needed
    }
        

        for x, y, surf in tmx_map.get_layer_by_name('Walls').tiles():
            Sprite((x * 32, y * 32), surf, [self.all_sprites, self.obstacles])
        for obj in tmx_map.get_layer_by_name('Pistons'):
            gid = obj.gid
            direction = obj.properties.get('direction', 'up')  # Default to 'up' if no direction is specified
            print(gid)
            image_path = gid_to_image_path.get(gid, './graphics/tileset/IndustrialTile_45down.png')  # Default image path
            PistonDoor((obj.x, obj.y), image_path, [self.all_sprites, self.obstacles], direction)

        for obj in tmx_map.get_layer_by_name('Buttons'):
            Button((obj.x, obj.y), obj.image, [self.all_sprites, self.obstacles])

        for obj in tmx_map.get_layer_by_name('Entities'):
            if obj.name == 'Player':
                self.player = Player(
                    pos=(obj.x, obj.y),
                    groups=self.all_sprites,
                    path=PATHS['player'],
                    collision_sprites=self.obstacles,
                    create_bullet=self.create_bullet,
                    display_surf=self.display_surface)
            if obj.name == 'Coffin':
                Coffin((obj.x, obj.y), [self.all_sprites, self.monsters], PATHS['coffin'], self.obstacles, self.player)
            if obj.name == 'Cactus':
                Cactus((obj.x, obj.y), [self.all_sprites, self.monsters], PATHS['cactus'], self.obstacles, self.player, self.create_bullet)

        self.heart_surf = pygame.image.load('./graphics/other/heart.png').convert_alpha()


    def display_win(self):
        Highscore_text = 'You Escaped!'
        text_surf = self.font.render(Highscore_text, True, (255, 0, 0))
        text_rect = text_surf.get_rect(midbottom = (WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2))
        self.display_surface.blit(text_surf, text_rect)
        pygame.draw.rect(self.display_surface, (255, 0, 0), text_rect.inflate(30, 30), width = 8, border_radius = 5)
        pygame.display.update()
        time.sleep(5)


    def check_button_presses(self):
        for button in self.obstacles:
            if isinstance(button, Button) and button.is_pressed(self.player):
                for door in self.obstacles:
                    if isinstance(door, PistonDoor):
                        door.open_door()


    def run(self):
        while self.player.score != 25:
            # event loop 
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
            dt = self.clock.tick() / 1000

            # Update
            self.all_sprites.update(dt)
            self.bullet_collision()
            self.check_button_presses()
            # Draw
            self.display_surface.fill('black')
            
            self.all_sprites.customize_draw(self.player)

            Highscore_text = f'Score: {self.player.score}'
            text_surf = self.font.render(Highscore_text, True, (255, 255, 255))
            text_rect = text_surf.get_rect(midbottom = (WINDOW_WIDTH / 4 , WINDOW_HEIGHT - 50))
            self.display_surface.blit(text_surf, text_rect)
            pygame.draw.rect(self.display_surface, (255, 255, 255), text_rect.inflate(30, 30), width = 8, border_radius = 5)
            
            if self.player.health >= 1:    
                self.display_surface.blit(self.heart_surf, ((WINDOW_WIDTH / 60) + 200, WINDOW_HEIGHT / 90))
            if self.player.health >= 2:
                self.display_surface.blit(self.heart_surf, ((WINDOW_WIDTH / 60) + 100, WINDOW_HEIGHT / 90))
            if self.player.health >= 3:
                self.display_surface.blit(self.heart_surf, (WINDOW_WIDTH / 60, WINDOW_HEIGHT / 90))
            
            self.ammo_display()
            self.player.draw(self.display_surface)
            if self.player.reloading:
                self.Reload_display()
            pygame.display.update()
        self.display_win()

if __name__ == '__main__':
    print('Please edit the settings file before playing.')

    if AGREE:
        game = Game()
        game.run()
    else:
        print("You have not agreed to the t's and c's, find them in the settings file")