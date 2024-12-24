import pygame
import random
from player import Player
from wall import Wall
from constant import *
from neat_classes import *
from components import *

pygame.init()
clock = pygame.time.Clock()
screen = pygame.display.set_mode((SCREEN_WIDTH,SCREEN_HEIGHT))
game_window_rect = pygame.Rect(GAME_POS_X,GAME_POS_Y,GAME_WIDTH,GAME_HEIGHT)
num_left_text = Title((GAME_POS_X, GAME_POS_Y + GAME_HEIGHT), (400,50), WHITE, 5, "Players Left", 30, BLACK)
neat_players = []
players = []
walls = []
timer = 0
wall_timer = 0
spawn_time = 1
generation = 0
speed = 3
#neat algorithm
neat = NEAT(6,1,100)
neat.initalizeSpecies()
for species in neat.species:
    for genome in species:
        new_player = Player(genome)
        players.append(new_player)
print(repr(neat))
def drawApplication():
    #draw game window
    pygame.draw.rect(screen, BLACK, game_window_rect, width=5)
    #draw ground line
    pygame.draw.line(screen, BLACK,(GAME_POS_X, GAME_POS_Y + GAME_HEIGHT/2), (GAME_POS_X + GAME_WIDTH, GAME_POS_Y + GAME_HEIGHT/2))
    #draw players
    for p in players:
        player_pixel_pos = game_to_pixel_conversion(p.pos)
        player_pixel_size = game_to_pixel_scale(p.size)
        player_rect = pygame.Rect(player_pixel_pos[0] - player_pixel_size[0]/2,player_pixel_pos[1] - player_pixel_size[1]/2,player_pixel_size[0], player_pixel_size[1])
        pygame.draw.rect(screen, BLACK, player_rect, width=5)
        #draw rays
        pixel_distance = game_to_pixel_scale([p.raycast_distance, p.raycast_distance])
        for i in range(p.raycast_num):
            pygame.draw.circle(screen, GREEN,p.raycast_hit[i], 5)
            if i == 0:
                end_line = (player_pixel_pos[0] + pixel_distance[0] * 1, player_pixel_pos[1] + pixel_distance[1] * 0)
                color = GREEN if p.raycast_hit[i][0] > 0 else RED
                pygame.draw.line(screen, color, player_pixel_pos, end_line)
            elif i % 2 == 0:
                end_line = (player_pixel_pos[0] + pixel_distance[0] * (1 - i * 0.1), player_pixel_pos[1] + pixel_distance[1] * (i * 0.1))
                color = GREEN if p.raycast_hit[i][0] > 0 else RED
                pygame.draw.line(screen, color, player_pixel_pos, end_line)
            else:
                end_line = (player_pixel_pos[0] + pixel_distance[0] * (1 - i * 0.1), player_pixel_pos[1] + pixel_distance[1] * (-i * 0.1))
                color = GREEN if p.raycast_hit[i][0] > 0 else RED
                pygame.draw.line(screen, color, player_pixel_pos, end_line)

    #draw walls
    for wall in walls[:]:
        if wall.pos[0] <= -100 + wall.size[0]:
            walls.remove(wall)
        elif wall.pos[0] < 100 - wall.size[0]:
            wall_pixel_pos = game_to_pixel_conversion(wall.pos)
            wall_pixel_size = game_to_pixel_scale(wall.size)
            wall_rect = pygame.Rect(wall_pixel_pos[0] - wall_pixel_size[0]/2, wall_pixel_pos[1] - wall_pixel_size[1]/2, wall_pixel_size[0], wall_pixel_size[1])
            pygame.draw.rect(screen,BLACK, wall_rect, width = 5)
    #draw text
    num_left_text.draw(screen)
def game_update():
    global timer
    global wall_timer
    global spawn_time
    global players
    global generation
    global speed
    # check if generation is over
    if len(players) == 0 or timer > 30 * speed:
        if (timer > 30 * speed):
            for p in players:
                p.genome.fitness = p.score / speed
        players.clear()
        generation += 1
        print(f"Generation {generation}: ",repr(neat))
        neat.keepFittestGenomes()
        neat.breedWithinSpecies()
        for species in neat.species:
            for genome in species:
                new_player = Player(genome)
                players.append(new_player)
        walls.clear()
        timer = 0
        wall_timer = 0
        spawn_time = 1
    else:
        #check player collisions
        for p in players[:]:
            p.on_ground = (p.pos[1] - p.size[1]/2 <= 0)
            #raycasts
            for i in range(p.raycast_num):
                hits = []
                for wall in walls:
                    origin = game_to_pixel_conversion(p.pos)
                    distance = game_to_pixel_scale([p.raycast_distance, p.raycast_distance])
                    dir = 1 if i % 2 == 0 else -1
                    direction = [(1-i*0.1), (dir * i *0.1)]
                    wall_pixel_pos = game_to_pixel_conversion(wall.pos)
                    wall_pixel_size = game_to_pixel_scale(wall.size)
                    wall_rect = pygame.Rect(wall_pixel_pos[0] - wall_pixel_size[0]/2, wall_pixel_pos[1] - wall_pixel_size[1]/2, wall_pixel_size[0], wall_pixel_size[1])
                    intersection = cast_ray(origin, distance, direction, wall_rect)
                    if intersection is not None:
                        hits.append(intersection)
                p.raycast_hit[i] = min(hits) if len(hits) > 0 else [0,0]
            #player collision
            for w in walls:
                player_pixel_pos = game_to_pixel_conversion(p.pos)
                player_pixel_size = game_to_pixel_scale(p.size)
                player_rect = pygame.Rect(player_pixel_pos[0] - player_pixel_size[0]/2,player_pixel_pos[1] - player_pixel_size[1]/2,player_pixel_size[0], player_pixel_size[1])
                wall_pixel_pos = game_to_pixel_conversion(w.pos)
                wall_pixel_size = game_to_pixel_scale(w.size)
                wall_rect = pygame.Rect(wall_pixel_pos[0] - wall_pixel_size[0]/2, wall_pixel_pos[1] - wall_pixel_size[1]/2, wall_pixel_size[0], wall_pixel_size[1])
                if player_rect.colliderect(wall_rect):
                    p.genome.fitness = p.score / speed
                    players.remove(p)
        #add or destroy walls
        if wall_timer >= spawn_time:
            walls.append(Wall([120,15],10,30,30))
            wall_timer = 0
            spawn_time = random.uniform(2, 4.5)
        #update text
        num_left_text.update_text("Players Left: " + str(len(players)))

def cast_ray(origin, distance, direction, rect):
    end = (origin[0] + distance[0] * direction[0], origin[1] + distance[1] * direction[1])
    pygame.draw.line(screen, BLACK, origin, end)
    clipped_line = rect.clipline(origin,end)
    if clipped_line:
        intersection_point = clipped_line[0]
        return intersection_point
    else:
        return None

running = True
while running:
    #set fps and time delta
    delta_time = speed * clock.tick(60) / 1000
    wall_timer += delta_time
    timer += delta_time
    #get events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False             
    #update
    for p in players:
        p.set_time_step(delta_time)
        p.update()
    for w in walls:
        w.set_time_step(delta_time)
        w.update()
    game_update()
    #draw game
    screen.fill(WHITE)
    drawApplication()
    pygame.display.update()
pygame.quit()