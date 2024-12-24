SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
GAME_WIDTH = 400
GAME_HEIGHT = 400
GAME_POS_X = 50
GAME_POS_Y = 50
GAME_SIZE_X = 100
GAME_SIZE_Y = 100
BLACK = (0,0,0)
WHITE = (255,255,255)
RED = (255,0,0)
GREEN = (0,255,0)

def game_to_pixel_conversion(pos):
    new_pos = [0,0]
    new_pos[0] = (GAME_WIDTH/2)/GAME_SIZE_X  * pos[0] + GAME_POS_X + GAME_WIDTH/2
    new_pos[1] = -(GAME_HEIGHT/2)/GAME_SIZE_Y * pos[1] + GAME_POS_Y + GAME_HEIGHT/2
    return new_pos
def game_to_pixel_scale(size):
    new_size = [0,0]
    new_size[0] = (GAME_WIDTH/2)/GAME_SIZE_X  * size[0]
    new_size[1] = (GAME_HEIGHT/2)/GAME_SIZE_Y * size[1]
    return new_size

