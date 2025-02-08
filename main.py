import pygame
import random
import json

# Constants
SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 700
CAR_WIDTH = 80
CAR_HEIGHT = 160
ROAD_WIDTH = 600
FPS = 60
WHITE = (255, 255, 255)
CYBERPUNK_BLUE = (0, 255, 255)
CYBERPUNK_PINK = (255, 0, 255)
CYBERPUNK_GREEN = (0, 255, 0)
FONT_NAME = "arial"

# Initialize Pygame
pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Titans Of Track")
clock = pygame.time.Clock()

# Load assets
car_images = {
    "car1": pygame.transform.scale(pygame.image.load("images/car1.png"), (CAR_WIDTH, CAR_HEIGHT)),
    "car2": pygame.transform.scale(pygame.image.load("images/car2.png"), (CAR_WIDTH, CAR_HEIGHT)),
    "car3": pygame.transform.scale(pygame.image.load("images/car3.png"), (CAR_WIDTH, CAR_HEIGHT)),
}
road_image = pygame.transform.scale(pygame.image.load("images/cyberpunk_road.jpg"), (ROAD_WIDTH, SCREEN_HEIGHT))
coin_image = pygame.transform.scale(pygame.image.load("images/coin.png"), (30, 30))
hurdle_image = pygame.transform.scale(pygame.image.load("images/hurdle.png"), (60, 60))
heart_image = pygame.transform.scale(pygame.image.load("images/heart.png"), (40, 40))
jump_sound = pygame.mixer.Sound("sounds/jump.wav")
coin_sound = pygame.mixer.Sound("sounds/coin.wav")
crash_sound = pygame.mixer.Sound("sounds/crash.wav")
success_sound = pygame.mixer.Sound("sounds/success.wav")
life_sound = pygame.mixer.Sound("sounds/life.wav")

class Car:
    def __init__(self, car_type):
        self.x = SCREEN_WIDTH // 2 - CAR_WIDTH // 2
        self.y = SCREEN_HEIGHT - CAR_HEIGHT - 10
        self.speed_x = 0
        self.speed_y = 0
        self.image = car_images[car_type]
        self.is_jumping = False
        self.jump_velocity = 15
        self.gravity = 0.8

    def move_left(self):
        if self.x > SCREEN_WIDTH // 4 - CAR_WIDTH:
            self.speed_x = -5

    def move_right(self):
        if self.x < SCREEN_WIDTH // 2 + ROAD_WIDTH // 2 - CAR_WIDTH:
            self.speed_x = 5

    def stop_x(self):
        self.speed_x = 0

    def jump(self):
        if not self.is_jumping:
            self.is_jumping = True
            self.jump_velocity = 15
            jump_sound.play()

    def update_position(self):
        self.x += self.speed_x
        self.y += self.speed_y

        if self.is_jumping:
            self.y -= self.jump_velocity
            self.jump_velocity -= self.gravity
            if self.jump_velocity < -15:
                self.is_jumping = False
                self.jump_velocity = 15

    def draw(self):
        screen.blit(self.image, (self.x, self.y))

class Road:
    def __init__(self):
        self.y = 0
        self.speed = 5
        self.image = road_image

    def move(self):
        self.y += self.speed
        if self.y > SCREEN_HEIGHT:
            self.y = 0

    def draw(self):
        screen.blit(self.image, (SCREEN_WIDTH // 4, self.y))
        screen.blit(self.image, (SCREEN_WIDTH // 4, self.y - SCREEN_HEIGHT))

class CoinManager:
    def __init__(self):
        self.coins = []
        self.speed = 5

    def create_coin(self):
        if random.randint(1, 100) < 5:
            x = random.randint(SCREEN_WIDTH // 4, SCREEN_WIDTH // 4 + ROAD_WIDTH - 30)
            y = -30
            self.coins.append(pygame.Rect(x, y, 30, 30))

    def move_coins(self):
        for coin in self.coins:
            coin.y += self.speed
            if coin.y > SCREEN_HEIGHT:
                self.coins.remove(coin)

    def draw_coins(self):
        for coin in self.coins:
            screen.blit(coin_image, coin)

class HurdleManager:
    def __init__(self):
        self.hurdles = []
        self.speed = 5

    def create_hurdle(self):
        if random.randint(1, 100) < 3:
            x = random.randint(SCREEN_WIDTH // 4, SCREEN_WIDTH // 4 + ROAD_WIDTH - 60)
            y = -60
            self.hurdles.append(pygame.Rect(x, y, 60, 60))

    def move_hurdles(self):
        for hurdle in self.hurdles:
            hurdle.y += self.speed
            if hurdle.y > SCREEN_HEIGHT:
                self.hurdles.remove(hurdle)

    def draw_hurdles(self):
        for hurdle in self.hurdles:
            screen.blit(hurdle_image, hurdle)

class HeartManager:
    def __init__(self):
        self.hearts = []
        self.speed = 5
        self.spawn_delay = random.randint(500, 1000)

    def create_heart(self):
        if random.randint(1, 1000) < 2:
            x = random.randint(SCREEN_WIDTH // 4, SCREEN_WIDTH // 4 + ROAD_WIDTH - 40)
            y = -40
            self.hearts.append(pygame.Rect(x, y, 40, 40))

    def move_hearts(self):
        for heart in self.hearts:
            heart.y += self.speed
            if heart.y > SCREEN_HEIGHT:
                self.hearts.remove(heart)

    def draw_hearts(self):
        for heart in self.hearts:
            screen.blit(heart_image, heart)

class Game:
    def __init__(self):
        self.car = None
        self.road = Road()
        self.coin_manager = CoinManager()
        self.hurdle_manager = HurdleManager()
        self.heart_manager = HeartManager()
        self.score = 0
        self.lives = 3
        self.high_scores = self.load_high_scores()
        self.username = ""
        self.game_over = False
        self.paused = False

    def load_high_scores(self):
        try:
            with open("high_scores.json", "r") as file:
                return json.load(file)
        except FileNotFoundError:
            return []

    def save_high_scores(self):
        with open("high_scores.json", "w") as file:
            json.dump(self.high_scores[:10], file)

    def show_start_screen(self):
        screen.fill((0, 0, 0))
        font = pygame.font.SysFont(FONT_NAME, 74)
        title_text = font.render("Titans Of Track", True, CYBERPUNK_BLUE)
        screen.blit(title_text, (SCREEN_WIDTH // 2 - 250, SCREEN_HEIGHT // 2 - 150))

        font = pygame.font.SysFont(FONT_NAME, 36)
        start_text = font.render("Press SPACE to Start", True, CYBERPUNK_PINK)
        screen.blit(start_text, (SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT // 2))

        high_score_text = font.render("Press H to View High Scores", True, CYBERPUNK_GREEN)
        screen.blit(high_score_text, (SCREEN_WIDTH // 2 - 200, SCREEN_HEIGHT // 2 + 50))

        pygame.display.update()
        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    quit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        waiting = False
                    if event.key == pygame.K_h:
                        self.show_high_scores()

    def show_high_scores(self):
        screen.fill((0, 0, 0))
        font = pygame.font.SysFont(FONT_NAME, 74)
        title_text = font.render("High Scores", True, CYBERPUNK_BLUE)
        screen.blit(title_text, (SCREEN_WIDTH // 2 - 200, SCREEN_HEIGHT // 2 - 200))

        font = pygame.font.SysFont(FONT_NAME, 36)
        y_offset = SCREEN_HEIGHT // 2 - 100
        header_text = font.render("Rank   Name           Score", True, CYBERPUNK_PINK)
        screen.blit(header_text, (SCREEN_WIDTH // 2 - 250, y_offset))
        y_offset += 50

        for i, score in enumerate(self.high_scores):
            rank = f"{i + 1}."
            name = score['name']
            score_value = score['score']
            score_text = font.render(f"{rank:<5} {name:<15} {score_value}", True, CYBERPUNK_GREEN)
            screen.blit(score_text, (SCREEN_WIDTH // 2 - 250, y_offset))
            y_offset += 50

        back_text = font.render("Press B to Go Back", True, CYBERPUNK_GREEN)
        screen.blit(back_text, (SCREEN_WIDTH // 2 - 150, y_offset + 50))

        pygame.display.update()
        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    quit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_b:
                        waiting = False

    def show_car_selection(self):
        screen.fill((0, 0, 0))
        font = pygame.font.SysFont(FONT_NAME, 74)
        title_text = font.render("Select Your Car", True, CYBERPUNK_BLUE)
        screen.blit(title_text, (SCREEN_WIDTH // 2 - 250, SCREEN_HEIGHT // 2 - 150))

        font = pygame.font.SysFont(FONT_NAME, 36)
        car1_text = font.render("Press 1 for Car 1", True, CYBERPUNK_PINK)
        screen.blit(car1_text, (SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT // 2 - 50))

        car2_text = font.render("Press 2 for Car 2", True, CYBERPUNK_PINK)
        screen.blit(car2_text, (SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT // 2))

        car3_text = font.render("Press 3 for Car 3", True, CYBERPUNK_PINK)
        screen.blit(car3_text, (SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT // 2 + 50))

        pygame.display.update()
        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    quit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_1:
                        self.car = Car("car1")
                        waiting = False
                    if event.key == pygame.K_2:
                        self.car = Car("car2")
                        waiting = False
                    if event.key == pygame.K_3:
                        self.car = Car("car3")
                        waiting = False

    def get_username(self):
        screen.fill((0, 0, 0))
        font = pygame.font.SysFont(FONT_NAME, 74)
        title_text = font.render("Enter Your Name", True, CYBERPUNK_BLUE)
        screen.blit(title_text, (SCREEN_WIDTH // 2 - 250, SCREEN_HEIGHT // 2 - 150))

        font = pygame.font.SysFont(FONT_NAME, 36)
        input_box = pygame.Rect(SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT // 2 - 50, 300, 50)
        color_inactive = CYBERPUNK_PINK
        color_active = CYBERPUNK_GREEN
        color = color_inactive
        active = False
        text = ''
        done = False

        while not done:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    quit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if input_box.collidepoint(event.pos):
                        active = not active
                    else:
                        active = False
                    color = color_active if active else color_inactive
                if event.type == pygame.KEYDOWN:
                    if active:
                        if event.key == pygame.K_RETURN:
                            done = True
                        elif event.key == pygame.K_BACKSPACE:
                            text = text[:-1]
                        else:
                            text += event.unicode

            screen.fill((0, 0, 0))
            screen.blit(title_text, (SCREEN_WIDTH // 2 - 250, SCREEN_HEIGHT // 2 - 150))
            txt_surface = font.render(text, True, color)
            width = max(200, txt_surface.get_width() + 10)
            input_box.w = width
            screen.blit(txt_surface, (input_box.x + 5, input_box.y + 5))
            pygame.draw.rect(screen, color, input_box, 2)
            pygame.display.update()

        self.username = text

    def show_game_over_screen(self):
        screen.fill((0, 0, 0))
        font = pygame.font.SysFont(FONT_NAME, 74)
        game_over_text = font.render("Game Over", True, CYBERPUNK_PINK)
        screen.blit(game_over_text, (SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT // 2 - 100))

        font = pygame.font.SysFont(FONT_NAME, 36)
        score_text = font.render(f"Final Score: {self.score}", True, CYBERPUNK_BLUE)
        screen.blit(score_text, (SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2))

        if self.lives > 0:
            continue_text = font.render("Press C to Continue", True, CYBERPUNK_GREEN)
            screen.blit(continue_text, (SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT // 2 + 50))
        else:
            restart_text = font.render("Press R to Restart or Q to Quit", True, CYBERPUNK_GREEN)
            screen.blit(restart_text, (SCREEN_WIDTH // 2 - 200, SCREEN_HEIGHT // 2 + 50))

        pygame.display.update()
        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    quit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_c and self.lives > 0:
                        self.game_over = False
                        waiting = False
                    if event.key == pygame.K_r:
                        self.__init__()
                        self.run()
                        waiting = False
                    if event.key == pygame.K_q:
                        pygame.quit()
                        quit()

    def run(self):
        self.show_start_screen()
        self.get_username()
        self.show_car_selection()
        self.road = Road()
        self.coin_manager = CoinManager()
        self.hurdle_manager = HurdleManager()
        self.heart_manager = HeartManager()
        self.score = 0
        self.lives = 3
        self.game_over = False
        self.paused = False

        while not self.game_over:
            self.handle_events()
            if not self.paused:
                self.update()
                self.draw()
            clock.tick(FPS)

        self.high_scores.append({"name": self.username, "score": self.score})
        self.high_scores.sort(key=lambda x: x["score"], reverse=True)
        self.save_high_scores()
        self.show_game_over_screen()

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    self.car.jump()
                if event.key == pygame.K_p:
                    self.paused = not self.paused

        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            self.car.move_left()
        if keys[pygame.K_RIGHT]:
            self.car.move_right()
        if not keys[pygame.K_LEFT] and not keys[pygame.K_RIGHT]:
            self.car.stop_x()

    def update(self):
        self.road.move()
        self.coin_manager.create_coin()
        self.coin_manager.move_coins()
        self.hurdle_manager.create_hurdle()
        self.hurdle_manager.move_hurdles()
        self.heart_manager.create_heart()
        self.heart_manager.move_hearts()
        self.car.update_position()

        # Check collisions
        car_rect = pygame.Rect(self.car.x, self.car.y, CAR_WIDTH, CAR_HEIGHT)
        for coin in self.coin_manager.coins:
            if car_rect.colliderect(coin):
                self.coin_manager.coins.remove(coin)
                self.score += 10
                coin_sound.play()

        for hurdle in self.hurdle_manager.hurdles:
            if car_rect.colliderect(hurdle):
                if self.car.is_jumping:
                    self.hurdle_manager.hurdles.remove(hurdle)
                    self.score += 20
                    success_sound.play()
                else:
                    crash_sound.play()
                    self.lives -= 1
                    if self.lives <= 0:
                        self.game_over = True
                    else:
                        self.hurdle_manager.hurdles.remove(hurdle)

        for heart in self.heart_manager.hearts:
            if car_rect.colliderect(heart):
                self.heart_manager.hearts.remove(heart)
                self.lives += 1
                life_sound.play()

    def draw(self):
        screen.fill((0, 0, 0))
        self.road.draw()
        self.coin_manager.draw_coins()
        self.hurdle_manager.draw_hurdles()
        self.heart_manager.draw_hearts()
        self.car.draw()

        font = pygame.font.SysFont(FONT_NAME, 36)
        score_text = font.render(f"Score: {self.score}", True, CYBERPUNK_GREEN)
        screen.blit(score_text, (10, 10))

        lives_text = font.render(f"Lives: {self.lives}", True, CYBERPUNK_PINK)
        screen.blit(lives_text, (SCREEN_WIDTH - 150, 10))

        if self.paused:
            pause_text = font.render("Paused", True, CYBERPUNK_PINK)
            screen.blit(pause_text, (SCREEN_WIDTH // 2 - 50, SCREEN_HEIGHT // 2))

        pygame.display.update()

# Run the game
game = Game()
game.run()