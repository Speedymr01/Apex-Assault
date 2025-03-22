import pygame
from pygame.math import Vector2 as vector
import random

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
    def __init__(self, pos, image_path, groups, door=None, player=None, button_id=None):
        super().__init__(groups)
        self.image = pygame.image.load(image_path).convert_alpha()
        self.rect = self.image.get_rect(topleft=pos)
        self.hitbox = self.rect.inflate(0, 0)
        self.door = door
        self.player = player
        self.pressed = False
        self.button_id = button_id
        self.sound = pygame.mixer.Sound('./sound/opening.mp3')  # Load the sound
        self.deny_sound = pygame.mixer.Sound('./sound/denied.mp3')
        self.press_count = 0
        self.random_press = 0

    def press(self):
        if not self.pressed:
            self.pressed = True
            if self.door:
                if self.button_id != 2 or 6 or 7:
                    self.door.start_moving()
            if self.button_id == 2:
                if self.player.pickedup_key:
                    self.door.speed = 100
                    self.door.pair.speed = 100
                    self.sound.play()  # Play the sound if button_id is 2
                    self.door.start_moving()
                    if not self.door.moving:
                        self.sound.stop()
                else:
                    self.pressed = False
                    self.deny_sound.play()
                    
            if self.button_id == 6:
                self.press_count += 1
                if self.press_count == 2:
                    self.door.start_moving()
                    self.pressed = True

            if self.button_id == 7:
                self.random_press = random.randint(0, 1)
                if self.random_press == 1:
                    self.door.start_moving()
                else:
                    self.deny_sound.play()
                    self.random_press = 1



class Key(pygame.sprite.Sprite):
    def __init__(self, pos, groups, player):
        super().__init__(groups)
        original_image = pygame.image.load('./graphics/key.png').convert_alpha()
        scale_factor = 2.5
        new_size = (int(original_image.get_width() * scale_factor), int(original_image.get_height() * scale_factor))
        self.image = pygame.transform.scale(original_image, new_size)
        self.rect = self.image.get_rect(topleft=pos)
        self.hitbox = self.rect.inflate(0, -self.rect.height / 3)
        self.mask = pygame.mask.from_surface(self.image)
        self.picked = False
        self.player = player
                
    def pickup(self):
        if self.rect.colliderect(self.player.hitbox):
            self.picked = True
            self.player.pickedup_key = True
            self.kill()


    def update(self, dt):
        self.pickup()
