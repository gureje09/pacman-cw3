# game.py - Game mechanics
import pygame
import random
from config import *
from astar import get_next_move

class Entity:
    """Base class for game entities"""
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.direction = RIGHT  # Default direction
        self.next_direction = RIGHT
        self.animation_frame = 0
        self.animation_speed = 0.2
        self.animation_timer = 0
    
    def update_animation(self, dt):
        """Update animation frame"""
        self.animation_timer += dt
        if self.animation_timer >= self.animation_speed:
            self.animation_frame = (self.animation_frame + 1) % 4
            self.animation_timer = 0
    
    def get_position(self):
        """Get grid position"""
        return (int(self.x), int(self.y))
    
    def set_position(self, x, y):
        """Set grid position"""
        self.x = x
        self.y = y

class Pacman(Entity):
    """Pacman character"""
    def __init__(self, x, y):
        super().__init__(x, y)
        self.speed = PACMAN_SPEED
        self.score = 0
        self.lives = 3
        self.power_pellet_active = False
        self.power_pellet_timer = 0
    
    def update(self, maze, dt):
        """Update pacman position"""
        # Store current position
        old_x, old_y = self.x, self.y
        
        # Try to change direction if requested
        if self.next_direction != self.direction:
            # Calculate next position in the requested direction
            next_x = self.x + self.next_direction[0] * self.speed
            next_y = self.y + self.next_direction[1] * self.speed
            
            # Check if movement is valid
            if not self.check_collision(next_x, next_y, maze):
                self.direction = self.next_direction
            
        # Move in current direction
        self.x += self.direction[0] * self.speed
        self.y += self.direction[1] * self.speed
        
        # Check for collision with walls
        if self.check_collision(self.x, self.y, maze):
            # Reset position
            self.x, self.y = old_x, old_y
        
        # Update animation
        self.update_animation(dt)
        
        # Update power pellet timer
        if self.power_pellet_active:
            self.power_pellet_timer -= dt
            if self.power_pellet_timer <= 0:
                self.power_pellet_active = False
    
    def check_collision(self, x, y, maze):
        """Check if position collides with a wall"""
        # Get grid coordinates
        grid_x = int(x)
        grid_y = int(y)
        
        # Check boundaries
        if grid_x < 0 or grid_x >= len(maze[0]) or grid_y < 0 or grid_y >= len(maze):
            return True
        
        # Check for wall collision
        return maze[grid_y][grid_x] == 'X'
    
    def eat_pellet(self, maze):
        """Check and eat pellets at current position"""
        grid_x, grid_y = int(self.x), int(self.y)
        
        # Check if there's a pellet
        if maze[grid_y][grid_x] == '.':
            maze[grid_y] = maze[grid_y][:grid_x] + ' ' + maze[grid_y][grid_x+1:]
            self.score += 10
            return True
        # Check if there's a power pellet
        elif maze[grid_y][grid_x] == 'O':
            maze[grid_y] = maze[grid_y][:grid_x] + ' ' + maze[grid_y][grid_x+1:]
            self.score += 50
            self.power_pellet_active = True
            self.power_pellet_timer = 10  # Power pellet lasts 10 seconds
            return True
        
        return False
    
    def set_direction(self, direction):
        """Set movement direction"""
        self.next_direction = direction

class Ghost(Entity):
    """Ghost character with A* pathfinding"""
    def __init__(self, x, y, name, color):
        super().__init__(x, y)
        self.name = name
        self.color = color
        self.speed = GHOST_SPEED
        self.path = []
        self.explored_paths = set()
        self.scared = False
        self.reset_position = (x, y)
        self.state = "chase"  # states: chase, scatter, scared, returning
        self.scatter_timer = 0
        self.scatter_target = None
        self.path_update_timer = 0
        self.eaten = False
        self.target_position = None
        self.last_position = None  # To detect if ghost is stuck
        self.stuck_counter = 0


    def set_personality_offset(self):
        """Set personality offset based on ghost name"""
        if self.name == "blinky":  # Aggressive - targets Pac-Man directly
            return (0, 0)
        elif self.name == "pinky":  # Ambusher - targets 4 tiles ahead of Pac-Man
            return (4, 4)
        elif self.name == "inky":   # Unpredictable - targets point based on Blinky and Pac-Man
            return (-4, 0)
        elif self.name == "clyde":  # Shy - targets Pac-Man until close, then retreats
            return (0, -4)
        return (0, 0)
    
    # Modified Ghost class update method
    def update(self, pacman, maze, grid_width, grid_height, dt):
        """Update ghost position using A* pathfinding"""
        # Update animation
        self.update_animation(dt)
        
        # Update scatter mode
        if self.state == "scatter":
            self.scatter_timer -= dt
            if self.scatter_timer <= 0:
                self.state = "chase"
        
        # Check if pacman has power pellet
        self.scared = pacman.power_pellet_active
        
        # Get current position on grid
        current_pos = self.get_position() 
        
        # Track if ghost is stuck (same position for too long)
        if current_pos == self.last_position:
            self.stuck_counter += 1
        else:
            self.stuck_counter = 0
            self.last_position = current_pos
        
        # If ghost is stuck, force a path update
        force_path_update = self.stuck_counter >= 3
        
        # Update path timer
        self.path_update_timer += dt
        
        # Get target position based on state and personality
        target_pos = self.get_target_position(pacman, grid_width, grid_height)
        self.target_position = target_pos  # Store for visualization
        
        # Update path less frequently to make movement smoother
        # But update more often when scared or if the target has moved significantly
        update_path = False
        
        # Determine if we need to update the path
        if force_path_update:
            update_path = True
        elif self.scared:
            update_path = self.path_update_timer >= 0.5  # Update more frequently when scared
        elif not self.path:
            update_path = True  # No path, definitely need to update
        elif target_pos != self.target_position:
            update_path = True  # Target changed, update path
        else:
            update_path = self.path_update_timer >= 1.0  # Regular update interval
        
        if update_path:
            self.path_update_timer = 0
            next_pos, full_path, explored = get_next_move(
                current_pos, target_pos, maze, grid_width, grid_height
            )
            
            # Make sure we got a valid path
            if full_path:
                self.path = full_path
                self.explored_paths = explored
            else:
                # If no path, try to find a random valid direction
                self.find_random_direction(maze)
        
        # Move ghost along path
        self.move_along_path(maze, dt)


    def move_along_path(self, maze, dt):
        """Move ghost smoothly along the calculated path"""
        if not self.path:
            # No path, move randomly
            self.find_random_direction(maze)
            speed_factor = 0.5 if self.scared else 1.0
            
            # Calculate next position
            next_x = self.x + self.direction[0] * self.speed * speed_factor * dt * FPS
            next_y = self.y + self.direction[1] * self.speed * speed_factor * dt * FPS
            
            # Check for wall collision before moving
            if not self.check_collision(next_x, next_y, maze):
                self.x = next_x
                self.y = next_y
            else:
                # Find a new direction if we hit a wall
                self.find_random_direction(maze)
            return
        
        # Target is the next point in the path
        target = self.path[0]
        
        # Calculate direction vector to target
        dx = target[0] - self.x
        dy = target[1] - self.y
        
        # Determine primary direction
        if abs(dx) > abs(dy):
            if dx > 0:
                self.direction = RIGHT
            else:
                self.direction = LEFT
        else:
            if dy > 0:
                self.direction = DOWN
            else:
                self.direction = UP
        
        # Calculate speed based on state
        speed_factor = 0.5 if self.scared else 1.0
        move_speed = self.speed * speed_factor * dt * FPS
        
        # Calculate next position with smooth movement
        if self.direction == RIGHT or self.direction == LEFT:
            # Move horizontally
            if abs(dx) < move_speed:
                self.x = target[0]  # Snap to target x
                # Move vertically with remaining speed
                if dy > 0:
                    self.y += min(move_speed - abs(dx), abs(dy))
                elif dy < 0:
                    self.y -= min(move_speed - abs(dx), abs(dy))
            else:
                # Move horizontally with full speed
                if dx > 0:
                    self.x += move_speed
                else:
                    self.x -= move_speed
        else:
            # Move vertically
            if abs(dy) < move_speed:
                self.y = target[1]  # Snap to target y
                # Move horizontally with remaining speed
                if dx > 0:
                    self.x += min(move_speed - abs(dy), abs(dx))
                elif dx < 0:
                    self.x -= min(move_speed - abs(dy), abs(dx))
            else:
                # Move vertically with full speed
                if dy > 0:
                    self.y += move_speed
                else:
                    self.y -= move_speed
        
        # Check if we've reached the target point (with a small threshold)
        if abs(self.x - target[0]) < 0.1 and abs(self.y - target[1]) < 0.1:
            # Snap to grid position
            self.x, self.y = target
            # Remove this position from the path
            if len(self.path) > 0:
                self.path.pop(0)
    
    def check_collision(self, x, y, maze):
        """Check if position collides with a wall"""
        # Get grid coordinates
        grid_x = int(x)
        grid_y = int(y)
        
        # Check boundaries
        if grid_x < 0 or grid_x >= len(maze[0]) or grid_y < 0 or grid_y >= len(maze):
            return True
        
        # Check for wall collision
        return maze[grid_y][grid_x] == 'X'
    
    def find_random_direction(self, maze):
        """Find a random valid direction to move"""
        valid_directions = []
        for direction in DIRECTIONS:
            next_x = self.x + direction[0]
            next_y = self.y + direction[1]
            if not self.check_collision(next_x, next_y, maze):
                valid_directions.append(direction)
        
        # Don't reverse direction unless necessary
        if valid_directions and len(valid_directions) > 1:
            reversed_dir = (-self.direction[0], -self.direction[1])
            if reversed_dir in valid_directions:
                valid_directions.remove(reversed_dir)
        
        if valid_directions:
            self.direction = random.choice(valid_directions)
    
    def get_target_position(self, pacman, grid_width, grid_height):
        """Get target position based on ghost personality"""
        if self.eaten:
            # When eaten, head back to ghost house
            return self.reset_position
            
        if self.scared:
            # When scared, move away from Pac-Man
            pacman_x, pacman_y = pacman.get_position()
            
            # Try to move in the opposite direction from Pac-Man
            away_x = max(1, min(grid_width-2, 2*int(self.x) - pacman_x))
            away_y = max(1, min(grid_height-2, 2*int(self.y) - pacman_y))
            return (away_x, away_y)
            
        elif self.state == "scatter":
            # Ghosts scatter to their home corners
            if not self.scatter_target:
                if self.name == "blinky":
                    self.scatter_target = (grid_width-2, 1)  # Top-right
                elif self.name == "pinky":
                    self.scatter_target = (1, 1)  # Top-left
                elif self.name == "inky":
                    self.scatter_target = (grid_width-2, grid_height-2)  # Bottom-right
                elif self.name == "clyde":
                    self.scatter_target = (1, grid_height-2)  # Bottom-left
                else:
                    corners = [(1, 1), (grid_width-2, 1), 
                              (1, grid_height-2), (grid_width-2, grid_height-2)]
                    self.scatter_target = random.choice(corners)
            return self.scatter_target
        else:
            # Chase Pac-Man with personality-based targeting
            pacman_x, pacman_y = pacman.get_position()
            pacman_dir = pacman.direction
            
            if self.name == "blinky":  # Red ghost - direct chaser
                # Blinky directly targets Pac-Man's position
                target_x, target_y = pacman_x, pacman_y
                
            elif self.name == "pinky":  # Pink ghost - ambusher
                # Pinky targets 4 tiles ahead of Pac-Man's direction
                target_x = pacman_x + (pacman_dir[0] * 4)
                target_y = pacman_y + (pacman_dir[1] * 4)
                
                # Special case for the original Pac-Man bug when facing up
                if pacman_dir == UP:
                    # Pinky targets 4 tiles up and 4 tiles left (due to the bug)
                    target_x = pacman_x - 4
                    target_y = pacman_y - 4
                
            elif self.name == "inky":  # Cyan ghost - unpredictable
                # Inky uses Blinky's position to determine target
                # First, get a point 2 tiles ahead of Pac-Man
                intermediate_x = pacman_x + (pacman_dir[0] * 2)
                intermediate_y = pacman_y + (pacman_dir[1] * 2)
                
                # Find the "pivot" ghost (Blinky) position
                # Since we might not have a reference to Blinky here,
                # we'll use a fixed position (this is a simplification)
                blinky_x, blinky_y = pacman_x, pacman_y
                for ghost in pacman.game.ghosts if hasattr(pacman, 'game') else []:
                    if ghost.name == "blinky":
                        blinky_x, blinky_y = ghost.get_position()
                        break
                
                # Calculate the vector from Blinky to the intermediate point
                vector_x = intermediate_x - blinky_x
                vector_y = intermediate_y - blinky_y
                
                # Double the vector to get Inky's target
                target_x = intermediate_x + vector_x
                target_y = intermediate_y + vector_y
                
            elif self.name == "clyde":  # Orange ghost - shy
                # Clyde targets Pac-Man directly if far, but scatters if within 8 tiles
                distance = abs(self.x - pacman_x) + abs(self.y - pacman_y)
                if distance > 8:
                    target_x, target_y = pacman_x, pacman_y
                else:
                    # Retreat to bottom-left when close
                    target_x, target_y = 1, grid_height-2
            else:
                # Default behavior for other ghosts
                target_x, target_y = pacman_x, pacman_y
                
            # Ensure target is within grid bounds
            target_x = max(1, min(grid_width-2, target_x))
            target_y = max(1, min(grid_height-2, target_y))
            
            return (int(target_x), int(target_y))
        
    
    def enter_scatter_mode(self, duration=5):
        """Enter scatter mode for a duration"""
        self.state = "scatter"
        self.scatter_timer = duration
        self.scatter_target = None
        
    def handle_collision_with_pacman(self, pacman):
        """Handle collision with Pac-Man"""
        if self.scared:
            # Ghost gets eaten
            self.eaten = True
            self.scared = False
            self.path = []  # Clear current path
            return True  # Ghost was eaten
        elif not self.eaten:
            # Pac-Man gets eaten
            return False  # Pac-Man was eaten
        return None  # No relevant collision
    
    def reset(self):
        """Reset ghost to starting position"""
        self.x, self.y = self.reset_position
        self.path = []
        self.explored_paths = set()
        self.state = "chase"
        self.scared = False
        self.eaten = False
        self.target_position = None
        self.last_position = None
        self.stuck_counter = 0

class Game:
    """Main game class"""
    def __init__(self):
        self.state = GAME_START
        self.maze = self.initialize_maze()
        self.pacman = None
        self.ghosts = []
        self.score = 0
        self.level = 1
        self.timer = 0
        self.debug_mode = False

        # Initialize ghost mode attributes
        self.ghost_modes = [
            ("scatter", 7),    # Scatter for 7 seconds
            ("chase", 20),     # Chase for 20 seconds
            ("scatter", 7),    # Scatter for 7 seconds
            ("chase", 20),     # Chase for 20 seconds
            ("scatter", 5),    # Scatter for 5 seconds
            ("chase", 20),     # Chase for 20 seconds
            ("scatter", 5),    # Scatter for 5 seconds
            ("chase", 0)       # Chase permanently
        ]
        self.current_ghost_mode = 0
        self.ghost_mode_timer = 0
        
        self.initialize_entities()
    
    def initialize_maze(self):
        """Initialize maze with pellets"""
        maze = []
        for row in MAZE:
            # Replace empty spaces with pellets
            new_row = ""
            for cell in row:
                if cell == ' ':
                    new_row += '.'  # Regular pellet
                elif cell == 'P':  # Pacman starting position
                    new_row += ' '
                elif cell == 'G':  # Ghost starting position
                    new_row += ' '
                else:
                    new_row += cell
            maze.append(new_row)
        
        # Add some power pellets
        power_pellet_positions = [(3, 3), (21, 3), (3, 15), (21, 15)]
        for x, y in power_pellet_positions:
            if 0 <= y < len(maze) and 0 <= x < len(maze[y]) and maze[y][x] == '.':
                maze[y] = maze[y][:x] + 'O' + maze[y][x+1:]
        
        return maze
    
    def initialize_entities(self):
        """Initialize pacman and ghosts"""
        # Find pacman start position
        pacman_start_x, pacman_start_y = None, None
        for y, row in enumerate(MAZE):
            for x, cell in enumerate(row):
                if cell == 'P':
                    pacman_start_x, pacman_start_y = x, y
        
        # Find ghost start position
        ghost_start_x, ghost_start_y = None, None
        for y, row in enumerate(MAZE):
            for x, cell in enumerate(row):
                if cell == 'G':
                    ghost_start_x, ghost_start_y = x, y
        
        # If no P marker found, set default position
        if pacman_start_x is None or pacman_start_y is None:
            pacman_start_x, pacman_start_y = 1, 1
        
        self.pacman = Pacman(pacman_start_x, pacman_start_y)
        # Set reference to the game instance
        self.pacman.game = self
        
        # Create ghosts with appropriate spacing
        if ghost_start_x and ghost_start_y:
            ghost_positions = [
                (ghost_start_x, ghost_start_y),      # Blinky
                (ghost_start_x-1, ghost_start_y),    # Pinky
                (ghost_start_x, ghost_start_y-1),    # Inky
                (ghost_start_x-1, ghost_start_y-1)   # Clyde
            ]
        else:
            # Default positions if no ghost marker
            ghost_positions = [
                (23, 17),  # Blinky
                (22, 17),  # Pinky
                (23, 16),  # Inky
                (22, 16)   # Clyde
            ]
        
        self.ghosts = [
            Ghost(ghost_positions[0][0], ghost_positions[0][1], "blinky", BLINKY_COLOR),
            Ghost(ghost_positions[1][0], ghost_positions[1][1], "pinky", PINKY_COLOR),
            Ghost(ghost_positions[2][0], ghost_positions[2][1], "inky", INKY_COLOR),
            Ghost(ghost_positions[3][0], ghost_positions[3][1], "clyde", CLYDE_COLOR)
        ]
        
        # Set reference to the game instance for each ghost
        for ghost in self.ghosts:
            ghost.game = self
    

    # Add ghost mode cycling
    def update_ghost_modes(self, dt):
        """Update ghost modes based on timers"""
        if self.current_ghost_mode >= len(self.ghost_modes):
            return  # No more mode changes
            
        mode, duration = self.ghost_modes[self.current_ghost_mode]
        self.ghost_mode_timer += dt
        
        if duration > 0 and self.ghost_mode_timer >= duration:
            # Time to switch modes
            self.ghost_mode_timer = 0
            self.current_ghost_mode += 1
            
            if self.current_ghost_mode < len(self.ghost_modes):
                new_mode, _ = self.ghost_modes[self.current_ghost_mode]
                
                # Update all ghosts to the new mode
                for ghost in self.ghosts:
                    if not ghost.scared and not ghost.eaten:  # Don't change mode if scared or eaten
                        ghost.state = new_mode
                        
                        # Reset scatter targets when entering scatter mode
                        if new_mode == "scatter":
                            ghost.scatter_target = None


    def update(self, dt):
        """Update game state"""
        if self.state == GAME_RUNNING:
            # Update ghost modes
            self.update_ghost_modes(dt)
            
            # Update pacman
            self.pacman.update(self.maze, dt)
            
            # Check for pellet eating
            self.pacman.eat_pellet(self.maze)
            
            # Update ghosts
            for ghost in self.ghosts:
                ghost.update(self.pacman, self.maze, GRID_WIDTH, GRID_HEIGHT, dt)
            
            # Check for pacman/ghost collision
            self.check_ghost_collision()
            
            # Check win condition
            if self.check_win_condition():
                self.state = GAME_WON
    
    def check_ghost_collision(self):
        """Check for collision between pacman and ghosts"""
        pacman_pos = self.pacman.get_position()
        
        for ghost in self.ghosts:
            ghost_pos = ghost.get_position()
            
            # Check if positions overlap
            if abs(ghost.x - self.pacman.x) < 0.5 and abs(ghost.y - self.pacman.y) < 0.5:
                result = ghost.handle_collision_with_pacman(self.pacman)
                
                if result is True:  # Ghost was eaten
                    self.pacman.score += 200
                elif result is False:  # Pacman was eaten
                    self.pacman.lives -= 1
                    if self.pacman.lives <= 0:
                        self.state = GAME_OVER
                    else:
                        # Reset positions but keep score
                        self.reset_positions()
        
    def reset_positions(self):
        """Reset pacman and ghost positions"""
        # Find pacman start position
        for y, row in enumerate(MAZE):
            for x, cell in enumerate(row):
                if cell == 'P':
                    self.pacman.set_position(x, y)
        
        # Reset each ghost
        for ghost in self.ghosts:
            ghost.reset()
    
    def check_win_condition(self):
        """Check if all pellets have been eaten"""
        for row in self.maze:
            if '.' in row or 'O' in row:
                return False  # Still pellets left
        return True  # All pellets eaten
    
    def reset_game(self):
        """Reset the game for a new level"""
        self.maze = self.initialize_maze()
        self.initialize_entities()
        self.state = GAME_RUNNING
        self.level += 1
        
        # Increase difficulty
        for ghost in self.ghosts:
            ghost.speed += 0.1
    
    def toggle_debug_mode(self):
        """Toggle debug mode to show A* paths"""
        self.debug_mode = not self.debug_mode
    
    def handle_input(self, key):
        """Handle keyboard input"""
        if self.state == GAME_RUNNING:
            if key == pygame.K_UP:
                self.pacman.set_direction(UP)
            elif key == pygame.K_DOWN:
                self.pacman.set_direction(DOWN)
            elif key == pygame.K_LEFT:
                self.pacman.set_direction(LEFT)
            elif key == pygame.K_RIGHT:
                self.pacman.set_direction(RIGHT)
            elif key == pygame.K_d:
                self.toggle_debug_mode()
        elif self.state == GAME_START or self.state == GAME_OVER or self.state == GAME_WON:
            if key == pygame.K_SPACE:
                self.reset_game()
        elif self.state == GAME_PAUSED:
            if key == pygame.K_p:
                self.state = GAME_RUNNING
    
    def toggle_pause(self):
        """Toggle pause state"""
        if self.state == GAME_RUNNING:
            self.state = GAME_PAUSED
        elif self.state == GAME_PAUSED:
            self.state = GAME_RUNNING