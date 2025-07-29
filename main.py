import pygame
from random import randint, uniform, choice
from os.path import join
import os
# High score file management
HIGH_SCORE_FILE = "high_score.txt"
if not os.path.exists(HIGH_SCORE_FILE):
    with open(HIGH_SCORE_FILE, 'w') as f:
        f.write("0")

# Read high score from file
with open(HIGH_SCORE_FILE, 'r') as f:
    high_score = int(f.read())


class Player(pygame.sprite.Sprite):
    def __init__(self, groups):
        super().__init__(groups)
        self.image = pygame.image.load(join('images','player.png')).convert_alpha()
        self.rect = self.image.get_frect(center = (WIND_WIDTH/2,WIND_HEIGHT/2))
        self.dirt = pygame.math.Vector2()
        self.speed = 300
        self.mask = pygame.mask.from_surface(self.image)

        #cooldown
        self.can_shoot = True
        self.shoot_timer = 0
        self.cooldown_duration = 400

    def lazer_timer(self):
        if not self.can_shoot:
            current_time = pygame.time.get_ticks()
            if current_time - self.shoot_timer > self.cooldown_duration:
                self.can_shoot = True


    def update(self, dt):
        if not isMenu:
            keys = pygame.key.get_pressed()
            self.dirt.x = int(keys[pygame.K_RIGHT]) - int(keys[pygame.K_LEFT])
            self.dirt.y = int(keys[pygame.K_DOWN]) - int(keys[pygame.K_UP])
            self.dirt = self.dirt.normalize() if self.dirt else self.dirt
            self.rect.center += self.dirt * self.speed * dt

            resent_keys = pygame.key.get_just_pressed()
            if resent_keys[pygame.K_SPACE] and self.can_shoot:
                Laser((all_sprites,laser_sprites), laser_surf, self.rect.midtop)
                self.can_shoot = False
                self.shoot_timer = pygame.time.get_ticks()
                laser_sound.play()

        self.lazer_timer()

class Stars(pygame.sprite.Sprite):
    def __init__(self, groups, star_surf):
        super().__init__(groups)
        self.image = star_surf
        self.rect = self.image.get_frect(center = (randint(0,WIND_WIDTH),randint(0,WIND_HEIGHT)))

class Laser(pygame.sprite.Sprite):
    def __init__(self, groups, surf, pos):
        super().__init__(groups)
        self.image = surf
        self.rect = self.image.get_frect(midbottom = pos)

    def update(self, dt):
        self.rect.centery -= 400 * dt
        if self.rect.centery < -100:
            self.kill()

class Meteor(pygame.sprite.Sprite):
    def __init__(self, surf, groups):
        super().__init__(groups)
        self.original = surf
        self.image = surf
        self.rect = self.image.get_frect(center = (randint(0,WIND_WIDTH), -100))
        self.speed = randint(400,500)
        self.dirt = pygame.math.Vector2(uniform(-0.5,0.5),1)
        self.lifetime = 2000
        self.born = pygame.time.get_ticks()
        self.rotation = 0
        self.rotation_dirt = choice([1,-1])

    def update(self, dt):
        self.rect.center += self.speed * self.dirt * dt
        if pygame.time.get_ticks() - self.born >= self.lifetime:
            self.kill()

        self.rotation += randint(50,80) * self.rotation_dirt* dt
        self.image = pygame.transform.rotozoom(self.original, self.rotation,1)
        self.rect = self.image.get_frect(center = self.rect.center)

class Animation_Explosion(pygame.sprite.Sprite):
    def __init__(self, frames, pos, groups):
        super().__init__(groups)
        self.frames = frames
        self.index = 0
        self.image = self.frames[self.index]
        self.rect = self.image.get_frect(center = pos)
        explosion_sound.play()

    def update(self, dt):
        self.index += 20* dt
        if self.index <= len(self.frames):
            self.image = self.frames[int(self.index)]
        else:
            self.kill()

def collision_control():
    global isRunning
    collision_sprits = pygame.sprite.spritecollide(player, meteor_sprites, True, pygame.sprite.collide_mask)
    if collision_sprits:
        damage_sound.play()
        isRunning = False

    for laser in laser_sprites:
        if pygame.sprite.spritecollide(laser, meteor_sprites, True):
            laser.kill()
            Animation_Explosion(explosion_frames, laser.rect.midtop, all_sprites)

def display_score():
    score = (pygame.time.get_ticks() - game_started_time) // 100
    score_surf = font.render(str(score), True, (240, 240, 240))
    score_rect = score_surf.get_frect(midbottom = (WIND_WIDTH/2, WIND_HEIGHT-50))
    screen.blit(score_surf,score_rect)
    return score

def show_menu():
    screen.fill('#3a2e4f')
    all_sprites.draw(screen)

    # High score text
    high_surf = font.render(f'High Score: {high_score}', True, (255, 255, 255))
    high_rect = high_surf.get_frect(midtop=(WIND_WIDTH / 2, 100))
    screen.blit(high_surf, high_rect)

    # Prompt to start
    prompt_surf = font.render('Press ENTER to Start', True, (200, 200, 200))
    prompt_rect = prompt_surf.get_frect(midtop=(WIND_WIDTH / 2, 160))
    screen.blit(prompt_surf, prompt_rect)

    pygame.display.update()

def check_and_save_highscore(score):
    global high_score
    if score > high_score:
        high_score = score
        with open(HIGH_SCORE_FILE, 'w') as f:
            f.write(str(score))

def show_game_over(score):
    screen.fill('#3a2e4f')
    all_sprites.draw(screen)

    gameover_surf = font.render("Game Over", True, (255, 0, 0))
    score_surf = font.render(f"Your Score: {score}", True, (240, 240, 240))
    high_surf = font.render(f"High Score: {high_score}", True, (255, 255, 255))
    restart_surf = font.render("Press R to Restart or ESC to Quit", True, (200, 200, 200))

    screen.blit(gameover_surf, gameover_surf.get_frect(center=(WIND_WIDTH / 2, 150)))
    screen.blit(score_surf, score_surf.get_frect(center=(WIND_WIDTH / 2, 210)))
    screen.blit(high_surf, high_surf.get_frect(center=(WIND_WIDTH / 2, 260)))
    screen.blit(restart_surf, restart_surf.get_frect(center=(WIND_WIDTH / 2, 320)))

    pygame.display.update()

def restart_game():
    global player, isMenu, waiting, isRunning
    all_sprites.empty()
    meteor_sprites.empty()
    laser_sprites.empty()
    for _ in range(20):
        Stars(all_sprites, star_surf)
    player = Player(all_sprites)
    player.can_shoot = True
    isMenu = True
    waiting = False
    isRunning = True

# Screen setup
WIND_WIDTH, WIND_HEIGHT =1000, 700
pygame.init()
screen = pygame.display.set_mode((WIND_WIDTH,WIND_HEIGHT))
pygame.display.set_caption("Space Survivor game")
isRunning = True
isMenu = True
clock = pygame.time.Clock()

# Plain Surface
surf = pygame.Surface((100,200))
surf.fill("orange")
x = 100

# Import
meteor_surf = pygame.image.load(join('images','meteor.png')).convert_alpha()
star_surf = pygame.image.load(join('images','star.png')).convert_alpha()
laser_surf = pygame.image.load(join('images','laser.png')).convert_alpha()
font = pygame.font.Font(join('images','Oxanium-Bold.ttf'),30)
explosion_frames = [pygame.image.load(join('images','explosion',f'{i}.png')).convert_alpha() for i in range(21)]
laser_sound = pygame.mixer.Sound(join('audio','laser.wav'))
laser_sound.set_volume(0.4)
explosion_sound = pygame.mixer.Sound(join('audio','explosion.wav'))
explosion_sound.set_volume(0.5)
damage_sound = pygame.mixer.Sound(join('audio','damage.ogg'))
game_music = pygame.mixer.Sound(join('audio','game_music.wav'))
game_music.set_volume(0.25)
game_music.play(loops=-1)


# Sprite setup
all_sprites = pygame.sprite.Group()
meteor_sprites = pygame.sprite.Group()
laser_sprites = pygame.sprite.Group()

for _ in range(20):
    Stars(all_sprites,star_surf)
player = Player(all_sprites)

# Custom events
meteor_event = pygame.event.custom_type()
pygame.time.set_timer(meteor_event,500)

while True:
    game_started_time = 0

    # Display
    while isRunning:
        dt = clock.tick() / 1000

        # event Loop
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                isRunning = False
                pygame.quit()
                exit()

            if isMenu and event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                isMenu = False
                game_started_time = pygame.time.get_ticks()

            if not isMenu and event.type == meteor_event:
                Meteor(meteor_surf,(all_sprites,meteor_sprites))

        # Display Main menu
        if isMenu:
            all_sprites.update(dt)
            show_menu()
            continue

        # Updating Game
        all_sprites.update(dt)

        # Painting Game
        screen.fill('#3a2e4f')
        display_score()
        all_sprites.draw(screen)

        collision_control()
        pygame.display.update()

    # Game ends and Highscore is compared
    final_score = (pygame.time.get_ticks() - game_started_time) // 100
    check_and_save_highscore(final_score)
    show_game_over(final_score)

    # waiting loop
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                waiting = False
                isRunning = False
                pygame.quit()
                exit()

            if event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                restart_game()
