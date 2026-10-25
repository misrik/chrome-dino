import math
import os
import random
import sys

import pygame

WIDTH = 1100
HEIGHT = 600
FPS = 60

DINO_X = 80
DINO_Y = 310
CACTUS_Y = 325
TRACK_Y = 380

GRAVITY = 0.8
JUMP_SPEED = -16
START_SPEED = 8

WHITE = (255, 255, 255)
GRAY = (83, 83, 83)

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Chrome Dinosaur")
clock = pygame.time.Clock()

IMAGES_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Dino")


def load_image(name):
    return pygame.image.load(os.path.join(IMAGES_DIR, name)).convert_alpha()


RUN_FRAMES = [load_image("DinoRun1.png"), load_image("DinoRun2.png")]
JUMP_IMAGE = load_image("DinoJump.png")
CACTUS_IMAGES = [load_image(f"SmallCactus{i}.png") for i in range(1, 4)]
CLOUD_IMAGE = load_image("Cloud.png")
TRACK_IMAGE = load_image("Track.png")

FONT_BIG = pygame.font.SysFont("arial", 64, bold=True)
FONT = pygame.font.SysFont("arial", 32, bold=True)
FONT_SMALL = pygame.font.SysFont("arial", 22)


class Sprite(pygame.sprite.Sprite):
    def __init__(self, image, x, y):
        super().__init__()
        self.image = image
        self.rect = self.image.get_rect(topleft=(x, y))
        self.x = float(x)
        self.y = float(y)

    def draw(self, surface):
        surface.blit(self.image, self.rect)


class Player(Sprite):
    def __init__(self):
        super().__init__(RUN_FRAMES[0], DINO_X, DINO_Y)
        self.frames = RUN_FRAMES
        self.jump_image = JUMP_IMAGE
        self.frame_index = 0
        self.velocity = 0
        self.on_ground = True

    def jump(self):
        if self.on_ground:
            self.velocity = JUMP_SPEED
            self.on_ground = False

    def apply_gravity(self):
        self.velocity += GRAVITY
        self.y += self.velocity
        if self.y >= DINO_Y:
            self.y = DINO_Y
            self.velocity = 0
            self.on_ground = True
        self.rect.y = int(self.y)

    def animate(self):
        if self.on_ground:
            self.frame_index = (self.frame_index + 1) % (len(self.frames) * 6)
            self.image = self.frames[self.frame_index // 6]
        else:
            self.image = self.jump_image

    def update(self):
        self.apply_gravity()
        self.animate()


class Cactus(Sprite):
    def __init__(self, x):
        super().__init__(random.choice(CACTUS_IMAGES), x, CACTUS_Y)

    def update(self, speed):
        self.x -= speed
        self.rect.x = int(self.x)
        if self.rect.right < 0:
            self.kill()


class CactusGroup(pygame.sprite.Group):
    def __init__(self):
        super().__init__()
        self.distance = 0
        self.next_gap = 300

    def update(self, speed):
        super().update(speed)
        self.distance += speed
        if self.distance >= self.next_gap:
            self.add(Cactus(WIDTH + random.randint(0, 100)))
            self.distance = 0
            self.next_gap = random.randint(450, 900) + speed * 20

    def collides(self, player):
        return pygame.sprite.spritecollideany(player, self, pygame.sprite.collide_mask) is not None


class Cloud(Sprite):
    def __init__(self):
        super().__init__(CLOUD_IMAGE, random.randint(0, WIDTH), random.randint(50, 250))
        self.speed = random.uniform(1, 2)

    def reset(self):
        self.x = WIDTH + random.randint(50, 400)
        self.rect.y = random.randint(50, 250)

    def update(self):
        self.x -= self.speed
        if self.x + self.rect.width < 0:
            self.reset()
        self.rect.x = int(self.x)


class Track(Sprite):
    def __init__(self):
        super().__init__(TRACK_IMAGE, 0, TRACK_Y)

    def update(self, speed):
        self.x -= speed
        if self.x <= -self.rect.width:
            self.x += self.rect.width
        self.rect.x = int(self.x)

    def draw(self, surface):
        surface.blit(self.image, (self.rect.x, self.rect.y))
        surface.blit(self.image, (self.rect.x + self.rect.width, self.rect.y))


class Button:
    def __init__(self, text, center):
        self.text = text
        self.rect = pygame.Rect(0, 0, 220, 60)
        self.rect.center = center

    def draw(self, surface):
        hovered = self.rect.collidepoint(pygame.mouse.get_pos())
        background = GRAY if hovered else WHITE
        text_color = WHITE if hovered else GRAY
        pygame.draw.rect(surface, background, self.rect, border_radius=10)
        pygame.draw.rect(surface, GRAY, self.rect, 3, border_radius=10)
        label = FONT.render(self.text, True, text_color)
        surface.blit(label, label.get_rect(center=self.rect.center))

    def is_clicked(self, event):
        return (event.type == pygame.MOUSEBUTTONDOWN and event.button == 1
                and self.rect.collidepoint(event.pos))


def draw_text(text, font, center, color=GRAY):
    label = font.render(text, True, color)
    screen.blit(label, label.get_rect(center=center))


def menu(last_score=None):
    player = Player()
    track = Track()
    clouds = [Cloud() for i in range(3)]
    start_button = Button("Start", (WIDTH // 2 - 130, 470))
    exit_button = Button("Exit", (WIDTH // 2 + 130, 470))
    pygame.event.clear()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if start_button.is_clicked(event):
                return True
            if exit_button.is_clicked(event):
                return False
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_SPACE, pygame.K_RETURN):
                    return True
                if event.key == pygame.K_ESCAPE:
                    return False

        player.animate()
        track.update(3)
        for cloud in clouds:
            cloud.update()

        screen.fill(WHITE)
        for cloud in clouds:
            cloud.draw(screen)
        track.draw(screen)
        player.draw(screen)

        time = pygame.time.get_ticks() / 300
        draw_text("Chrome Dinosaur", FONT_BIG, (WIDTH // 2, 100 + math.sin(time) * 10))

        if last_score is not None:
            draw_text("Game Over", FONT, (WIDTH // 2, 190))
            draw_text(f"Score: {last_score}", FONT_SMALL, (WIDTH // 2, 230))

        start_button.draw(screen)
        exit_button.draw(screen)
        draw_text("Пробіл або стрибок стрілкою вгору", FONT_SMALL, (WIDTH // 2, 540))
        draw_text("Перестрибуй кактуси, щоб набрати більше очок", FONT_SMALL, (WIDTH // 2, 570))

        pygame.display.flip()
        clock.tick(FPS)


def game():
    player = Player()
    track = Track()
    clouds = [Cloud() for i in range(3)]
    cacti = CactusGroup()
    speed = START_SPEED
    frames = 0

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_SPACE, pygame.K_UP):
                    player.jump()
                if event.key == pygame.K_ESCAPE:
                    return frames // 5

        frames += 1
        if frames % 500 == 0:
            speed += 1
        score = frames // 5

        player.update()
        track.update(speed)
        for cloud in clouds:
            cloud.update()
        cacti.update(speed)

        screen.fill(WHITE)
        for cloud in clouds:
            cloud.draw(screen)
        track.draw(screen)
        cacti.draw(screen)
        player.draw(screen)
        draw_text(f"Score: {score:05d}", FONT_SMALL, (WIDTH - 100, 30))

        if cacti.collides(player):
            draw_text("Game Over", FONT_BIG, (WIDTH // 2, HEIGHT // 2 - 80))
            pygame.display.flip()
            pygame.time.delay(1200)
            return score

        pygame.display.flip()
        clock.tick(FPS)


def main():
    last_score = None
    while menu(last_score):
        last_score = game()
    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()