import pygame
from entity import Entity
from pygame.math import Vector2 as vector
from settings import *
import os

class Monster():
    def get_player_distance_direction(self):
        enemy_pos = vector(self.rect.center)
        player_pos = vector(self.player.rect.center)
        distance = (player_pos - enemy_pos).magnitude()

        if distance != 0:
            direction = (player_pos - enemy_pos).normalize()
        else:
            direction = vector()

        return (distance, direction)

    def face_player(self):
        distance, direction = self.get_player_distance_direction()

        if distance < self.notice_radius:
            if -0.5 < direction.y < 0.5:
                if direction.x < 0: # player to the left
                    self.status = 'left_idle'
                elif direction.x > 0: # player to the right
                    self.status = 'right_idle'
            else:
                if direction.y < 0: # player to the top
                    self.status = 'up_idle'
                elif direction.y > 0: # player to the bottom
                    self.status = 'down_idle'

    def walk_to_player(self):
        distance, direction = self.get_player_distance_direction()
        if self.attack_radius < distance < self.walk_radius:
            self.direction = direction
            self.status = self.status.split('_')[0]
        else:
            self.direction = vector()

class Coffin(Entity, Monster):
    def __init__(self, pos, groups, path, collision_sprites, player):
        super().__init__(pos, groups, path, collision_sprites)
        
        # overwrites
        self.speed = 150
        self.attack_frame = 4
        self.health = 2 + DIFFICULTY

        # player interaction
        self.player = player
        self.notice_radius = 550
        self.walk_radius = 400
        self.attack_radius = 50
        self.player.score = 0

    def animate(self, dt):
        current_animation = self.animations[self.status]

        if int(self.frame_index) == self.attack_frame and self.attacking:
            if self.get_player_distance_direction()[0] < self.attack_radius:
                self.player.damage()
                
        self.frame_index += 7 * dt
        if self.frame_index >= len(current_animation):
            self.frame_index = 0
            if self.attacking:
                self.attacking = False
        self.image = current_animation[int(self.frame_index)]
        self.mask = pygame.mask.from_surface(self.image)
        self.hitbox = self.mask.get_bounding_rects()[0]

    def attack(self):
        distance = self.get_player_distance_direction()[0]
        if distance < self.attack_radius and not self.attacking:
            self.attacking = True
            self.frame_index = 0
        if self.attacking:
            self.status = self.status.split('_')[0] + '_attack'

    def check_death(self):
        if self.health <= 0:
            self.kill()
            self.player.score += 1

    def update(self, dt):
        self.face_player()
        self.walk_to_player()
        self.attack()
        self.move(dt)
        self.animate(dt)
        self.blink()
        self.check_death()
        self.vulnerability_timer()

class Cactus(Entity, Monster):
    def __init__(self, pos, groups, path, collision_sprites, player, create_bullet):
        super().__init__(pos, groups, path, collision_sprites)
        self.player = player

        # player interaction
        self.player = player
        self.notice_radius = 600
        self.walk_radius = 500
        self.attack_radius = 350
        self.speed = 90
        self.attack_frame = 6
        

        #bullets
        self.create_bullet = create_bullet
        self.bullet_shot = False
        self.health = 1 + DIFFICULTY
    
    def animate(self, dt):
        current_animation = self.animations[self.status]

        if int(self.frame_index) == self.attack_frame and self.attacking and not self.bullet_shot:
            direction = self.get_player_distance_direction()[1]
            pos = self.rect.center + direction * 150
            self.create_bullet(pos, direction)
            self.bullet_shot = True

        self.frame_index += 7 * dt
        if self.frame_index >= len(current_animation):
            self.frame_index = 0
            if self.attacking: self.attacking = False

        self.image = current_animation[int(self.frame_index)]
        self.mask = pygame.mask.from_surface(self.image)
        self.hitbox = self.mask.get_bounding_rects()[0]
    
    def check_death(self):
        if self.health <= 0:
            self.kill()
            self.player.score += 1

    def attack(self):
        distance = self.get_player_distance_direction()[0]
        if distance < self.attack_radius and not self.attacking:
            self.attacking = True
            self.frame_index = 0
            self.bullet_shot = False
            self.shoot_sound.play()
        if self.attacking:
            self.status = self.status.split('_')[0] + '_attack'    

    def update(self, dt):
        self.face_player()
        self.walk_to_player()
        self.attack()
        self.move(dt)
        self.animate(dt)
        self.check_death()
        self.vulnerability_timer()
        self.blink()

class HybridEnemy(Entity, Monster):
    def __init__(self, pos, groups, path, collision_sprites, player, create_bullet):
        super().__init__(pos, groups, path, collision_sprites)
        
        # overwrites
        self.speed = 120
        self.attack_frame = 4
        self.health = 3 + DIFFICULTY

        # player interaction
        self.player = player
        self.notice_radius = 600
        self.walk_radius = 500
        self.melee_attack_radius = 50
        self.player.score = 0

        # bullets
        self.create_bullet = create_bullet
        self.bullet_shot = False

        # Load sounds
        self.shoot_sound = pygame.mixer.Sound('./sound/shoot.mp3')
        self.shoot_sound.set_volume(SHOOT_SOUND_VOLUME)

        # Load animations
        self.animations = self.import_assets(path)
        self.frame_index = 0
        self.status = 'Idle'

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

        # Debug print to check dimensions
        print(f"Image size: {image.get_size()}, Frame size: ({frame_width}, {frame_height}), Num frames: {num_frames}")

        for i in range(num_frames):
            if (i * frame_width + frame_width <= image.get_width()) and (frame_height <= image.get_height()):
                frame = image.subsurface((i * frame_width, 0, frame_width, frame_height))
                frames.append(frame)
            else:
                print(f"Skipping frame {i} as it is outside the surface area")
        return frames

    def animate(self, dt):
        current_animation = self.animations[self.status]

        if int(self.frame_index) == self.attack_frame and self.attacking:
            if self.get_player_distance_direction()[0] < self.attack_radius:
                self.player.damage()
            elif not self.bullet_shot:
                direction = self.get_player_distance_direction()[1]
                pos = self.rect.center + direction * 150
                self.create_bullet(pos, direction)
                self.bullet_shot = True

        self.frame_index += 7 * dt
        if self.frame_index >= len(current_animation):
            self.frame_index = 0
            if self.attacking:
                self.attacking = False

        self.image = current_animation[int(self.frame_index)]
        self.mask = pygame.mask.from_surface(self.image)
        self.hitbox = self.mask.get_bounding_rects()[0]

    def attack(self):
        distance = self.get_player_distance_direction()[0]
        if distance < self.melee_attack_radius and not self.attacking:
            self.attacking = True
            self.frame_index = 0
            self.bullet_shot = False
            self.shoot_sound.play()
        if self.attacking:
            if self.get_player_distance_direction()[0] < self.melee_attack_radius:
                self.status = 'Attack3'

    def check_death(self):
        if self.health <= 0:
            self.kill()
            self.player.score += 1

    def update(self, dt):
        self.face_player()
        self.walk_to_player()
        self.attack()
        self.move(dt)
        self.animate(dt)
        self.check_death()
        self.vulnerability_timer()
        self.blink()

