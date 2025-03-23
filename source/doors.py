import pygame, pytmx
from sprite import Sprite

class DoorStopNotFound(Exception):
    pass

class PistonDoor(Sprite):
    def __init__(self, pos, image_path, groups, pair=None, door_id=None, door_stop=None):
        print(f"Loading image from path: {image_path}")  # Debugging print
        surf = pygame.image.load(image_path).convert_alpha()
        super().__init__(pos, surf, groups)
        self.path = image_path
        self.rect = self.image.get_rect(topleft=pos)
        self.hitbox = self.rect.inflate(0, -self.rect.height / 3)
        self.mask = pygame.mask.from_surface(self.image)
        self.speed = 250  # Adjust the speed as needed
        self.moving = False
        self.pair = pair  # Add pair attribute
        print(door_id)
        self.door_id = door_id
        self.direction = self.find_direction()
        PistonDoor.all_doors = pygame.sprite.Group()
        PistonDoor.door_stops = pygame.sprite.Group()
        PistonDoor.all_doors.add(self)
        self.door_stop = self.find_door_stop()

    def set_speed(self, speed):
        self.speed = speed


    def find_door_stop(self):
        tmx_map = pytmx.load_pygame('./data/map.tmx')
        found_rects = []
        for layer in tmx_map.layers:
            if layer.name == 'Entities':
                for obj in layer:
                    if obj.name == 'door_stop':
                        if obj.door_id == self.door_id:
                            found_rects.append((pygame.Rect(obj.x, obj.y, obj.width, obj.height)))
                            door_stop = pygame.Rect(obj.x, obj.y, obj.width, obj.height)
                            return door_stop
        



    def start_moving(self):
        self.moving = True
        print(f'Door {self.door_id} moving')
        if self.pair and not self.pair.moving:
            self.pair.start_moving()

    def stop_moving(self):
        self.moving = False
        print('Stopped')
        pygame.mixer.stop()

    def find_direction(self):
        if "down" in self.path:
            return "up"
        elif "up" in self.path:
            return "down"
        elif "left" in self.path:
            if self.door_id == 7:
                return "left"
            return "right"
        elif "right" in self.path:
            if self.door_id == 7:
                return "right"
            return "left"
        return None

    def update(self, dt, walls):
        if self.moving:
            # Move the door based on its direction
            if self.direction == 'up':
                self.rect.y -= self.speed * dt
            elif self.direction == 'down':
                self.rect.y += self.speed * dt
            elif self.direction == 'left':
                self.rect.x -= self.speed * dt
            elif self.direction == 'right':
                self.rect.x += self.speed * dt

            # Update hitbox position
            self.hitbox.topleft = self.rect.topleft

            # Check for collision with walls, other doors, or door_stops
            if (
                pygame.sprite.spritecollide(self, walls, False, pygame.sprite.collide_mask) or
                pygame.sprite.spritecollide(self, PistonDoor.all_doors, False, pygame.sprite.collide_mask) or
                pygame.sprite.spritecollide(self, PistonDoor.door_stops, False, pygame.sprite.collide_mask) or
                (self.door_stop and self.hitbox.colliderect(self.door_stop))
            ):
                self.stop_moving()
                print(f'Door {self.door_id} stopped due to collision with a wall, another door, a door_stop, or its own door_stop.')
