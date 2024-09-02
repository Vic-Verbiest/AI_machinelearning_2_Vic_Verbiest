import pygame
import centipede_lib
import graph
import random
import numpy as np
import concurrent.futures
import os

# Dimensions
SCREEN_WIDTH = 700
SCREEN_HEIGHT = 700

GRID_SIZE = [SCREEN_WIDTH // 25, SCREEN_WIDTH // 25]
BUGBLASTER_MOVEMENTSPEED = SCREEN_WIDTH // 100

# Colors
BLACK = (0, 0, 0)

# Game Loop
def game_loop(genome, index):
    # Initialize Pygame
    pygame.init()

    # Creating screen
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Centipede")

    # Sprites
    bugblaster_sprite = pygame.sprite.Group()

    # Loading Images
    BUGBLASTER_IMAGE = pygame.image.load("sprites/bugblaster.PNG").convert_alpha()
    CENTIPEDE_HEAD_IMAGE = pygame.image.load("sprites/centipede_head.PNG").convert_alpha()
    CENTIPEDE_BODY_IMAGE = pygame.image.load("sprites/centipede_body.PNG").convert_alpha()
    MUSHROOM_IMAGE = pygame.image.load("sprites/mushroom.PNG").convert_alpha()
    BULLET_IMAGE = pygame.image.load("sprites/bullet.PNG").convert_alpha()

    # Game variables
    BUGBLASTER_POS = [SCREEN_WIDTH // 2, SCREEN_HEIGHT - GRID_SIZE[0]]
    CENTIPEDE_POS = [SCREEN_WIDTH // 2, (3 * GRID_SIZE[0])]
    points = 0

    # Initialize Sprites
    bugblaster = centipede_lib.Sprite(GRID_SIZE, BUGBLASTER_POS, BUGBLASTER_IMAGE)
    bugblaster_sprite.add(bugblaster)

    centipedes_all = []
    centipede = centipede_lib.centipede(CENTIPEDE_POS, 1, -1, 12, SCREEN_WIDTH // 100, CENTIPEDE_HEAD_IMAGE, CENTIPEDE_BODY_IMAGE)
    centipedes_all.append(centipede)

    centipede_sprites = pygame.sprite.Group()
    for centipede in centipedes_all:
        for bodypart in centipede.construction:
            centipede_sprites.add(bodypart.sprite)

    mushrooms_all = []
    for i in range(15):
        mushrooms_all.append(centipede_lib.mushroom([(random.randint(0, 24) + 0) * GRID_SIZE[0] + GRID_SIZE[0] // 2,
                                                     (random.randint(0, 19) + 4) * GRID_SIZE[1] + GRID_SIZE[1] // 2],
                                                    MUSHROOM_IMAGE))

    mushrooms_sprites = pygame.sprite.Group()
    for mushroom in mushrooms_all:
        mushrooms_sprites.add(mushroom.sprite)

    bullets_sprites = pygame.sprite.Group()
    shoot = False
    BULLET_SPEED = 10
    BULLET_SIZE = [5, 6]
    bullet_time = 0
    quit_counter = 0

    running = True
    clock = pygame.time.Clock()
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        points_text = pygame.font.Font(None, 74).render(str(points), True, (255, 255, 255))
        
        # Genome-based movement decision
        action = genome.make_decision(BUGBLASTER_POS, centipedes_all, mushrooms_all, bullets_sprites)

        # Movement bugblaster
        if action == "LEFT" and BUGBLASTER_POS[0] > 0:
            BUGBLASTER_POS[0] -= BUGBLASTER_MOVEMENTSPEED
        elif action == "RIGHT" and BUGBLASTER_POS[0] < SCREEN_WIDTH - GRID_SIZE[0]:
            BUGBLASTER_POS[0] += BUGBLASTER_MOVEMENTSPEED
        elif action == "UP" and BUGBLASTER_POS[1] > SCREEN_HEIGHT - (GRID_SIZE[1] * 5):
            BUGBLASTER_POS[1] -= BUGBLASTER_MOVEMENTSPEED
        elif action == "DOWN" and BUGBLASTER_POS[1] < SCREEN_HEIGHT - GRID_SIZE[1]:
            BUGBLASTER_POS[1] += BUGBLASTER_MOVEMENTSPEED
        elif action == "SHOOT":
            if shoot == False and bullet_time <= 0:
                bullets_sprites.add(centipede_lib.Sprite(BULLET_SIZE, [BUGBLASTER_POS[0]+GRID_SIZE[0]//2 , BUGBLASTER_POS[1]], BULLET_IMAGE))
                bullet_time = 1
                shoot = True

        else:
            shoot = False

        if bullet_time > 0:
            bullet_time -= 1

        bugblaster.rect.x = BUGBLASTER_POS[0]
        bugblaster.rect.y = BUGBLASTER_POS[1]

        # Death check using Pygame's collision detection
        if pygame.sprite.spritecollideany(bugblaster, centipede_sprites):
            print("game over")
            running = False

        # Bullets
        for bullet in bullets_sprites:
            if bullet.rect.y < 0:
                bullets_sprites.remove(bullet)

            hit = False
            for mushroom in mushrooms_all:
                if bullet.rect.y - BULLET_SPEED < mushroom.pos[1] + GRID_SIZE[1] // 2:
                    if bullet.rect.x < mushroom.pos[0] + GRID_SIZE[0] // 2 and bullet.rect.x > mushroom.pos[0] - GRID_SIZE[0] // 2:
                        hit = True
                        bullets_sprites.remove(bullet)
                        mushroom.lifes -= 1
                        if mushroom.lifes == 0:
                            mushrooms_sprites.remove(mushroom.sprite)
                            mushrooms_all.remove(mushroom)
                            points += 1
                            print("mushroom removed")
                        

            for centipede in centipedes_all:
                for bodypart in centipede.construction:
                    if bullet.rect.y - BULLET_SPEED < bodypart.pos[1] + GRID_SIZE[1] // 2:
                        if bullet.rect.x < bodypart.pos[0] + GRID_SIZE[0] // 2 and bullet.rect.x > bodypart.pos[0] - GRID_SIZE[0] // 2:
                            hit = True
                            bullets_sprites.remove(bullet)
                            centipede.construction.remove(bodypart)
                            mushroom2 = centipede_lib.mushroom([bodypart.pos[0], bodypart.pos[1] + GRID_SIZE[1]//2], MUSHROOM_IMAGE)
                            mushrooms_all.append(mushroom2)
                            mushrooms_sprites.add(mushroom2.sprite)
                            centipede_sprites.remove(bodypart.sprite)
                            points += 10
                            if len(centipede.construction) == 0:
                                centipedes_all.remove(centipede)
                                centipede_sprites.remove(centipede_sprites)
                                points += 90
                                print("centipede removed")
                                centipedes_all = []
                                centipede = centipede_lib.centipede(CENTIPEDE_POS, 1, -1, 12, SCREEN_WIDTH//100, CENTIPEDE_HEAD_IMAGE, CENTIPEDE_BODY_IMAGE)
                                centipedes_all.append(centipede)

                                centipede_sprites = pygame.sprite.Group()
                                for centipede in centipedes_all:
                                    for bodypart in centipede.construction:
                                        centipede_sprites.add(bodypart.sprite)

            if hit == False:
                bullet.rect.y -= BULLET_SPEED

        # Movement centipede
        for centipede in centipedes_all:
            for bodypart in centipede.construction:
                mushroom_hit = False
                for mushroom in mushrooms_all:
                    if mushroom.pos[1] == bodypart.pos[1] + GRID_SIZE[1] // 2:
                        if mushroom.pos[0] - GRID_SIZE[0] * 1.5 < bodypart.pos[0] + centipede.speed and bodypart.pos[0] - centipede.speed < mushroom.pos[0] + GRID_SIZE[0] // 2:
                            mushroom_hit = True

                if bodypart.direction_x == 1:
                    if bodypart.pos[0] - centipede.speed > SCREEN_WIDTH - GRID_SIZE[0] * 1.5 or mushroom_hit == True:
                        if bodypart.direction_y == -1:
                            bodypart.pos[1] += GRID_SIZE[1]
                            bodypart.direction_x = bodypart.direction_x * -1
                        else:
                            bodypart.pos[1] -= GRID_SIZE[1]
                            bodypart.direction_x = bodypart.direction_x * -1
                        bodypart.sprite.image = pygame.transform.flip(bodypart.sprite.image, True, False)
                    else:
                        bodypart.pos[0] += centipede.speed

                else:
                    if bodypart.pos[0] - centipede.speed < GRID_SIZE[0] * 0.5 or mushroom_hit == True:
                        if bodypart.direction_y == -1:
                            bodypart.pos[1] += GRID_SIZE[1]
                            bodypart.direction_x = bodypart.direction_x * -1
                        else:
                            bodypart.pos[1] -= GRID_SIZE[1]
                            bodypart.direction_x = bodypart.direction_x * -1
                        bodypart.sprite.image = pygame.transform.flip(bodypart.sprite.image, True, False)
                    else:
                        bodypart.pos[0] -= centipede.speed

                if bodypart.pos[1] >= SCREEN_HEIGHT - GRID_SIZE[1]:
                    if bodypart.direction_y == -1:
                        quit_counter = quit_counter + 1
                    if quit_counter == 5:
                        running = False
                    bodypart.direction_y = 1



                if bodypart.pos[1] <= SCREEN_HEIGHT - (5 * GRID_SIZE[1]):
                    bodypart.direction_y = -1


                bodypart.sprite.rect.x = bodypart.pos[0]
                bodypart.sprite.rect.y = bodypart.pos[1]

        # Redrawing Screen
        screen.fill(BLACK)
        mushrooms_sprites.draw(screen)
        bullets_sprites.draw(screen)
        centipede_sprites.draw(screen)
        bugblaster_sprite.draw(screen)
        screen.blit(points_text, (SCREEN_WIDTH // 2, 25))
        pygame.display.flip()
        clock.tick(240)

    pygame.quit()
    return points, index


class BasicGenome:
    def __init__(self, max_state_length):
        # Initialize weights dynamically based on the current max state length
        self.weights = np.random.rand(5, max_state_length)  # 5 actions, each with max_state_length weights

    def make_decision(self, bug_pos, centipedes, mushrooms, bullets):
        state = self.get_state_representation(bug_pos, centipedes, mushrooms, bullets)

        # Ensure state is a numpy array for compatibility
        state = np.array(state)

        # Calculate action scores
        action_scores = np.dot(self.weights[:, :len(state)], state)

        # Debugging information
        #print(f"Action Scores: {action_scores}")

        # Determine the best action
        action_index = np.argmax(action_scores)
        actions = ["LEFT", "RIGHT", "UP", "DOWN", "SHOOT"]

        return actions[action_index]

    def get_state_representation(self, bugblaster_pos, centipedes, mushrooms, bullets):
        # Create a state representation
        state = [
            bugblaster_pos[0] / SCREEN_WIDTH,  # Normalized x position of bugblaster
            bugblaster_pos[1] / SCREEN_HEIGHT, # Normalized y position of bugblaster
        ]

        for centipede in centipedes:
            for bodypart in centipede.construction:
                state.extend([
                    bodypart.pos[0] / SCREEN_WIDTH,
                    bodypart.pos[1] / SCREEN_HEIGHT
                ])

        for mushroom in mushrooms:
            state.extend([
                mushroom.pos[0] / SCREEN_WIDTH,
                mushroom.pos[1] / SCREEN_HEIGHT
            ])

        for bullet in bullets:
            state.extend([
                bullet.rect.x / SCREEN_WIDTH,
                bullet.rect.y / SCREEN_HEIGHT
            ])

        return state


# Evolving population with variable state length
def evolve_population(population, fitness_scores, max_state_length):
    # Pair each genome with its fitness score
    paired_population = list(zip(fitness_scores, population))

    # Sort by fitness score in descending order
    sorted_population = [genome for _, genome in sorted(paired_population, reverse=True, key=lambda x: x[0])]

    # Select the top-performing genomes
    top_genomes = sorted_population[:len(population)//5]

    # Generate new population through crossover and mutation
    new_population = []
    for _ in range(len(population)):
        parent1, parent2 = random.sample(top_genomes, 2)
        child = BasicGenome(max_state_length)
        # Simple crossover
        child.weights = (parent1.weights + parent2.weights) / 2
        # Mutation
        if random.random() < 0.1:
            child.weights += np.random.normal(0, 0.1, size=child.weights.shape)
        new_population.append(child)
    file2 = open("populations.txt","a")
    file2.write(str(new_population))
    file2.write("\n")
    return new_population

# Main Evolutionary Loop with dynamic state length

# Determine the number of workers
# For ProcessPoolExecutor, it's often beneficial to match the number of CPU cores
#num_workers = os.cpu_count()  # or another number based on your testing
num_workers = 5

if __name__ == "__main__":
    population_size = 50
    generations =1000

    # Assume initial max state length
    max_state_length = 100  # Example starting value
    population = [BasicGenome(max_state_length) for _ in range(population_size)]

    for generation in range(generations):
        print(f"Generation {generation + 1}/{generations}")

        # Determine max state length dynamically based on the game state
        # Here, you can calculate the max_state_length based on actual game conditions

        with concurrent.futures.ThreadPoolExecutor() as executor:
            with concurrent.futures.ProcessPoolExecutor(max_workers=num_workers) as executor:
                futures = {executor.submit(game_loop, genome, idx): idx for idx, genome in enumerate(population)}
                results = [future.result() for future in concurrent.futures.as_completed(futures)]

        # Sort the results based on index to maintain order
        results.sort(key=lambda x: x[1])
        fitness_scores = [result[0] for result in results]
        
        print(fitness_scores)
        file = open("fitness.txt", "a")
        file.write(str(fitness_scores))
        file.write("\n")

        population = evolve_population(population, fitness_scores, max_state_length)
    graph.plot()

    

