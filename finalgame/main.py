# main.py - Main game loop and rendering
import pygame
import sys
import time
from config import *
from game import Game
from sprite_loader import SpriteLoader

# Initialize pygame
pygame.init()
pygame.display.set_caption("Pac-Man with A* Pathfinding")
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
clock = pygame.time.Clock()

# Font setup
pygame.font.init()
font_large = pygame.font.Font(None, 64)
font_medium = pygame.font.Font(None, 36)
font_small = pygame.font.Font(None, 24)

# Load sprites
sprites = SpriteLoader()

# Initialize game
game = Game()

# Animation timer
animation_time = 0
last_time = time.time()

def draw_maze():
    """Draw the maze and pellets"""
    for y, row in enumerate(game.maze):
        for x, cell in enumerate(row):
            position = (x * TILE_SIZE, y * TILE_SIZE)
            
            # Draw walls
            if cell == 'X':
                screen.blit(sprites.wall_sprite, position)
            # Draw pellets
            elif cell == '.':
                screen.blit(sprites.pellet_sprite, position)
            # Draw power pellets
            elif cell == 'O':
                screen.blit(sprites.power_pellet_sprite, position)

def draw_entities():
    """Draw pacman and ghosts"""
    # Draw pacman
    pacman_pos = (game.pacman.x * TILE_SIZE, game.pacman.y * TILE_SIZE)
    pacman_sprite = sprites.pacman_sprites[game.pacman.direction][game.pacman.animation_frame]
    screen.blit(pacman_sprite, pacman_pos)
    
    # Draw ghosts
    for ghost in game.ghosts:
        ghost_pos = (ghost.x * TILE_SIZE, ghost.y * TILE_SIZE)
        
        if ghost.scared:
            screen.blit(sprites.scared_ghost_sprite, ghost_pos)
        else:
            screen.blit(sprites.ghost_sprites[ghost.name], ghost_pos)

def draw_debug_paths():
    """Draw A* paths for debugging"""
    if not game.debug_mode:
        return
    
    # Draw explored paths
    for ghost in game.ghosts:
        for pos in ghost.explored_paths:
            x, y = pos
            pygame.draw.rect(screen, DEBUG_PATH_COLOR, 
                           (x * TILE_SIZE + TILE_SIZE//4, y * TILE_SIZE + TILE_SIZE//4, 
                            TILE_SIZE//2, TILE_SIZE//2))
    
    # Draw actual paths
    for ghost in game.ghosts:
        if ghost.path:
            for i in range(len(ghost.path) - 1):
                x1, y1 = ghost.path[i]
                x2, y2 = ghost.path[i + 1]
                pygame.draw.line(screen, ghost.color, 
                               (x1 * TILE_SIZE + TILE_SIZE//2, y1 * TILE_SIZE + TILE_SIZE//2),
                               (x2 * TILE_SIZE + TILE_SIZE//2, y2 * TILE_SIZE + TILE_SIZE//2), 2)

def draw_ui():
    """Draw user interface"""
    # Draw score
    score_text = font_medium.render(f"Score: {game.pacman.score}", True, WHITE)
    screen.blit(score_text, (10, 10))
    
    # Draw lives
    lives_text = font_medium.render(f"Lives: {game.pacman.lives}", True, WHITE)
    screen.blit(lives_text, (SCREEN_WIDTH - 150, 10))
    
    # Draw level
    level_text = font_medium.render(f"Level: {game.level}", True, WHITE)
    screen.blit(level_text, (SCREEN_WIDTH // 2 - 50, 10))
    
    # Ghost mode display
    if game.current_ghost_mode < len(game.ghost_modes):
        mode, duration = game.ghost_modes[game.current_ghost_mode]
        if duration > 0:
            mode_text = font_small.render(f"Ghost Mode: {mode} ({int(duration - game.ghost_mode_timer)}s)", True, WHITE)
            screen.blit(mode_text, (10, 50))
        else:
            mode_text = font_small.render(f"Ghost Mode: {mode}", True, WHITE)
            screen.blit(mode_text, (10, 50))
    
    # Power pellet timer
    if game.pacman.power_pellet_active:
        timer_text = font_small.render(f"Power: {int(game.pacman.power_pellet_timer)}", True, YELLOW)
        screen.blit(timer_text, (10, 80))
    
    # Debug mode indicator
    if game.debug_mode:
        debug_text = font_small.render("Debug Mode: ON", True, GREEN)
        screen.blit(debug_text, (SCREEN_WIDTH - 150, 50))

        
def draw_start_screen():
    """Draw start screen"""
    # Background
    screen.fill(BLACK)
    
    # Title
    title_text = font_large.render("PAC-MAN", True, YELLOW)
    screen.blit(title_text, (SCREEN_WIDTH // 2 - title_text.get_width() // 2, 100))
    
    # Subtitle
    subtitle_text = font_medium.render("with A* Pathfinding", True, WHITE)
    screen.blit(subtitle_text, (SCREEN_WIDTH // 2 - subtitle_text.get_width() // 2, 180))
    
    # Instructions
    instructions = [
        "Use arrow keys to move",
        "Eat all pellets to win",
        "Power pellets make ghosts vulnerable",
        "Press 'D' to toggle debug mode",
        "Press 'P' to pause",
        "",
        "Press SPACE to start"
    ]
    
    for i, instruction in enumerate(instructions):
        instruction_text = font_small.render(instruction, True, WHITE)
        screen.blit(instruction_text, (SCREEN_WIDTH // 2 - instruction_text.get_width() // 2, 250 + i * 40))
    
    # Draw animated pacman
    pacman_sprite = sprites.pacman_sprites[RIGHT][int(animation_time * 10) % 4]
    screen.blit(pacman_sprite, (150, 400))
    
    # Draw ghosts
    ghost_positions = [(300, 400), (350, 400), (400, 400), (450, 400)]
    ghost_names = ["blinky", "pinky", "inky", "clyde"]
    
    for pos, name in zip(ghost_positions, ghost_names):
        screen.blit(sprites.ghost_sprites[name], pos)

def draw_game_over_screen():
    """Draw game over screen"""
    # Overlay
    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 200))
    screen.blit(overlay, (0, 0))
    
    # Game Over text
    game_over_text = font_large.render("GAME OVER", True, RED)
    screen.blit(game_over_text, (SCREEN_WIDTH // 2 - game_over_text.get_width() // 2, 200))
    
    # Score
    score_text = font_medium.render(f"Final Score: {game.pacman.score}", True, WHITE)
    screen.blit(score_text, (SCREEN_WIDTH // 2 - score_text.get_width() // 2, 300))
    
    # Restart prompt
    restart_text = font_small.render("Press SPACE to try again", True, WHITE)
    screen.blit(restart_text, (SCREEN_WIDTH // 2 - restart_text.get_width() // 2, 400))

def draw_win_screen():
    """Draw win screen"""
    # Overlay
    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 200))
    screen.blit(overlay, (0, 0))
    
    # Win text
    win_text = font_large.render("YOU WIN!", True, GREEN)
    screen.blit(win_text, (SCREEN_WIDTH // 2 - win_text.get_width() // 2, 200))
    
    # Score
    score_text = font_medium.render(f"Final Score: {game.pacman.score}", True, WHITE)
    screen.blit(score_text, (SCREEN_WIDTH // 2 - score_text.get_width() // 2, 300))
    
    # Level
    level_text = font_medium.render(f"Level {game.level} Completed", True, WHITE)
    screen.blit(level_text, (SCREEN_WIDTH // 2 - level_text.get_width() // 2, 350))
    
    # Next level prompt
    next_text = font_small.render("Press SPACE for next level", True, WHITE)
    screen.blit(next_text, (SCREEN_WIDTH // 2 - next_text.get_width() // 2, 450))

def draw_pause_screen():
    """Draw pause screen"""
    # Overlay
    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 150))
    screen.blit(overlay, (0, 0))
    
    # Pause text
    pause_text = font_large.render("PAUSED", True, WHITE)
    screen.blit(pause_text, (SCREEN_WIDTH // 2 - pause_text.get_width() // 2, 250))
    
    # Resume prompt
    resume_text = font_small.render("Press P to resume", True, WHITE)
    screen.blit(resume_text, (SCREEN_WIDTH // 2 - resume_text.get_width() // 2, 350))

# Game loop
running = True
while running:
    # Calculate delta time
    current_time = time.time()
    dt = current_time - last_time
    last_time = current_time
    animation_time += dt
    
    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
            elif event.key == pygame.K_p:
                game.toggle_pause()
            else:
                game.handle_input(event.key)
    
    # Update game
    if game.state == GAME_RUNNING:
        game.update(dt)
    
    # Drawing
    screen.fill(BLACK)
    
    if game.state == GAME_START:
        draw_start_screen()
    else:
        # Draw game elements
        draw_maze()
        draw_entities()
        draw_debug_paths()
        draw_ui()
        
        # Draw overlays for different game states
        if game.state == GAME_OVER:
            draw_game_over_screen()
        elif game.state == GAME_WON:
            draw_win_screen()
        elif game.state == GAME_PAUSED:
            draw_pause_screen()
    
    # Update display
    pygame.display.flip()
    clock.tick(FPS)

# Clean up
pygame.quit()
sys.exit()