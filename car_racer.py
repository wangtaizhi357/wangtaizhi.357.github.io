import pygame
import random
import sys
import numpy as np

pygame.init()
pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)

WIDTH = 800
HEIGHT = 600
FPS = 60

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
GRAY = (128, 128, 128)
ORANGE = (255, 165, 0)
BROWN = (139, 69, 19)

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("汽车跑酷游戏")
clock = pygame.time.Clock()
font = pygame.font.Font(None, 36)
large_font = pygame.font.Font(None, 72)

def generate_tone(frequency, duration, volume=0.3):
    sample_rate = 44100
    n_samples = int(sample_rate * duration)
    t = np.linspace(0, duration, n_samples, False)
    wave = np.sin(2 * np.pi * frequency * t) * volume
    wave = (wave * 32767).astype(np.int16)
    stereo_wave = np.column_stack((wave, wave))
    return pygame.sndarray.make_sound(stereo_wave)

def generate_arcade_music():
    notes = [
        (262, 0.15), (330, 0.15), (392, 0.15), (523, 0.15),
        (392, 0.15), (330, 0.15), (262, 0.15), (330, 0.15),
        (392, 0.15), (523, 0.15), (392, 0.15), (330, 0.15),
        (262, 0.30), (294, 0.15), (330, 0.15), (262, 0.30),
        (523, 0.15), (587, 0.15), (659, 0.15), (523, 0.15),
        (392, 0.15), (440, 0.15), (494, 0.15), (392, 0.15),
        (330, 0.15), (294, 0.15), (262, 0.15), (330, 0.15),
        (392, 0.15), (440, 0.15), (523, 0.15), (587, 0.15),
        (659, 0.15), (523, 0.15), (392, 0.15), (262, 0.15),
    ]
    
    sounds = []
    for freq, dur in notes:
        sounds.append(generate_tone(freq, dur))
    
    return sounds

arcade_sounds = generate_arcade_music()
current_note = 0
note_timer = 0
note_duration = 10

class Car:
    def __init__(self):
        self.width = 50
        self.height = 80
        self.x = WIDTH // 2 - self.width // 2
        self.y = HEIGHT - 150
        self.speed = 5
        self.base_speed = 5
        self.max_speed = 10
        self.min_speed = 2
        self.color = BLUE

    def move(self, keys):
        if keys[pygame.K_LEFT] and self.x > 50:
            self.x -= self.speed
        if keys[pygame.K_RIGHT] and self.x < WIDTH - 50 - self.width:
            self.x += self.speed
        if keys[pygame.K_UP]:
            self.speed = min(self.max_speed, self.speed + 0.2)
        if keys[pygame.K_DOWN]:
            self.speed = max(self.min_speed, self.speed - 0.2)

    def draw(self):
        body_color = RED
        tire_color = BLACK
        cockpit_color = YELLOW

        pygame.draw.rect(screen, body_color, (self.x + 10, self.y + 15, 30, 50))
        pygame.draw.rect(screen, BLACK, (self.x + 10, self.y + 15, 30, 50), 2)

        nose_points = [(self.x + 25, self.y), (self.x + 5, self.y + 12), (self.x + 45, self.y + 12)]
        pygame.draw.polygon(screen, body_color, nose_points)
        pygame.draw.polygon(screen, BLACK, nose_points, 2)

        pygame.draw.rect(screen, body_color, (self.x + 8, self.y + 62, 34, 10))
        pygame.draw.rect(screen, BLACK, (self.x + 8, self.y + 62, 34, 10), 2)

        pygame.draw.ellipse(screen, cockpit_color, (self.x + 15, self.y + 25, 20, 15))
        pygame.draw.ellipse(screen, BLACK, (self.x + 15, self.y + 25, 20, 15), 2)

        pygame.draw.circle(screen, tire_color, (self.x + 5, self.y + 10), 8)
        pygame.draw.circle(screen, tire_color, (self.x + 45, self.y + 10), 8)
        pygame.draw.circle(screen, tire_color, (self.x + 5, self.y + 65), 8)
        pygame.draw.circle(screen, tire_color, (self.x + 45, self.y + 65), 8)

        pygame.draw.circle(screen, GRAY, (self.x + 5, self.y + 10), 4)
        pygame.draw.circle(screen, GRAY, (self.x + 45, self.y + 10), 4)
        pygame.draw.circle(screen, GRAY, (self.x + 5, self.y + 65), 4)
        pygame.draw.circle(screen, GRAY, (self.x + 45, self.y + 65), 4)

    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)

class Obstacle:
    def __init__(self, obstacle_type):
        self.obstacle_type = obstacle_type
        self.width = 40
        self.height = 40
        self.x = random.randint(50, WIDTH - 90)
        self.y = -50
        self.speed = 3

        if obstacle_type == "pedestrian":
            self.color = ORANGE
            self.width = 30
            self.height = 50
        elif obstacle_type == "animal":
            self.color = BROWN
            self.width = 35
            self.height = 35
        elif obstacle_type == "barrier":
            self.color = RED
            self.width = 50
            self.height = 30

    def update(self, game_speed):
        self.y += self.speed + game_speed

    def draw(self):
        if self.obstacle_type == "pedestrian":
            pygame.draw.circle(screen, self.color, (self.x + 15, self.y + 10), 10)
            pygame.draw.rect(screen, self.color, (self.x + 5, self.y + 20, 20, 30))
        elif self.obstacle_type == "animal":
            pygame.draw.ellipse(screen, self.color, (self.x, self.y, self.width, self.height))
            pygame.draw.circle(screen, BLACK, (self.x + 10, self.y + 10), 3)
            pygame.draw.circle(screen, BLACK, (self.x + 25, self.y + 10), 3)
        elif self.obstacle_type == "barrier":
            pygame.draw.rect(screen, self.color, (self.x, self.y, self.width, self.height))
            pygame.draw.rect(screen, WHITE, (self.x + 5, self.y + 5, self.width - 10, 5))
            pygame.draw.rect(screen, WHITE, (self.x + 5, self.y + 20, self.width - 10, 5))

    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)

class Game:
    def __init__(self):
        self.car = Car()
        self.obstacles = []
        self.score = 0
        self.game_over = False
        self.game_speed = 0
        self.spawn_timer = 0
        self.spawn_delay = 60

    def spawn_obstacle(self):
        self.spawn_timer += 1
        if self.spawn_timer >= self.spawn_delay:
            obstacle_types = ["pedestrian", "animal", "barrier"]
            obstacle_type = random.choice(obstacle_types)
            self.obstacles.append(Obstacle(obstacle_type))
            self.spawn_timer = 0
            self.spawn_delay = max(30, 60 - self.score // 100)

    def update(self):
        global current_note, note_timer
        
        if self.game_over:
            return

        keys = pygame.key.get_pressed()
        self.car.move(keys)
        self.game_speed = self.car.speed - self.car.base_speed

        self.spawn_obstacle()

        for obstacle in self.obstacles[:]:
            obstacle.update(self.game_speed)
            if obstacle.y > HEIGHT:
                self.obstacles.remove(obstacle)
                self.score += 10

        if self.check_collision():
            self.game_over = True

        note_timer += 1
        if note_timer >= note_duration:
            arcade_sounds[current_note].play()
            current_note = (current_note + 1) % len(arcade_sounds)
            note_timer = 0

    def check_collision(self):
        car_rect = self.car.get_rect()
        for obstacle in self.obstacles:
            if car_rect.colliderect(obstacle.get_rect()):
                return True
        return False

    def draw(self):
        screen.fill(GRAY)

        pygame.draw.rect(screen, GREEN, (0, 0, 50, HEIGHT))
        pygame.draw.rect(screen, GREEN, (WIDTH - 50, 0, 50, HEIGHT))

        for i in range(0, HEIGHT, 40):
            pygame.draw.line(screen, WHITE, (WIDTH // 2, i), (WIDTH // 2, i + 20), 3)

        self.car.draw()

        for obstacle in self.obstacles:
            obstacle.draw()

        score_text = font.render(f"分数: {self.score}", True, WHITE)
        speed_text = font.render(f"速度: {self.car.speed:.1f}", True, WHITE)
        screen.blit(score_text, (10, 10))
        screen.blit(speed_text, (10, 50))

        if self.game_over:
            overlay = pygame.Surface((WIDTH, HEIGHT))
            overlay.set_alpha(128)
            overlay.fill(BLACK)
            screen.blit(overlay, (0, 0))

            game_over_text = large_font.render("游戏结束!", True, RED)
            final_score_text = font.render(f"最终分数: {self.score}", True, WHITE)
            restart_text = font.render("按 R 键重新开始", True, WHITE)

            screen.blit(game_over_text, (WIDTH // 2 - game_over_text.get_width() // 2, HEIGHT // 2 - 100))
            screen.blit(final_score_text, (WIDTH // 2 - final_score_text.get_width() // 2, HEIGHT // 2))
            screen.blit(restart_text, (WIDTH // 2 - restart_text.get_width() // 2, HEIGHT // 2 + 60))

        pygame.display.flip()

    def reset(self):
        self.car = Car()
        self.obstacles = []
        self.score = 0
        self.game_over = False
        self.game_speed = 0
        self.spawn_timer = 0
        self.spawn_delay = 60

def main():
    game = Game()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r and game.game_over:
                    game.reset()

        game.update()
        game.draw()
        clock.tick(FPS)

if __name__ == "__main__":
    main()
