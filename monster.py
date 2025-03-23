import pygame
from entity import Entity
from pygame.math import Vector2 as vector
from settings import *
import os
from os import walk
import time
from math import sin

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
                    self.status = 'Idle'
                elif direction.x > 0: # player to the right
                    self.status = 'Idle'
            else:
                if direction.y < 0: # player to the top
                    self.status = 'Idle'
                elif direction.y > 0: # player to the bottom
                    self.status = 'Idle'

    def walk_to_player(self):
        distance, direction = self.get_player_distance_direction()
        if self.ranged_radius < distance < self.walk_radius:
            self.direction = direction
            self.status = 'Walk'
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
        self.ranged_radius = 1000

        # bullets
        self.create_bullet = create_bullet
        self.bullet_shot = False
        self.dead = False

        # Load sounds
        self.shoot_sound = pygame.mixer.Sound('./sound/charged_shot.mp3')
        self.shoot_sound.set_volume(SHOOT_SOUND_VOLUME)
        self.melee_attack_sound = pygame.mixer.Sound('./sound/damage.mp3')
        self.melee_attack_sound.set_volume(0.1)

        # Load animations
        self.animations = self.import_assets(path)
        self.frame_index = 0
        self.status = 'Idle'
        self.damaging = False

        # Load projectile image
        self.projectile_image = pygame.image.load(os.path.join(path, 'Projectile.png')).convert_alpha()
        print(self.animations)
        
        # Cooldowns
        self.melee_cooldown = 5000  # 5 seconds
        self.ranged_cooldown = 6000  # 6 seconds
        self.global_cooldown = 2000  # 2 seconds
        self.last_attack_time = 0
        self.damage_cooldown = 1000  # 1 second

    def import_assets(self, path):
        self.animations = {}
        for index, folder in enumerate(walk(path)):
            if index == 0:
                for name in folder[1]:
                    self.animations[name] = []
            else:
                for file_name in sorted(folder[2], key=lambda string: int(''.join(filter(str.isdigit, string)) or 0)):
                    path = folder[0].replace('\\', '/') + '/' + file_name
                    surf = pygame.image.load(path).convert_alpha()
                    surf = pygame.transform.scale(surf, (surf.get_width() * 2, surf.get_height() * 2))  # Scale the image
                    key = folder[0].split('\\')[1]
                    self.animations[key].append(surf)
                    print(f"Loaded {file_name} into {key}")
        return self.animations

    def blink(self):
        """Blink effect to indicate damage."""
        if self.status != 'Die' and not self.is_vulnerable:
            if self.wave_value():
                mask = pygame.mask.from_surface(self.image)
                white_surf = mask.to_surface()
                white_surf.set_colorkey((0, 0, 0))
                self.image = white_surf

    def wave_value(self):
        """Helper method for blinking effect."""
        value = sin(pygame.time.get_ticks())
        return value >= 0

    def damage(self):
        """Apply damage to the enemy and trigger the blink effect."""
        if self.is_vulnerable:
            print('Enemy damaged')
            self.health -= 1
            self.is_vulnerable = False
            self.hit_time = pygame.time.get_ticks()

    def animate(self, dt):
        """Update animations, excluding the 'Hurt' animation."""
        if not self.status == 'Die':
            current_animation = self.animations.get(self.status)
            if not current_animation:
                print(f"No animation found for status: {self.status}")
                return

            self.frame_index += 7 * dt

            # Ensure the attack animation completes before switching
            if self.attacking and self.status == 'Ranged' and int(self.frame_index) == 4 and not self.bullet_shot:
                direction = self.get_player_distance_direction()[1]
                self.create_bullet(self.rect.center, direction, self, self.projectile_image)
                self.shoot_sound.play()
                self.bullet_shot = True

            if self.attacking and self.frame_index >= len(current_animation) - 1:
                self.attacking = False  # Reset after full animation
                self.status = 'Idle'

            if self.frame_index >= len(current_animation):
                self.frame_index = 0  # Loop idle animations

            self.image = current_animation[int(self.frame_index)]
            self.mask = pygame.mask.from_surface(self.image)
            self.hitbox = self.mask.get_bounding_rects()[0]
        elif self.status == 'Die':
            current_animation = self.animations.get(self.status)
            self.frame_index += 7 * dt
            if self.frame_index >= len(current_animation):
                print('Killing enemy')
                self.kill()
            if self.frame_index >= len(current_animation):
                self.frame_index = 0  # Loop idle animations
            self.image = current_animation[int(self.frame_index)]
            self.mask = pygame.mask.from_surface(self.image)
            self.hitbox = self.mask.get_bounding_rects()[0]

    def check_attack(self):
        """Handles attack decision-making based on player distance, obstructions, and cooldowns."""
        current_time = pygame.time.get_ticks()
        distance, direction = self.get_player_distance_direction()

        # Global cooldown check
        if current_time - self.last_attack_time < self.global_cooldown:
            return  # Still in cooldown, do nothing

        # Melee Attack (if player is close enough and cooldown is over)
        if distance < self.melee_attack_radius and (current_time - self.last_attack_time) >= self.melee_cooldown:
            if not self.dead:
                self.attack('melee')
                self.last_attack_time = current_time
                return  # Prioritize melee attack, do not check ranged

        # Ranged Attack (only if no wall blocks the shot)
        # Check if player is within ranged attack radius AND outside melee attack radius
        if self.melee_attack_radius <= distance < self.ranged_radius and (current_time - self.last_attack_time) >= self.ranged_cooldown:
            if not self.is_obstructed(self.rect.center, self.player.rect.center):  
                if not self.dead:
                    print('Ranged attack')
                    self.attack('ranged')
                    self.last_attack_time = current_time

    def attack(self, mode):
        direction = self.get_player_distance_direction()[1]

        if mode == 'ranged':
            if not self.attacking:  # Prevent re-triggering mid-animation
                self.attacking = True
                self.status = 'Ranged'
                self.frame_index = 0
                self.bullet_shot = False
                
                # Projectile will now be created in the animate method on frame 4

        elif mode == 'melee':
            if not self.attacking:
                self.attacking = True
                self.frame_index = 0
                self.status = 'Melee'
                self.melee_attack_sound.play()
                self.player.damage()

    def check_death(self):
        if self.health <= 0 and not self.dead:
            self.dead = True
            self.status = 'Die'
            self.player.score += 1

    def check_collision_with_obstacles(self):
        """Check if the enemy hitbox is inside an obstacle and move it 10px left if it is."""
        for obstacle in self.collision_sprites:
            if self.hitbox.colliderect(obstacle.rect):
                self.rect.x -= 1
                self.hitbox = self.mask.get_bounding_rects()[0]  # Update hitbox position

    def isdamaging(self):
        if self.damage_cooldown < pygame.time.get_ticks() - self.hit_time:
            self.is_vulnerable = True
            self.status = 'Idle'
            return True
        return False

    def update(self, dt):
        """Updates the enemy's behavior each frame."""
        
        
        if not self.attacking:  # Only move if not attacking
            self.walk_to_player()
            self.move(dt)

        self.animate(dt)
        self.check_attack()  # Attack logic
        self.check_death()
        self.vulnerability_timer()
        self.blink()
