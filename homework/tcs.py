import pygame
import random
import sys
from pygame.locals import *

# Initialize pygame
pygame.init()

# Constants
SCREEN_WIDTH = 600
SCREEN_HEIGHT = 450
GRID_SIZE = 20
GRID_WIDTH = SCREEN_WIDTH // GRID_SIZE
GRID_HEIGHT = (SCREEN_HEIGHT - 50) // GRID_SIZE  # Leave space for score display
SNAKE_SPEEDS = {'Easy': 10, 'Medium': 15, 'Hard': 20}
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
DARK_GREEN = (0, 200, 0)
BLUE = (0, 0, 255)
GRAY = (100, 100, 100)

# Directions
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)

class Snake:
    def __init__(self):
        self.positions = [(GRID_WIDTH // 2, GRID_HEIGHT // 2)]
        self.length = 3
        self.direction = RIGHT
        self.color_head = GREEN
        self.color_body = DARK_GREEN
        self.score = 0
        self.reset()

    def reset(self):
        self.positions = [(GRID_WIDTH // 2, GRID_HEIGHT // 2)]
        self.length = 3
        self.direction = RIGHT
        self.score = 0

    def get_head_position(self):
        return self.positions[0]

    def update(self):
        head = self.get_head_position()
        x, y = self.direction
        new_head = ((head[0] + x) % GRID_WIDTH, (head[1] + y) % GRID_HEIGHT)
        
        if new_head in self.positions[1:]:
            return True  # Game over - collision with self
        elif new_head[0] < 0 or new_head[0] >= GRID_WIDTH or new_head[1] < 0 or new_head[1] >= GRID_HEIGHT:
            return True  # Game over - collision with wall
        
        self.positions.insert(0, new_head)
        if len(self.positions) > self.length:
            self.positions.pop()
        
        return False  # Game continues

    def grow(self):
        self.length += 1
        self.score += 10

    def render(self, surface):
        for i, p in enumerate(self.positions):
            color = self.color_head if i == 0 else self.color_body
            rect = pygame.Rect((p[0] * GRID_SIZE, p[1] * GRID_SIZE + 50), (GRID_SIZE, GRID_SIZE))
            pygame.draw.rect(surface, color, rect)
            pygame.draw.rect(surface, BLACK, rect, 1)

    def change_direction(self, direction):
        # Prevent 180-degree turns
        if (direction[0] * -1, direction[1] * -1) != self.direction:
            self.direction = direction

class Food:
    def __init__(self):
        self.position = (0, 0)
        self.color = RED
        self.randomize_position()

    def randomize_position(self, snake_positions=None):
        if snake_positions is None:
            snake_positions = []
        
        while True:
            self.position = (random.randint(0, GRID_WIDTH - 1), random.randint(0, GRID_HEIGHT - 1))
            if self.position not in snake_positions:
                break

    def render(self, surface):
        rect = pygame.Rect((self.position[0] * GRID_SIZE, self.position[1] * GRID_SIZE + 50), (GRID_SIZE, GRID_SIZE))
        pygame.draw.rect(surface, self.color, rect)
        pygame.draw.rect(surface, BLACK, rect, 1)

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption('Snake Game')
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont('arial', 20)
        self.big_font = pygame.font.SysFont('arial', 40)
        self.snake = Snake()
        self.food = Food()
        self.difficulty = None
        self.game_over = False
        self.paused = False
        self.state = "MENU"  # MENU, PLAYING, GAME_OVER

    def draw_menu(self):
        self.screen.fill(WHITE)
        title = self.big_font.render("SNAKE GAME", True, BLUE)
        self.screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 50))
        
        easy = self.font.render("[1] Easy", True, BLACK)
        medium = self.font.render("[2] Medium", True, BLACK)
        hard = self.font.render("[3] Hard", True, BLACK)
        
        self.screen.blit(easy, (SCREEN_WIDTH // 2 - easy.get_width() // 2, 150))
        self.screen.blit(medium, (SCREEN_WIDTH // 2 - medium.get_width() // 2, 180))
        self.screen.blit(hard, (SCREEN_WIDTH // 2 - hard.get_width() // 2, 210))
        
        instruction = self.font.render("Press number to select difficulty", True, GRAY)
        self.screen.blit(instruction, (SCREEN_WIDTH // 2 - instruction.get_width() // 2, 300))

    def draw_game(self):
        self.screen.fill(WHITE)
        
        # Draw score and difficulty
        score_text = self.font.render(f"Score: {self.snake.score}", True, BLACK)
        difficulty_text = self.font.render(f"Difficulty: {self.difficulty}", True, BLACK)
        self.screen.blit(score_text, (20, 10))
        self.screen.blit(difficulty_text, (SCREEN_WIDTH - difficulty_text.get_width() - 20, 10))
        
        # Draw game area border
        border_rect = pygame.Rect(0, 50, SCREEN_WIDTH, GRID_HEIGHT * GRID_SIZE)
        pygame.draw.rect(self.screen, GRAY, border_rect, 2)
        
        # Draw snake and food
        self.snake.render(self.screen)
        self.food.render(self.screen)
        
        # Draw instructions
        instructions = self.font.render("P: Pause   R: Restart", True, GRAY)
        self.screen.blit(instructions, (SCREEN_WIDTH // 2 - instructions.get_width() // 2, SCREEN_HEIGHT - 30))
        
        if self.paused:
            pause_text = self.big_font.render("PAUSED", True, BLUE)
            self.screen.blit(pause_text, (SCREEN_WIDTH // 2 - pause_text.get_width() // 2, 
                                         SCREEN_HEIGHT // 2 - pause_text.get_height() // 2))

    def draw_game_over(self):
        self.screen.fill(WHITE)
        game_over = self.big_font.render("GAME OVER", True, RED)
        self.screen.blit(game_over, (SCREEN_WIDTH // 2 - game_over.get_width() // 2, 100))
        
        score_text = self.font.render(f"Your score: {self.snake.score}", True, BLACK)
        self.screen.blit(score_text, (SCREEN_WIDTH // 2 - score_text.get_width() // 2, 180))
        
        restart = self.font.render("Press R to restart", True, BLACK)
        quit_text = self.font.render("Press ESC to quit", True, BLACK)
        
        self.screen.blit(restart, (SCREEN_WIDTH // 2 - restart.get_width() // 2, 250))
        self.screen.blit(quit_text, (SCREEN_WIDTH // 2 - quit_text.get_width() // 2, 280))

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == KEYDOWN:
                if self.state == "MENU":
                    if event.key == K_1:
                        self.difficulty = "Easy"
                        self.state = "PLAYING"
                    elif event.key == K_2:
                        self.difficulty = "Medium"
                        self.state = "PLAYING"
                    elif event.key == K_3:
                        self.difficulty = "Hard"
                        self.state = "PLAYING"
                    elif event.key == K_ESCAPE:
                        pygame.quit()
                        sys.exit()
                elif self.state == "PLAYING":
                    if event.key == K_UP:
                        self.snake.change_direction(UP)
                    elif event.key == K_DOWN:
                        self.snake.change_direction(DOWN)
                    elif event.key == K_LEFT:
                        self.snake.change_direction(LEFT)
                    elif event.key == K_RIGHT:
                        self.snake.change_direction(RIGHT)
                    elif event.key == K_p:
                        self.paused = not self.paused
                    elif event.key == K_r:
                        self.reset_game()
                    elif event.key == K_ESCAPE:
                        pygame.quit()
                        sys.exit()
                elif self.state == "GAME_OVER":
                    if event.key == K_r:
                        self.reset_game()
                    elif event.key == K_ESCAPE:
                        pygame.quit()
                        sys.exit()

    def update(self):
        if self.state == "PLAYING" and not self.paused and not self.game_over:
            self.game_over = self.snake.update()
            
            if self.snake.get_head_position() == self.food.position:
                self.snake.grow()
                self.food.randomize_position(self.snake.positions)
            
            if self.game_over:
                self.state = "GAME_OVER"

    def reset_game(self):
        self.snake.reset()
        self.food.randomize_position()
        self.game_over = False
        self.paused = False
        self.state = "PLAYING"

    def run(self):
        while True:
            self.handle_events()
            self.update()
            
            if self.state == "MENU":
                self.draw_menu()
            elif self.state == "PLAYING":
                self.draw_game()
            elif self.state == "GAME_OVER":
                self.draw_game_over()
            
            pygame.display.update()
            
            if self.state == "PLAYING" and not self.paused:
                self.clock.tick(SNAKE_SPEEDS[self.difficulty])
            else:
                self.clock.tick(10)

if __name__ == "__main__":
    game = Game()
    game.run()