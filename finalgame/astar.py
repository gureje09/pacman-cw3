# astar.py - A* pathfinding algorithm
from queue import PriorityQueue

def heuristic(a, b):
    """Calculate the Manhattan distance between two points"""
    return abs(a[0] - b[0]) + abs(a[1] - b[1])

def a_star(start, goal, maze, grid_width, grid_height, allow_diagonal=False):
    """
    A* pathfinding algorithm
    Args:
        start: Tuple (x, y) of starting position
        goal: Tuple (x, y) of target position
        maze: 2D list representing the maze layout
        grid_width: Width of the grid
        grid_height: Height of the grid
        allow_diagonal: Whether diagonal movement is allowed
    Returns:
        List of coordinates representing the path from start to goal
    """
    # Convert positions to tuples for hashability
    start = tuple(start)
    goal = tuple(goal)
    
    # Initialize open set with start position
    open_set = PriorityQueue()
    open_set.put((0, start))
    
    # Dictionary to store where we came from
    came_from = {}
    
    # Cost from start to each node
    g_score = {start: 0}
    
    # Estimated total cost from start to goal through each node
    f_score = {start: heuristic(start, goal)}
    
    # Keep track of nodes in open set for faster lookup
    open_set_hash = {start}
    
    # Define movement directions
    if allow_diagonal:
        directions = [(0, 1), (1, 0), (0, -1), (-1, 0), 
                      (1, 1), (1, -1), (-1, 1), (-1, -1)]
    else:
        directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]
    
    explored_paths = set()  # For visualization
    
    while not open_set.empty():
        # Get the node with lowest f_score
        current_f, current = open_set.get()
        open_set_hash.remove(current)
        
        # Add current to explored paths for visualization
        explored_paths.add(current)
        
        # Check if we reached the goal
        if current == goal:
            # Reconstruct the path
            path = []
            temp = current
            while temp in came_from:
                path.append(temp)
                temp = came_from[temp]
            path.reverse()
            return path, explored_paths
        
        # Check neighbors
        x, y = current
        for dx, dy in directions:
            neighbor = (x + dx, y + dy)
            nx, ny = neighbor
            
            # Check if neighbor is valid
            if (0 <= nx < grid_width and 0 <= ny < grid_height and 
                maze[ny][nx] != 'X'):  # X represents wall
                
                # Calculate tentative g_score
                tentative_g = g_score[current] + 1
                
                # Check if this path is better than previous ones
                if neighbor not in g_score or tentative_g < g_score[neighbor]:
                    # Update path info
                    came_from[neighbor] = current
                    g_score[neighbor] = tentative_g
                    f_score[neighbor] = tentative_g + heuristic(neighbor, goal)
                    
                    # Add to open set if not already there
                    if neighbor not in open_set_hash:
                        open_set.put((f_score[neighbor], neighbor))
                        open_set_hash.add(neighbor)
    
    # No path found - return empty path but explored paths for visualization
    return [], explored_paths

def get_next_move(ghost_pos, pacman_pos, maze, grid_width, grid_height):
    """
    Calculate next move for ghost using A* pathfinding
    Args:
        ghost_pos: Current ghost position (x, y)
        pacman_pos: Current pacman position (x, y)
        maze: 2D list representing the maze layout
        grid_width: Width of the grid
        grid_height: Height of the grid
    Returns:
        Tuple containing next position and full path
    """
    path, explored = a_star(ghost_pos, pacman_pos, maze, grid_width, grid_height)
    
    if not path:
        return ghost_pos, [], explored  # No valid path found
    
    return path[0], path, explored  # Return next position and full path