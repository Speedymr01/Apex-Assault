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

import pygame, sys
from settings import * 
from player import Player
from pygame.math import Vector2 as vector
from pytmx.util_pygame import load_pygame
from sprite import Sprite, Bullet, Button
from monster import Coffin, Cactus
import time
from doors import PistonDoor
from spawner import Spawner

class Allsprites(pygame.sprite.Group):
    def __init__(self):
        super().__init__()
        self.offset = vector()
        self.display_surface = pygame.display.get_surface()
        self.bg = pygame.image.load('./graphics/other/map.png').convert()
    
    def customize_draw(self, player):
        self.offset.x = player.rect.centerx - WINDOW_WIDTH / 2
        self.offset.y = player.rect.centery - WINDOW_HEIGHT / 2

        self.display_surface.blit(self.bg, -self.offset)
        for sprite in sorted(self.sprites(), key = lambda sprite: sprite.rect.centery):
            offset_rect = sprite.image.get_rect(center = sprite.rect.center)
            offset_rect.center -= self.offset
            self.display_surface.blit(sprite.image, offset_rect)

        
class Intro:
    def __init__(self):
        pygame.init()
        self.display_surface = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption('Apex Assault')
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font('./font/subatomic.ttf', 50)
        self.music = pygame.mixer.Sound('./sound/music.mp3')
        self.music.set_volume(MUSIC_VOLUME)
        self.music.play()

        # Skip text
        self.skip_font = pygame.font.Font('./font/subatomic.ttf', 25)
        self.skip_text = self.skip_font.render('Press [SPACE] to skip', True, (255, 255, 255))
        self.skip_text_rect = self.skip_text.get_rect(bottomright=(WINDOW_WIDTH - 20, WINDOW_HEIGHT - 20))

        # Scrolling text
        self.scroll_text = SCROLLING_TEXT
        self.scroll_font = pygame.font.Font('./font/subatomic.ttf', 20)
        self.scroll_speed = 0.38  # Adjusted to allow smooth floating-point scrolling
        self.scroll_y = WINDOW_HEIGHT  # Initial y position of scrolling text
        self.final_text_y = WINDOW_HEIGHT
        self.show_final_text = False
        self.introing = True
        self.music_stopped = False
        self.run()

    def run(self):
        while self.introing:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        if not self.music_stopped:
                            self.music.stop()
                            self.music_stopped = True
                            self.show_final_text = True
                            self.final_text_y = WINDOW_HEIGHT / 2 - 130
                        else:
                            self.introing = False

            self.display_surface.fill('black')

            self.display_surface.blit(self.skip_text, self.skip_text_rect)

            # Update and draw scrolling text
            if not self.show_final_text:
                self.scroll_y -= self.scroll_speed
                for i, line in enumerate(self.scroll_text):
                    scroll_text_surf = self.scroll_font.render(line, True, (255, 255, 255))
                    scroll_text_rect = scroll_text_surf.get_rect(center=(WINDOW_WIDTH / 2, self.scroll_y + i * 30))
                    self.display_surface.blit(scroll_text_surf, scroll_text_rect)
                if self.scroll_y + len(self.scroll_text) * 30 < WINDOW_HEIGHT / 2:
                    self.show_final_text = True
            if self.show_final_text:
                self.final_text_y -= self.scroll_speed
                final_text_font_small = pygame.font.Font('./font/subatomic.ttf', 30)
                final_text_font_large = pygame.font.Font('./font/subatomic.ttf', 70)
                final_text_small = final_text_font_small.render("This is", True, (255, 255, 255))
                final_text_large = final_text_font_large.render("Apex Assault", True, (255, 255, 255))
                combat_text = final_text_font_small.render("Combat", True, (255, 255, 255))
                combat_rect = combat_text.get_rect(center=(WINDOW_WIDTH / 2, self.final_text_y + 130))
                pygame.draw.rect(self.display_surface, (255, 255, 255), combat_rect.inflate(20, 10), 2)
                self.display_surface.blit(final_text_small, final_text_small.get_rect(center=(WINDOW_WIDTH / 2, self.final_text_y)))
                self.display_surface.blit(final_text_large, final_text_large.get_rect(center=(WINDOW_WIDTH / 2, self.final_text_y + 50)))
                self.display_surface.blit(combat_text, combat_rect)

                if self.final_text_y + 130 <= WINDOW_HEIGHT / 2:
                    self.final_text_y = WINDOW_HEIGHT / 2 - 130

            pygame.display.update()
            self.clock.tick(60)




class Game: 
    def __init__(self):
        pygame.init()
        self.display_surface = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption('Western shooter')
        self.clock = pygame.time.Clock()
        self.bullet_surf = pygame.image.load('./graphics/other/bullet.png').convert_alpha()
        

        # Groups
        self.all_sprites = Allsprites()
        self.obstacles = pygame.sprite.Group()
        self.bullets = pygame.sprite.Group()
        self.monsters = pygame.sprite.Group()
        self.spawners = pygame.sprite.Group()
        
        self.enemy_groups = [self.obstacles, self.monsters, self.all_sprites]
        self.setup()
        self.font = pygame.font.Font('./font/subatomic.ttf', 50)
        #self.music = pygame.mixer.Sound('./sound/music.mp3')
        #self.music.set_volume(MUSIC_VOLUME)
        #self.music.play(loops = -1)
        

    def create_bullet(self, pos, direction):
        Bullet(pos, direction, self.bullet_surf, [self.all_sprites, self.bullets], self.player)

    def bullet_collision(self):
        for obstacle in self.obstacles.sprites():
            if not isinstance(obstacle, Spawner):
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

        # Handle collisions between bullets and spawners
        for bullet in self.bullets.sprites():
            spawners = pygame.sprite.spritecollide(bullet, self.obstacles, False, pygame.sprite.collide_mask)
            for spawner in spawners:
                if isinstance(spawner, Spawner):
                    bullet.kill()
                    spawner.damage()

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
        pistons_layer = tmx_map.get_layer_by_name('Pistons')

        doors = {}
        for obj in pistons_layer:
            image_path = obj.source.replace("..", ".")
            print(f"Door image path: {image_path}")  # Debugging print
            door = PistonDoor((obj.x, obj.y), image_path, [self.all_sprites, self.obstacles])
            door_id = int(obj.properties['door'])
            if door_id not in doors:
                doors[door_id] = []
            doors[door_id].append(door)

        for door_pair in doors.values():
            if len(door_pair) == 2:
                door_pair[0].pair = door_pair[1]
                door_pair[1].pair = door_pair[0]


        self.walls = pygame.sprite.Group()
        for x, y, surf in tmx_map.get_layer_by_name('Walls').tiles():
            Sprite((x * 32, y * 32), surf, [self.all_sprites, self.obstacles, self.walls])
        
        for x, y, surf in tmx_map.get_layer_by_name('Pistonwall').tiles():
            Sprite((x * 32, y * 32), surf, [self.all_sprites, self.obstacles])
        
        buttons_layer = tmx_map.get_layer_by_name('Buttons')
        for obj in buttons_layer:
            button_image_path = obj.source.replace("..", ".")
            print(f"Button image path: {button_image_path}")  # Debugging print
            button = Button((obj.x, obj.y), button_image_path, [self.all_sprites, self.obstacles])
            button_id = int(obj.properties['door'])
            if button_id in doors:
                button.door = doors[button_id][0]  # Assign the first door in the pair to the button

        for obj in tmx_map.get_layer_by_name('Entities'):
            if obj.name == 'Player':
                self.player = Player(
                    pos=(obj.x, obj.y),
                    groups=self.all_sprites,
                    path=PATHS['player'],
                    collision_sprites=self.obstacles,
                    create_bullet=self.create_bullet,
                    display_surf=self.display_surface)
            
            if obj.name == 'Spawner':
                spawn_number = obj.properties['spawner']
                Spawner((obj.x, obj.y), [self.all_sprites, self.obstacles, self.spawners], self.obstacles, self.player, self.create_bullet, self.enemy_groups, spawn_number)

        self.heart_surf = pygame.image.load('./graphics/other/heart.png').convert_alpha()
        
    def extract_number_from_path(self, path):
        # Assuming the number is part of the filename, e.g., "1.png"
        filename = path.split('/')[-1]
        number = int(filename.split('.')[0])
        return number

    def display_win(self):
        Highscore_text = 'You Escaped!'
        text_surf = self.font.render(Highscore_text, True, (255, 0, 0))
        text_rect = text_surf.get_rect(midbottom = (WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2))
        self.display_surface.blit(text_surf, text_rect)
        pygame.draw.rect(self.display_surface, (255, 0, 0), text_rect.inflate(30, 30), width = 8, border_radius = 5)
        pygame.display.update()
        time.sleep(5)

    def check_button_presses(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_e]:
            for button in self.obstacles:
                if isinstance(button, Button) and self.player.rect.colliderect(button.rect):
                    if not button.pressed:
                        print(f"Button pressed at {button.rect.topleft}")
                        print('yes')
                        if button.door:
                            button.door.start_moving()
                        button.pressed = True
                        print(f"Door at {button.door.rect.topleft} started moving")

    def run(self):
        while self.player.score != 25:
            # event loop 
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
            dt = self.clock.tick() / 1000

            # Update
            for sprite in self.all_sprites.sprites():
                if not isinstance(sprite, PistonDoor):
                    sprite.update(dt)
                elif isinstance(sprite, PistonDoor):
                    sprite.update(dt, self.walls)
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
    install_modules(modules)
    
    intro = Intro()
    intro.run()

    if AGREE:
        game = Game()
        game.run()
    else:
        print("You have not agreed to the t's and c's, find them in the settings file")