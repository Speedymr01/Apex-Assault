import pygame
import os
from pygame.math import Vector2 as vector
from entity import Entity
from settings import *
import sys
from math import sin

class Player(Entity):
    def __init__(self, pos, groups, path, collision_sprites, create_bullet, display_surf):
        super().__init__(pos, groups, path, collision_sprites)
        self.create_bullet = create_bullet
        self.bullet_shot = False
        self.health = 3
        self.reloading = False
        self.reload_start_time = 0
        self.reload_duration = 750
        self.ammo = AMMO
        self.reload_sound = pygame.mixer.Sound('sound/reload.mp3')
        self.score = 0
        self.display_surf = display_surf
        self.flip = False

        # Load animations
        self.animations = self.import_assets(path)
        self.frame_index = 0
        self.status = 'Walk'

        # Ensure the status key exists in the animations dictionary
        if self.status not in self.animations:
            self.status = list(self.animations.keys())[0] if self.animations else 'Idle'

        self.shoot_effect = pygame.image.load('./graphics/other/shooteffect.png').convert_alpha()
        self.bullet_surf = pygame.image.load('./graphics/other/bullet.png').convert_alpha()
        self.bullet_surf = pygame.transform.scale(self.bullet_surf, (int(self.bullet_surf.get_width() * 2), int(self.bullet_surf.get_height() * 2)))
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

        # Cooldown attributes
        self.last_shot_time = 0
        self.shot_cooldown = 500  # Cooldown period in milliseconds

    def import_assets(self, path):
        """Import animation assets from the given path."""
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

    def blink(self):
        if not self.is_vulnerable:
            if self.wave_value():
                mask = pygame.mask.from_surface(self.image)
                white_surf = mask.to_surface()
                white_surf.set_colorkey((0, 0, 0))
                self.image = white_surf

    def wave_value(self):
        value = sin(pygame.time.get_ticks())
        return value >= 0

    def damage(self):
        if self.is_vulnerable:
            self.health -= 1
            self.is_vulnerable = False
            self.hit_time = pygame.time.get_ticks()
            if not self.coffin_damage:
                self.hit_sound.stop()
                self.hit_sound.play()


    def extract_frames(self, image):
        """Extract frames from a sprite sheet image."""
        frames = []
        frame_width, frame_height = 16, 36
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
        """Determine the player's current status based on movement and actions."""
        if self.direction.x == 0 and self.direction.y == 0:
            self.status = 'Idle'
        if self.attacking:
            self.status = 'Attack'
        elif self.direction.magnitude() > 0:
            self.status = 'Walk'
    
    def get_shoot_effect_position(self, mouse_direction):
        """Calculate the position for the shooting effect based on the mouse direction."""
        offset_distance = 0  # Adjust this value as needed
        effect_pos = vector(WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2) + (mouse_direction)
        return effect_pos

    def input(self):
        """Handle player input for movement, shooting, and reloading."""
        keys = pygame.key.get_pressed()
        current_time = pygame.time.get_ticks()
        if not self.attacking:
            if keys[pygame.K_d]:
                self.direction.x = 1
                self.status = 'Walk'
                self.flip = False
            elif keys[pygame.K_a]:
                self.direction.x = -1
                self.status = 'Walk'
                self.flip = True
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
                if self.ammo > 0 and not self.reloading and (current_time - self.last_shot_time >= self.shot_cooldown):
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
                    self.shoot()
                    self.last_shot_time = current_time  # Update the last shot time

    def animate(self, dt):
        """Animate the player sprite based on the current status."""
        current_animation = self.animations.get(self.status, [self.image])
        
        self.frame_index += 7 * dt
        if int(self.frame_index) >= len(current_animation):
            self.frame_index = 0
            if self.attacking:
                self.attacking = False
        
        self.image = current_animation[int(self.frame_index)]
        if self.flip:
            self.image = pygame.transform.flip(self.image, True, False)
        self.mask = pygame.mask.from_surface(self.image)

    def draw(self, screen):
        """Draw the player sprite on the screen."""
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
        if self.attacking:
            self.arrow_pos = vector(WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2) + (mouse_direction * 200)
        else:
            self.arrow_pos = vector(WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2) + (mouse_direction * 50)

        # Get rect and draw player image
        arrow_rect = rotated_image.get_rect(center=self.arrow_pos)
        screen.blit(rotated_image, arrow_rect.topleft)

    def reload(self):
        """Reload the player's weapon if ammo is less than the maximum."""
        if self.ammo < AMMO and not self.reloading:
            self.reloading = True
            self.reload_start_time = pygame.time.get_ticks()
            self.reload_sound.play()

    def check_death(self):
        """Check if the player is dead and quit the game if so."""
        if self.health <= 0:
            pygame.quit()
            sys.exit()

    def get_mouse_direction(self):
        """Get the direction vector from the player to the mouse cursor."""
        mouse_pos = vector(pygame.mouse.get_pos())  # Get mouse position
        player_pos = vector(WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2)  # Player is always at window center

        if mouse_pos == player_pos:
            return vector()  # Prevent division by zero

        return (mouse_pos - player_pos).normalize()  # Get normalized direction vector

    def shoot(self):
        """Shoot a bullet in the direction of the mouse cursor."""
        bullet_direction = self.get_mouse_direction()  # Calculate direction at the moment of shooting
        self.create_bullet(self.rect.center, bullet_direction, self, self.bullet_surf)  # Pass self as the shooter

    def update(self, dt):
        """Update the player's state and handle animations, input, and other actions."""
        if self.reloading:
            elapsed_time = pygame.time.get_ticks() - self.reload_start_time
            if elapsed_time >= self.reload_duration:
                self.reloading = False
                self.ammo = AMMO
        
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
