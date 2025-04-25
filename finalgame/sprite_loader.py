# sprite_loader.py - Handling game sprites
import pygame
import os
from config import TILE_SIZE

class SpriteLoader:
    def __init__(self):
        # Create placeholder graphics
        self.pacman_sprites = self._create_pacman_sprites()
        self.ghost_sprites = self._create_ghost_sprites()
        self.wall_sprite = self._create_wall_sprite()
        self.pellet_sprite = self._create_pellet_sprite()
        self.power_pellet_sprite = self._create_power_pellet_sprite()
        self.scared_ghost_sprite = self.create_scared_ghost_sprite()  # Remove the underscore
        
    def _create_pacman_sprites(self):
        """Create pacman animation sprites"""
        sprites = []
        
        # Open sprite
        open_surface = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
        pygame.draw.circle(open_surface, (255, 255, 0), (TILE_SIZE//2, TILE_SIZE//2), TILE_SIZE//2 - 2)
        
        # Closed sprite
        closed_surface = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
        pygame.draw.circle(closed_surface, (255, 255, 0), (TILE_SIZE//2, TILE_SIZE//2), TILE_SIZE//2 - 2)
        pygame.draw.polygon(closed_surface, (0, 0, 0), [
            (TILE_SIZE//2, TILE_SIZE//2),
            (TILE_SIZE, TILE_SIZE//4),
            (TILE_SIZE, TILE_SIZE*3//4)
        ])
        
        # Half-open sprite
        half_surface = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
        pygame.draw.circle(half_surface, (255, 255, 0), (TILE_SIZE//2, TILE_SIZE//2), TILE_SIZE//2 - 2)
        pygame.draw.polygon(half_surface, (0, 0, 0), [
            (TILE_SIZE//2, TILE_SIZE//2),
            (TILE_SIZE, TILE_SIZE//3),
            (TILE_SIZE, TILE_SIZE*2//3)
        ])
        
        # Add sprites in animation order
        sprites.append(closed_surface)
        sprites.append(half_surface)
        sprites.append(open_surface)
        sprites.append(half_surface)
        
        # Create rotated versions for each direction
        all_sprites = {
            (1, 0): sprites,  # Right - default
            (-1, 0): [pygame.transform.flip(sprite, True, False) for sprite in sprites],  # Left
            (0, -1): [pygame.transform.rotate(sprite, 90) for sprite in sprites],  # Up
            (0, 1): [pygame.transform.rotate(sprite, -90) for sprite in sprites]  # Down
        }
        
        return all_sprites
    
    def _create_ghost_sprites(self):
        """Create ghost sprites with different colors"""
        ghost_colors = {
            "blinky": (255, 0, 0),     # Red
            "pinky": (255, 192, 203),  # Pink
            "inky": (0, 255, 255),     # Cyan
            "clyde": (255, 165, 0)     # Orange
        }
        
        ghost_sprites = {}
        
        for name, color in ghost_colors.items():
            # Create ghost body
            ghost = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
            
            # Draw ghost body (semi-circle top with wavy bottom)
            pygame.draw.rect(ghost, color, (0, TILE_SIZE//2, TILE_SIZE, TILE_SIZE//2))
            pygame.draw.arc(ghost, color, (0, 0, TILE_SIZE, TILE_SIZE), 0, 3.14, width=TILE_SIZE)
            
            # Draw the wavy bottom
            wave_height = TILE_SIZE // 6
            rect_width = TILE_SIZE // 3
            for i in range(3):
                pygame.draw.rect(ghost, (0, 0, 0), 
                               (i*rect_width, TILE_SIZE - wave_height, rect_width, wave_height))
            
            # Add eyes
            eye_radius = TILE_SIZE // 8
            eye_pos_y = TILE_SIZE // 3
            pygame.draw.circle(ghost, (255, 255, 255), (TILE_SIZE//3, eye_pos_y), eye_radius)
            pygame.draw.circle(ghost, (255, 255, 255), (TILE_SIZE*2//3, eye_pos_y), eye_radius)
            
            # Add pupils
            pupil_radius = eye_radius // 2
            pygame.draw.circle(ghost, (0, 0, 255), (TILE_SIZE//3, eye_pos_y), pupil_radius)
            pygame.draw.circle(ghost, (0, 0, 255), (TILE_SIZE*2//3, eye_pos_y), pupil_radius)
            
            ghost_sprites[name] = ghost
            
        return ghost_sprites
    
    def _create_wall_sprite(self):
        """Create wall sprite"""
        wall = pygame.Surface((TILE_SIZE, TILE_SIZE))
        wall.fill((33, 33, 255))  # Blue wall
        
        # Add some texture
        pygame.draw.line(wall, (0, 0, 200), (0, 0), (TILE_SIZE, 0), 2)
        pygame.draw.line(wall, (0, 0, 200), (0, 0), (0, TILE_SIZE), 2)
        pygame.draw.line(wall, (60, 60, 255), (0, TILE_SIZE-1), (TILE_SIZE-1, TILE_SIZE-1), 2)
        pygame.draw.line(wall, (60, 60, 255), (TILE_SIZE-1, 0), (TILE_SIZE-1, TILE_SIZE-1), 2)
        
        return wall
    
    def _create_pellet_sprite(self):
        """Create pellet sprite"""
        pellet = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
        pellet_radius = TILE_SIZE // 8
        pygame.draw.circle(pellet, (255, 255, 255), (TILE_SIZE//2, TILE_SIZE//2), pellet_radius)
        return pellet
    
    def _create_power_pellet_sprite(self):
        """Create power pellet sprite"""
        power_pellet = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
        pellet_radius = TILE_SIZE // 4
        pygame.draw.circle(power_pellet, (255, 255, 255), (TILE_SIZE//2, TILE_SIZE//2), pellet_radius)
        
        # Add pulsing effect (could be animated in game loop)
        pygame.draw.circle(power_pellet, (200, 200, 200), (TILE_SIZE//2, TILE_SIZE//2), pellet_radius-2, 2)
        
        return power_pellet
    
    # Fix for the scared ghost sprite in sprite_loader.py
    def create_scared_ghost_sprite(self):
        """Create scared ghost sprite (when power pellet is active)"""
        ghost = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
        
        # Draw ghost body (using PURPLE color)
        pygame.draw.rect(ghost, (0, 0, 255), (0, TILE_SIZE//2, TILE_SIZE, TILE_SIZE//2))
        pygame.draw.arc(ghost, (0, 0, 255), (0, 0, TILE_SIZE, TILE_SIZE), 0, 3.14, width=TILE_SIZE)
        
        # Draw the wavy bottom
        wave_height = TILE_SIZE // 6
        rect_width = TILE_SIZE // 3
        for i in range(3):
            pygame.draw.rect(ghost, (0, 0, 0), 
                        (i*rect_width, TILE_SIZE - wave_height, rect_width, wave_height))
        
        # Add scared eyes (X's)
        eye_pos_y = TILE_SIZE // 3
        eye_size = TILE_SIZE // 8
        
        # Left eye X
        pygame.draw.line(ghost, (255, 255, 255), 
                    (TILE_SIZE//3 - eye_size, eye_pos_y - eye_size),
                    (TILE_SIZE//3 + eye_size, eye_pos_y + eye_size), 2)
        pygame.draw.line(ghost, (255, 255, 255), 
                    (TILE_SIZE//3 - eye_size, eye_pos_y + eye_size),
                    (TILE_SIZE//3 + eye_size, eye_pos_y - eye_size), 2)
        
        # Right eye X - Fixed typo in TILE_SIZE*2//3 (was TILE_SIZE2//3)
        pygame.draw.line(ghost, (255, 255, 255), 
                    (TILE_SIZE*2//3 - eye_size, eye_pos_y - eye_size),
                    (TILE_SIZE*2//3 + eye_size, eye_pos_y + eye_size), 2)
        pygame.draw.line(ghost, (255, 255, 255), 
                    (TILE_SIZE*2//3 - eye_size, eye_pos_y + eye_size),
                    (TILE_SIZE*2//3 + eye_size, eye_pos_y - eye_size), 2)
        
        # Add mouth (squiggly line)
        mouth_y = TILE_SIZE // 2
        pygame.draw.line(ghost, (255, 255, 255), 
                    (TILE_SIZE//4, mouth_y),
                    (TILE_SIZE*3//4, mouth_y), 2)
        
        return ghost