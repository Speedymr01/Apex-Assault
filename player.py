import pygame
import os
from pygame.math import Vector2 as vector
from entity import Entity
from settings import *
import sys

class Player(Entity):
    def __init__(self, pos, groups, path, collision_sprites, create_bullet, display_surf):
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
        self.display_surf = display_surf

        # Load animations
        self.animations = self.import_assets(path)
        self.frame_index = 0
        self.status = 'Idle'
        self.shoot_effect = pygame.image.load('./graphics/other/shooteffect.png').convert_alpha()

        # Load shooting images
        self.left_shooting_image = pygame.image.load('./graphics/player/left_shooting.png').convert_alpha()
        self.right_shooting_image = pygame.image.load('./graphics/player/right_shooting.png').convert_alpha()

        # Attributes for fading effect
        self.fade_start_time = 0
        self.fade_duration = 1000  # 1 second
        self.fading = False
        self.current_alpha = 255

        # Flag to track if player has shot
        self.shot = False

        # Attribute to store fixed effect position
        self.effect_pos = None

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

    def get_status(self):
        if self.direction.x == 0 and self.direction.y == 0:
            self.status = 'Idle'
        if self.attacking:
            self.status = 'Attack'
        elif self.direction.magnitude() > 0:
            self.status = 'Walk'
    
    def get_shoot_effect_position(self, mouse_direction):
        # Determine the offset distance for the shoot effect
        offset_distance = 50  # Adjust this value as needed

        # Calculate the effect position in relation to the player
        effect_pos = vector(WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2) + (mouse_direction * offset_distance)

        return effect_pos

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
                    self.shot = True
                    self.shoot_sound.play()
                    # Store effect position relative to the player's initial position
                    self.effect_pos = self.rect.center + self.get_shoot_effect_position(self.get_mouse_direction())
                    self.effect_angle = -self.get_mouse_direction().angle_to(vector(1, 0))

    def animate(self, dt):
        current_animation = self.animations.get(self.status, [self.image])
        
        self.frame_index += 7 * dt
        if int(self.frame_index) >= len(current_animation):
            self.frame_index = 0
            if self.attacking:
                self.attacking = False
        
        self.image = current_animation[int(self.frame_index)]
        self.mask = pygame.mask.from_surface(self.image)

    def draw(self, screen):
        # Get mouse direction
        mouse_direction = self.get_mouse_direction()
        angle = -mouse_direction.angle_to(vector(1, 0))  # Calculate rotation angle

        # Choose and load image based on mouse direction and shooting status
        if self.attacking:
            if mouse_direction.x < 0:
                player_image = self.left_shooting_image
            else:
                player_image = self.right_shooting_image
        else:
            if mouse_direction.x < 0:
                image_path = './graphics/player/left.png'
            else:
                image_path = './graphics/player/right.png'
            player_image = pygame.image.load(image_path).convert_alpha()

        # Enlarge the image by a factor of 2
        width, height = player_image.get_size()
        enlarged_image = pygame.transform.scale(player_image, (width * 1.5, height * 1.5))

        # Flip the image if it is left.png
        if mouse_direction.x < 0:
            enlarged_image = pygame.transform.flip(enlarged_image, True, False)  # Flip horizontally
            enlarged_image = pygame.transform.flip(enlarged_image, False, True)  # Flip vertically

        # Rotate the image
        rotated_image = pygame.transform.rotate(enlarged_image, -angle)

        # Position the arrow image a little away from the player
        arrow_pos = vector(WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2) + (mouse_direction * 50)

        # Get rect and draw player image
        arrow_rect = rotated_image.get_rect(center=arrow_pos)
        screen.blit(rotated_image, arrow_rect.topleft)

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
        mouse_pos = vector(pygame.mouse.get_pos())  # Get mouse position
        player_pos = vector(WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2)  # Player is always at window center

        if mouse_pos == player_pos:
            return vector()  # Prevent division by zero

        direction = (mouse_pos - player_pos).normalize()  # Get normalized direction vector
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
        self.draw(self.display_surf)

        # Start fading if player shot and attacking just stopped
        if not self.attacking and self.shot and not self.fading:
            self.fade_start_time = pygame.time.get_ticks()
            self.fading = True
            self.current_alpha = 255
            self.shot = False  # Reset shot flag
