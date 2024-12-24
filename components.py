import pygame
#####################COLORS############################
WHITE = (255,255,255)
BLACK = (0,0,0)
GREEN = (0, 255, 0)
GREEN_LIGHT = (144, 238, 144)
GREEN_DARK = (0, 100, 0)
RED = (255, 0, 0)
RED_LIGHT = (255, 182, 193)
RED_DARK = (139, 0, 0)
BLUE = (0, 0, 255)
BLUE_LIGHT = (71, 196, 237)
BLUE_DARK = (0, 0, 139)
YELLOW = (255,255,0)
YELLOW_LIGHT = (255,255,224)
YELLOW_DARK = (204,204,0)
GRAY = (128, 128, 128)
GRAY_LIGHT = (211, 211, 211)
GRAY_DARK = (169, 169, 169)
##################GRID CLASS################################
class GridDisplay:
    def __init__(self,screen,grid_start,grid_end, grid, agent):
        self.grid_start = grid_start
        self.grid_end = grid_end
        self.grid_size = [grid.rows,grid.cols]
        self.cell_width = (grid_end[0] - grid_start[0])/self.grid_size[0]
        self.cell_height = (grid_end[1] - grid_start[1])/self.grid_size[1]
        self.screen = screen
        self.grid = grid
        self.agent = agent
    def drawGrid(self):
        self.updateDisplay()
        for i in range(self.grid_size[0] + 1):
            line_start = [self.grid_start[0] + i * self.cell_width, self.grid_start[1]]
            line_end = [self.grid_start[0] + i * self.cell_width, self.grid_end[1]]
            pygame.draw.line(self.screen, BLACK,line_start, line_end, 1)
        for j in range(self.grid_size[1] + 1):
            line_start = [self.grid_start[0], self.grid_start[1] + j * self.cell_height]
            line_end = [self.grid_end[0], self.grid_start[1] + j * self.cell_height]
            pygame.draw.line(self.screen, BLACK,line_start, line_end, 1)   
    def drawCells(self):
        self.updateDisplay()
        for i in range(self.grid_size[0]):
            for j in range(self.grid_size[1]):
                color = WHITE
                value = self.grid.grid[i][j]
                if (value == "#"):
                    color = BLACK
                elif (value == "&"):
                    color = BLUE
                elif (self.is_int(value)):
                    color = GREEN if int(value) > 0 else RED
                else:
                    color = WHITE
                if (not color == WHITE):
                    rect = pygame.Rect(self.grid_start[0] + i * self.cell_width + 1, self.grid_start[1] + j * self.cell_height + 1, self.cell_width - 1, self.cell_height - 1)
                    pygame.draw.rect(self.screen, color, rect)
                else:
                    #draw reward
                    if (i,j) in self.agent.q_table.keys():
                        color = self.value_to_color((max(self.agent.q_table[(i,j)].values()) / (2 * self.grid_size[0] if self.grid_size[0] > self.grid_size[1] else 2 * self.grid_size[1])))
                    rect = pygame.Rect(self.grid_start[0] + i * self.cell_width + 1, self.grid_start[1] + j * self.cell_height + 1, self.cell_width - 1, self.cell_height - 1)
                    pygame.draw.rect(self.screen,color, rect)
    def detectMouseOnGrid(self,mouse_clicks, mouse_pos):
        left, middle, right = mouse_clicks
        grid_pos_x = int((mouse_pos[0] - self.grid_start[0]) / self.cell_width)
        grid_pos_y = int((mouse_pos[1] - self.grid_start[1]) / self.cell_height)
        if (grid_pos_x < self.grid_size[0] and grid_pos_x >= 0 and grid_pos_y < self.grid_size[1] and grid_pos_y >= 0):
            if (left == 1):
                return grid_pos_x, grid_pos_y, 1
            elif (right == 1):
                return grid_pos_x, grid_pos_y, 0
    def placeOnGrid(self,character,grid_pos_x,grid_pos_y, num):
        if character is not None:
            if num == 1:
                self.grid.placeAtPosition((grid_pos_x,grid_pos_y), character)
            else:
                self.grid.removeAtPosition((grid_pos_x,grid_pos_y))
        if character is None and num == 0:
            self.grid.removeAtPosition((grid_pos_x,grid_pos_y))
        self.grid.updateGrid()
    def updateDisplay(self):
        self.grid_size = [self.grid.rows,self.grid.cols]
        self.cell_width = (self.grid_end[0] - self.grid_start[0])/self.grid_size[0]
        self.cell_height = (self.grid_end[1] - self.grid_start[1])/self.grid_size[1]
    def is_int(self,s):
        try:
            int(s)
            return True
        except ValueError:
            return False
    def interpolate_color(self,value, color1, color2):
        return tuple(
            int(color1[i] + (color2[i] - color1[i]) * value) for i in range(3)
        )

    def value_to_color(self,value):
        # Ensure the value is clamped between -1 and 1
        value = max(-1, min(1, value))
        
        if value <= 0:
            return self.interpolate_color((value + 1) / 1, RED_DARK, RED_LIGHT)
        else:
            return self.interpolate_color(value / 1, GREEN_LIGHT, GREEN_DARK)
##################Button CLASS################################
class Button:
    def __init__(self, top_left, size, normal_color, pressed_color, highlighted_color, border_width, text, text_size, text_color, font=None):
        self.rect = pygame.Rect(top_left, size)
        self.normal_color = normal_color
        self.pressed_color = pressed_color
        self.highlighted_color = highlighted_color
        self.border_width = border_width
        self.text = text
        self.text_size = text_size
        self.font = pygame.font.Font(font, text_size) if font else pygame.font.SysFont(None, text_size)
        self.text_surface = self.font.render(text, True, text_color)
        self.text_rect = self.text_surface.get_rect(center=self.rect.center)
        self.button_pressed = False
        self.mouse_pressed = False
        self.highlighted = False
        self.button_clicked = False
        self.button_was_pressed = False

    def checkHighlighted(self, position):
        if self.rect.collidepoint(position):
            self.highlighted = True
        else:
            self.highlighted = False
    def checkPressed(self, position):
        self.button_pressed = True if self.mouse_pressed and self.rect.collidepoint(position) else False
    def checkClicked(self):
        if self.button_pressed == True:
            if self.button_was_pressed == False:
                self.button_clicked = True
                self.button_was_pressed = True
            else:
                self.button_clicked = False
        else:
            self.button_was_pressed = False
            self.button_clicked = False
    def draw(self, screen):
        if self.button_pressed:
            color = self.pressed_color
        elif self.highlighted:
            color = self.highlighted_color
        else:
            color = self.normal_color

        pygame.draw.rect(screen, color, self.rect)

        if self.border_width > 0:
            pygame.draw.rect(screen, pygame.Color('black'), self.rect, self.border_width)
        screen.blit(self.text_surface, self.text_rect)

    def updateAndDraw(self, screen, mouse_position):
        self.checkHighlighted(mouse_position)
        self.checkPressed(mouse_position)
        self.checkClicked()
        self.draw(screen)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1: 
                self.mouse_pressed = True
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                self.mouse_pressed = False
#################TITLE CLASS#############################

class Title:
    def __init__(self, top_left, size, color, border_width, text, font_size, font_color, font=None):
        self.rect = pygame.Rect(top_left, size)
        self.color = color
        self.border_width = border_width
        self.font = pygame.font.Font(font, font_size) if font else pygame.font.Font(None, font_size)
        self.font_color = font_color
        self.text = text
        self.update_text(text)

    def update_text(self, new_text):
        self.text = new_text
        self.text_surface = self.font.render(self.text, True, self.font_color)
        self.text_rect = self.text_surface.get_rect(center=self.rect.center)

    def draw(self, screen):
        pygame.draw.rect(screen, self.color, self.rect)
        if self.border_width > 0:
            pygame.draw.rect(screen,BLACK, self.rect, self.border_width)
        screen.blit(self.text_surface, self.text_rect)