import pygame
import random
import math
import sys

# Инициализация Pygame
pygame.init()

# Настройки экрана (4:3 как в старых аркадах)
SCREEN_WIDTH = 1024
SCREEN_HEIGHT = 768
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("RETRO ARCADE COLLECTION '80s")
clock = pygame.time.Clock()

# Аутентичная палитра CGA/EGA (4-битная)
class Colors:
    BLACK = (0, 0, 0)
    BLUE = (0, 0, 170)
    GREEN = (0, 170, 0)
    CYAN = (0, 170, 170)
    RED = (170, 0, 0)
    MAGENTA = (170, 0, 170)
    BROWN = (170, 85, 0)
    LIGHT_GRAY = (170, 170, 170)
    DARK_GRAY = (85, 85, 85)
    LIGHT_BLUE = (85, 85, 255)
    LIGHT_GREEN = (85, 255, 85)
    LIGHT_CYAN = (85, 255, 255)
    LIGHT_RED = (255, 85, 85)
    LIGHT_MAGENTA = (255, 85, 255)
    YELLOW = (255, 255, 85)
    WHITE = (255, 255, 255)

# Пиксельные шрифты
try:
    font_large = pygame.font.Font("PressStart2P.ttf", 32)
    font_medium = pygame.font.Font("PressStart2P.ttf", 20)
    font_small = pygame.font.Font("PressStart2P.ttf", 12)
except:
    print("Ретро-шрифт не найден, используем системный")
    font_large = pygame.font.Font(None, 48)
    font_medium = pygame.font.Font(None, 32)
    font_small = pygame.font.Font(None, 20)

# Класс для создания ретро-эффектов
class RetroEffects:
    @staticmethod
    def draw_scanlines(surface):
        scanline = pygame.Surface((SCREEN_WIDTH, 2))
        scanline.set_alpha(30)
        scanline.fill(Colors.BLACK)
        for y in range(0, SCREEN_HEIGHT, 4):
            surface.blit(scanline, (0, y))
    
    @staticmethod
    def draw_crt_corner(surface):
        for x in range(0, SCREEN_WIDTH, 2):
            for y in range(0, SCREEN_HEIGHT, 2):
                dist = math.sqrt((x - SCREEN_WIDTH//2)**2 + (y - SCREEN_HEIGHT//2)**2)
                if dist > 400:
                    alpha = min(255, int((dist - 400) / 2))
                    dark = pygame.Surface((2, 2))
                    dark.set_alpha(alpha)
                    dark.fill(Colors.BLACK)
                    surface.blit(dark, (x, y))

# Космический фон со звездами
class SpaceBackground:
    def __init__(self):
        self.stars = []
        for _ in range(200):
            self.stars.append({
                'x': random.randint(0, SCREEN_WIDTH),
                'y': random.randint(0, SCREEN_HEIGHT),
                'size': random.choice([1, 1, 1, 2]),
                'brightness': random.randint(100, 255)
            })
    
    def draw(self, surface):
        surface.fill(Colors.BLACK)
        
        for star in self.stars:
            brightness = star['brightness']
            pygame.draw.circle(surface, (brightness, brightness, brightness), 
                             (star['x'], star['y']), star['size'])

# Базовый класс для всех игр с ретро-стилем
class RetroGame:
    def __init__(self, name, color):
        self.name = name
        self.color = color
        self.score = 0
        self.lives = 3
        self.game_over = False
        self.high_score = self.load_high_score()
        
    def load_high_score(self):
        try:
            with open(f"{self.name.lower().replace(' ', '_')}_highscore.txt", "r") as f:
                return int(f.read())
        except:
            return 0
    
    def save_high_score(self):
        if self.score > self.high_score:
            self.high_score = self.score
            try:
                with open(f"{self.name.lower().replace(' ', '_')}_highscore.txt", "w") as f:
                    f.write(str(self.high_score))
            except:
                pass
    
    def draw_hud(self):
        pygame.draw.rect(screen, Colors.BLACK, (0, 0, SCREEN_WIDTH, 60))
        pygame.draw.line(screen, self.color, (0, 60), (SCREEN_WIDTH, 60), 2)
        
        title = font_medium.render(self.name, True, self.color)
        screen.blit(title, (20, 20))
        
        score_text = font_small.render(f"SCORE {self.score:06d}", True, Colors.YELLOW)
        screen.blit(score_text, (300, 25))
        
        high_text = font_small.render(f"HISCORE {self.high_score:06d}", True, Colors.LIGHT_RED)
        screen.blit(high_text, (550, 25))
        
        lives_text = font_small.render(f"LIVES {self.lives}", True, Colors.LIGHT_GREEN)
        screen.blit(lives_text, (800, 25))
        
        pygame.draw.line(screen, self.color, (0, SCREEN_HEIGHT-30), 
                        (SCREEN_WIDTH, SCREEN_HEIGHT-30), 2)
        help_text = font_small.render("PRESS ESC FOR MENU", True, Colors.LIGHT_GRAY)
        screen.blit(help_text, (20, SCREEN_HEIGHT-25))
    
    def draw_game_over(self):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(180)
        overlay.fill(Colors.BLACK)
        screen.blit(overlay, (0, 0))
        
        if (pygame.time.get_ticks() // 500) % 2:
            game_over = font_large.render("GAME OVER", True, Colors.RED)
            text_rect = game_over.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2))
            screen.blit(game_over, text_rect)
        
        if self.score > self.high_score:
            self.save_high_score()
            new_record = font_medium.render("NEW RECORD!", True, Colors.YELLOW)
            record_rect = new_record.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 50))
            screen.blit(new_record, record_rect)
    
    def handle_input(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                return "menu"
            if event.key == pygame.K_r:
                self.reset()
        return None

# Игра 1: Змейка
class RetroSnake(RetroGame):
    def __init__(self):
        super().__init__("SNAKE", Colors.GREEN)
        self.cell_size = 20
        self.grid_width = SCREEN_WIDTH // self.cell_size
        self.grid_height = (SCREEN_HEIGHT - 100) // self.cell_size
        self.reset()
        
    def reset(self):
        self.snake = [(self.grid_width//2, self.grid_height//2 + 3)]
        self.direction = (1, 0)
        self.food = self.generate_food()
        self.game_over = False
        self.score = 0
        
    def generate_food(self):
        while True:
            food = (random.randint(0, self.grid_width-1), 
                   random.randint(0, self.grid_height-1) + 3)
            if food not in self.snake:
                return food
    
    def update(self):
        if self.game_over:
            return
            
        head = self.snake[0]
        new_head = (head[0] + self.direction[0], head[1] + self.direction[1])
        
        if (new_head[0] < 0 or new_head[0] >= self.grid_width or
            new_head[1] < 3 or new_head[1] >= self.grid_height + 3 or
            new_head in self.snake):
            self.game_over = True
            return
            
        self.snake.insert(0, new_head)
        
        if new_head == self.food:
            self.score += 10
            self.food = self.generate_food()
        else:
            self.snake.pop()
    
    def draw(self):
        screen.fill(Colors.BLACK)
        
        for x in range(0, SCREEN_WIDTH, self.cell_size):
            pygame.draw.line(screen, Colors.DARK_GRAY, (x, 60), (x, SCREEN_HEIGHT-30), 1)
        for y in range(60, SCREEN_HEIGHT-30, self.cell_size):
            pygame.draw.line(screen, Colors.DARK_GRAY, (0, y), (SCREEN_WIDTH, y), 1)
        
        for i, segment in enumerate(self.snake):
            rect = pygame.Rect(segment[0]*self.cell_size, segment[1]*self.cell_size,
                             self.cell_size-2, self.cell_size-2)
            
            if i == 0:
                pygame.draw.rect(screen, Colors.LIGHT_GREEN, rect)
                eye_color = Colors.BLACK if (pygame.time.get_ticks() // 500) % 2 else Colors.WHITE
                if self.direction == (1, 0):
                    pygame.draw.circle(screen, eye_color, (rect.x + 15, rect.y + 5), 2)
                    pygame.draw.circle(screen, eye_color, (rect.x + 15, rect.y + 15), 2)
                elif self.direction == (-1, 0):
                    pygame.draw.circle(screen, eye_color, (rect.x + 5, rect.y + 5), 2)
                    pygame.draw.circle(screen, eye_color, (rect.x + 5, rect.y + 15), 2)
                else:
                    pygame.draw.circle(screen, eye_color, (rect.x + 5, rect.y + 10), 2)
                    pygame.draw.circle(screen, eye_color, (rect.x + 15, rect.y + 10), 2)
            else:
                pygame.draw.rect(screen, Colors.GREEN, rect)
            pygame.draw.rect(screen, Colors.WHITE, rect, 1)
        
        food_rect = pygame.Rect(self.food[0]*self.cell_size, self.food[1]*self.cell_size,
                               self.cell_size-2, self.cell_size-2)
        pygame.draw.rect(screen, Colors.RED, food_rect)
        pygame.draw.rect(screen, Colors.YELLOW, food_rect, 1)
        pygame.draw.circle(screen, Colors.GREEN, (food_rect.x + 15, food_rect.y - 3), 3)
        
        self.draw_hud()
        
        if self.game_over:
            self.draw_game_over()
        
        RetroEffects.draw_scanlines(screen)
    
    def handle_input(self, event):
        result = super().handle_input(event)
        if result: return result
        
        if event.type == pygame.KEYDOWN and not self.game_over:
            if event.key == pygame.K_UP and self.direction != (0, 1):
                self.direction = (0, -1)
            elif event.key == pygame.K_DOWN and self.direction != (0, -1):
                self.direction = (0, 1)
            elif event.key == pygame.K_LEFT and self.direction != (1, 0):
                self.direction = (-1, 0)
            elif event.key == pygame.K_RIGHT and self.direction != (-1, 0):
                self.direction = (1, 0)

# Игра 2: Арканоид
class RetroArkanoid(RetroGame):
    def __init__(self):
        super().__init__("ARKANOID", Colors.LIGHT_BLUE)
        self.reset()
        
    def reset(self):
        self.paddle_x = SCREEN_WIDTH//2 - 50
        self.paddle_y = SCREEN_HEIGHT - 80
        self.paddle_width = 100
        self.ball_x = SCREEN_WIDTH//2
        self.ball_y = SCREEN_HEIGHT//2
        self.ball_dx = 4
        self.ball_dy = -4
        self.ball_radius = 6
        
        self.bricks = []
        colors = [Colors.RED, Colors.YELLOW, Colors.GREEN, Colors.BLUE, Colors.MAGENTA]
        for row in range(5):
            for col in range(10):
                brick_x = col * 90 + 50
                brick_y = row * 30 + 80
                self.bricks.append({
                    'rect': pygame.Rect(brick_x, brick_y, 80, 20),
                    'color': colors[row]
                })
        
        self.game_over = False
        self.score = 0
        self.lives = 3
        
    def update(self):
        if self.game_over:
            return
            
        self.ball_x += self.ball_dx
        self.ball_y += self.ball_dy
        
        if self.ball_x <= self.ball_radius or self.ball_x >= SCREEN_WIDTH - self.ball_radius:
            self.ball_dx *= -1
        if self.ball_y <= 60:
            self.ball_dy *= -1
            
        paddle_rect = pygame.Rect(self.paddle_x, self.paddle_y, self.paddle_width, 15)
        ball_rect = pygame.Rect(self.ball_x - self.ball_radius, 
                               self.ball_y - self.ball_radius,
                               self.ball_radius*2, self.ball_radius*2)
        
        if ball_rect.colliderect(paddle_rect) and self.ball_dy > 0:
            self.ball_dy *= -1
            
        for brick in self.bricks[:]:
            if ball_rect.colliderect(brick['rect']):
                self.bricks.remove(brick)
                self.score += 10
                self.ball_dy *= -1
                break
                
        if self.ball_y >= SCREEN_HEIGHT:
            self.lives -= 1
            if self.lives <= 0:
                self.game_over = True
            else:
                self.ball_x, self.ball_y = SCREEN_WIDTH//2, SCREEN_HEIGHT//2
                self.ball_dx, self.ball_dy = 4, -4
                
        if len(self.bricks) == 0:
            self.game_over = True
    
    def draw(self):
        screen.fill(Colors.BLACK)
        
        for brick in self.bricks:
            pygame.draw.rect(screen, brick['color'], brick['rect'])
            for i in range(0, brick['rect'].width, 4):
                pygame.draw.line(screen, Colors.WHITE, 
                               (brick['rect'].x + i, brick['rect'].y),
                               (brick['rect'].x + i, brick['rect'].y + brick['rect'].height), 1)
            pygame.draw.rect(screen, Colors.WHITE, brick['rect'], 2)
        
        pygame.draw.rect(screen, Colors.LIGHT_CYAN, 
                        (self.paddle_x, self.paddle_y, self.paddle_width, 15))
        pygame.draw.rect(screen, Colors.WHITE, 
                        (self.paddle_x, self.paddle_y, self.paddle_width, 15), 2)
        
        pygame.draw.circle(screen, Colors.WHITE, (int(self.ball_x), int(self.ball_y)), self.ball_radius)
        pygame.draw.circle(screen, Colors.YELLOW, (int(self.ball_x), int(self.ball_y)), self.ball_radius-2)
        
        self.draw_hud()
        
        if self.game_over:
            self.draw_game_over()
        
        RetroEffects.draw_scanlines(screen)
    
    def handle_input(self, event):
        result = super().handle_input(event)
        if result: return result
        
        if event.type == pygame.MOUSEMOTION and not self.game_over:
            mouse_x, _ = event.pos
            self.paddle_x = max(0, min(mouse_x - self.paddle_width//2, 
                                      SCREEN_WIDTH - self.paddle_width))

# Игра 3: Лабиринт (исправленная версия)
class RetroMaze(RetroGame):
    def __init__(self):
        super().__init__("MAZE", Colors.YELLOW)
        self.cell_size = 30
        self.grid_width = SCREEN_WIDTH // self.cell_size
        self.grid_height = (SCREEN_HEIGHT - 100) // self.cell_size
        self.generate_maze()
        self.reset()
        
    def generate_maze(self):
        # Сначала определяем позиции выхода
        self.exit_x = self.grid_width - 2
        self.exit_y = self.grid_height - 1
        
        # Создаем лабиринт
        self.maze = [[1 for _ in range(self.grid_width)] for _ in range(self.grid_height)]
        stack = [(1, 2)]
        self.maze[1][2] = 0
        
        while stack:
            x, y = stack[-1]
            neighbors = []
            for dx, dy in [(2,0), (-2,0), (0,2), (0,-2)]:
                nx, ny = x + dx, y + dy
                if 0 < nx < self.grid_width-1 and 1 < ny < self.grid_height-1 and self.maze[ny][nx] == 1:
                    neighbors.append((nx, ny, dx//2, dy//2))
            
            if neighbors:
                nx, ny, wx, wy = random.choice(neighbors)
                self.maze[ny][nx] = 0
                self.maze[y + wy][x + wx] = 0
                stack.append((nx, ny))
            else:
                stack.pop()
        
        # Устанавливаем выход
        self.maze[self.exit_y][self.exit_x] = 2
        
    def reset(self):
        self.player_x = 1
        self.player_y = 2
        self.game_over = False
        self.won = False
        self.score = 0
        self.moves = 0
    
    def update(self):
        if self.won or self.game_over:
            return
    
    def draw(self):
        screen.fill(Colors.BLACK)
        
        for y in range(self.grid_height):
            for x in range(self.grid_width):
                if self.maze[y][x] == 1:
                    rect = pygame.Rect(x*self.cell_size, y*self.cell_size + 60,
                                      self.cell_size-2, self.cell_size-2)
                    pygame.draw.rect(screen, Colors.BLUE, rect)
                    pygame.draw.rect(screen, Colors.LIGHT_BLUE, rect, 1)
                elif self.maze[y][x] == 2:
                    rect = pygame.Rect(x*self.cell_size, y*self.cell_size + 60,
                                      self.cell_size-2, self.cell_size-2)
                    pygame.draw.rect(screen, Colors.GREEN, rect)
                    star_x = rect.x + rect.width//2
                    star_y = rect.y + rect.height//2
                    pygame.draw.circle(screen, Colors.YELLOW, (star_x, star_y), 5)
        
        player_rect = pygame.Rect(self.player_x*self.cell_size, self.player_y*self.cell_size + 60,
                                 self.cell_size-2, self.cell_size-2)
        pygame.draw.rect(screen, Colors.RED, player_rect)
        pygame.draw.circle(screen, Colors.WHITE, (player_rect.x + 5, player_rect.y + 5), 2)
        pygame.draw.circle(screen, Colors.WHITE, (player_rect.x + 15, player_rect.y + 5), 2)
        
        self.draw_hud()
        
        if self.won:
            self.draw_win()
        elif self.game_over:
            self.draw_game_over()
        
        RetroEffects.draw_scanlines(screen)
    
    def draw_win(self):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(180)
        overlay.fill(Colors.BLACK)
        screen.blit(overlay, (0, 0))
        
        win_text = font_large.render("YOU ESCAPED!", True, Colors.GREEN)
        text_rect = win_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2))
        screen.blit(win_text, text_rect)
    
    def handle_input(self, event):
        result = super().handle_input(event)
        if result: return result
        
        if event.type == pygame.KEYDOWN and not self.won and not self.game_over:
            new_x, new_y = self.player_x, self.player_y
            if event.key == pygame.K_UP:
                new_y -= 1
            elif event.key == pygame.K_DOWN:
                new_y += 1
            elif event.key == pygame.K_LEFT:
                new_x -= 1
            elif event.key == pygame.K_RIGHT:
                new_x += 1
            
            if (0 <= new_x < self.grid_width and 0 <= new_y < self.grid_height and
                self.maze[new_y][new_x] != 1):
                self.player_x, self.player_y = new_x, new_y
                self.moves += 1
                if self.maze[new_y][new_x] == 2:
                    self.won = True
                    self.score += 1000 - self.moves * 10

# Игра 4: Пинг-понг
class RetroPong(RetroGame):
    def __init__(self):
        super().__init__("PONG", Colors.LIGHT_CYAN)
        self.reset()
        
    def reset(self):
        self.paddle_width = 15
        self.paddle_height = 100
        self.left_paddle = SCREEN_HEIGHT//2 - self.paddle_height//2
        self.right_paddle = SCREEN_HEIGHT//2 - self.paddle_height//2
        
        self.ball_size = 10
        self.ball_x = SCREEN_WIDTH//2
        self.ball_y = SCREEN_HEIGHT//2
        self.ball_dx = random.choice([-5, 5])
        self.ball_dy = random.uniform(-3, 3)
        
        self.left_score = 0
        self.right_score = 0
        self.game_over = False
        
    def update(self):
        if self.game_over:
            return
            
        self.ball_x += self.ball_dx
        self.ball_y += self.ball_dy
        
        if self.ball_y <= 60 or self.ball_y >= SCREEN_HEIGHT - 30 - self.ball_size:
            self.ball_dy *= -1
        
        left_rect = pygame.Rect(50, self.left_paddle, self.paddle_width, self.paddle_height)
        right_rect = pygame.Rect(SCREEN_WIDTH - 50 - self.paddle_width, self.right_paddle,
                                self.paddle_width, self.paddle_height)
        ball_rect = pygame.Rect(self.ball_x, self.ball_y, self.ball_size, self.ball_size)
        
        if ball_rect.colliderect(left_rect) and self.ball_dx < 0:
            self.ball_dx = abs(self.ball_dx)
            offset = (self.ball_y + self.ball_size/2) - (self.left_paddle + self.paddle_height/2)
            self.ball_dy = offset / (self.paddle_height/2) * 7
            
        if ball_rect.colliderect(right_rect) and self.ball_dx > 0:
            self.ball_dx = -abs(self.ball_dx)
            offset = (self.ball_y + self.ball_size/2) - (self.right_paddle + self.paddle_height/2)
            self.ball_dy = offset / (self.paddle_height/2) * 7
        
        if self.ball_x <= 0:
            self.right_score += 1
            self.reset_ball()
        elif self.ball_x >= SCREEN_WIDTH - self.ball_size:
            self.left_score += 1
            self.reset_ball()
        
        target_y = self.ball_y - self.paddle_height/2
        self.right_paddle += (target_y - self.right_paddle) * 0.1
        self.right_paddle = max(60, min(self.right_paddle, SCREEN_HEIGHT - 30 - self.paddle_height))
    
    def reset_ball(self):
        self.ball_x = SCREEN_WIDTH//2
        self.ball_y = SCREEN_HEIGHT//2
        self.ball_dx = random.choice([-5, 5])
        self.ball_dy = random.uniform(-3, 3)
    
    def draw(self):
        screen.fill(Colors.BLACK)
        
        pygame.draw.line(screen, Colors.WHITE, (SCREEN_WIDTH//2, 60), 
                        (SCREEN_WIDTH//2, SCREEN_HEIGHT-30), 2)
        
        pygame.draw.rect(screen, Colors.WHITE, (50, self.left_paddle, self.paddle_width, self.paddle_height))
        pygame.draw.rect(screen, Colors.WHITE, (SCREEN_WIDTH-50-self.paddle_width, self.right_paddle,
                                               self.paddle_width, self.paddle_height))
        
        pygame.draw.rect(screen, Colors.YELLOW, (self.ball_x, self.ball_y, self.ball_size, self.ball_size))
        
        left_score_text = font_large.render(str(self.left_score), True, Colors.LIGHT_CYAN)
        right_score_text = font_large.render(str(self.right_score), True, Colors.LIGHT_CYAN)
        screen.blit(left_score_text, (SCREEN_WIDTH//2 - 100, 100))
        screen.blit(right_score_text, (SCREEN_WIDTH//2 + 50, 100))
        
        self.draw_hud()
        
        if self.game_over:
            self.draw_game_over()
        
        RetroEffects.draw_scanlines(screen)
    
    def handle_input(self, event):
        result = super().handle_input(event)
        if result: return result
        
        keys = pygame.key.get_pressed()
        if keys[pygame.K_w]:
            self.left_paddle -= 8
        if keys[pygame.K_s]:
            self.left_paddle += 8
        self.left_paddle = max(60, min(self.left_paddle, SCREEN_HEIGHT - 30 - self.paddle_height))

# Игра 5: Угадай число
class RetroGuessNumber(RetroGame):
    def __init__(self):
        super().__init__("GUESS NUMBER", Colors.LIGHT_MAGENTA)
        self.reset()
        
    def reset(self):
        self.secret = random.randint(1, 100)
        self.guess = ""
        self.message = "ENTER NUMBER 1-100"
        self.attempts = 0
        self.game_over = False
        self.won = False
        
    def update(self):
        pass
    
    def draw(self):
        screen.fill(Colors.BLACK)
        
        title = font_medium.render("GUESS THE NUMBER", True, self.color)
        title_rect = title.get_rect(center=(SCREEN_WIDTH//2, 150))
        screen.blit(title, title_rect)
        
        msg_text = font_medium.render(self.message, True, Colors.YELLOW)
        msg_rect = msg_text.get_rect(center=(SCREEN_WIDTH//2, 250))
        screen.blit(msg_text, msg_rect)
        
        if not self.won and not self.game_over:
            guess_text = font_large.render(self.guess, True, Colors.CYAN)
            guess_rect = guess_text.get_rect(center=(SCREEN_WIDTH//2, 350))
            screen.blit(guess_text, guess_rect)
            
            pygame.draw.rect(screen, Colors.CYAN, 
                           (guess_rect.x - 10, guess_rect.y - 10, 
                            guess_rect.width + 20, guess_rect.height + 20), 2)
        
        attempts_text = font_small.render(f"ATTEMPTS: {self.attempts}", True, Colors.LIGHT_GRAY)
        screen.blit(attempts_text, (50, 450))
        
        if self.won:
            win_text = font_large.render(f"WIN! {self.secret}", True, Colors.GREEN)
            win_rect = win_text.get_rect(center=(SCREEN_WIDTH//2, 500))
            screen.blit(win_text, win_rect)
        
        self.draw_hud()
        RetroEffects.draw_scanlines(screen)
    
    def handle_input(self, event):
        result = super().handle_input(event)
        if result: return result
        
        if event.type == pygame.KEYDOWN and not self.won and not self.game_over:
            if event.key == pygame.K_RETURN and self.guess:
                try:
                    num = int(self.guess)
                    self.attempts += 1
                    if num < self.secret:
                        self.message = "TOO LOW"
                    elif num > self.secret:
                        self.message = "TOO HIGH"
                    else:
                        self.message = f"CORRECT! {self.attempts} ATTEMPTS"
                        self.won = True
                        self.score += max(0, 1000 - self.attempts * 10)
                    self.guess = ""
                except:
                    self.message = "INVALID INPUT"
            elif event.key == pygame.K_BACKSPACE:
                self.guess = self.guess[:-1]
            elif event.unicode.isdigit():
                self.guess += event.unicode

# Игра 6: Кликер
class RetroClicker(RetroGame):
    def __init__(self):
        super().__init__("CLICKER", Colors.LIGHT_RED)
        self.reset()
        
    def reset(self):
        self.score = 0
        self.time_left = 30
        self.last_time = pygame.time.get_ticks()
        self.game_over = False
        self.targets = []
        self.spawn_timer = 0
        
    def spawn_target(self):
        self.targets.append({
            'x': random.randint(100, SCREEN_WIDTH-100),
            'y': random.randint(100, SCREEN_HEIGHT-100),
            'radius': 30,
            'life': 60
        })
    
    def update(self):
        if self.game_over:
            return
        
        current_time = pygame.time.get_ticks()
        if current_time - self.last_time >= 1000:
            self.time_left -= 1
            self.last_time = current_time
            if self.time_left <= 0:
                self.game_over = True
        
        self.spawn_timer += 1
        if self.spawn_timer >= 30:
            self.spawn_target()
            self.spawn_timer = 0
        
        for target in self.targets[:]:
            target['life'] -= 1
            if target['life'] <= 0:
                self.targets.remove(target)
    
    def draw(self):
        screen.fill(Colors.BLACK)
        
        for target in self.targets:
            alpha = int(255 * (target['life'] / 60))
            pygame.draw.circle(screen, Colors.RED, (target['x'], target['y']), target['radius'])
            pygame.draw.circle(screen, Colors.WHITE, (target['x'], target['y']), target['radius'], 2)
            pygame.draw.circle(screen, Colors.YELLOW, (target['x'], target['y']), 5)
        
        score_text = font_large.render(str(self.score), True, Colors.YELLOW)
        score_rect = score_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2))
        screen.blit(score_text, score_rect)
        
        time_text = font_medium.render(f"TIME: {self.time_left}", True, Colors.CYAN)
        screen.blit(time_text, (SCREEN_WIDTH//2 - 50, 150))
        
        self.draw_hud()
        
        if self.game_over:
            self.draw_game_over()
        
        RetroEffects.draw_scanlines(screen)
    
    def handle_input(self, event):
        result = super().handle_input(event)
        if result: return result
        
        if event.type == pygame.MOUSEBUTTONDOWN and not self.game_over:
            mouse_x, mouse_y = event.pos
            for target in self.targets[:]:
                dist = math.sqrt((mouse_x - target['x'])**2 + (mouse_y - target['y'])**2)
                if dist <= target['radius']:
                    self.targets.remove(target)
                    self.score += 10
                    break

# Игра 7: Тир
class RetroShootingGallery(RetroGame):
    def __init__(self):
        super().__init__("SHOOTING GALLERY", Colors.LIGHT_GREEN)
        self.reset()
        
    def reset(self):
        self.score = 0
        self.targets = []
        self.spawn_timer = 0
        self.game_over = False
        self.lives = 5
        self.ammo = 30
        
    def spawn_target(self):
        self.targets.append({
            'x': random.randint(50, SCREEN_WIDTH-50),
            'y': random.randint(80, SCREEN_HEIGHT-80),
            'vx': random.choice([-2, -1, 1, 2]),
            'vy': random.choice([-2, -1, 1, 2]),
            'size': random.randint(20, 40),
            'color': random.choice([Colors.RED, Colors.YELLOW, Colors.GREEN, Colors.BLUE])
        })
    
    def update(self):
        if self.game_over:
            return
        
        self.spawn_timer += 1
        if self.spawn_timer >= 45 and len(self.targets) < 8:
            self.spawn_target()
            self.spawn_timer = 0
        
        for target in self.targets[:]:
            target['x'] += target['vx']
            target['y'] += target['vy']
            
            if target['x'] <= 0 or target['x'] >= SCREEN_WIDTH:
                target['vx'] *= -1
            if target['y'] <= 60 or target['y'] >= SCREEN_HEIGHT-30:
                target['vy'] *= -1
    
    def draw(self):
        screen.fill(Colors.BLACK)
        
        for target in self.targets:
            pygame.draw.rect(screen, target['color'], 
                           (target['x'] - target['size']//2, target['y'] - target['size']//2,
                            target['size'], target['size']))
            pygame.draw.circle(screen, Colors.WHITE, (target['x'], target['y']), target['size']//3)
            pygame.draw.circle(screen, Colors.RED, (target['x'], target['y']), target['size']//6)
        
        ammo_text = font_small.render(f"AMMO: {self.ammo}", True, Colors.YELLOW)
        screen.blit(ammo_text, (50, 650))
        
        lives_text = font_small.render(f"LIVES: {self.lives}", True, Colors.RED)
        screen.blit(lives_text, (200, 650))
        
        self.draw_hud()
        
        if self.game_over:
            self.draw_game_over()
        
        RetroEffects.draw_scanlines(screen)
    
    def handle_input(self, event):
        result = super().handle_input(event)
        if result: return result
        
        if event.type == pygame.MOUSEBUTTONDOWN and not self.game_over:
            if self.ammo <= 0:
                return
            self.ammo -= 1
            mouse_x, mouse_y = event.pos
            hit = False
            for target in self.targets[:]:
                if (abs(mouse_x - target['x']) <= target['size']//2 and
                    abs(mouse_y - target['y']) <= target['size']//2):
                    self.targets.remove(target)
                    self.score += 50
                    hit = True
                    break
            if not hit:
                self.lives -= 1
                if self.lives <= 0:
                    self.game_over = True

# Игра 8: Гонки
class RetroRacing(RetroGame):
    def __init__(self):
        super().__init__("RACING", Colors.LIGHT_RED)
        self.reset()
        
    def reset(self):
        self.car_x = SCREEN_WIDTH//2 - 20
        self.car_y = SCREEN_HEIGHT - 120
        self.car_width = 40
        self.car_height = 60
        
        self.obstacles = []
        self.spawn_timer = 0
        self.speed = 5
        self.score = 0
        self.game_over = False
        self.road_offset = 0
        
    def spawn_obstacle(self):
        x = random.randint(100, SCREEN_WIDTH - 100)
        self.obstacles.append({
            'rect': pygame.Rect(x, -50, 30, 50),
            'color': random.choice([Colors.RED, Colors.BLUE, Colors.YELLOW])
        })
    
    def update(self):
        if self.game_over:
            return
        
        self.spawn_timer += 1
        if self.spawn_timer >= 40:
            self.spawn_obstacle()
            self.spawn_timer = 0
        
        self.road_offset = (self.road_offset + self.speed) % 40
        
        for obstacle in self.obstacles[:]:
            obstacle['rect'].y += self.speed
            if obstacle['rect'].y > SCREEN_HEIGHT:
                self.obstacles.remove(obstacle)
                self.score += 10
        
        car_rect = pygame.Rect(self.car_x, self.car_y, self.car_width, self.car_height)
        for obstacle in self.obstacles:
            if car_rect.colliderect(obstacle['rect']):
                self.game_over = True
    
    def draw(self):
        screen.fill(Colors.BLACK)
        
        for i in range(0, SCREEN_WIDTH, 40):
            pygame.draw.line(screen, Colors.DARK_GRAY, (i, 60), (i, SCREEN_HEIGHT-30), 1)
        
        for i in range(0, SCREEN_HEIGHT-90, 40):
            y = i + self.road_offset + 60
            if y < SCREEN_HEIGHT-30:
                pygame.draw.line(screen, Colors.WHITE, (SCREEN_WIDTH//2 - 100, y),
                               (SCREEN_WIDTH//2 - 50, y), 2)
                pygame.draw.line(screen, Colors.WHITE, (SCREEN_WIDTH//2 + 50, y),
                               (SCREEN_WIDTH//2 + 100, y), 2)
        
        pygame.draw.rect(screen, Colors.LIGHT_BLUE, 
                        (self.car_x, self.car_y, self.car_width, self.car_height))
        pygame.draw.rect(screen, Colors.WHITE, 
                        (self.car_x + 5, self.car_y + 5, 10, 10))
        pygame.draw.rect(screen, Colors.WHITE, 
                        (self.car_x + 25, self.car_y + 5, 10, 10))
        
        for obstacle in self.obstacles:
            pygame.draw.rect(screen, obstacle['color'], obstacle['rect'])
        
        self.draw_hud()
        
        if self.game_over:
            self.draw_game_over()
        
        RetroEffects.draw_scanlines(screen)
    
    def handle_input(self, event):
        result = super().handle_input(event)
        if result: return result
        
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and self.car_x > 50:
            self.car_x -= 7
        if keys[pygame.K_RIGHT] and self.car_x < SCREEN_WIDTH - 50 - self.car_width:
            self.car_x += 7
        if keys[pygame.K_UP]:
            self.speed = min(self.speed + 0.1, 8)
        if keys[pygame.K_DOWN]:
            self.speed = max(self.speed - 0.1, 3)

# Игра 9: Тетрис
class RetroTetris(RetroGame):
    def __init__(self):
        super().__init__("TETRIS", Colors.LIGHT_CYAN)
        self.cell_size = 30
        self.grid_width = 10
        self.grid_height = 20
        self.grid_x = (SCREEN_WIDTH - self.cell_size * self.grid_width) // 2
        self.grid_y = 80
        
        self.shapes = [
            [[1,1,1,1]],  # I
            [[1,1],[1,1]],  # O
            [[0,1,0],[1,1,1]],  # T
            [[1,0,0],[1,1,1]],  # L
            [[0,0,1],[1,1,1]],  # J
            [[0,1,1],[1,1,0]],  # S
            [[1,1,0],[0,1,1]]   # Z
        ]
        self.colors = [Colors.CYAN, Colors.YELLOW, Colors.MAGENTA, 
                      Colors.GREEN, Colors.RED, Colors.BLUE, Colors.LIGHT_RED]
        self.reset()
    
    def reset(self):
        self.grid = [[0 for _ in range(self.grid_width)] for _ in range(self.grid_height)]
        self.current_piece = self.new_piece()
        self.next_piece = self.new_piece()
        self.score = 0
        self.game_over = False
        self.fall_time = 0
        self.fall_speed = 500
    
    def new_piece(self):
        shape_idx = random.randint(0, len(self.shapes)-1)
        return {
            'shape': [row[:] for row in self.shapes[shape_idx]],
            'x': self.grid_width//2 - len(self.shapes[shape_idx][0])//2,
            'y': 0,
            'color': self.colors[shape_idx]
        }
    
    def rotate_piece(self, piece):
        return [list(row) for row in zip(*piece['shape'][::-1])]
    
    def check_collision(self, piece, dx=0, dy=0):
        for y, row in enumerate(piece['shape']):
            for x, cell in enumerate(row):
                if cell:
                    new_x = piece['x'] + x + dx
                    new_y = piece['y'] + y + dy
                    if (new_x < 0 or new_x >= self.grid_width or
                        new_y >= self.grid_height or
                        (new_y >= 0 and self.grid[new_y][new_x])):
                        return True
        return False
    
    def merge_piece(self):
        for y, row in enumerate(self.current_piece['shape']):
            for x, cell in enumerate(row):
                if cell:
                    grid_y = self.current_piece['y'] + y
                    grid_x = self.current_piece['x'] + x
                    if 0 <= grid_y < self.grid_height:
                        self.grid[grid_y][grid_x] = self.current_piece['color']
        
        lines_cleared = 0
        y = self.grid_height - 1
        while y >= 0:
            if all(self.grid[y]):
                del self.grid[y]
                self.grid.insert(0, [0 for _ in range(self.grid_width)])
                lines_cleared += 1
            else:
                y -= 1
        
        self.score += lines_cleared * 100 * lines_cleared
        
        self.current_piece = self.next_piece
        self.next_piece = self.new_piece()
        
        if self.check_collision(self.current_piece):
            self.game_over = True
    
    def update(self):
        if self.game_over:
            return
        
        current_time = pygame.time.get_ticks()
        if current_time - self.fall_time > self.fall_speed:
            if not self.check_collision(self.current_piece, dy=1):
                self.current_piece['y'] += 1
            else:
                self.merge_piece()
            self.fall_time = current_time
    
    def draw(self):
        screen.fill(Colors.BLACK)
        
        for y in range(self.grid_height):
            for x in range(self.grid_width):
                rect = pygame.Rect(self.grid_x + x*self.cell_size,
                                 self.grid_y + y*self.cell_size,
                                 self.cell_size-2, self.cell_size-2)
                if self.grid[y][x]:
                    pygame.draw.rect(screen, self.grid[y][x], rect)
                pygame.draw.rect(screen, Colors.DARK_GRAY, rect, 1)
        
        if self.current_piece:
            for y, row in enumerate(self.current_piece['shape']):
                for x, cell in enumerate(row):
                    if cell:
                        rect = pygame.Rect(self.grid_x + (self.current_piece['x'] + x)*self.cell_size,
                                         self.grid_y + (self.current_piece['y'] + y)*self.cell_size,
                                         self.cell_size-2, self.cell_size-2)
                        pygame.draw.rect(screen, self.current_piece['color'], rect)
        
        next_text = font_small.render("NEXT", True, Colors.WHITE)
        screen.blit(next_text, (self.grid_x + self.grid_width*self.cell_size + 30, 150))
        
        if self.next_piece:
            for y, row in enumerate(self.next_piece['shape']):
                for x, cell in enumerate(row):
                    if cell:
                        rect = pygame.Rect(self.grid_x + self.grid_width*self.cell_size + 30 + x*30,
                                         200 + y*30, 28, 28)
                        pygame.draw.rect(screen, self.next_piece['color'], rect)
        
        self.draw_hud()
        
        if self.game_over:
            self.draw_game_over()
        
        RetroEffects.draw_scanlines(screen)
    
    def handle_input(self, event):
        result = super().handle_input(event)
        if result: return result
        
        if event.type == pygame.KEYDOWN and not self.game_over:
            if event.key == pygame.K_LEFT:
                if not self.check_collision(self.current_piece, dx=-1):
                    self.current_piece['x'] -= 1
            elif event.key == pygame.K_RIGHT:
                if not self.check_collision(self.current_piece, dx=1):
                    self.current_piece['x'] += 1
            elif event.key == pygame.K_UP:
                rotated = self.rotate_piece(self.current_piece)
                old_shape = self.current_piece['shape']
                self.current_piece['shape'] = rotated
                if self.check_collision(self.current_piece):
                    self.current_piece['shape'] = old_shape
            elif event.key == pygame.K_DOWN:
                if not self.check_collision(self.current_piece, dy=1):
                    self.current_piece['y'] += 1

# Игра 10: Флоппи Берд
class RetroFlappyBird(RetroGame):
    def __init__(self):
        super().__init__("FLAPPY BIRD", Colors.YELLOW)
        self.reset()
        
    def reset(self):
        self.bird_x = 200
        self.bird_y = SCREEN_HEIGHT//2
        self.bird_radius = 15
        self.bird_vy = 0
        self.gravity = 0.5
        self.jump = -10
        
        self.pipes = []
        self.pipe_width = 60
        self.pipe_gap = 200
        self.pipe_speed = 4
        self.spawn_timer = 0
        
        self.score = 0
        self.game_over = False
        
    def spawn_pipe(self):
        gap_y = random.randint(150, SCREEN_HEIGHT - 150 - self.pipe_gap)
        self.pipes.append({
            'x': SCREEN_WIDTH,
            'gap_y': gap_y,
            'passed': False
        })
    
    def update(self):
        if self.game_over:
            return
        
        self.bird_vy += self.gravity
        self.bird_y += self.bird_vy
        
        if self.bird_y <= 60 or self.bird_y >= SCREEN_HEIGHT - 30:
            self.game_over = True
        
        self.spawn_timer += 1
        if self.spawn_timer >= 90:
            self.spawn_pipe()
            self.spawn_timer = 0
        
        bird_rect = pygame.Rect(self.bird_x - self.bird_radius,
                               self.bird_y - self.bird_radius,
                               self.bird_radius*2, self.bird_radius*2)
        
        for pipe in self.pipes[:]:
            pipe['x'] -= self.pipe_speed
            
            top_pipe = pygame.Rect(pipe['x'], 60, self.pipe_width, pipe['gap_y'] - 60)
            bottom_pipe = pygame.Rect(pipe['x'], pipe['gap_y'] + self.pipe_gap,
                                     self.pipe_width, SCREEN_HEIGHT - pipe['gap_y'] - self.pipe_gap - 30)
            
            if bird_rect.colliderect(top_pipe) or bird_rect.colliderect(bottom_pipe):
                self.game_over = True
            
            if not pipe['passed'] and pipe['x'] + self.pipe_width < self.bird_x:
                pipe['passed'] = True
                self.score += 10
            
            if pipe['x'] + self.pipe_width < 0:
                self.pipes.remove(pipe)
    
    def draw(self):
        screen.fill(Colors.BLACK)
        
        for pipe in self.pipes:
            pygame.draw.rect(screen, Colors.GREEN, (pipe['x'], 60, self.pipe_width, pipe['gap_y'] - 60))
            pygame.draw.rect(screen, Colors.LIGHT_GREEN, (pipe['x'], pipe['gap_y'] - 30, self.pipe_width, 30))
            
            pygame.draw.rect(screen, Colors.GREEN, 
                           (pipe['x'], pipe['gap_y'] + self.pipe_gap,
                            self.pipe_width, SCREEN_HEIGHT - pipe['gap_y'] - self.pipe_gap - 30))
            pygame.draw.rect(screen, Colors.LIGHT_GREEN,
                           (pipe['x'], pipe['gap_y'] + self.pipe_gap,
                            self.pipe_width, 30))
        
        pygame.draw.circle(screen, Colors.YELLOW, (self.bird_x, int(self.bird_y)), self.bird_radius)
        pygame.draw.circle(screen, Colors.BLACK, (self.bird_x + 5, int(self.bird_y) - 5), 3)
        
        if (pygame.time.get_ticks() // 200) % 2:
            pygame.draw.ellipse(screen, Colors.YELLOW, 
                              (self.bird_x - 20, self.bird_y - 5, 15, 10))
        
        self.draw_hud()
        
        if self.game_over:
            self.draw_game_over()
        
        RetroEffects.draw_scanlines(screen)
    
    def handle_input(self, event):
        result = super().handle_input(event)
        if result: return result
        
        if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE and not self.game_over:
            self.bird_vy = self.jump

# Игра 11: Крестики-нолики
class RetroTicTacToe(RetroGame):
    def __init__(self):
        super().__init__("TIC TAC TOE", Colors.LIGHT_MAGENTA)
        self.cell_size = 150
        self.board_x = (SCREEN_WIDTH - self.cell_size * 3) // 2
        self.board_y = 150
        self.reset()
        
    def reset(self):
        self.board = [['' for _ in range(3)] for _ in range(3)]
        self.current_player = 'X'
        self.game_over = False
        self.winner = None
        self.score = 0
        
    def check_winner(self):
        for row in self.board:
            if row[0] == row[1] == row[2] != '':
                return row[0]
        
        for col in range(3):
            if self.board[0][col] == self.board[1][col] == self.board[2][col] != '':
                return self.board[0][col]
        
        if self.board[0][0] == self.board[1][1] == self.board[2][2] != '':
            return self.board[0][0]
        if self.board[0][2] == self.board[1][1] == self.board[2][0] != '':
            return self.board[0][2]
        
        if all(self.board[r][c] != '' for r in range(3) for c in range(3)):
            return 'draw'
        
        return None
    
    def update(self):
        winner = self.check_winner()
        if winner:
            self.game_over = True
            self.winner = winner
            if winner == 'X':
                self.score += 100
            elif winner == 'O':
                self.score += 50
    
    def draw(self):
        screen.fill(Colors.BLACK)
        
        for i in range(1, 3):
            x = self.board_x + i * self.cell_size
            pygame.draw.line(screen, Colors.WHITE, (x, self.board_y), 
                           (x, self.board_y + self.cell_size * 3), 3)
            y = self.board_y + i * self.cell_size
            pygame.draw.line(screen, Colors.WHITE, (self.board_x, y), 
                           (self.board_x + self.cell_size * 3, y), 3)
        
        for row in range(3):
            for col in range(3):
                x = self.board_x + col * self.cell_size + self.cell_size//2
                y = self.board_y + row * self.cell_size + self.cell_size//2
                
                if self.board[row][col] == 'X':
                    pygame.draw.line(screen, Colors.RED, (x - 40, y - 40), (x + 40, y + 40), 5)
                    pygame.draw.line(screen, Colors.RED, (x + 40, y - 40), (x - 40, y + 40), 5)
                elif self.board[row][col] == 'O':
                    pygame.draw.circle(screen, Colors.BLUE, (x, y), 50, 5)
        
        if not self.game_over:
            player_text = font_medium.render(f"PLAYER {self.current_player}", True, self.color)
            player_rect = player_text.get_rect(center=(SCREEN_WIDTH//2, 600))
            screen.blit(player_text, player_rect)
        else:
            if self.winner == 'draw':
                result_text = font_large.render("DRAW!", True, Colors.YELLOW)
            else:
                result_text = font_large.render(f"{self.winner} WINS!", True, Colors.GREEN)
            result_rect = result_text.get_rect(center=(SCREEN_WIDTH//2, 600))
            screen.blit(result_text, result_rect)
        
        self.draw_hud()
        
        if self.game_over:
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            overlay.set_alpha(128)
            overlay.fill(Colors.BLACK)
            screen.blit(overlay, (0, 0))
        
        RetroEffects.draw_scanlines(screen)
    
    def handle_input(self, event):
        result = super().handle_input(event)
        if result: return result
        
        if event.type == pygame.MOUSEBUTTONDOWN and not self.game_over:
            mouse_x, mouse_y = event.pos
            if (self.board_x <= mouse_x <= self.board_x + self.cell_size * 3 and
                self.board_y <= mouse_y <= self.board_y + self.cell_size * 3):
                col = (mouse_x - self.board_x) // self.cell_size
                row = (mouse_y - self.board_y) // self.cell_size
                if 0 <= row < 3 and 0 <= col < 3 and self.board[row][col] == '':
                    self.board[row][col] = self.current_player
                    self.current_player = 'O' if self.current_player == 'X' else 'X'

# Ретро-меню с космическим фоном
class RetroMenu:
    def __init__(self):
        self.games = [
            ("01  SNAKE", Colors.GREEN, RetroSnake),
            ("02  ARKANOID", Colors.LIGHT_BLUE, RetroArkanoid),
            ("03  MAZE", Colors.YELLOW, RetroMaze),
            ("04  PONG", Colors.LIGHT_CYAN, RetroPong),
            ("05  GUESS NUMBER", Colors.LIGHT_MAGENTA, RetroGuessNumber),
            ("06  CLICKER", Colors.LIGHT_RED, RetroClicker),
            ("07  SHOOTING GALLERY", Colors.LIGHT_GREEN, RetroShootingGallery),
            ("08  RACING", Colors.LIGHT_RED, RetroRacing),
            ("09  TETRIS", Colors.LIGHT_CYAN, RetroTetris),
            ("10  FLAPPY BIRD", Colors.YELLOW, RetroFlappyBird),
            ("11  TIC TAC TOE", Colors.LIGHT_MAGENTA, RetroTicTacToe),
            ("12  EXIT", Colors.RED, None)
        ]
        self.selected = 0
        self.space_bg = SpaceBackground()
        
    def draw(self):
        self.space_bg.draw(screen)
        
        pygame.draw.rect(screen, Colors.YELLOW, (20, 20, SCREEN_WIDTH-40, SCREEN_HEIGHT-40), 3)
        pygame.draw.rect(screen, Colors.LIGHT_GRAY, (25, 25, SCREEN_WIDTH-50, SCREEN_HEIGHT-50), 1)
        
        title_shadow = font_large.render("ARCADE 80's", True, Colors.DARK_GRAY)
        title = font_large.render("ARCADE 80's", True, Colors.YELLOW)
        title_rect = title.get_rect(center=(SCREEN_WIDTH//2, 70))
        screen.blit(title_shadow, (title_rect.x + 3, title_rect.y + 3))
        screen.blit(title, title_rect)
        
        start_y = 150
        for i, (game_name, color, _) in enumerate(self.games):
            y = start_y + i * 40
            
            if i == self.selected:
                pulse = int(50 * math.sin(pygame.time.get_ticks() / 200))
                glow_color = (
                    max(0, min(255, color[0] + pulse)),
                    max(0, min(255, color[1] + pulse)),
                    max(0, min(255, color[2] + pulse))
                )
                pygame.draw.rect(screen, glow_color, (200, y-10, SCREEN_WIDTH-400, 35), 3)
                pygame.draw.polygon(screen, Colors.YELLOW, 
                                   [(180, y), (160, y-5), (160, y+5)])
            
            num_text = font_medium.render(f"{i+1:02d}", True, Colors.LIGHT_GRAY)
            screen.blit(num_text, (250, y))
            name_text = font_medium.render(game_name, True, color)
            screen.blit(name_text, (350, y))
        
        inst_y = SCREEN_HEIGHT - 80
        pygame.draw.rect(screen, Colors.BLUE, (50, inst_y-10, SCREEN_WIDTH-100, 40))
        pygame.draw.rect(screen, Colors.WHITE, (50, inst_y-10, SCREEN_WIDTH-100, 40), 2)
        
        inst1 = font_small.render("UP/DOWN SELECT", True, Colors.WHITE)
        inst2 = font_small.render("ENTER START", True, Colors.WHITE)
        inst3 = font_small.render("ESC QUIT", True, Colors.WHITE)
        
        screen.blit(inst1, (150, inst_y))
        screen.blit(inst2, (400, inst_y))
        screen.blit(inst3, (650, inst_y))
        
        RetroEffects.draw_scanlines(screen)
        RetroEffects.draw_crt_corner(screen)
    
    def handle_input(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                self.selected = (self.selected - 1) % len(self.games)
            elif event.key == pygame.K_DOWN:
                self.selected = (self.selected + 1) % len(self.games)
            elif event.key == pygame.K_RETURN:
                return self.selected
        return None

# Основной класс приложения
class RetroArcade:
    def __init__(self):
        self.menu = RetroMenu()
        self.current_game = None
        self.running = True
        
    def run(self):
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                
                if self.current_game:
                    result = self.current_game.handle_input(event)
                    if result == "menu":
                        self.current_game = None
                else:
                    result = self.menu.handle_input(event)
                    if result is not None:
                        if result == 11:  # Exit
                            self.running = False
                        else:
                            game_class = self.menu.games[result][2]
                            if game_class:
                                self.current_game = game_class()
            
            if self.current_game:
                self.current_game.update()
                self.current_game.draw()
            else:
                self.menu.draw()
            
            pygame.display.flip()
            clock.tick(60)
        
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    game = RetroArcade()
    game.run()