import pygame
import neat
from neat.checkpoint import Checkpointer
import pickle
import os
import glob
import random
import math
import time

pygame.font.init()

WIN_WIDTH = 500
WIN_HEIGHT = 800
STAT_FONT = pygame.font.SysFont("comicsans", 50)
GEN = 0

def load_max_score():
    if os.path.exists("max_score.txt"):
        try:
            with open("max_score.txt", "r") as f:
                return int(f.read())
        except:
            return 0
    return 0

MAX_SCORE = load_max_score()

BIRD_IMGS = [pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", f"bird{i}.png"))) for i in range(1, 4)]
PIPE_IMGS = [pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", f"pipe{i}.png"))) for i in range(1,6)]
BASE_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "base.png")))
BG_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "bg.png")))

class Bird:
    IMGS = BIRD_IMGS
    MAX_ROTATION = 25
    ROT_VEL = 20
    ANIMATION_TIME = 5

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.tilt = 0
        self.tick_count = 0
        self.vel = 0
        self.height = y
        self.img_count = 0
        self.img = self.IMGS[0]

    def jump(self):
        self.vel = -10.5
        self.tick_count = 0
        self.height = self.y

    def move(self):
        self.tick_count += 1
        d = self.vel * self.tick_count + 1.5 * self.tick_count ** 2
        if d >= 16: d = 16
        if d < 0: d -= 2
        self.y += d
        if d < 0 or self.y < self.height + 50:
            if self.tilt < self.MAX_ROTATION:
                self.tilt = self.MAX_ROTATION
        else:
            if self.tilt > -90:
                self.tilt -= self.ROT_VEL

    def draw(self, win):
        self.img_count += 1
        self.img = self.IMGS[(self.img_count // self.ANIMATION_TIME) % len(self.IMGS)]
        if self.tilt <= -80:
            self.img = self.IMGS[1]
            self.img_count = self.ANIMATION_TIME * 2
        rotated_image = pygame.transform.rotate(self.img, self.tilt)
        new_rect = rotated_image.get_rect(center=self.img.get_rect(topleft=(self.x, self.y)).center)
        win.blit(rotated_image, new_rect.topleft)

    def get_mask(self):
        return pygame.mask.from_surface(self.img)

class Pipe:
    GAP = 200
    VEL = 5  # horizontal speed
    MIN_AMPLITUDE = 10
    MAX_AMPLITUDE = 30
    MIN_FREQ = 0.3
    MAX_FREQ = 0.6
    MIN_V_SPEED = 0.5
    MAX_V_SPEED = 1
    

    def __init__(self, x):
        self.PIPE_TOP = pygame.transform.flip(random.choice(PIPE_IMGS), False, True)
        self.PIPE_BOTTOM = random.choice(PIPE_IMGS)
        self.x = x + max(self.PIPE_TOP.get_width(),self.PIPE_BOTTOM.get_width())/2
        self.base_height = random.randrange(150, 350)  # central vertical position

        # Sinusoidal parameters
        self.amplitude = random.uniform(self.MIN_AMPLITUDE, self.MAX_AMPLITUDE)
        self.frequency = random.uniform(self.MIN_FREQ, self.MAX_FREQ)
        self.start_time = time.time()
        # Random vertical speed (direction included)
        self.v_speed = random.choice([-1, 1]) * random.uniform(self.MIN_V_SPEED, self.MAX_V_SPEED)

        
        self.passed = False

        self.GAP = random.randint(250, 400)
        self.height = self.base_height
        self.top = self.height - self.PIPE_TOP.get_height()
        self.bottom = self.height + self.GAP

    def move(self):
        self.x -= self.VEL  
        elapsed = time.time() - self.start_time
        sinusoidal_offset = self.amplitude * math.sin(2 * math.pi * self.frequency * elapsed)

        self.base_height += self.v_speed

        if self.base_height < 50:
            self.base_height = 50
            self.v_speed *= -1
        elif self.base_height > 450:
            self.base_height = 450
            self.v_speed *= -1

        self.height = self.base_height + sinusoidal_offset

        self.top = self.height - self.PIPE_TOP.get_height()
        self.bottom = self.height + self.GAP

    def draw(self, win):
        win.blit(self.PIPE_TOP, (self.x, self.top))
        win.blit(self.PIPE_BOTTOM, (self.x, self.bottom))

    def collide(self, bird):
        bird_mask = bird.get_mask()
        top_mask = pygame.mask.from_surface(self.PIPE_TOP)
        bottom_mask = pygame.mask.from_surface(self.PIPE_BOTTOM)
        top_offset = (self.x - bird.x, self.top - round(bird.y))
        bottom_offset = (self.x - bird.x, self.bottom - round(bird.y))
        return bird_mask.overlap(top_mask, top_offset) or bird_mask.overlap(bottom_mask, bottom_offset)

class Base:
    VEL = 5
    WIDTH = BASE_IMG.get_width()
    IMG = BASE_IMG

    def __init__(self, y):
        self.y = y
        self.x1 = 0
        self.x2 = self.WIDTH

    def move(self):
        self.x1 -= self.VEL
        self.x2 -= self.VEL
        if self.x1 + self.WIDTH < 0:
            self.x1 = self.x2 + self.WIDTH
        if self.x2 + self.WIDTH < 0:
            self.x2 = self.x1 + self.WIDTH

    def draw(self, win):
        win.blit(self.IMG, (self.x1, self.y))
        win.blit(self.IMG, (self.x2, self.y))

def draw_window(win, birds, pipes, base, score, gen, alive, paused, fast_mode, pipe_ind):
    win.blit(BG_IMG, (0, 0))
    for i, pipe in enumerate(pipes):
        pipe.draw(win)
        # if i == pipe_ind:
            # pygame.draw.rect(win, (255, 0, 0), (pipe.x, pipe.top, pipe.PIPE_TOP.get_width(), pipe.PIPE_TOP.get_height()), 3)
            # pygame.draw.rect(win, (255, 0, 0), (pipe.x, pipe.bottom, pipe.PIPE_BOTTOM.get_width(), pipe.PIPE_BOTTOM.get_height()), 3)
    base.draw(win)
    for bird in birds:
        bird.draw(win)
    score_text = STAT_FONT.render(f"Score: {score}", 1, (255, 255, 255))
    gen_text = STAT_FONT.render(f"Gen: {gen}", 1, (255, 255, 255))
    alive_text = STAT_FONT.render(f"Alive: {alive}", 1, (255, 255, 255))
    win.blit(score_text, (WIN_WIDTH - 10 - score_text.get_width(), 10))
    win.blit(gen_text, (10, 10))
    win.blit(alive_text, (10, 50))
    pygame.display.update()

def main(genomes, config):
    global GEN, MAX_SCORE
    GEN += 1
    nets = []
    ge = []
    birds = []

    for _, g in genomes:
        g.fitness = 0
        net = neat.nn.FeedForwardNetwork.create(g, config)
        nets.append(net)
        birds.append(Bird(230, 350))
        ge.append(g)

    base = Base(730)
    pipes = [Pipe(600)]
    win = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
    clock = pygame.time.Clock()
    score = 0
    run = True
    paused = False
    fast_mode = False
    MAX_RUN_SCORE = 30
    
    def reset_population():
        nonlocal birds, nets, ge, pipes, base, score
        birds = []
        nets = []
        ge = []
        for _, g in genomes:
            g.fitness = 0
            net = neat.nn.FeedForwardNetwork.create(g, config)
            nets.append(net)
            birds.append(Bird(230, 350))
            ge.append(g)
        pipes = [Pipe(600)]
        base = Base(730)
        score = 0

    while run and len(birds) > 0:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                if ge:
                    if score >= MAX_SCORE:
                        MAX_SCORE = score
                        print("Saving model before exiting...")
                        best_genome = max(ge, key=lambda g: g.fitness)
                        with open("best_bird.pkl", "wb") as f:
                            pickle.dump(best_genome, f)
                        with open("max_score.txt", "w") as f:
                            f.write(str(MAX_SCORE))
                        print("Model saved. Exiting now.")
                run = False
                pygame.quit()
                quit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_p:
                    paused = not paused
                if event.key == pygame.K_f:
                    fast_mode = not fast_mode

        if paused:
            clock.tick(10)
            continue

        pipe_ind = 0
        if len(pipes) > 1 and birds[0].x > pipes[0].x + pipes[0].PIPE_TOP.get_width():
            pipe_ind = 1

        if not fast_mode:
            draw_window(win, birds, pipes, base, score, GEN, len(birds), paused, fast_mode, pipe_ind)

        clock.tick(200 if fast_mode else 30)

        for x, bird in enumerate(birds):
            bird.move()
            ge[x].fitness += 0.1
            output = nets[x].activate((
                bird.y,
                bird.vel,
                pipes[pipe_ind].x - bird.x,
                pipes[pipe_ind].height,
                pipes[pipe_ind].bottom
            ))
            if output[0] > 0.5:
                bird.jump()

        add_pipe = False
        rem = []
        remove_indices = []
        

        for pipe in pipes:
            pipe.move()
            for x, bird in enumerate(birds):
                if pipe.collide(bird):
                    ge[x].fitness -= 5
                    remove_indices.append(x)
                if not pipe.passed and pipe.x < bird.x:
                    pipe.passed = True
                    add_pipe = True
            if pipe.x + pipe.PIPE_TOP.get_width() < 0:
                rem.append(pipe)

        for x in sorted(remove_indices, reverse=True):
            birds.pop(x)
            nets.pop(x)
            ge.pop(x)

        if add_pipe:
            score += 1
            for g in ge:
                g.fitness += 10
            pipes.append(Pipe(600))
            if score >= MAX_SCORE:
                MAX_SCORE = score
                print(f"New max score: {MAX_SCORE} at generation {GEN}")
                best_genome = max(ge, key=lambda g: g.fitness)
                with open("best_bird.pkl", "wb") as f:
                    pickle.dump(best_genome, f)
                with open("max_score.txt", "w") as f:
                    f.write(str(MAX_SCORE))
                print("Saved best genome and max score due to score improvement")

        pipes = [pipe for pipe in pipes if pipe not in rem]

        for x in range(len(birds) - 1, -1, -1):
            if birds[x].y + birds[x].img.get_height() >= 730 or birds[x].y < 0:
                ge[x].fitness -= 5
                birds.pop(x)
                nets.pop(x)
                ge.pop(x)

        base.move()
        
        alive_count = len(birds)
        if score >= 20: 
            if alive_count > 5:
                MAX_RUN_SCORE = 100
            else:
                run = False  
        if score >= MAX_RUN_SCORE:
            print(f"Score reached {score}, alive birds: {alive_count}")

            if alive_count <= 5:
                print("Very few birds survived, stopping generation as model is not learning well.")
                run = False
            elif alive_count <= 30:
                print("Not enough birds survived, model needs more training. Stopping generation.")
                run = False
            else:
                print("Enough birds survived, resetting population for next round...")
                reset_population()
                
        if fast_mode:
            draw_window(win, birds, pipes, base, score, GEN, len(birds), paused, fast_mode, pipe_ind)

def run(config_path, resume=False):
    global GEN
    model_path = "best_bird.pkl"
    checkpoint_prefix = "neat-checkpoint-"
    config = neat.config.Config(
        neat.DefaultGenome,
        neat.DefaultReproduction,
        neat.DefaultSpeciesSet,
        neat.DefaultStagnation,
        config_path
    )

    if resume:
        checkpoints = sorted(glob.glob(f"{checkpoint_prefix}*"), key=os.path.getmtime)
        if checkpoints:
            latest = checkpoints[-1]
            GEN = int(latest.split("-")[-1]) -1 
            print(f"Resuming from latest checkpoint: {latest}")
            p = neat.Checkpointer.restore_checkpoint(latest)
        elif os.path.exists(model_path) and os.path.getsize(model_path) > 0:
            print("No checkpoint found, loading saved best model...")
            with open(model_path, "rb") as f:
                winner_genome = pickle.load(f)
            p = neat.Population(config)
            print("Seeding new population with saved best genome...")
            for gid, genome in p.population.items():
                genome.connections = winner_genome.connections.copy()
                genome.nodes = winner_genome.nodes.copy()
        else:
            print("No checkpoint or saved model found. Starting fresh.")
            p = neat.Population(config)
    else:
        p = neat.Population(config)

    p.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    p.add_reporter(stats)
    p.add_reporter(Checkpointer(generation_interval=5, filename_prefix=checkpoint_prefix))

    try:
        winner = p.run(main)
    except KeyboardInterrupt:
        print("Training interrupted by user.")
        if 'winner' in locals():
            with open(model_path, "wb") as f:
                pickle.dump(winner, f)
        pygame.quit()
        quit()

    with open(model_path, "wb") as f:
        pickle.dump(winner, f)
    print("Training complete. Winner saved.")

if __name__ == "__main__":
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, "config-feedforward.txt")

    choice = input("Enter 'train' to train new or 'resume' to continue training best model: ").strip().lower()

    if choice == "resume":
        run(config_path, resume=True)
    else:
        run(config_path, resume=False)
    
    
