import unittest
from unittest.mock import Mock, patch
import pygame
from monster import HybridEnemy, Coffin, Cactus
from player import Player
from sprite import Bullet
from spawner import Spawner
from settings import DIFFICULTY, AMMO, WINDOW_WIDTH, WINDOW_HEIGHT

class TestHybridEnemy(unittest.TestCase):
    def setUp(self):
        pygame.init()
        self.screen = pygame.display.set_mode((800, 600))
        self.groups = pygame.sprite.Group()
        self.collision_sprites = pygame.sprite.Group()
        self.player = Mock()
        self.create_bullet = Mock()
        self.path = './graphics/enemy'
        self.hybrid_enemy = HybridEnemy((100, 100), self.groups, self.path, self.collision_sprites, self.player, self.create_bullet)

    def test_initialization(self):
        self.assertEqual(self.hybrid_enemy.speed, 120)
        self.assertEqual(self.hybrid_enemy.attack_frame, 4)
        self.assertEqual(self.hybrid_enemy.health, 3 + DIFFICULTY)
        self.assertEqual(self.hybrid_enemy.notice_radius, 600)
        self.assertEqual(self.hybrid_enemy.walk_radius, 500)
        self.assertEqual(self.hybrid_enemy.attack_radius, 50)
        self.assertFalse(self.hybrid_enemy.bullet_shot)

    @patch('pygame.mixer.Sound')
    def test_attack(self, mock_sound):
        self.hybrid_enemy.get_player_distance_direction = Mock(return_value=(40, pygame.math.Vector2(1, 0)))
        self.hybrid_enemy.attack()
        self.assertTrue(self.hybrid_enemy.attacking)
        self.assertEqual(self.hybrid_enemy.frame_index, 0)
        self.assertFalse(self.hybrid_enemy.bullet_shot)
        mock_sound.return_value.play.assert_called_once()

    def test_animate(self):
        self.hybrid_enemy.attacking = True
        self.hybrid_enemy.get_player_distance_direction = Mock(return_value=(40, pygame.math.Vector2(1, 0)))
        self.hybrid_enemy.frame_index = self.hybrid_enemy.attack_frame
        self.hybrid_enemy.animate(1)
        self.assertTrue(self.hybrid_enemy.bullet_shot)
        self.create_bullet.assert_called_once()

    def test_check_death(self):
        self.hybrid_enemy.health = 0
        self.hybrid_enemy.check_death()
        self.assertFalse(self.hybrid_enemy.alive())
        self.player.score += 1

    def test_update(self):
        self.hybrid_enemy.face_player = Mock()
        self.hybrid_enemy.walk_to_player = Mock()
        self.hybrid_enemy.attack = Mock()
        self.hybrid_enemy.move = Mock()
        self.hybrid_enemy.animate = Mock()
        self.hybrid_enemy.check_death = Mock()
        self.hybrid_enemy.vulnerability_timer = Mock()
        self.hybrid_enemy.blink = Mock()

        self.hybrid_enemy.update(1)
        self.hybrid_enemy.face_player.assert_called_once()
        self.hybrid_enemy.walk_to_player.assert_called_once()
        self.hybrid_enemy.attack.assert_called_once()
        self.hybrid_enemy.move.assert_called_once()
        self.hybrid_enemy.animate.assert_called_once()
        self.hybrid_enemy.check_death.assert_called_once()
        self.hybrid_enemy.vulnerability_timer.assert_called_once()
        self.hybrid_enemy.blink.assert_called_once()

class TestPlayer(unittest.TestCase):
    def setUp(self):
        pygame.init()
        self.screen = pygame.display.set_mode((800, 600))
        self.groups = pygame.sprite.Group()
        self.collision_sprites = pygame.sprite.Group()
        self.create_bullet = Mock()
        self.display_surf = Mock()
        self.player = Player((100, 100), self.groups, './graphics/player', self.collision_sprites, self.create_bullet, self.display_surf)

    def test_initialization(self):
        self.assertEqual(self.player.health, 3)
        self.assertEqual(self.player.ammo, AMMO)
        self.assertFalse(self.player.bullet_shot)
        self.assertFalse(self.player.reloading)

    def test_reload(self):
        self.player.ammo = 0
        self.player.reload()
        self.assertTrue(self.player.reloading)

    def test_shoot(self):
        self.player.ammo = 1
        self.player.shoot()
        self.assertTrue(self.player.bullet_shot)
        self.assertEqual(self.player.ammo, 0)

class TestBullet(unittest.TestCase):
    def setUp(self):
        pygame.init()
        self.screen = pygame.display.set_mode((800, 600))
        self.groups = pygame.sprite.Group()
        self.bullet = Bullet((100, 100), pygame.math.Vector2(1, 0), pygame.Surface((10, 10)), self.groups, Mock())

    def test_update(self):
        initial_pos = self.bullet.pos.copy()
        self.bullet.update(1)
        self.assertNotEqual(self.bullet.pos, initial_pos)

class TestSpawner(unittest.TestCase):
    def setUp(self):
        pygame.init()
        self.screen = pygame.display.set_mode((800, 600))
        self.groups = pygame.sprite.Group()
        self.collision_sprites = pygame.sprite.Group()
        self.player = Mock()
        self.create_bullet = Mock()
        self.spawner = Spawner((100, 100), self.groups, self.collision_sprites, self.player, self.create_bullet)

    def test_damage(self):
        initial_health = self.spawner.health
        self.spawner.damage()
        self.assertEqual(self.spawner.health, initial_health - 1)

    def test_spawn_enemy(self):
        with patch('random.uniform', return_value=0):
            self.spawner.spawn_enemy()
            self.assertEqual(len(self.groups), 1)

if __name__ == '__main__':
    unittest.main()