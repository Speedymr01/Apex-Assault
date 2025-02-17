import pygame
import os
from pygame.math import Vector2 as vector
from entity import Entity
from settings import *
import sys

class Player(Entity):
    def __init__(self, pos, groups, path, collision_sprites, create_bullet):
        super().__init__(pos, groups, path, collision_sprites)
        self.create_bullet = create_bullet
        self.bullet_shot = False
        self.health = 3
        self.reloading = False
        self.reload_start_time = 0
        self.reload_duration = 750
        self.ammo = 6
        self.reload_sound = pygame.mixer.Sound('sound/reload.mp3')
        self.score = 0

        # Load animations
        self.animations = self.import_assets(path)
        self.frame_index = 0
        self.status = 'Idle'

        # Load right image
        self.right_image = pygame.image.load('./graphics/player/right.png').convert_alpha()

    def import_assets(self, path):
        animations = {}
        for root, _, files in os.walk(path):
            for file in files:
                if file.endswith('.png'):
                    animation_name = file.split('.')[0]
                    image = pygame.image.load(os.path.join(root, file)).convert_alpha()
                    image = pygame.transform.scale(image, (int(image.get_width() * 2), int(image.get_height() * 2))) 
                    frames = self.extract_frames(image)
                    animations[animation_name] = frames
        return animations

    def extract_frames(self, image):
        frames = []
        frame_width, frame_height = 48, 48
        frame_width = int(frame_width * 2)
        frame_height = int(frame_height * 2)
        num_frames = image.get_width() // frame_width
        
        for i in range(num_frames):
            frame = image.subsurface((i * frame_width, 0, frame_width, frame_height))
            frames.append(frame)
        return frames

    def get_status(self):
        if self.direction.x == 0 and self.direction.y == 0:
            self.status = 'Idle'
        if self.attacking:
            self.status = 'Attack'
        elif self.direction.magnitude() > 0:
            self.status = 'Walk'

    def input(self):
        keys = pygame.key.get_pressed()
        if not self.attacking:
            if keys[pygame.K_d]:
                self.direction.x = 1
                self.status = 'Walk'
            elif keys[pygame.K_a]:
                self.direction.x = -1
                self.status = 'Walk'
            else:
                self.direction.x = 0
            if keys[pygame.K_w]:
                self.direction.y = -1
                self.status = 'Walk'
            elif keys[pygame.K_s]:
                self.direction.y = 1
                self.status = 'Walk'
            else:
                self.direction.y = 0
            if keys[pygame.K_r]:
                self.reload()
            if pygame.mouse.get_pressed()[0]:
                if self.ammo > 0 and not self.reloading:
                    self.attacking = True
                    self.direction = vector()
                    self.frame_index = 0
                    self.bullet_shot = False
                    self.ammo -= 1

    def animate(self, dt):
        current_animation = self.animations.get(self.status, [self.image])
        
        self.frame_index += 7 * dt
        if int(self.frame_index) >= len(current_animation):
            self.frame_index = 0
            if self.attacking:
                self.attacking = False
        
        self.image = current_animation[int(self.frame_index)]
        self.mask = pygame.mask.from_surface(self.image)

        # Calculate angle to mouse
        mouse_direction = self.get_mouse_direction()
        angle = mouse_direction.angle_to(vector(1, 0))

        # Rotate right image
        rotated_right_image = pygame.transform.rotate(self.right_image, -angle)

        # Blit rotated right image at specified coordinates
        self.image.blit(rotated_right_image, (self.image.get_width() / 2 - rotated_right_image.get_width() / 2, self.image.get_height() / 2 - rotated_right_image.get_height() / 2))

    def reload(self):
        if self.ammo < 6 and not self.reloading:
            self.reloading = True
            self.reload_start_time = pygame.time.get_ticks()
            self.reload_sound.play()

    def check_death(self):
        if self.health <= 0:
            pygame.quit()
            sys.exit()

    def get_mouse_direction(self):
        mouse_pos = vector(pygame.mouse.get_pos())
        player_pos = vector(self.rect.center)
        if mouse_pos == player_pos:
            return vector()
        direction = (mouse_pos - player_pos).normalize()
        return direction

    def update(self, dt):
        if self.reloading:
            elapsed_time = pygame.time.get_ticks() - self.reload_start_time
            if elapsed_time >= self.reload_duration:
                self.reloading = False
                self.ammo = 6
        
        self.get_status()
        self.input()
        self.move(dt)
        self.animate(dt)
        self.blink()
        self.vulnerability_timer()
        self.check_death()
