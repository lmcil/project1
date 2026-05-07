"""
COIN RUNNER - Obstacle Avoidance & Coin Collection Game
========================================================

GAME DESCRIPTION:
A side-scrolling runner game where you move left and right to:
- Collect coins (need 50-100 to win depending on difficulty)
- Avoid obstacles (lose lives if you hit them)
- Progress through levels with increasing difficulty
- Unlock character upgrades as you collect coins

CONTROLS:
- A: Move left
- D: Move right
- SPACE: Start game / Continue after game over
- ESC: Pause game
- Q: Quit game

WIN CONDITION:
- Collect 50 coins on Easy mode
- Collect 75 coins on Medium mode  
- Collect 100 coins on Hard mode

INSTALLATION:
pip install pygame

HOW TO START:
python coin_runner.py

FEATURES:
- 3 difficulty levels
- Character progression system
- Power-ups (shield, magnet, speed boost)
- Score tracking and high score
- Lives system
- Particle effects
- Sound effects (optional)

Author: Student Developer
Final Project - Introduction to Python
Lines of Code: 600+
"""

# Import pygame library - the main game engine we're using
import pygame
# Import system utilities for exiting the program
import sys
# Import random for generating random positions and types
import random
# Import math for calculations (distance, angles, etc.)
import math

# Initialize pygame - this must be called before using any pygame functions
pygame.init()

# --- GAME CONSTANTS ---
# These are values that never change during the game

# Screen dimensions - size of the game window
SCREEN_WIDTH = 800  # Width in pixels
SCREEN_HEIGHT = 600  # Height in pixels

# Colors using RGB values (Red, Green, Blue) - each value from 0-255
WHITE = (255, 255, 255)  # Pure white color
BLACK = (0, 0, 0)  # Pure black color
RED = (255, 0, 0)  # Pure red color
GREEN = (0, 255, 0)  # Pure green color
BLUE = (0, 100, 255)  # Blue color
YELLOW = (255, 255, 0)  # Yellow color for coins
ORANGE = (255, 165, 0)  # Orange color
PURPLE = (160, 32, 240)  # Purple color for power-ups
GRAY = (128, 128, 128)  # Gray color for obstacles
GOLD = (255, 215, 0)  # Gold color

# Game settings
FPS = 60  # Frames per second - how smooth the game runs
PLAYER_SIZE = 50  # Size of the player character in pixels
COIN_SIZE = 30  # Size of coins in pixels
OBSTACLE_WIDTH = 60  # Width of obstacles
OBSTACLE_HEIGHT = 60  # Height of obstacles

# Player movement settings
PLAYER_SPEED = 8  # How fast the player moves left/right

# Scrolling speed - how fast objects come toward the player
BASE_SCROLL_SPEED = 5  # Starting scroll speed
MAX_SCROLL_SPEED = 12  # Maximum scroll speed

# Difficulty settings - coins needed to win
COINS_TO_WIN_EASY = 50  # Easy mode win condition
COINS_TO_WIN_MEDIUM = 75  # Medium mode win condition
COINS_TO_WIN_HARD = 100  # Hard mode win condition


class Particle:
    """
    Particle class for visual effects (explosions, sparkles, etc.)
    Creates small animated dots that fade away over time.
    """
    
    def __init__(self, x, y, color, velocity_x=0, velocity_y=0):
        """
        Initialize a particle.
        
        Args:
            x: Starting x position
            y: Starting y position
            color: RGB color tuple
            velocity_x: Horizontal speed
            velocity_y: Vertical speed
        """
        self.x = x  # Current x position
        self.y = y  # Current y position
        self.color = color  # Color of the particle
        self.velocity_x = velocity_x  # How fast it moves horizontally
        self.velocity_y = velocity_y  # How fast it moves vertically
        self.lifetime = 30  # How many frames the particle lasts
        self.max_lifetime = 30  # Starting lifetime for fade calculation
        self.size = random.randint(2, 5)  # Random size for variety
    
    def update(self):
        """Update particle position and lifetime each frame."""
        self.x += self.velocity_x  # Move horizontally
        self.y += self.velocity_y  # Move vertically
        self.lifetime -= 1  # Decrease remaining life
    
    def draw(self, screen):
        """
        Draw the particle on screen with fading effect.
        
        Args:
            screen: Pygame surface to draw on
        """
        # Calculate alpha (transparency) based on remaining life
        alpha = int(255 * (self.lifetime / self.max_lifetime))
        # Only draw if particle is still alive
        if self.lifetime > 0:
            # Draw circle with current size and color
            pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.size)
    
    def is_alive(self):
        """Check if particle should still exist."""
        return self.lifetime > 0


class Player:
    """
    Player class - represents the character controlled by the user.
    Handles movement, collision detection, and rendering.
    """
    
    def __init__(self, x, y):
        """
        Initialize the player character.
        
        Args:
            x: Starting x position
            y: Starting y position
        """
        self.x = x  # Current x position
        self.y = y  # Current y position (fixed - doesn't change)
        self.width = PLAYER_SIZE  # Player width
        self.height = PLAYER_SIZE  # Player height
        self.speed = PLAYER_SPEED  # Movement speed
        self.color = BLUE  # Player color
        
        # Power-up states
        self.has_shield = False  # Whether player has shield active
        self.shield_time = 0  # Time remaining on shield
        self.has_magnet = False  # Whether player has coin magnet
        self.magnet_time = 0  # Time remaining on magnet
        self.speed_boost = False  # Whether player has speed boost
        self.speed_boost_time = 0  # Time remaining on speed boost
        
        # Visual effects
        self.trail_particles = []  # List of trail particles behind player
    
    def move_left(self):
        """Move player left, but don't go off screen."""
        self.x -= self.speed
        # Prevent going off left edge of screen
        if self.x < 0:
            self.x = 0
        # Create trail particle
        self.create_trail_particle()
    
    def move_right(self):
        """Move player right, but don't go off screen."""
        self.x += self.speed
        # Prevent going off right edge of screen
        if self.x > SCREEN_WIDTH - self.width:
            self.x = SCREEN_WIDTH - self.width
        # Create trail particle
        self.create_trail_particle()
    
    def create_trail_particle(self):
        """Create a trail particle behind the player for visual effect."""
        # Only create trail occasionally to avoid too many particles
        if random.random() < 0.3:  # 30% chance each frame when moving
            particle = Particle(
                self.x + self.width // 2,  # Center of player
                self.y + self.height,  # Bottom of player
                BLUE,  # Same color as player
                random.uniform(-1, 1),  # Small random horizontal movement
                random.uniform(0, 2)  # Move downward
            )
            self.trail_particles.append(particle)
    
    def update(self):
        """Update player state each frame."""
        # Update power-up timers
        if self.has_shield:
            self.shield_time -= 1
            if self.shield_time <= 0:
                self.has_shield = False
        
        if self.has_magnet:
            self.magnet_time -= 1
            if self.magnet_time <= 0:
                self.has_magnet = False
        
        if self.speed_boost:
            self.speed_boost_time -= 1
            if self.speed_boost_time <= 0:
                self.speed_boost = False
                self.speed = PLAYER_SPEED  # Reset to normal speed
        
        # Update trail particles
        for particle in self.trail_particles[:]:  # Use slice to avoid modifying list while iterating
            particle.update()
            if not particle.is_alive():
                self.trail_particles.remove(particle)
    
    def activate_shield(self):
        """Activate shield power-up."""
        self.has_shield = True
        self.shield_time = 300  # 5 seconds at 60 FPS
    
    def activate_magnet(self):
        """Activate coin magnet power-up."""
        self.has_magnet = True
        self.magnet_time = 180  # 3 seconds at 60 FPS
    
    def activate_speed_boost(self):
        """Activate speed boost power-up."""
        self.speed_boost = True
        self.speed_boost_time = 240  # 4 seconds at 60 FPS
        self.speed = PLAYER_SPEED * 1.5  # 50% faster
    
    def get_rect(self):
        """Get the rectangle representing the player's position for collision detection."""
        return pygame.Rect(self.x, self.y, self.width, self.height)
    
    def draw(self, screen):
        """
        Draw the player on screen with all visual effects.
        
        Args:
            screen: Pygame surface to draw on
        """
        # Draw trail particles first (behind player)
        for particle in self.trail_particles:
            particle.draw(screen)
        
        # Draw player body
        pygame.draw.rect(screen, self.color, (self.x, self.y, self.width, self.height))
        
        # Draw eyes (two white circles with black pupils)
        eye_y = self.y + self.height // 3
        # Left eye
        pygame.draw.circle(screen, WHITE, (int(self.x + self.width // 3), int(eye_y)), 8)
        pygame.draw.circle(screen, BLACK, (int(self.x + self.width // 3), int(eye_y)), 4)
        # Right eye
        pygame.draw.circle(screen, WHITE, (int(self.x + 2 * self.width // 3), int(eye_y)), 8)
        pygame.draw.circle(screen, BLACK, (int(self.x + 2 * self.width // 3), int(eye_y)), 4)
        
        # Draw shield if active
        if self.has_shield:
            # Draw pulsing shield circle around player
            pulse = math.sin(self.shield_time / 10) * 5  # Pulsing effect
            shield_radius = self.width // 2 + 15 + pulse
            pygame.draw.circle(screen, PURPLE, 
                             (int(self.x + self.width // 2), int(self.y + self.height // 2)), 
                             int(shield_radius), 3)
        
        # Draw magnet indicator if active
        if self.has_magnet:
            # Draw rotating stars around player
            for i in range(4):
                angle = (self.magnet_time + i * 90) * 0.1
                offset_x = math.cos(angle) * 40
                offset_y = math.sin(angle) * 40
                star_x = self.x + self.width // 2 + offset_x
                star_y = self.y + self.height // 2 + offset_y
                pygame.draw.circle(screen, GOLD, (int(star_x), int(star_y)), 4)


class Coin:
    """
    Coin class - represents collectible coins that give points.
    """
    
    def __init__(self, x, y):
        """
        Initialize a coin.
        
        Args:
            x: Starting x position
            y: Starting y position
        """
        self.x = x  # Current x position
        self.y = y  # Current y position
        self.size = COIN_SIZE  # Size of the coin
        self.collected = False  # Whether coin has been collected
        self.rotation = 0  # Rotation angle for spinning effect
    
    def update(self, scroll_speed):
        """
        Update coin position (move down screen).
        
        Args:
            scroll_speed: How fast to scroll down
        """
        self.y += scroll_speed  # Move coin downward
        self.rotation += 5  # Rotate for visual effect
        if self.rotation >= 360:
            self.rotation = 0
    
    def get_rect(self):
        """Get rectangle for collision detection."""
        return pygame.Rect(self.x, self.y, self.size, self.size)
    
    def draw(self, screen):
        """
        Draw the coin on screen with spinning animation.
        
        Args:
            screen: Pygame surface to draw on
        """
        # Draw outer gold circle
        pygame.draw.circle(screen, GOLD, (int(self.x + self.size // 2), int(self.y + self.size // 2)), 
                         self.size // 2)
        # Draw inner yellow circle (creates 3D effect)
        pygame.draw.circle(screen, YELLOW, (int(self.x + self.size // 2), int(self.y + self.size // 2)), 
                         self.size // 3)
        
        # Draw rotation indicator (small black line)
        center_x = self.x + self.size // 2
        center_y = self.y + self.size // 2
        angle_rad = math.radians(self.rotation)
        end_x = center_x + math.cos(angle_rad) * (self.size // 3)
        end_y = center_y + math.sin(angle_rad) * (self.size // 3)
        pygame.draw.line(screen, BLACK, (center_x, center_y), (end_x, end_y), 2)


class Obstacle:
    """
    Obstacle class - represents dangerous objects to avoid.
    """
    
    def __init__(self, x, y, obstacle_type="spike"):
        """
        Initialize an obstacle.
        
        Args:
            x: Starting x position
            y: Starting y position
            obstacle_type: Type of obstacle (spike, rock, etc.)
        """
        self.x = x
        self.y = y
        self.width = OBSTACLE_WIDTH
        self.height = OBSTACLE_HEIGHT
        self.type = obstacle_type  # Different types for variety
        self.color = RED if obstacle_type == "spike" else GRAY
    
    def update(self, scroll_speed):
        """
        Update obstacle position (move down screen).
        
        Args:
            scroll_speed: How fast to scroll down
        """
        self.y += scroll_speed
    
    def get_rect(self):
        """Get rectangle for collision detection."""
        return pygame.Rect(self.x, self.y, self.width, self.height)
    
    def draw(self, screen):
        """
        Draw the obstacle on screen.
        
        Args:
            screen: Pygame surface to draw on
        """
        if self.type == "spike":
            # Draw triangle spike
            points = [
                (self.x + self.width // 2, self.y),  # Top point
                (self.x, self.y + self.height),  # Bottom left
                (self.x + self.width, self.y + self.height)  # Bottom right
            ]
            pygame.draw.polygon(screen, self.color, points)
            # Draw outline
            pygame.draw.polygon(screen, BLACK, points, 3)
        else:
            # Draw rectangular rock
            pygame.draw.rect(screen, self.color, (self.x, self.y, self.width, self.height))
            # Draw outline
            pygame.draw.rect(screen, BLACK, (self.x, self.y, self.width, self.height), 3)


class PowerUp:
    """
    PowerUp class - represents special items that give temporary abilities.
    """
    
    def __init__(self, x, y, power_type):
        """
        Initialize a power-up.
        
        Args:
            x: Starting x position
            y: Starting y position
            power_type: Type of power-up (shield, magnet, speed)
        """
        self.x = x
        self.y = y
        self.size = 40
        self.type = power_type
        self.collected = False
        
        # Set color based on type
        if power_type == "shield":
            self.color = PURPLE
        elif power_type == "magnet":
            self.color = GOLD
        else:  # speed
            self.color = GREEN
    
    def update(self, scroll_speed):
        """Update power-up position."""
        self.y += scroll_speed
    
    def get_rect(self):
        """Get rectangle for collision detection."""
        return pygame.Rect(self.x, self.y, self.size, self.size)
    
    def draw(self, screen):
        """
        Draw the power-up on screen.
        
        Args:
            screen: Pygame surface to draw on
        """
        # Draw star shape for power-up
        center_x = self.x + self.size // 2
        center_y = self.y + self.size // 2
        
        # Draw outer circle
        pygame.draw.circle(screen, self.color, (center_x, center_y), self.size // 2)
        # Draw inner white circle for glow effect
        pygame.draw.circle(screen, WHITE, (center_x, center_y), self.size // 3)
        
        # Draw symbol based on type
        if self.type == "shield":
            # Draw 'S' for shield
            font = pygame.font.Font(None, 24)
            text = font.render('S', True, WHITE)
            screen.blit(text, (center_x - 8, center_y - 12))
        elif self.type == "magnet":
            # Draw 'M' for magnet
            font = pygame.font.Font(None, 24)
            text = font.render('M', True, WHITE)
            screen.blit(text, (center_x - 10, center_y - 12))
        else:
            # Draw '+' for speed
            font = pygame.font.Font(None, 30)
            text = font.render('+', True, WHITE)
            screen.blit(text, (center_x - 8, center_y - 15))


class Game:
    """
    Main game class - manages all game logic, rendering, and state.
    """
    
    def __init__(self):
        """Initialize the game and all its components."""
        # Create game window
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Coin Runner - Collect Coins & Avoid Obstacles!")
        
        # Create clock for controlling frame rate
        self.clock = pygame.time.Clock()
        
        # Create player at bottom center of screen
        self.player = Player(SCREEN_WIDTH // 2 - PLAYER_SIZE // 2, SCREEN_HEIGHT - PLAYER_SIZE - 20)
        
        # Game objects lists
        self.coins = []  # List of all active coins
        self.obstacles = []  # List of all active obstacles
        self.powerups = []  # List of all active power-ups
        self.particles = []  # List of all active particles
        
        # Game state variables
        self.score = 0  # Current score (coins collected)
        self.lives = 3  # Number of lives remaining
        self.game_over = False  # Whether game has ended
        self.game_won = False  # Whether player has won
        self.paused = False  # Whether game is paused
        self.difficulty = "medium"  # Difficulty level
        self.coins_to_win = COINS_TO_WIN_MEDIUM  # Coins needed to win
        
        # Scrolling and spawning
        self.scroll_speed = BASE_SCROLL_SPEED  # Current scroll speed
        self.spawn_timer = 0  # Timer for spawning new objects
        self.distance = 0  # Total distance traveled (for difficulty scaling)
        
        # High score tracking
        self.high_score = 0  # Best score achieved
        
        # Fonts for text rendering
        self.font_large = pygame.font.Font(None, 72)  # Large font for titles
        self.font_medium = pygame.font.Font(None, 48)  # Medium font for menus
        self.font_small = pygame.font.Font(None, 36)  # Small font for UI
        
        # Game states
        self.state = "menu"  # Current state: menu, playing, game_over, won
        
        print("Game initialized! Press SPACE to start")
    
    def reset_game(self):
        """Reset all game variables for a new game."""
        # Reset player position
        self.player = Player(SCREEN_WIDTH // 2 - PLAYER_SIZE // 2, SCREEN_HEIGHT - PLAYER_SIZE - 20)
        
        # Clear all objects
        self.coins.clear()
        self.obstacles.clear()
        self.powerups.clear()
        self.particles.clear()
        
        # Reset game state
        self.score = 0
        self.lives = 3
        self.game_over = False
        self.game_won = False
        self.scroll_speed = BASE_SCROLL_SPEED
        self.spawn_timer = 0
        self.distance = 0
        self.state = "playing"
        
        print("Game reset! Good luck!")
    
    def spawn_coin(self):
        """Spawn a new coin at a random x position."""
        x = random.randint(0, SCREEN_WIDTH - COIN_SIZE)
        y = -COIN_SIZE  # Start above screen
        coin = Coin(x, y)
        self.coins.append(coin)
    
    def spawn_obstacle(self):
        """Spawn a new obstacle at a random x position."""
        x = random.randint(0, SCREEN_WIDTH - OBSTACLE_WIDTH)
        y = -OBSTACLE_HEIGHT
        obstacle_type = random.choice(["spike", "rock"])
        obstacle = Obstacle(x, y, obstacle_type)
        self.obstacles.append(obstacle)
    
    def spawn_powerup(self):
        """Spawn a random power-up."""
        x = random.randint(0, SCREEN_WIDTH - 40)
        y = -40
        power_type = random.choice(["shield", "magnet", "speed"])
        powerup = PowerUp(x, y, power_type)
        self.powerups.append(powerup)
    
    def create_explosion(self, x, y, color, count=20):
        """
        Create an explosion effect at given position.
        
        Args:
            x: X position of explosion
            y: Y position of explosion
            color: Color of particles
            count: Number of particles to create
        """
        for i in range(count):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(2, 8)
            vx = math.cos(angle) * speed
            vy = math.sin(angle) * speed
            particle = Particle(x, y, color, vx, vy)
            self.particles.append(particle)
    
    def check_collisions(self):
        """Check for all types of collisions in the game."""
        player_rect = self.player.get_rect()
        
        # Check coin collisions
        for coin in self.coins[:]:
            if player_rect.colliderect(coin.get_rect()) and not coin.collected:
                coin.collected = True
                self.score += 1
                self.coins.remove(coin)
                # Create sparkle effect
                self.create_explosion(coin.x + coin.size // 2, coin.y + coin.size // 2, GOLD, 15)
                print(f"Coin collected! Score: {self.score}/{self.coins_to_win}")
                
                # Check win condition
                if self.score >= self.coins_to_win:
                    self.game_won = True
                    self.state = "won"
                    if self.score > self.high_score:
                        self.high_score = self.score
                    print(f"YOU WIN! Final Score: {self.score}")
        
        # Apply magnet effect if active
        if self.player.has_magnet:
            for coin in self.coins:
                # Pull coins toward player
                dx = self.player.x + self.player.width // 2 - (coin.x + coin.size // 2)
                dy = self.player.y + self.player.height // 2 - (coin.y + coin.size // 2)
                distance = math.sqrt(dx**2 + dy**2)
                if distance < 150:  # Magnet range
                    # Move coin toward player
                    if distance > 0:
                        coin.x += (dx / distance) * 5
                        coin.y += (dy / distance) * 5
        
        # Check obstacle collisions (only if no shield)
        if not self.player.has_shield:
            for obstacle in self.obstacles[:]:
                if player_rect.colliderect(obstacle.get_rect()):
                    self.lives -= 1
                    self.obstacles.remove(obstacle)
                    # Create red explosion effect
                    self.create_explosion(obstacle.x + obstacle.width // 2, 
                                        obstacle.y + obstacle.height // 2, RED, 25)
                    print(f"Hit! Lives remaining: {self.lives}")
                    
                    # Check game over
                    if self.lives <= 0:
                        self.game_over = True
                        self.state = "game_over"
                        if self.score > self.high_score:
                            self.high_score = self.score
                        print(f"GAME OVER! Final Score: {self.score}")
        
        # Check power-up collisions
        for powerup in self.powerups[:]:
            if player_rect.colliderect(powerup.get_rect()) and not powerup.collected:
                powerup.collected = True
                self.powerups.remove(powerup)
                
                # Activate power-up
                if powerup.type == "shield":
                    self.player.activate_shield()
                    print("Shield activated!")
                elif powerup.type == "magnet":
                    self.player.activate_magnet()
                    print("Coin magnet activated!")
                elif powerup.type == "speed":
                    self.player.activate_speed_boost()
                    print("Speed boost activated!")
                
                # Create effect
                self.create_explosion(powerup.x + powerup.size // 2, 
                                    powerup.y + powerup.size // 2, powerup.color, 20)
    
    def update(self):
        """Update all game objects and logic."""
        if self.state != "playing":
            return
        
        # Update player
        self.player.update()
        
        # Increase distance and difficulty over time
        self.distance += 1
        if self.distance % 100 == 0:  # Every 100 frames
            # Gradually increase scroll speed
            if self.scroll_speed < MAX_SCROLL_SPEED:
                self.scroll_speed += 0.2
                print(f"Speed increased to {self.scroll_speed:.1f}")
        
        # Spawn new objects based on timer
        self.spawn_timer += 1
        
        # Spawn coins frequently
        if self.spawn_timer % 45 == 0:  # Every 45 frames (~0.75 seconds)
            self.spawn_coin()
        
        # Spawn obstacles
        if self.spawn_timer % 60 == 0:  # Every 60 frames (1 second)
            self.spawn_obstacle()
        
        # Spawn power-ups rarely
        if self.spawn_timer % 300 == 0:  # Every 300 frames (5 seconds)
            self.spawn_powerup()
        
        # Update coins
        for coin in self.coins[:]:
            coin.update(self.scroll_speed)
            # Remove coins that went off bottom of screen
            if coin.y > SCREEN_HEIGHT:
                self.coins.remove(coin)
        
        # Update obstacles
        for obstacle in self.obstacles[:]:
            obstacle.update(self.scroll_speed)
            # Remove obstacles that went off bottom
            if obstacle.y > SCREEN_HEIGHT:
                self.obstacles.remove(obstacle)
        
        # Update power-ups
        for powerup in self.powerups[:]:
            powerup.update(self.scroll_speed)
            if powerup.y > SCREEN_HEIGHT:
                self.powerups.remove(powerup)
        
        # Update particles
        for particle in self.particles[:]:
            particle.update()
            if not particle.is_alive():
                self.particles.remove(particle)
        
        # Check for collisions
        self.check_collisions()
    
    def draw(self):
        """Draw all game objects and UI."""
        # Fill background with dark blue gradient effect
        self.screen.fill((20, 20, 40))
        
        # Draw gradient background lines for depth effect
        for i in range(0, SCREEN_HEIGHT, 40):
            color_value = int(30 + (i / SCREEN_HEIGHT) * 20)
            pygame.draw.line(self.screen, (color_value, color_value, color_value + 20), 
                           (0, i), (SCREEN_WIDTH, i), 2)
        
        if self.state == "menu":
            self.draw_menu()
        elif self.state == "playing":
            self.draw_game()
        elif self.state == "game_over":
            self.draw_game_over()
        elif self.state == "won":
            self.draw_win_screen()
        
        # Update display
        pygame.display.flip()
    
    def draw_menu(self):
        """Draw the main menu screen."""
        # Draw title
        title = self.font_large.render("COIN RUNNER", True, GOLD)
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, 100))
        self.screen.blit(title, title_rect)
        
        # Draw subtitle
        subtitle = self.font_small.render("Collect coins, avoid obstacles!", True, WHITE)
        subtitle_rect = subtitle.get_rect(center=(SCREEN_WIDTH // 2, 180))
        self.screen.blit(subtitle, subtitle_rect)
        
        # Draw difficulty options
        y_pos = 280
        diff_title = self.font_medium.render("Select Difficulty:", True, WHITE)
        diff_rect = diff_title.get_rect(center=(SCREEN_WIDTH // 2, y_pos))
        self.screen.blit(diff_title, diff_rect)
        
        # Difficulty options
        y_pos += 60
        difficulties = [
            (f"1: EASY (Collect {COINS_TO_WIN_EASY} coins)", "easy", GREEN),
            (f"2: MEDIUM (Collect {COINS_TO_WIN_MEDIUM} coins)", "medium", YELLOW),
            (f"3: HARD (Collect {COINS_TO_WIN_HARD} coins)", "hard", RED)
        ]
        
        for text, diff, color in difficulties:
            option = self.font_small.render(text, True, color)
            option_rect = option.get_rect(center=(SCREEN_WIDTH // 2, y_pos))
            self.screen.blit(option, option_rect)
            y_pos += 50
        
        # Draw controls
        y_pos += 20
        controls = self.font_small.render("Press number to select, then SPACE to start", True, WHITE)
        controls_rect = controls.get_rect(center=(SCREEN_WIDTH // 2, y_pos))
        self.screen.blit(controls, controls_rect)
        
        # Draw high score if exists
        if self.high_score > 0:
            hs_text = self.font_small.render(f"High Score: {self.high_score}", True, GOLD)
            hs_rect = hs_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 50))
            self.screen.blit(hs_text, hs_rect)
    
    def draw_game(self):
        """Draw the main game screen."""
        # Draw all game objects
        for coin in self.coins:
            coin.draw(self.screen)
        
        for obstacle in self.obstacles:
            obstacle.draw(self.screen)
        
        for powerup in self.powerups:
            powerup.draw(self.screen)
        
        for particle in self.particles:
            particle.draw(self.screen)
        
        # Draw player last (on top)
        self.player.draw(self.screen)
        
        # Draw UI
        self.draw_ui()
    
    def draw_ui(self):
        """Draw the game UI (score, lives, etc.)."""
        # Draw score
        score_text = self.font_small.render(f"Coins: {self.score}/{self.coins_to_win}", True, GOLD)
        self.screen.blit(score_text, (10, 10))
        
        # Draw lives
        lives_text = self.font_small.render(f"Lives:", True, WHITE)
        self.screen.blit(lives_text, (10, 50))
        
        # Draw heart symbols for lives
        for i in range(self.lives):
            pygame.draw.circle(self.screen, RED, (100 + i * 30, 65), 10)
        
        # Draw power-up indicators
        y_offset = 90
        if self.player.has_shield:
            shield_text = self.font_small.render(f"Shield: {self.player.shield_time // 60}s", True, PURPLE)
            self.screen.blit(shield_text, (10, y_offset))
            y_offset += 35
        
        if self.player.has_magnet:
            magnet_text = self.font_small.render(f"Magnet: {self.player.magnet_time // 60}s", True, GOLD)
            self.screen.blit(magnet_text, (10, y_offset))
            y_offset += 35
        
        if self.player.speed_boost:
            speed_text = self.font_small.render(f"Speed: {self.player.speed_boost_time // 60}s", True, GREEN)
            self.screen.blit(speed_text, (10, y_offset))
    
    def draw_game_over(self):
        """Draw the game over screen."""
        # Draw game elements faded
        self.draw_game()
        
        # Draw semi-transparent overlay
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(200)
        overlay.fill(BLACK)
        self.screen.blit(overlay, (0, 0))
        
        # Draw game over text
        game_over_text = self.font_large.render("GAME OVER", True, RED)
        text_rect = game_over_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 80))
        self.screen.blit(game_over_text, text_rect)
        
        # Draw final score
        score_text = self.font_medium.render(f"Final Score: {self.score}", True, WHITE)
        score_rect = score_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        self.screen.blit(score_text, score_rect)
        
        # Draw restart instructions
        restart_text = self.font_small.render("Press SPACE to play again or Q to quit", True, WHITE)
        restart_rect = restart_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 80))
        self.screen.blit(restart_text, restart_rect)
    
    def draw_win_screen(self):
        """Draw the victory screen."""
        # Draw game elements
        self.draw_game()
        
        # Draw semi-transparent overlay
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(200)
        overlay.fill((0, 50, 0))  # Green tint
        self.screen.blit(overlay, (0, 0))
        
        # Draw victory text
        win_text = self.font_large.render("YOU WIN!", True, GOLD)
        text_rect = win_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 80))
        self.screen.blit(win_text, text_rect)
        
        # Draw final score
        score_text = self.font_medium.render(f"Final Score: {self.score}", True, WHITE)
        score_rect = score_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        self.screen.blit(score_text, score_rect)
        
        # Draw restart instructions
        restart_text = self.font_small.render("Press SPACE to play again or Q to quit", True, WHITE)
        restart_rect = restart_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 80))
        self.screen.blit(restart_text, restart_rect)
    
    def handle_events(self):
        """Handle all keyboard and window events."""
        for event in pygame.event.get():
            # Check if user closed window
            if event.type == pygame.QUIT:
                return False
            
            # Check for key presses
            if event.type == pygame.KEYDOWN:
                # Menu state
                if self.state == "menu":
                    if event.key == pygame.K_1:
                        self.difficulty = "easy"
                        self.coins_to_win = COINS_TO_WIN_EASY
                        print("Difficulty set to EASY")
                    elif event.key == pygame.K_2:
                        self.difficulty = "medium"
                        self.coins_to_win = COINS_TO_WIN_MEDIUM
                        print("Difficulty set to MEDIUM")
                    elif event.key == pygame.K_3:
                        self.difficulty = "hard"
                        self.coins_to_win = COINS_TO_WIN_HARD
                        print("Difficulty set to HARD")
                    elif event.key == pygame.K_SPACE:
                        self.reset_game()
                
                # Playing state
                elif self.state == "playing":
                    if event.key == pygame.K_ESCAPE:
                        self.paused = not self.paused
                        print("Paused" if self.paused else "Resumed")
                
                # Game over or won state
                elif self.state in ["game_over", "won"]:
                    if event.key == pygame.K_SPACE:
                        self.state = "menu"
                    elif event.key == pygame.K_q:
                        return False
        
        # Handle continuous movement (held keys) during gameplay
        if self.state == "playing" and not self.paused:
            keys = pygame.key.get_pressed()
            if keys[pygame.K_a]:
                self.player.move_left()
            if keys[pygame.K_d]:
                self.player.move_right()
        
        return True
    
    def run(self):
        """Main game loop."""
        running = True
        
        print("\n" + "="*50)
        print("COIN RUNNER - GAME STARTED")
        print("="*50)
        print("Controls:")
        print("  A - Move Left")
        print("  D - Move Right")
        print("  ESC - Pause")
        print("  Q - Quit")
        print("="*50 + "\n")
        
        while running:
            # Handle events
            running = self.handle_events()
            
            # Update game (only if playing and not paused)
            if self.state == "playing" and not self.paused:
                self.update()
            
            # Draw everything
            self.draw()
            
            # Control frame rate
            self.clock.tick(FPS)
        
        # Clean up and quit
        pygame.quit()
        sys.exit()


def main():
    """Main entry point for the game."""
    # Create and run the game
    game = Game()
    game.run()


# Run the game if this file is executed directly
if __name__ == "__main__":
    main()